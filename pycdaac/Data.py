from . import Info
from . import Download
from . import Plot
import os
import tarfile
import copy
import netCDF4
import matplotlib.pyplot as plt


class Data():
    def __init__(self, info=None):
        self.info = info
        if self.info is not None:
            self.update_info(info)
        pass

    def update_info(self, info):
        self.info = info
        self.get_content(info)

    def get_content(self, info):
        # print('upward_self')
        data_info = info.data_info
        if data_info['data_base'] == 'COSMIC' and \
                data_info['data_type'] == 'podTec':
            self.content = Data_GRACE_podTec(info)
            return True
        if data_info['data_base'] == 'GRACE' and \
                data_info['data_type'] == 'podTec':
            self.content = Data_GRACE_podTec(info)
            return True
        self.content = Data_base(info)

    pass


class Data_base():
    def __init__(self, info):
        self.info = copy.deepcopy(info)
        self.filename = info.data_info['filename']
        self.load_nc()
        pass

    def load_nc(self):
        try:
            self.nc = netCDF4.Dataset(self.filename)
        except:
            print('error load nc file!')
            self.nc = None
        return self.nc

    def load_data(self):
        nc = self.load_nc()

    def __del__(self):
        try:
            if self.nc is not None:
                self.nc.close()
        except:
            pass


class Data_podTec(Data_base):
    def __init__(self, info):
        super(Data_podTec, self).__init__(info)
        self.load_data()
        # print('Data_podTec')
        pass

    def load_data(self):
        nc = self.nc
        if nc is None:
            return


class Data_GRACE_podTec(Data_podTec):
    def __init__(self, info):
        super(Data_GRACE_podTec, self).__init__(info)
        self.load_data()
        # print('Data_podTec')
        pass

    def load_data(self):
        nc = self.nc
        if nc is None:
            return


class Data_COSMIC_podTec(Data_podTec):
    def __init__(self, info):
        super(Data_COSMIC_podTec, self).__init__(info)
        self.load_data()
        # print('Data_podTec')
        pass

    def load_data(self):
        nc = self.nc
        if nc is None:
            return
