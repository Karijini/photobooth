import zmq
import time
import gphoto2 as gp
import io

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
    use_real_camera = False
    countdown_pen = QtGui.QPen(QtGui.QColor(255,0,0),400)
    count_down_changed = QtCore.Signal(int)
    threads = {}
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
        
    def __init_camera(self):
        error, self.__camera = gp.gp_camera_new()
        self.__context = gp.gp_context_new()
        error = gp.gp_camera_init(self.__camera, self.__context)
        error, text = gp.gp_camera_get_summary(self.__camera, self.__context)
        #print('Summary')
        #('=======')
        #print(text.text)
        self.__config = gp.check_result(gp.gp_camera_get_config(self.__camera, self.__context))
        
    def __stop_camera(self):
        gp.check_result(gp.gp_camera_exit(self.__camera, self.__context))
        
    def __init_zmq(self):
        self.__zmq_context = zmq.Context()
        self.__zmq_socket = self.__zmq_context.socket(zmq.PUB)
        self.__zmq_socket.setsockopt(zmq.CONFLATE,True)
        self.__zmq_socket.bind("tcp://*:%i" % self.__previewport)

    @QtCore.Slot()
    def start(self):
        print 'camera'
        self.__init_zmq()
        if self.use_real_camera:
            self.__init_camera()
        self.__running = True
        while self.__running:
            if self.__count_down_start!=None:
                count_down_n = int(self.__count_down_start + self.__count_down - time.time())
                if count_down_n!=self.__count_down_n:
                    self.__count_down_n = count_down_n
                    self.count_down_changed.emit(count_down_n)
                if time.time() - self.__count_down_start > self.__count_down:
                    self.__take_pic()
                    self.__count_down_start = None
                    self.__show_pic_start = time.time()
                    
            if self.__show_pic_start!=None:
                if time.time() - self.__show_pic_start > self.__show_pic_time:
                    self.__show_pic_start=None
                    self.live_stream_activated.emit()

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
        self.__commands.append({'cmd':'start_preview','args':[]})

    @QtCore.Slot()
    def stop_preview(self):
        self.__commands.append({'cmd':'stop_preview','args':[]})

    @QtCore.Slot(dict)
    def process_cmd(self,cmd):
        self.__commands.append(cmd)
    
    def __process_cmd(self, cmd):
        if cmd['cmd']=='take_pic':
            self.__count_down_start = time.time()
        elif cmd['cmd']=='start_preview':
            self.__preview = True
            
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
            image.load('preview.jpg')
        else:
            camera_file = gp.check_result(gp.gp_camera_capture_preview(self.__camera, self.__context))
            file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
            image_data = io.BytesIO(file_data)
            self.__pub_image(image_data.getvalue())
            image.loadFromData(image_data.getvalue())

        if self.__count_down_start!=None:
            p = QtGui.QPainter(image)
            p.setPen(Camera.countdown_pen)
            size = 180
            p.setFont(QtGui.QFont("Arial",size))
            p.drawText((image.width()+size)/2,
                       (image.height()+size)/2,
                       '%i'%(self.__count_down_n))
            p.end()
        #print self.__preview_rect
        
        self.new_preview_image.emit(image)#.scaled(120,80))
        #time.sleep(1)
            
    def __take_pic(self):
        print 'camera.__take_pic'
        target = './test.jpg'
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
        image = QtGui.QImage(target).scaledToWidth(1200)
        self.new_preview_image.emit(image)
        #time.sleep(5)
        
