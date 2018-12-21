from . import Info
import os
import subprocess
import tarfile


class Download():
    def __init__(self, info=None):
        self.info = info
        self.download_str = 'curl -s -f -u {}:{} https://cdaac-www.cosmic.ucar.edu/cdaac/rest/tarservice/data/{}/{}/{:0>4d}.{:0>3d} -o {}'
        pass

    # @staticmethod
    def untar(self, file):
        doy = file[-7:-4]
        dirname = '{}/{}'.format(os.path.dirname(file), doy)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        tar = tarfile.open(file, 'r')
        nc_files = []
        need_update_plot = False
        for member in tar.getmembers():
            if member.isreg():  # skip if the TarInfo is not files
                member.name = os.path.basename(member.name)  # remove the path by reset it
                save_name = '{}/{}'.format(dirname, member.name)
                nc_files.append(save_name)
                if os.path.isfile(save_name):
                    continue
                need_update_plot = True
                tar.extract(member, dirname)  # extract
        if need_update_plot:
            pass

        Info.remove_empty_folders(dirname)
        self.nc_files = nc_files
        return nc_files

    def get_all(self, info, username, passwd, need_untar):
        all_data = []
        for this_info in info.all_data_info():
            # this_info.get_info()

            this_data = self.get(this_info, username, passwd, False)
            all_data.append(this_data)
        return all_data

        pass

    def get(self, info=None, username=None, passwd=None, need_untar=True, is_all=False):

        if info is None:
            info = self.info
            if info is None:
                print('No info!')
                return None
        if is_all:
            self.get_all(info, username, passwd, need_untar)
        data_info = info.data_info
        path_tar = '{}'.format(data_info['path_save'])

        if os.path.isfile(path_tar):
            print(path_tar)
            if need_untar:
                return self.untar(path_tar)
            else:
                return [path_tar]
        else:
            if username is None or passwd is None:
                print('Need download but no username or passwd')
                return None
            else:
                if self.download(username, passwd, info):
                    print(path_tar)
                    if need_untar:
                        return self.untar(path_tar)
                    else:
                        return [path_tar]
        return []

    def download(self, username, passwd, info=None):
        # cosmic/atmPrf/2018/cosmic_atmPrf_2018.001.tar
        if info is None:
            info = self.info
        data_info = info.data_info
        data_date = data_info['date']
        path_save = data_info['path_save']
        path_save_dir = os.path.dirname(path_save)
        if not os.path.isdir(path_save_dir):
            os.makedirs(path_save_dir)
        try:
            output = subprocess.check_output(self.download_str.format(
                username, passwd, data_info['data_name'],
                data_info['data_type'], data_date.year, data_date.dayofyear,
                path_save
            ), shell=True)
            if output != b'':
                print(output)
        except:
            print('can not download, please check data info! {}'.format(path_save))
            Info.remove_empty_folders(path_save_dir)
            return False
        return True

        pass
