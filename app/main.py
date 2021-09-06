import os
import pandas as pd
import numpy as np
from shutil import copy2
from app.tools.tools import timeit
from app.tools.manipulation import check_lines, check_file_charge
from app.tools.io import path_create, append_to_zip, clean_startup
from app.tools.plots import machine_plots

archive_option = 'copy'  # do_nothing | copy | zip
do_not_delete = True    # Don't delete from Source Input when True

directory = {
    'input': 'E:/PLSA2MES/',
    # 'input': 'D:\PLSA',
    # E:\assets
    'output': 'E:/assets/output/',
    'zip': 'E:/assets/archive/',
    'crap': 'E:/assets/archive/crap/',
    'ansatz': 'E:/assets/archive/RP01_Ansatz/',
    'recipe': 'E:/assets/archive/recipes/',
    'error': 'E:/assets/archive/error',
    'plots': 'E:/assets/html/plots/'
}

files_dict = {
    'csv': 'E:/assets/output/raw.csv'
}


@timeit
def main():
    pd.set_option('display.max_columns', None)

    clean_startup(directory)
    df = dataframe_load(files_dict)
    f_list = file_walker(directory)
    c_list = construct(directory, f_list, df)
    data = make_data(c_list)
    final_df = dataframe_save(files_dict, df, data)
    machine_plots(final_df, plot_path=directory['plots'])
    file_handling(directory, c_list)


def make_data(c_list):
    data = []
    for c in c_list:
        if c['summary']:
            data.append(c['summary'])
    return data


def dataframe_load(f_dict):
    if os.path.isfile(f_dict['csv']):
        df_actual = pd.read_csv(f_dict['csv'])
        print(df_actual.info())
        return df_actual
    else:
        return None


def dataframe_save(f_dict, df, new_data):
    df_new = pd.DataFrame(new_data, columns=['charge', 'anlage', 'area', 'product', 'recipe', 'start', 'ende'])
    df_new['start'] = pd.to_datetime(df_new['start'])
    df_new['ende'] = pd.to_datetime(df_new['ende'])
    df_new['diff'] = df_new['ende'] - df_new['start']
    df_new['diffm'] = df_new['diff'] / np.timedelta64(1, 'm')

    if isinstance(df, pd.DataFrame):
        bigdata = df.append(df_new, ignore_index=True)
        bigdata.to_csv(f_dict['csv'], encoding='utf-8', index=False)
        return bigdata
    else:
        df_new.to_csv(files_dict['csv'], encoding='utf-8', index=False)
        return df_new


def file_handling(dirs, c_list):
    for c in c_list:
        if c.get('dst'):
            path_create(os.path.dirname(c['dst']), is_file=False)
            if archive_option == 'copy':
                if do_not_delete:
                    copy2(c['src'], c['dst'])
                else:
                    os.replace(c['src'], c['dst'])
            elif archive_option == 'zip':
                append_to_zip(dirs['zip'] + 'archive.zip', c['src'], c['arcname'])
                if not do_not_delete:
                    os.remove(c['src'])
            else:
                pass
        else:
            if not do_not_delete:
                os.remove(c['src'])


def construct(dirs, f_list, df):
    for f in f_list:
        if isinstance(df, pd.DataFrame):
            is_in_df = check_file_charge(f['name'], df)
        else:
            is_in_df = False

        if is_in_df:
            f['summary'] = None
            pass  # is in df
        else:
            # is not in df
            if f['name'].startswith('SB8'):
                summary = check_lines(f['src'])
                if summary:
                    charge, anlage, area, product, recipe, start, ende = summary
                    if recipe != 'RP01_ANSATZ':
                        if start and ende:
                            arcname = area + '/' + product + '/' + recipe + '/'
                            f['mode'] = 'recipe'
                            f['dst'] = os.path.join(dirs['recipe'] + arcname, f['name'])
                            f['arcname'] = 'recipes/' + arcname
                            f['summary'] = summary
                        else:
                            f['mode'] = 'error'
                            f['dst'] = os.path.join(dirs['error'], f['name'])
                            f['arcname'] = 'error/'
                            f['summary'] = None
                    else:
                        f['mode'] = 'ansatz'
                        f['dst'] = os.path.join(dirs['ansatz'], f['name'])
                        f['arcname'] = 'RP01_Ansatz/'
                        f['summary'] = None
                else:
                    f['mode'] = 'error'
                    f['dst'] = os.path.join(dirs['error'], f['name'])
                    f['arcname'] = 'error/'
                    f['summary'] = None
            else:
                f['mode'] = 'crap'
                f['dst'] = os.path.join(dirs['crap'], f['name'])
                f['arcname'] = 'crap/'
                f['summary'] = None
    return f_list


def file_walker(dirs):
    file_list = []
    if os.path.isdir(dirs['input']):
        for path, dirs, files in os.walk(dirs['input']):
            for file in files:
                ext = file.lower().rpartition('.')[-1]
                if ext in 'xml':
                    filename = os.path.join(path, file)
                    file_list.append({'name': file, 'src': filename})
    return file_list


if __name__ == '__main__':
    main()
