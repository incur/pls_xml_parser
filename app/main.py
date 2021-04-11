import os
import pandas as pd
from app.tools.tools import timeit
from app.tools.manipulation import check_lines, check_file_charge
from app.tools.io import path_create, append_to_zip, clean_startup, file_walker

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


if __name__ == '__main__':
    main()
