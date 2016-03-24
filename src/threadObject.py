from PySide import QtGui, QtCore
class ThreadObject(QtCore.QObject):
    threads={}
    def __init__(self):
        super(ThreadObject,self).__init__()

    def start(self):
        pass

    @classmethod
    def startThread(cls, instance):
        thread = QtCore.QThread()
        instance.moveToThread(thread)
        thread.started.connect(instance.start)
        thread.start()
        cls.threads[instance]=thread
        return thread
