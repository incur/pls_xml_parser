import xml.etree.ElementTree as Et
import logging

logger = logging.getLogger(__name__)


def main():
    # tree = Et.parse('assets/input/SB8_2-127-22264460_7441655_7441659_7441655_7441659_29488.xml')
    tree = Et.parse('assets/input/SB8_2-127-22264460_7442042_7442046_7442042_7442046_29492.xml')
    # tree = Et.parse('assets/input/SB8_2-127-22264460_7439203_7439212_7439203_7439212_29465.xml')
    root = tree.getroot()

    pre = '{SIMATIC_BATCH_V8_1_0}'

    charge = root.findall(f'.{pre}Cr[@name]')[0].get('name')
    product = root.findall(f'{pre}Cr[@productname]')[0].get('productname')
    recipe = root.findall(f'{pre}Cr[@recipeprocedurename]')[0].get('recipeprocedurename')
    start = root.findall(f'.{pre}Cr/{pre}Batchmessagecltn/{pre}Messagecltn/*[@eventname="Rezeptoperation läuft"]')
    ende = root.findall(f'.{pre}Cr/{pre}Batchmessagecltn/{pre}Messagecltn/*[@eventname="Rezeptoperation beendet"]')
    origin = start[0].attrib.get('origin').split('/')
    area = start[0].attrib.get('area')

    if recipe != 'RP01_ANSATZ':
        print(charge, area, product, recipe)
        print(origin)
        if len(start) == 1 and len(start) == 1:
            print(start[0].attrib)
            print(ende[0].attrib)
        else:
            print('Start:', len(start))
            for item in start:
                print(item.attrib)
            print()
            print('Ende:', len(ende))
            for item in ende:
                print(item.attrib)
            print('Start und Ende sind nicht abzugrenzen')
    else:
        print('Ansatzrezepte werden noch nicht unterstützt')


if __name__ == '__main__':
    main()
