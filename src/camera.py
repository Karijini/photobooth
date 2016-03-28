import zmq
import time
import gphoto2 as gp
import io
from collections import OrderedDict
import ConfigParser

from PySide import QtGui, QtCore
from threadObject import ThreadObject
from config import Config

camera_preview_port = 5558

class Camera(ThreadObject):
    new_preview_image = QtCore.Signal(QtGui.QImage)
    pic_taken = QtCore.Signal(str)
    live_stream_activated = QtCore.Signal()
    #start = QtCore.Signal()
    stopped = QtCore.Signal()
    use_real_camera = True
    countdown_pen = QtGui.QPen(QtGui.QColor(255,0,0),400)
    count_down_changed = QtCore.Signal(int)
    threads = {}
    draw_countdown = False
    def __init__(self,previewPort=5558):
        super(Camera,self).__init__()
        self.__previewport = camera_preview_port
        self.__camera = None #holds gphoto instance of camera
        self.__context = None
        self.__running = False
        self.__preview = False
        self.__commands = []
        self.__count_down_start = None
        self.__show_pic_start = None
        self.__preview_image = None
        self.__count_down = Config.count_down_time
        self.__show_pic_time = Config.show_pic_time
        self.__count_down_n = 0
        self.__preview_settings = {}
        self.__capture_settings = {}
        self.__cfg_file_path = Config.camera_cfg
        self.__watcher = None
        self.__preview_width = 1200
        self.__preview_height = 800
        
    def set_preview_size(self, width, height):
        self.__preview_width = width
        self.__preview_height = height
        
    def __init_camera(self):
        error, self.__camera = gp.gp_camera_new()
        self.__context = gp.gp_context_new()
        error = gp.gp_camera_init(self.__camera, self.__context)
        error, text = gp.gp_camera_get_summary(self.__camera, self.__context)
        #print('Summary')
        #('=======')
        #print(text.text)
        self.__config = gp.check_result(gp.gp_camera_get_config(self.__camera, self.__context))
        self.__config_dict = OrderedDict()
        self.__walk_config(self.__config,self.__config_dict)
        self.print_settings()
        self.__watcher = QtCore.QFileSystemWatcher([self.__cfg_file_path], self)
        self.__watcher.fileChanged.connect(self.load_settings)
        self.load_settings(self.__cfg_file_path)
        
    def __stop_camera(self):
        gp.check_result(gp.gp_camera_exit(self.__camera, self.__context))
        
    def __init_zmq(self):
        self.__zmq_context = zmq.Context()
        self.__zmq_socket = self.__zmq_context.socket(zmq.PUB)
        self.__zmq_socket.setsockopt(zmq.CONFLATE,True)
        self.__zmq_socket.bind("tcp://*:%i" % self.__previewport)
        
    def __update_config(self):
        gp.check_result(gp.gp_camera_set_config(
            self.__camera, self.__config, self.__context))
            
    def __walk_config(self, widget,  cfg, pname=''):
        child_count = gp.check_result(gp.gp_widget_count_children(widget))
        for n in range(child_count):
            child = gp.check_result(gp.gp_widget_get_child(widget, n))
            label = gp.check_result(gp.gp_widget_get_label(child))
            name = gp.check_result(gp.gp_widget_get_name(child))
            child_type = gp.check_result(gp.gp_widget_get_type(child))
            _name = pname + '/' +name
            _cfg = {'_type':child_type,'_widget':child,'_label':label}
            if child_type != gp.GP_WIDGET_SECTION:
                value = gp.check_result(gp.gp_widget_get_value(child))
                print label, name, value
                _cfg['_value'] = value
                if child_type == gp.GP_WIDGET_RADIO:
                    _cfg['_choice'] = []
                    choice_count = gp.check_result(gp.gp_widget_count_choices(child))
                    for n in range(choice_count):
                        choice = gp.check_result(gp.gp_widget_get_choice(child, n))
                        if choice:
                            _cfg['_choice'].append(choice)
                if child_type == gp.GP_WIDGET_RANGE:
                    lo, hi, inc = gp.check_result(gp.gp_widget_get_range(child))
                    _cfg['_lo'] = lo
                    _cfg['_hi'] = hi
                    _cfg['_inc'] = inc
            
            cfg[_name]=_cfg
            self.__walk_config(child,cfg,pname=_name)
            
    def load_settings(self, config_file):
        print 'loading camera settings...'
        self.__preview_settings.clear()
        self.__capture_settings.clear()
        cfg = ConfigParser.ConfigParser()
        cfg.readfp(open(config_file))
        if cfg.has_section('capture'):
            for option in cfg.options('capture'):
                self.__capture_settings[option]=cfg.get('capture',option)
        if cfg.has_section('preview'):
            for option in cfg.options('preview'):
                self.__preview_settings[option]=cfg.get('preview',option)
        self.__apply_settings(self.__preview_settings)
                
    def print_settings(self):
        for name in self.__config_dict:
            print name, self.__config_dict[name].get('_value'),self.__config_dict[name].get('_choice')
            
    def __apply_settings(self, settings):
        """
        takes dict of keys as option names and the corresponding values
        """
        print '__apply_settings'
        for key, value in settings.items():
            if key not in self.__config_dict:
                print 'camera: can not set %s '%(key,value)
                continue
            widget = self.__config_dict[key].get('_widget')
            if not widget:
                print 'camera: can not set %s '%(key,value)
                continue
            print key, value
            gp.check_result(gp.gp_widget_set_value(widget, value))
            self.__config_dict[key]['_value']=value
        gp.check_result(gp.gp_camera_set_config(
            self.__camera, self.__config, self.__context))
    
    @QtCore.Slot()
    def start(self):
        print 'camera'
        self.__init_zmq()
        if self.use_real_camera:
            self.__init_camera()
        self.__running = True
        while self.__running:
            if self.__count_down_start!=None:
                count_down_n = max(int(self.__count_down_start + self.__count_down - time.time()),0)
                if count_down_n!=self.__count_down_n:
                    self.__count_down_n = count_down_n
                    self.count_down_changed.emit(count_down_n)
                if time.time() - self.__count_down_start > self.__count_down:
                    self.__apply_settings(self.__capture_settings)
                    self.__take_pic()
                    self.__count_down_start = None
                    self.__show_pic_start = time.time()
                    
            if self.__show_pic_start!=None:
                if time.time() - self.__show_pic_start > self.__show_pic_time:
                    self.__show_pic_start=None
                    self.start_preview()

            if self.__preview and self.__show_pic_start==None:
                self.__take_preview_pic()
            else:
                time.sleep(.1)
            while len(self.__commands)!=0:
                self.__process_cmd(self.__commands.pop())
            QtGui.QApplication.processEvents()
        if self.use_real_camera:
            self.__stop_camera()
        self.stopped.emit()
        print 'stopped'

    @QtCore.Slot()
    def stop(self):
        print 'stop'
        self.__running = False

    @QtCore.Slot()
    def take_pic(self):
        self.__commands.append({'cmd':'take_pic','args':[]})

    @QtCore.Slot()
    def start_preview(self):
        self.__apply_settings(self.__preview_settings)
        self.__commands.append({'cmd':'start_preview','args':[]})

    @QtCore.Slot()
    def stop_preview(self):
        self.__commands.append({'cmd':'stop_preview','args':[]})
        
    @QtCore.Slot()
    def set_config_value(self, key, value):
        self.__commands.append({'cmd':'stop_preview','args':[]})
        
    def get_config_value(self, key):
        return None

    @QtCore.Slot(dict)
    def process_cmd(self,cmd):
        self.__commands.append(cmd)
    
    def __process_cmd(self, cmd):
        if cmd['cmd']=='take_pic':
            
            self.__count_down_start = time.time()
        elif cmd['cmd']=='start_preview':
            self.__preview = True
            self.live_stream_activated.emit()
            
        elif cmd['cmd']=='stop_preview':
            self.__preview = False

    def __pub_image(self, image_data):
        #kp1, des1 = self.__detector.detectAndCompute(img,None)
        #cv2.drawKeypoints(img,kp1,img)
        #cv2.imwrite('test.jpg',img)
        #print len(image_data)
        self.__zmq_socket.send(image_data)
        #time.sleep(5)

    def __take_preview_pic(self):
        #print 'camera.__take_preview_pic'
        image = QtGui.QImage()
        if not self.use_real_camera:
            image.load('./data/preview.jpg')
        else:
            camera_file = gp.check_result(gp.gp_camera_capture_preview(self.__camera, self.__context))
            file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
            image_data = io.BytesIO(file_data)
            self.__pub_image(image_data.getvalue())
            image.loadFromData(image_data.getvalue())

        if self.__count_down_start!=None and self.draw_countdown:
            p = QtGui.QPainter(image)
            p.setPen(Camera.countdown_pen)
            size = 180
            p.setFont(QtGui.QFont("Arial",size))
            p.drawText((image.width()+size)/2,
                       (image.height()+size)/2,
                       '%i'%(self.__count_down_n))
            p.end()
        #print self.__preview_rect
        image = QtGui.QImage(image).scaledToWidth(self.__preview_width,
                                    transformMode=QtCore.Qt.SmoothTransformation)

        self.new_preview_image.emit(image)
        #time.sleep(1)
            
    def __take_pic(self):
        print 'camera.__take_pic'
        target = './data/preview.jpg'
        if not self.use_real_camera:
            pass
            #self.pic_taken.emit('test.jpg')
        else:
            file_path = gp.check_result(gp.gp_camera_capture(self.__camera, gp.GP_CAPTURE_IMAGE, self.__context))
            camera_file = gp.check_result(gp.gp_camera_file_get(
                self.__camera, file_path.folder, file_path.name,
                gp.GP_FILE_TYPE_NORMAL, self.__context))
            print camera_file
            gp.check_result(gp.gp_file_save(camera_file, target))
        self.pic_taken.emit(target)
        image = QtGui.QImage(target).scaledToWidth(self.__preview_width,
                                    transformMode=QtCore.Qt.SmoothTransformation)
        self.new_preview_image.emit(image)
        #time.sleep(5)
        
