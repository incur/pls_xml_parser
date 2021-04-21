import os
import pandas as pd
import numpy as np
from shutil import copy2
from app.tools.tools import timeit
from app.tools.manipulation import check_lines, check_file_charge
from app.tools.io import path_create, append_to_zip, clean_startup, file_walker

archive_option = 'pass'  # do_nothing | copy | zip
do_not_delete = True    # Don't delete from Source Input when True

directory = {
    'input': 'assets/input/',
    # 'input': 'D:\PLSA',
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
    file_list = file_walker(directory['input'], directory, do_not_delete)

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
                    if not do_not_delete:
                        os.remove(file)
        df_new = pd.DataFrame(data, columns=['charge', 'anlage', 'area', 'product', 'recipe', 'start', 'ende'])
        df_new['start'] = pd.to_datetime(df_new['start'])
        df_new['ende'] = pd.to_datetime(df_new['ende'])
        df_new ['diff'] = df_new ['ende'] - df_new ['start']
        df_new ['diffm'] = df_new ['diff'] / np.timedelta64(1, 'm')
        bigdata = df_actual.append(df_new, ignore_index=True)
        bigdata.to_csv(files_dict['csv'], encoding='utf-8', index=False)
    else:
        data = []
        for file in file_list:
            xml_summary = check_lines(file)
            entry = check_recipe(xml_summary, file)
            if entry:
                data.append(entry)
        df = pd.DataFrame(data, columns=['charge', 'anlage', 'area', 'product', 'recipe', 'start', 'ende'])
        df['start'] = pd.to_datetime(df['start'])
        df['ende'] = pd.to_datetime(df['ende'])
        df['diff'] = df['ende'] - df['start']
        df['diffm'] = df['diff'] / np.timedelta64(1, 'm')
        df.to_csv(files_dict['csv'], encoding='utf-8', index=False)


def check_recipe(summary, file):
    charge, anlage, area, product, recipe, start, ende = summary
    if recipe != 'RP01_ANSATZ':
        if start and ende:
            arcname = area + '/' + product + '/' + recipe + '/'
            if archive_option == 'copy':
                src = file
                dst = os.path.join(directory['recipe'] + arcname, os.path.basename(file))
                path_create(os.path.dirname(dst), is_file=False)
                if not do_not_delete:
                    os.replace(src, dst)
                else:
                    copy2(src, dst)
            elif archive_option == 'zip':
                append_to_zip(directory['zip'] + 'archive.zip', file, 'recipes/' + arcname)
                if not do_not_delete:
                    os.remove(file)
            else:
                pass
        else:
            arcname = 'error/'
            summary = None
            if archive_option == 'copy':
                src = file
                dst = os.path.join(directory['error'], os.path.basename(file))
                if not do_not_delete:
                    os.replace(src, dst)
                else:
                    copy2(src, dst)
            elif archive_option == 'zip':
                append_to_zip(directory['zip'] + 'archive.zip', file, arcname)
                if not do_not_delete:
                    os.remove(file)
            else:
                pass
    else:
        arcname = 'RP01_Ansatz/'
        summary = None
        if archive_option == 'copy':
            src = file
            dst = os.path.join(directory['ansatz'], os.path.basename(file))
            if not do_not_delete:
                os.replace(src, dst)
            else:
                copy2(src, dst)
        elif archive_option == 'zip':
            append_to_zip(directory['zip'] + 'archive.zip', file, arcname)
            if not do_not_delete:
                os.remove(file)
        else:
            pass

    return summary


if __name__ == '__main__':
    main()
