import sys
import time
import zmq
import os

import RPi.GPIO as GPIO
from PySide import QtGui, QtCore
from threadObject import ThreadObject
from config import Config

# Classe zum Stueren der Buttons ueber den GPIO des Raspberry Pi
class Buttons(ThreadObject):
    stopped = QtCore.Signal()                                                                  
    started = QtCore.Signal()
    button1 = 4 # 7
    button2 = 23 # 16
    led1 = 17#12
    led2 = 18#11
    STATE_LIVE_STREAM = 0
    STATE_TAKING_PICTURE = 1
    STATE_PICTURE_SHOWN = 2
    STATE_PRINTING_PICTURE = 3
    msg_recieved = QtCore.Signal(dict)
    def __init__(self, ip, req_port, sub_port):
        super(Buttons,self).__init__()
        self.__running = False
        self.__ctx = None
        self.__req_port = req_port
        self.__sub_port = sub_port
        self.__ip = '127.0.0.1'
        self.__current_image_name = None
        self.__state = self.STATE_LIVE_STREAM

    def __init_zmq(self):
        self.__ctx = zmq.Context()
        self.__req_socket = self.__ctx.socket(zmq.REQ)
        req = "tcp://%s:%s" % (self.__ip,self.__req_port)
        self.__req_socket.connect(req)
        self.__sub_socket = self.__ctx.socket(zmq.SUB)
        self.__sub_socket.setsockopt(zmq.CONFLATE,True)
        sub = "tcp://%s:%s" % (self.__ip,self.__sub_port)
        self.__sub_socket.connect(sub)
        sub_filter = ""
        self.__sub_socket.setsockopt(zmq.SUBSCRIBE, sub_filter)
        
        
    @QtCore.Slot()
    def start(self):
        self.__init_zmq()
        #GPIO.setmode(GPIO.BOARD)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.led1, GPIO.OUT)
        GPIO.setup(self.led2, GPIO.OUT)
	# Zu Beginn ist eine Laufbestaetigung wichtig deswegen mit High beginnen.
        GPIO.output(self.led1, GPIO.HIGH)
        GPIO.output(self.led2, GPIO.HIGH)

	# Event Detection 
	#GPIO.add_event_detect(self.button1, GPIO.FALLING, callback=self.__take_pic(), bouncetime=300)
	#GPIO.add_event_detect(self.button2, GPIO.FALLING, callback=self.__print_pic(), bouncetime=300)

        poller = zmq.Poller()
        poller.register(self.__sub_socket, zmq.POLLIN)
        self.__running = True
        
	# Buttons in einer Schleife ueberpruefen ist eine schlechte Idee
	#(lieber events s.o.)!


        while self.__running:
            #print 'tick', "tcp://%s:%s" % (self.__ip,self.__sub_port)
            button1_pressed = GPIO.input(self.button1)==GPIO.LOW
            button2_pressed = GPIO.input(self.button2)==GPIO.LOW
            #print button1_pressed, button2_pressed
            if button1_pressed and self.__state in [self.STATE_LIVE_STREAM,
                                                    self.STATE_PICTURE_SHOWN]:
                self.__take_pic()
            if button2_pressed:
                self.__print_pic()
            socks = dict(poller.poll(10))
            if self.__sub_socket in socks:
                msg = self.__sub_socket.recv_json()
                if type(msg)==dict and 'event' in msg:
                    self.__process_event(msg)
            if self.__state == self.STATE_PICTURE_SHOWN:
                GPIO.output(self.led2, GPIO.HIGH)
            else:
                GPIO.output(self.led2, GPIO.LOW)

    # Funktion schickt Signal an Camera.py zum fotografieren eines Fotos
    def __take_pic(self):
        self.__req_socket.send_json({'cmd':'take_pic',
                                     'args':[]})
        msg = self.__req_socket.recv_json()
        print msg
        if type(msg)==dict and 'cmdRecieved' in  msg and msg['cmdRecieved']=='take_pic':
            self.__state = self.STATE_TAKING_PICTURE
        

    def __print_pic(self):
        if self.__state == self.STATE_PICTURE_SHOWN:
            self.__req_socket.send_json({'cmd':'print_pic',
                                         'args':[self.__current_image_name]})
            msg = self.__req_socket.recv_json()
            print msg
            if type(msg)==dict and 'cmdRecieved' in  msg and msg['cmdRecieved']=='print_pic':
                self.__state = self.STATE_PRINTING_PICTURE

    # Funktion empfaengt Signal zum steuern der LEDS wieso nicht in class LEDs 
    # Welche events werden hier empfangen.
    # Denke das wir hier nicht andere Siganle abfangen sollten sonder fuenf Events brauchen
    # Events: LED an, LED aus, LED Blinken start, LED Blinken Stop, LED Blinken x-mal  
        
    def __process_event(self, event):
        if event['event'] == "new_image":
            self.__current_image_name = event['image_name']
            self.__state = self.STATE_PICTURE_SHOWN
        elif event['event'] == "count_down_changed":
            self.__state = self.STATE_LIVE_STREAM
            GPIO.output(self.led1, GPIO.HIGH)
            time.sleep(.05)
            GPIO.output(self.led1, GPIO.LOW)
            self.__state = self.STATE_TAKING_PICTURE
        elif event['event'] == "live_stream_activated":
            self.__state = self.STATE_LIVE_STREAM
    
    # Funktion zum Blinken der LEDs? (machen wir das nicht schon in process_event
    def __blink(self):
        pass

# Klasse zum Stueren der LEDs
class LEDs(ThreadObject):
    stopped = QtCore.Signal()                                                                  
    started = QtCore.Signal()
    msg_recieved = QtCore.Signal(dict)
    def __init__(self):
        super(LEDs,self).__init__()

    @QtCore.Slot()
    def start(self):
        while self.__running:
            print 'GO'
            time.sleep(1)

import signal

def greatExit(signal, frame):
    print 'Received:', signal
    print orig_sigint
    signal.signal(signal.SIGINT, orig_sigint)
    try:
        print('Closing GPIO Control System save')
        GPIO.cleanup()
        sys.exit(0)
    except KeyboardInterrupt:
        print('Quitting without cleanup')
        sys.exit(1)
        

def main():
    #import signal
    orig_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGUSR1, greatExit)
    
    a = QtGui.QApplication(sys.argv)

    print 'My PID is:', os.getpid()
    
    leds = LEDs()
    buttons = Buttons('127.0.0.1',
                        Config.req_rep_port,
                        Config.pub_sub_port)

    button_thread = Buttons.startThread(buttons)

    sys.exit(a.exec_())
             
    print('Clean exit')
    GPIO.cleanup()           # clean up GPIO on normal exit 

if __name__ == "__main__":
    main()
