import os
import shutil
from PySide import QtGui, QtCore

class Library(QtCore.QObject):
    thumbnail_dir = 'thumbnails'
    image_dir = 'images'
    image_prefix = 'img'
    thumbnail_prefix = 'thumb'
    image_ext = 'jpg'
    image_added = QtCore.Signal(str)
    def __init__(self, path):
        super(Library,self).__init__()
        self.__path = path
        self.__image_path = os.path.join(path,self.image_dir)
        self.__thumbnail_path = os.path.join(path,self.thumbnail_dir)
        if not os.path.isdir(self.__image_path):
            os.makedirs(self.__image_path)
        if not os.path.isdir(self.__thumbnail_path):
            os.makedirs(self.__thumbnail_path)
        self.__image_names = set()
        self.__init_name_list()

    def __init_name_list(self):
        for f in os.listdir(self.__image_path):
            if not f.endswith(self.image_ext):
                continue
            path = os.path.join(self.__image_path,f)
            if os.path.isfile(path):
                image_name = os.path.splitext(f)[0]
                self.__image_names.add(image_name)

    def get_all_images(self):
        return sorted(list(self.__image_names))

    @QtCore.Slot(str)
    def add_image(self,image_path):
        library_file_name = self.get_next_image_name()
        shutil.copy(image_path, os.path.join(self.__image_path,library_file_name+'.%s'%self.image_ext))
        print library_file_name,os.path.basename(image_path)
        self.__image_names.add(library_file_name)
        self.__generate_thumbnail(library_file_name)
        self.image_added.emit(library_file_name)

    def __generate_thumbnail(self,image_name):
        _path = os.path.join(self.__image_path,image_name+'.%s'%self.image_ext)
        thumbnail_path = os.path.join(self.__thumbnail_path,image_name+'.%s'%self.image_ext)
        i = QtGui.QImage(_path)
        thumbnail = i.scaledToWidth(Config.thumbnail_width)
        thumbnail.save(thumbnail_path)

    def get_next_image_name(self):
        name = '%s%04i'%(self.image_prefix,len(self.__image_names))
        i = len(self.__image_names)
        while name in self.__image_names:
            name = '%s%04i'%(self.image_prefix,i)
            i+=1
        return name

    def get_preview(self,image_name):
        path = os.path.join(self.__thumbnail_path,image_name+'.%s'%self.image_ext)
        print 'preview',path
        if os.path.isfile(path):
            i=QtGui.QImage(path)
            buffer = QtCore.QBuffer()
            buffer.open(QtCore.QIODevice.ReadWrite)
            i.save(buffer,'JPG')
            return buffer.data()
        return None

    def get_image_path(self, image_name):
        path = os.path.join(self.__image_path,image_name+'.%s'%self.image_ext)
        if os.path.isfile(path):
            return path
        return None

    def get_thumbnail_path(self, image_name):
        path = os.path.join(self.__thumbnail_path,image_name+'.%s'%self.image_ext)
        if os.path.isfile(path):
            return path
        return None
