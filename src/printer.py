# -*- coding: utf-8 -*-
from PySide import QtGui, QtCore
import cups # python-cups package zum Drucken

class Printer(QtCore.QObject):
    printing_image = QtCore.Signal(str)
    def __init__(self, library):
        super(Printer,self).__init__()
        self.__library = library

    def print_image(self, image_name):
        # Dateinahmen bestimmen:
        print 'printing:',self.__library.get_image_path(image_name)
        try:
            conn = cups.Connection()
            printers = conn.getPrinters()
            printer_name = printers.keys()[1] # Drucker auswaehlen
            cups.setUser('pi') #Benutzer einstellen
            # Drucken (Drucker, Datei, PrintJob Name, Optionen)
            conn.printFile(printer_name,
                           self.__library.get_image_path(image_name),
                           "Photobooth",{})
            self.printing_image.emit(image_name)
            # Fehler abfangen und ausgeben (z.B. Papierstau oder kein Papier
        except cups.IPPError as (status, description):
            print 'IPP statis is %d' % status
            print 'Meaning:', description
            
    def process_cmd(self,msg):
        print msg
        if msg['cmd']=='print_pic':
            self.print_image(*msg['args'])
