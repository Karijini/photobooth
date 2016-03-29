from PySide import QtGui, QtCore
import time

from config import Config

class Widget(QtGui.QWidget):
    def __init__(self,camera,server,library,printer,slide_show):
        super(Widget,self).__init__()
        self.setMouseTracking(True)
        self.__desktop = QtGui.QDesktopWidget().geometry()
        
        self.__last_update = time.time()
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.__bg_label = QtGui.QLabel()
        self.__preview_label = QtGui.QLabel()
        
        
        px, py, w, h = Config.preview_ui_pos_size
        posx = self.__desktop.width()*px
        posy = self.__desktop.height()*py
        width = self.__desktop.width()*w
        height = self.__desktop.height()*h
        
        self.__preview_label.resize(width, height)
        self.__preview_label.move(posx,posy)
        
        self.__preview_rect = QtCore.QRect(posx,posy,width,height)
        
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
        self.__slide_show = slide_show

        self.__camera.set_preview_size(width, height)
        self.__camera.new_preview_image.connect(self.__new_preview_image)
        self.__camera.pic_taken.connect(self.__pic_taken)
        self.__camera.count_down_changed.connect(self.__count_down_changed)
        
        self.__slide_show.show_image.connect(self.__new_preview_image)
        

        self.__start_preview_button.clicked.connect(self.__camera.start_preview)
        self.__stop_preview_button.clicked.connect(self.__camera.stop_preview)
        self.__take_pic_button.clicked.connect(self.__camera.take_pic)

        #self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setStyleSheet("background-color:grey;")
        
        self.__bg_pixmap = QtGui.QPixmap('data/bg.png').scaled(self.__desktop.width(),
                                                               self.__desktop.height())
        
        self.__bg_label.setPixmap(self.__bg_pixmap)
        #self.__preview_label.setPixmap(self.__bg_pixmap)
        #print self.__bg_pixmap.width()
        button_height = 40
        self.__start_preview_button.setParent(self)
        self.__start_preview_button.resize(100,button_height)
        self.__start_preview_button.move(300,self.__desktop.height()-button_height)
        
        self.__stop_preview_button.setParent(self)
        self.__stop_preview_button.resize(100,button_height)
        self.__stop_preview_button.move(500,self.__desktop.height()-button_height)
        
        self.__take_pic_button.setParent(self)
        self.__take_pic_button.resize(100,button_height)
        self.__take_pic_button.move(700,self.__desktop.height()-button_height)
        
        self.__count_down_label = QtGui.QLabel()
        self.__count_down_label.setParent(self)
        self.__count_down_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.__count_down_label.resize(width, height)
        self.__count_down_label.move(posx,posy)
        self.__count_down_label.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont("Arial",200,QtGui.QFont.Bold)
        self.__count_down_label.setFont(font)
        self.__count_down_label.setStyleSheet("QLabel {color : red; }")
        self.__button_timer = QtCore.QTimer.singleShot(1000*Config.button_hide_time, self.__hide_buttons)
        
    def mouseMoveEvent(self, e):
        self.__start_preview_button.show()
        self.__stop_preview_button.show()
        self.__take_pic_button.show()
        self.__button_timer = QtCore.QTimer.singleShot(1000*Config.button_hide_time, self.__hide_buttons)
        super(Widget,self).mouseMoveEvent(e)
        
    def __hide_buttons(self):
        self.__start_preview_button.hide()
        self.__stop_preview_button.hide()
        self.__take_pic_button.hide()

    def __new_preview_image(self, image):
        #_image = image.scaledToWidth(self.__preview_rect.width())
        image.scaledToWidth(self.__preview_rect.width())
        _image = image.scaled(self.__preview_rect.width(),self.__preview_rect.height())
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
    def __count_down_changed(self,count_down):
        print count_down
        self.__count_down_label.setText('%i'%count_down)
        if count_down == 0:
            self.__count_down_label.hide()
        else:
            self.__count_down_label.show()
