import xml.etree.ElementTree as Et
from app.tools.tools import timeit
from app.tools.io import path_create, append_to_zip
from app.tools.log import logg_handlers
import pandas as pd
import multiprocessing
import logging
import os

logger = logging.getLogger(__name__)
logg_handlers(False)

archive_option = 'do_nothing'  # do_nothing | copy | zip

dir_input = 'assets/input/'
dir_crap = 'assets/archive/crap/'
dir_ansatz = 'assets/archive/RP01_Ansatz/'

directory = {
    'input': 'assets/input/',
    'output': 'assets/output/',
    'zip': 'assets/archive/',
    'crap': 'assets/archive/crap/',
    'ansatz': 'assets/archive/RP01_Ansatz/',
    'recipe': 'assets/archive/recipes/',
    'error': 'assets/archive/error'
}


def main():
    clean_startup(directory)
    files = file_walker(directory['input'])
    data = []
    for file in files:
        xml_summary = check_xml(file)
        entry = check_recipe(xml_summary, file)
        if entry:
            data.append(entry)
    df = pd.DataFrame(data, columns=['charge', 'area', 'product', 'recipe', 'start', 'end'])
    df.to_csv(directory['output'] + 'raw.csv', encoding='utf-8', index=False)


# Todo: check_xml und check_recipe unabhängiger machen, files und xml_summary zusammenpacken und zwei loops machen

@timeit
def check_xml(file):
    logger.debug(f'File: {file}')
    tree = Et.parse(file)
    root = tree.getroot()

    pre = '{SIMATIC_BATCH_V8_1_0}'
    charge = root.findall(f'.{pre}Cr[@name]')[0].get('name')
    product = root.findall(f'{pre}Cr[@productname]')[0].get('productname')
    recipe = root.findall(f'{pre}Cr[@recipeprocedurename]')[0].get('recipeprocedurename')
    start = root.findall(f'.{pre}Cr/{pre}Batchmessagecltn/{pre}Messagecltn/*[@eventname="Rezeptoperation läuft"]')
    ende = root.findall(f'.{pre}Cr/{pre}Batchmessagecltn/{pre}Messagecltn/*[@eventname="Rezeptoperation beendet"]')
    area = start[0].attrib.get('area')

    return [charge, product, recipe, start, ende, area]


@timeit
def check_recipe(summary, file):
    charge, product, recipe, start, ende, area = summary
    entry = []

    if recipe != 'RP01_ANSATZ':
        if len(start) == 1 and len(ende) == 1:
            entry = [charge, area, product, recipe, start[0].attrib.get('timestamp'), ende[0].attrib.get('timestamp')]
            arcname = area + '/' + product + '/' + recipe + '/'
            if archive_option == 'copy':
                src = file
                dst = os.path.join(directory['recipe'] + arcname, os.path.basename(file))
                path_create(os.path.dirname(dst), is_file=False)
                os.rename(src, dst)
            elif archive_option == 'zip':
                append_to_zip(directory['zip'] + 'archive.zip', file, 'recipes/' + arcname)
                os.remove(file)
            else:
                pass
        else:
            arcname = 'error/'
            if archive_option == 'copy':
                src = file
                dst = os.path.join(directory['error'], os.path.basename(file))
                os.rename(src, dst)
                logger.info(f'Start und Ende sind nicht abzugrenzen, Archived to {dst}')
            elif archive_option == 'zip':
                append_to_zip(directory['zip'] + 'archive.zip', file, arcname)
                os.remove(file)
                logger.info(f'Start und Ende sind nicht abzugrenzen, Archived to zip')
            else:
                pass
    else:
        arcname = 'RP01_Ansatz/'
        if archive_option == 'copy':
            src = file
            dst = os.path.join(directory['ansatz'], os.path.basename(file))
            os.rename(src, dst)
            logger.info(f'Ansatzrezepte werden noch nicht unterstützt, Archived to {dst}')
        elif archive_option == 'zip':
            append_to_zip(directory['zip'] + 'archive.zip', file, arcname)
            os.remove(file)
            logger.info(f'Ansatzrezepte werden noch nicht unterstützt, Archived to zip')
        else:
            pass

    return entry


@timeit
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
                    os.rename(src, dst)
                    logger.info(f'File moved to crap: {file}')
    return file_list


def clean_startup(dir_dict):
    for item in dir_dict:
        path_create(dir_dict[item], is_file=False)


if __name__ == '__main__':
    main()
