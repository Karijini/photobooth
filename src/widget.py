from PySide import QtGui, QtCore
import time

class Widget(QtGui.QWidget):
    def __init__(self,camera,server,library,printer):
        super(Widget,self).__init__()
        self.__preview_rect = QtGui.QDesktopWidget().geometry()
        
        self.__last_update = time.time()
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.__bg_label = QtGui.QLabel()
        self.__preview_label = QtGui.QLabel()
        
        
        
        self.__preview_label.resize(self.__preview_rect.width()-100,self.__preview_rect.height()-300)
        self.__preview_label.move(50,150)
        #b_layout = QtGui.QHBoxLayout(self)
        self.__start_preview_button = QtGui.QPushButton('start_preview')
        #b_layout.addWidget(self.__start_preview_button)
        self.__stop_preview_button = QtGui.QPushButton('stop_preview')
        #b_layout.addWidget(self.__stop_preview_button)
        self.__take_pic_button = QtGui.QPushButton('take_pic')
        #b_layout.addWidget(self.__take_pic_button)
        
        layout.addWidget(self.__bg_label)
        self.__preview_label.setParent(self)
        
        #layout.addLayout(b_layout)
        self.__camera = camera
        self.__server = server
        self.__library = library
        self.__printer = printer

        self.__camera.new_preview_image.connect(self.__new_preview_image)
        self.__camera.pic_taken.connect(self.__pic_taken)

        self.__start_preview_button.clicked.connect(self.__camera.start_preview)
        self.__stop_preview_button.clicked.connect(self.__camera.stop_preview)
        self.__take_pic_button.clicked.connect(self.__camera.take_pic)

        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setStyleSheet("background-color:grey;")
        
        self.__bg_pixmap = QtGui.QPixmap('data/bg.png')
        self.__bg_label.setPixmap(self.__bg_pixmap)
        #self.__preview_label.setPixmap(self.__bg_pixmap)
        #print self.__bg_pixmap.width()
        self.__start_preview_button.setParent(self)
        self.__start_preview_button.resize(100,40)
        self.__start_preview_button.move(300,self.__preview_rect.height()-100)
        
        self.__stop_preview_button.setParent(self)
        self.__stop_preview_button.resize(100,40)
        self.__stop_preview_button.move(500,self.__preview_rect.height()-100)
        
        self.__take_pic_button.setParent(self)
        self.__take_pic_button.resize(100,40)
        self.__take_pic_button.move(700,self.__preview_rect.height()-100)
        #self.__take_pic_button.setGeometry(100,100,200,200)
        

    def __new_preview_image(self, image):
        #_image = image.scaledToWidth(self.__preview_rect.width()/2)
        _image = image.scaled(self.__preview_rect.width()-100,self.__preview_rect.height()-300)
        p = QtGui.QPixmap.fromImage(_image)
        self.__preview_label.setPixmap(p)
        fps = int(1.0 / (time.time()-self.__last_update))
        self.__update_fps(fps)
        self.__last_update = time.time()
        self.update()
    def __pic_taken(self,file_path):
        print 'pic_taken',file_path
    def __update_fps(self,fps):
        self.setWindowTitle('fps:%i'%fps)
