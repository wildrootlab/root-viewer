import configparser
import os
from PIL import Image
import numpy as np

#import dearpygui.dearpygui as dpg
Done = False
class Config():
    def __init__(self):
        if os.name == 'nt':
            __config_path = os.path.join(os.getenv('APPDATA'), '2P-Analyser')
            if not os.path.exists(__config_path):
                os.makedirs(__config_path)
        else:
            __config_path = os.path.join(os.path.expanduser('~'), '.2P-Analyser')
            if not os.path.exists(__config_path):
                os.makedirs(__config_path)


        self.__config = configparser.ConfigParser()
        self.__config.optionxform = lambda option: option
        if os.name == 'nt':
            self.config_dir = os.path.join(os.getenv('APPDATA'), '2P-Analyser')
        else: 
            self.config_dir = os.path.join(os.getenv('HOME'), '.2P-Analyser')
        
        self.__config.read('config')
        self.__config['window']['geometry'] = '100x100'
        self.__config['window']['state'] = 'normal'
        self.__config['window']['opened_path'] = 'C:\\'
        with open('config', 'w') as configfile:
            self.__config.write(configfile)

class Temp():
    def __init__(self):

        if os.name == 'nt':
            self.__config_path_tmp = os.path.join(os.getenv('APPDATA'), '2P-Analyser', 'tmp')
            if not os.path.exists(self.__config_path_tmp):
                os.makedirs(self.__config_path_tmp)
        else:
            self.__config_path_tmp = os.path.join(os.path.expanduser('~'), '.2P-Analyser', 'tmp')
            if not os.path.exists(self.__config_path_tmp):
                os.makedirs(self.__config_path_tmp)
        self.Done = False
        self.__extensions = ("jpg", "jpeg", "png", "bmp", "psd", "gif","hdr","pic","ppm","pgm")

    def images_to_tmp(self, sender, app_data):
        """
        Copy desiered files with proper extension into tmp folder
        """
        # set path for tmp images folder
        self.__config_path_tmp_images = os.path.join(self.__config_path_tmp, 'images')
        if not os.path.exists(self.__config_path_tmp_images):
            os.makedirs(self.__config_path_tmp_images)
        # get list of files from file dialog
        self.directory = os.path.normpath(app_data.get("current_path"))

        num = 1
        # copy files with proper extension into tmp folder
        for file in os.listdir(self.directory):
            if file.endswith(tuple(self.__extensions)):
                os.system(f"copy {os.path.join(self.directory, file)} {os.path.join(self.__config_path_tmp_images,f'{num}.{os.path.splitext(file)[1]}')}")
                num += 1
            # if tif file check bit depth and convert to jpg
            elif file.endswith("tif"):
                im = np.array(Image.open(f"{os.path.join(self.directory, file)}"))
                if im.dtype == 'uint16':
                    image = Image.fromarray(im / np.amax(im) * 255).convert('L')
                    image.save(f"{os.path.join(self.__config_path_tmp_images, f'{num}.png')}")
                else:
                    image = Image.fromarray(im).convert('L')
                    image.save(f"{os.path.join(self.__config_path_tmp_images, f'{num}.png')}")
                num += 1
            else:
                pass

    
    def convert_files(self, sender, app_data):
        """INCOMPLETE"""
        if not os.path.exists(self.__config_path_tmp_images):
            os.makedirs(self.__config_path_tmp_images)

        directory = os.path.normpath(app_data.get("current_path"))
        num = 1
        
        for file in os.listdir(directory):
            if file.endswith("tif"):
                im = np.array(Image.open(f"{os.path.join(directory, file)}"))
                image = Image.fromarray(im / np.amax(im) * 255).convert('L')
                image.save(f"{os.path.join(self.__config_path_tmp_images, f'{num}.png')}")
                num += 1
    
    def del_tmp_img_dir(self, sender, app_data):
        """
        Delete tmp folder
        """
        os.system(f"rmdir {self.self.__config_path_tmp_images}")