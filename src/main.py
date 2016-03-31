import sys
from PySide import QtGui, QtCore
#from camera import Camera
import time
import zmq
#import cv2
import numpy as np
import shutil
import os
import argparse

from threadObject import ThreadObject
from camera import Camera
from library import Library
from server import Server
from printer import Printer
from widget import Widget
from config import Config
#from qrscanner import QRScanner
from slide_show import SlideShow

def main(args):
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    a = QtGui.QApplication(sys.argv)
    library = Library(Config.library_path)
    server = Server('*',
                    Config.req_rep_port,
                    Config.pub_sub_port,
                    library)
    camera = Camera()
    printer = Printer(library)
    slide_show = SlideShow(library)

    server.msg_recieved.connect(camera.process_cmd)
    server.msg_recieved.connect(printer.process_cmd)
    server.msg_recieved.connect(slide_show.process_cmd)
    printer.printing_image.connect(server.printing_image)
    camera.pic_taken.connect(library.add_image)
    camera.count_down_changed.connect(server.count_down_changed)
    camera.live_stream_activated.connect(server.live_stream_activated)
    library.image_added.connect(server.image_added_to_lib)
    
    #qrscanner = QRScanner()
    #camera.new_preview_image.connect(qrscanner.new_preview_image)

    server_thread = Server.startThread(server)
    camera_thread = Camera.startThread(camera)
    
    #camera_thread.started.connect(camera.start_preview)
    #qrscanner_thread = QRScanner.startThread(qrscanner)
    
    def exit_app():
        print 'stopping camera'
        camera.stop()
        print camera_thread.wait()
        print 'stopping server'
        server.stop()
        #print server_thread.wait()
        print 'exit'
        a.quit()
    
    if not args.no_ui:
        #w = Widget(camera,server,library,printer,slide_show)
        w = Widget(slide_show, camera, printer)
        w.grapicsView.scene().take_pic.connect(camera.take_pic)
        w.grapicsView.scene().print_pic.connect(printer.print_pic)
        w.grapicsView.exit_app.connect(exit_app)
        w.show()
        
    
    camera.count_down_started.connect(slide_show.stop)
    library.image_added.connect(slide_show.start)
    for image_name in library.get_all_images():
        slide_show.start(image_name)
        break
        
        
    sys.exit(a.exec_())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='photobooth')
    parser.add_argument('-no_ui', action='store_true')
    args = parser.parse_args()
    main(args)
