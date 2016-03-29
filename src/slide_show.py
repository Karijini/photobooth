import time
import ConfigParser

from PySide import QtGui, QtCore
from threadObject import ThreadObject
from config import Config

class SlideShow(QtCore.QObject):
    show_image = QtCore.Signal(QtGui.QImage)
    def __init__(self,library):
        super(SlideShow,self).__init__()
        self.__library = library
        library.image_added.connect(self.image_added_to_lib)
        self.__running = False
        self.__active = False
        self.__image_names = library.get_all_images()
        self.__current_index = len(self.__image_names)-1
        self.__next_pic_timer = QtCore.QTimer()
        self.__next_pic_timer.timeout.connect(self.__next_image)
    
    @QtCore.Slot()
    def start(self):
        self.__next_pic_timer.start(1000)
        
    @QtCore.Slot()
    def stop(self):
        self.__next_pic_timer.stop()
               
    def __next_image(self):
        image_name = self.__image_names[self.__current_index]
        image_path = self.__library.get_thumbnail_path(image_name)
        print image_path
        img = QtGui.QImage(image_path)
        self.show_image.emit(img)
        if self.__current_index == 0:
            self.__current_index = len(self.__image_names)-1
        else:
            self.__current_index -= 1
    
    @QtCore.Slot()
    def image_added_to_lib(self, image_name):
        self.__image_names.append(image_name)
        print image_name, self.__library.get_thumbnail_path(image_name)
        #library.image_added.connect(server.image_added_to_lib)
        #self.__current_index = self.__image_names.index(image_name)
        #self.start()
