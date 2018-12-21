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
        print('upward_self')
        data_info = info.data_info
        if data_info['data_base'] == 'GRACE' and \
                data_info['data_type'] == 'podTec':
            self.content = Data_GRACE_podTec(info)

    pass


class Data_base():
    def __init__(self, info):
        self.info = copy.deepcopy(info)
        self.filename = info.data_info['filename']
        self.nc = None
        pass

    def load_nc(self):
        try:
            self.nc = netCDF4.Dataset(self.filename)
        except:
            self.nc = None
        return True

    def __del__(self):
        try:
            if self.nc is not None:
                self.nc.close()
        except:
            pass


class Data_GRACE_podTec(Data_base):
    def __init__(self, info):
        super(Data_GRACE_podTec, self).__init__(info)
        self.load_data()
        # print('Data_podTec')
        pass

    def load_data(self):
        if not super(Data_GRACE_podTec, self).load_nc():
            print('error load nc file!')
            return False
        nc = self.nc
