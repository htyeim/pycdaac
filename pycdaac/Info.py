from lxml import html
import os
import pandas as pd
import copy
import urllib
import re


def remove_empty_folders(path, removeRoot=True):
    'Function to remove empty folders'
    if not os.path.isdir(path):
        return
    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                remove_empty_folders(fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0 and removeRoot:
        print("Removing empty folder: {}".format(path))
        os.rmdir(path)
        remove_empty_folders('{}/..'.format(path))


class Info():
    def __init__(self, path_root='./', path_tar='tar',
                 path_range_html=None, path_type_html=None):
        abs_curdir = os.path.dirname(os.path.abspath(__file__))
        if path_range_html is None:
            path_range_html = '{}/data_range_tbody.html'.format(abs_curdir)
        if path_type_html is None:
            path_type_html = '{}/CDAAC_ COSMIC Data Analysis and Archive Center - Data Products.html'.format(
                abs_curdir)
        self.path = {
            'root': path_root,
            'tar': path_tar,
            'range_html': path_range_html,
            'product.html': path_type_html,
        }
        self.all = False
        self.load_data_range_html()
        self.load_possible_data_type()
        pass

    def load_data_range_html(self):

        try:
            data_url = 'https://cdaac-www.cosmic.ucar.edu/cdaac/dataAve.js'
            with urllib.request.urlopen(data_url) as f:
                data = f.read().decode('utf-8')
            data_re = re.findall('document.write\(.?(\<.*?\>).?\)', data)
            bsdata = html.fromstring(''.join(data_re))
            bsdata = bsdata.getchildren()[1]
        except:

            path_html = self.path['range_html']
            with open(path_html, 'r') as f:
                bsdata = html.fromstring(f.read())

        trs = bsdata.getchildren()
        column_name = [td.getchildren()[0].getchildren()[0].text for td in trs[0]]
        rows = {}
        for i in trs[1:]:
            this_row = {column_name[0]: i.getchildren()[0].getchildren()[1].text}
            for j, jname in enumerate(column_name[1:]):
                jc = i[j + 1].getchildren()[0].getchildren()
                if len(jc) == 7:
                    this_cell = {'name': jc[0].text,
                                 'date': jc[3].text,
                                 'available': jc[6].text}
                else:
                    this_cell = {'name': None,
                                 "date": None,
                                 "available": None}
                this_row[jname] = this_cell
                rows[this_row[column_name[0]]] = this_row
                # this_row[j] =
        base_info = copy.deepcopy(rows)

        for key, value in base_info.items():
            value['data'] = []
            for j, jname in enumerate(column_name[1:]):
                this_cell = value[jname]
                if this_cell['available'] is None:
                    continue
                split_str = [i.strip() for i in this_cell['date'].split('-')]
                split_str = [i.split('.') for i in split_str]
                this_cell['date'] = [pd.Timestamp(year=int(i[0]), month=1, day=1) + pd.Timedelta(days=int(i[1]))
                                     for i in split_str]

                if this_cell['available'] == 'daily tar files per data type':
                    this_cell['available'] = ['tar']
                if this_cell['available'] == 'single files and FTP':
                    this_cell['available'] = ['tar', 'ftp']
                value['data'].append(this_cell)

        self.base_info = base_info
        pass

    def load_possible_data_type(self):
        path_html = self.path['product.html']
        with open(path_html, 'r') as f:
            bsdata = html.fromstring(f.read())
        trs = bsdata.getchildren()
        a = bsdata.getchildren()[1].getchildren()[1].getchildren()[0] \
            .getchildren()[6].getchildren()[0].getchildren()[1].getchildren()[1] \
            .getchildren()[2].getchildren()[1].getchildren()[0].getchildren()[0] \
            .getchildren()[0].getchildren()
        a_len = len(a)
        # index = 29  # 30 cosmic
        tags = ['p', 'font', 'b']
        tags_len = len(tags)
        i = -1
        data_types = []
        while i < a_len - 1:
            i += 1
            this_i = a[i]
            itag = 1
            for itag in range(tags_len):
                if this_i.tag != tags[itag]:
                    break
                this_pc = this_i.getchildren()
                if len(this_pc) != 1:
                    break
                this_i = this_pc[0]
            if itag == 2 and this_i.tag == tags[-1]:
                while i < a_len:
                    i += 1
                    this_ul = a[i]
                    if this_ul.tag != 'ul':
                        break
                    for this_li in this_ul.getchildren():
                        if this_li.tag != 'li':
                            continue
                        for item in this_li.getchildren()[0].getchildren():
                            if item.tag != 'li':
                                continue

                            data_types.append(item.getchildren()[0].text_content()[:-1])
                i -= 1
                pass
        data_types_dict = {}
        for i in data_types:
            data_types_dict[i.lower()] = i
        self.data_types = data_types_dict

    def get_info(self):
        print(self.data_info)
        pass

    def all_data_info(self, year=None, doy=None):
        base_info = self.base_info
        data_types = self.data_types
        ori_data_info = self.data_info
        ori_data_base = ori_data_info['data_base']
        ori_data_type = ori_data_info['data_type']
        ori_data_year = ori_data_info['date'].year
        ori_data_doy = ori_data_info['date'].dayofyear
        if year is None or doy is None:
            year = ori_data_year
            doy = ori_data_doy
        all_possible_len = len(base_info) * len(data_types)
        count = -1
        for i, ki in base_info.items():
            for j, kj in data_types.items():
                count += 1
                if self.add_data_info(i, year, doy, kj):
                    print('all_possible: {:>3d}/{:>3d}: {} {}'.format(count, all_possible_len, i, kj))
                    yield self
        self.add_data_info(ori_data_base, ori_data_year, ori_data_doy, ori_data_type)

        pass

    def add_data_info(self, data_base='cosmic', year=2017, doy=1, data_type='atmPrf', ):
        base_info = self.base_info
        data_info_base = data_base.upper()
        if data_info_base not in base_info:
            print('error data base!')
            return False
        data_types = self.data_types
        data_type = data_type.lower()
        if data_type not in data_types:
            print('error data type!')
            return False
        data_type = data_types[data_type]
        data_info_date = pd.Timestamp(year=year, month=1, day=1) + pd.Timedelta(days=doy - 1)
        data_info_name = None

        for ivalue in base_info[data_info_base]['data']:
            if data_info_date >= ivalue['date'][0] \
                    and data_info_date <= ivalue['date'][1]:
                data_info_name = ivalue['name']
        if data_info_name is None:
            return False
        data_path = '{}/{}/{:0>4d}/{}_{}_{:0>4d}.{:0>3d}.tar' \
            .format(data_info_name, data_type, data_info_date.year,
                    data_info_name, data_type, data_info_date.year, data_info_date.dayofyear)
        self.data_info = {
            'data_base': data_info_base,
            'date': data_info_date,
            'data_type': data_type,
            'data_name': data_info_name,
            "data_path": data_path,
            "path_save": '{}/{}'.format(self.path['root'], data_path)
            # 'cosmic / atmPrf / 2018 / cosmic_atmPrf_2018.001.tar'
        }
        return True
        pass

    def set_file_name(self, filename):
        self.data_info['filename'] = filename
