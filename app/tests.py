import xml.etree.ElementTree as Et
import logging
import os
import pandas as pd

logger = logging.getLogger(__name__)

# TODO: Check charge before open file in csv


def main():
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_columns', 1000)
    csv_file = 'assets/output/raw.csv'
    if os.path.isfile(csv_file):
        df = pd.read_csv(csv_file)
        print(df.head())
        print('Unique Charge:', df['charge'].nunique())
        print('Unique Products:', df['product'].unique())
        print('Unique Recipes:', df['recipe'].unique())
        print('Unique Areas:', df['area'].unique())

        if '6273951_62739d56' in df['charge'].unique():
            print('yes')
        else:
            print('No')

        # print(df.loc[(df['area'] == 'Partikelfiltration') & (df['product'] == 'SIP')])


if __name__ == '__main__':
    main()
