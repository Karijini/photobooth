from PIL import Image
import StringIO

import zbarlight
import time
import ConfigParser

from PySide import QtGui, QtCore
from threadObject import ThreadObject
from config import Config

class QRScanner(ThreadObject):
    def __init__(self):
        super(QRScanner,self).__init__()
        self.__running = False
        
    @QtCore.Slot()
    def start(self):
        self.__running = True
        while self.__running:
            QtGui.QApplication.processEvents()
            
    @QtCore.Slot()
    def stop(self):
        print 'stop'
        self.__running = False

    @QtCore.Slot(QtGui.QImage)
    def new_preview_image(self, image):
        print image
        buffer = QtCore.QBuffer()
        buffer.open(QtCore.QIODevice.ReadWrite)
        image.save(buffer, "PNG")

        strio = StringIO.StringIO()
        strio.write(buffer.data())
        buffer.close()
        strio.seek(0)
        pil_im = Image.open(strio)
        
        print zbarlight.scan_codes('qrcode', pil_im)
        
        #qImg = image.convertToFormat(QtGui.QImage.Format_Indexed8)
        #print zbarlight.qr_code_scanner(qImg.bits(), qImg.width(), qImg.height())
        #zbar.Image(qImage.width(), qImage.height(), "Y800", qImg.bits(), qImage.width()*qImage.height())
        #n = scanner.scan(image)
        #print n
