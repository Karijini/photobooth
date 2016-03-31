from PySide import QtGui, QtCore

from library import Library
from config import Config

if __name__ == '__main__':
    l = Library(Config.library_path)
    for image_name in l.get_all_images():
        print image_name
        i = QtGui.QImage(l.get_image_path(image_name))
        print i.width()
        print l.get_thumbnail_path(image_name)
        l.generate_thumbnail(image_name)
