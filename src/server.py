import zmq
from PySide import QtGui, QtCore

from threadObject import ThreadObject

class Server(ThreadObject):
    stopped = QtCore.Signal()
    started = QtCore.Signal()
    msg_recieved = QtCore.Signal(dict)
    threads = {}
    def __init__(self, ip, rep_port, pub_port,library):
        super(Server,self).__init__()
        self.__running = False
        self.__ctx = None
        self.__rep_socket = None
        self.__ip = ip
        self.__rep_port = rep_port
        self.__pub_port = pub_port
        self.__library = library

    @QtCore.Slot()
    def start(self):
        self.__running = True
        self.__ctx = zmq.Context()
        a = "tcp://%s:%s" % (self.__ip,self.__rep_port)
        self.__rep_socket = self.__ctx.socket(zmq.REP)
        self.__rep_socket.bind(a)
        self.__pub_socket = self.__ctx.socket(zmq.PUB)
        self.__pub_socket.bind("tcp://*:%i" % self.__pub_port)
        poller = zmq.Poller()
        poller.register(self.__rep_socket, zmq.POLLIN)
        self.started.emit()
        while self.__running:
            QtGui.QApplication.processEvents()
            socks = dict(poller.poll(100))
            if self.__rep_socket in socks:
                msg = self.__rep_socket.recv_json()
                if 'cmd' in msg:
                    print 'msg_recieved:',msg
                    self.msg_recieved.emit(msg)
                    response = self.__process_cmd(msg)
                    if type(response)==dict:
                        self.__rep_socket.send_json(response)
                    else:
                        self.__rep_socket.send(response)
                else:
                    self.__rep_socket.send_json({})
        self.stopped.emit()
        self.thread().terminate()

    def __process_cmd(self, msg):
        print msg
        response = {'cmdRecieved':msg['cmd']}
        if msg['cmd'] == 'load_preview_pic':
            return self.__library.get_preview(*msg['args'])
        if msg['cmd'] == 'get_all_images':
            return {'get_all_imagesResult': self.__library.get_all_images()}
        return response

    @QtCore.Slot() 
    def stop(self):
        print 'STOP'
        self.__running = False

    @QtCore.Slot(str)
    def image_added_to_lib(self, image_name):
        print self, image_name, "tcp://*:%i" % self.__pub_port
        self.__pub_socket.send_json({"event":"new_image","image_name":image_name})

    @QtCore.Slot()
    def live_stream_activated(self):
        print 'live_stream_activated'
        self.__pub_socket.send_json({"event":"live_stream_activated"})

    @QtCore.Slot(int)
    def count_down_changed(self,count_down):
        self.__pub_socket.send_json({"event":"count_down_changed","count_down":count_down})

    @QtCore.Slot(int)
    def printing_image(self,image_name):
        self.__pub_socket.send_json({"event":"printing_image","image_name":image_name})
