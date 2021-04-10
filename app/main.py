from app.tools.tools import timeit
from app.tools.io import path_create, append_to_zip
import os
import re
import pandas as pd
import xml.etree.ElementTree as Et

archive_option = 'copy'  # do_nothing | copy | zip

directory = {
    'input': 'assets/input/',
    'output': 'assets/output/',
    'zip': 'assets/archive/',
    'crap': 'assets/archive/crap/',
    'ansatz': 'assets/archive/RP01_Ansatz/',
    'recipe': 'assets/archive/recipes/',
    'error': 'assets/archive/error'
}

files_dict = {
    'csv': 'assets/output/raw.csv'
}


@timeit
def main_bck():
    clean_startup(directory)
    data = []
    file_list = file_walker(directory['input'])
    for file in file_list:
        xml_summary = check_lines(file)
        entry = check_recipe(xml_summary, file)
        if entry:
            data.append(entry)
    df = pd.DataFrame(data, columns=['charge', 'area', 'product', 'recipe', 'start', 'end'])
    df.to_csv(directory['output'] + 'raw.csv', encoding='utf-8', index=False)


@timeit
def main():
    clean_startup(directory)
    file_list = file_walker(directory['input'])

    if os.path.isfile(files_dict['csv']):
        data = []
        df_actual = pd.read_csv(files_dict['csv'])
        for file in file_list:
            is_in_df = check_file_charge(file, df_actual)
            if not is_in_df:
                xml_summary = check_lines(file)
                entry = check_recipe(xml_summary, file)
                if entry:
                    data.append(entry)
            else:
                if archive_option == 'zip' or archive_option == 'copy':
                    os.remove(file)
        df_new = pd.DataFrame(data, columns=['charge', 'area', 'product', 'recipe','start', 'end'])
        bigdata = df_actual.append(df_new, ignore_index=True)
        bigdata.to_csv(files_dict['csv'], encoding='utf-8', index=False)
    else:
        data = []
        for file in file_list:
            xml_summary = check_lines(file)
            entry = check_recipe(xml_summary, file)
            if entry:
                data.append(entry)
        df = pd.DataFrame(data, columns=['charge', 'area', 'product', 'recipe','start', 'end'])
        df.to_csv(files_dict['csv'], encoding='utf-8', index=False)


def check_recipe(summary, file):
    charge, area, product, recipe, start, ende = summary
    if recipe != 'RP01_ANSATZ':
        if start and ende:
            arcname = area + '/' + product + '/' + recipe + '/'
            if archive_option == 'copy':
                src = file
                dst = os.path.join(directory['recipe'] + arcname, os.path.basename(file))
                path_create(os.path.dirname(dst), is_file=False)
                os.replace(src, dst)
            elif archive_option == 'zip':
                append_to_zip(directory['zip'] + 'archive.zip', file, 'recipes/' + arcname)
                os.remove(file)
            else:
                pass
        else:
            arcname = 'error/'
            summary = None
            if archive_option == 'copy':
                src = file
                dst = os.path.join(directory['error'], os.path.basename(file))
                os.replace(src, dst)
            elif archive_option == 'zip':
                append_to_zip(directory['zip'] + 'archive.zip', file, arcname)
                os.remove(file)
            else:
                pass
    else:
        arcname = 'RP01_Ansatz/'
        summary = None
        if archive_option == 'copy':
            src = file
            dst = os.path.join(directory['ansatz'], os.path.basename(file))
            os.replace(src, dst)
        elif archive_option == 'zip':
            append_to_zip(directory['zip'] + 'archive.zip', file, arcname)
            os.remove(file)
        else:
            pass

    return summary


def check_lines(file):
    lines = search_lines(file, ['<Cr id', 'Rezeptoperation läuft'])
    charge = filter_string(lines[0], "name='", "' hdl=")
    product = filter_string(lines[0], "productname='", "' productcode=")
    recipe = filter_string(lines[0], "recipeprocedurename='", "' recipeprocedureversion=")
    start = filter_string(lines[0], "actstart='", "' actend=")
    ende = filter_string(lines[0], "actend='", "' startmodetype")
    area = filter_string(lines[1], "area='", "' />")
    
    return [charge, area, product, recipe, start, ende]


def search_lines(file, substrings):
    found = [None] * len(substrings)
    with fragile(open(file, encoding='utf-16')) as f:
        for line in f:
            for i, sub in enumerate(substrings):
                if sub in line:
                    found[i] = line
            if all(v is not None for v in found):
                return found
                raise fragile.Break


def filter_string(s, start, end):
    return re.search('%s(.*)%s' % (start, end), s).group(1)


def file_walker(path):
    file_list = []
    if os.path.isdir(path):
        for path, dirs, files in os.walk(path):
            for file in files:
                ext = file.lower().rpartition('.')[-1]
                if ext in 'xml' and file.startswith('SB8'):
                    filename = os.path.join(path, file)
                    file_list.append(filename)
                else:
                    src = os.path.join(path, file)
                    dst = os.path.join(directory['crap'], file)
                    os.replace(src, dst)
    return file_list


def check_file_charge(filename, test_charge):
    splitted_filename = filename.split('_')
    file_charge = splitted_filename[2] + '_' + splitted_filename[3]

    if file_charge in test_charge:
        return True
    else:
        return False


def clean_startup(dir_dict):
    for item in dir_dict:
        path_create(dir_dict[item], is_file=False)


def check_file_charge(filename, df):
    splitted_filename = filename.split('_')
    file_charge = splitted_filename[2] + '_' + splitted_filename[3]

    if file_charge in df['charge'].unique():
        return True
    else:
        return False


class fragile(object):
    class Break(Exception):
      """Break out of the with statement"""

    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value.__enter__()

    def __exit__(self, etype, value, traceback):
        error = self.value.__exit__(etype, value, traceback)
        if etype == self.Break:
            return True
        return error


if __name__ == '__main__':
    main()
