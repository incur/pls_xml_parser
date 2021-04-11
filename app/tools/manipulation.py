import re

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


def check_file_charge(filename, df):
    splitted_filename = filename.split('_')
    file_charge = splitted_filename[2] + '_' + splitted_filename[3]

    if file_charge in df['charge'].unique():
        return True
    else:
        return False
