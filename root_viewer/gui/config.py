import os
import shutil
from napari.settings import get_settings

class Settings:
    def __init__(self):
        self.set_readers()
    
    def set_readers(self):
        # set main reader
        get_settings().plugins.extension2reader = {'*': 'napari-aicsimageio', **get_settings().plugins.extension2reader}
        
        get_settings().plugins.extension2reader = {'*.tif': 'bfio', **get_settings().plugins.extension2reader}



class TempFile:
    if os.name == 'nt':
        config_path_tmp = os.path.join(os.getenv('APPDATA'), '2P-Analyser', 'tmp')
        if not os.path.exists(config_path_tmp):
            os.makedirs(config_path_tmp)
    else:
        config_path_tmp = os.path.join(os.path.expanduser('~'), '.2P-Analyser', 'tmp')
        if not os.path.exists(config_path_tmp):
            os.makedirs(config_path_tmp)
    
    def __init__(self):

        self.__config_path_tmp = TempFile.config_path_tmp
        # set path for tmp images folder
        self.__config_path_tmp_images = os.path.join(self.__config_path_tmp, 'images')

        # list of supported file extensions
        self.__extensions = ("tif", "jpg", "jpeg", "png", "bmp", "psd", "gif", "hdr", "pic", "ppm", "pgm")

    def del_tmp_images(self):
        # clear tmp images folder (sometimes files get included when folder is created)
        for file in os.listdir(self.__config_path_tmp_images):
            os.remove(os.path.join(self.__config_path_tmp_images, file))
    
    @staticmethod
    def get_tmp_path(self):
        return str(self.__config_path_tmp)

    def dir_images_to_tmp(self, directory):
        """
        Copy desiered files with proper extension into tmp folder
        """
        # create tmp images folder if not exists
        if not os.path.exists(self.__config_path_tmp_images):
            os.makedirs(self.__config_path_tmp_images)
        # clear tmp images folder (sometimes files get included when folder is created)
        self.del_tmp_images()
        
        # get directory from file dialog
        self.directory = os.path.normpath(directory)

        num = 1
        # copy files with proper extension into tmp folder
        for file in os.listdir(self.directory):
            if file.endswith(tuple(self.__extensions)):
                shutil.copy(os.path.join(self.directory, file), os.path.join(self.__config_path_tmp_images,f'{num:02d}.{os.path.splitext(file)[1]}'))
                num += 1
            # if tif file check bit depth and convert if neccessary
            else:
                pass