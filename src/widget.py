from PySide import QtGui, QtCore
import time

from config import Config

class Button(QtGui.QGraphicsItem):
    bg = QtGui.QBrush(QtGui.QColor(0,0,0,150))
    bg_over = QtGui.QBrush(QtGui.QColor(200,0,0,150))
    text_pen = QtGui.QPen(QtGui.QColor(255,255,255))
    #font = QtGui.QFont("schu",20)
    def __init__(self, text, callback):
        super(Button,self).__init__()
        super(Button,self).setAcceptHoverEvents(True)
        self.__text = text
        self.__r = None
        self.__m = None
        self.__callback = callback
        self.__over = False
        self.__font = QtGui.QFont("Arial",20)
        #
        self.setZValue(1)
        
    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemSceneHasChanged:
            self.__font = value.font()
            self.__font.setPixelSize(20)
            self.set_text(self.__text)
        return super(Button,self).itemChange(change, value)
        
    def hoverEnterEvent(self, e):
        super(Button,self).hoverEnterEvent(e)
        self.__over = True
        self.update()
        
    def hoverLeaveEvent(self, e):
        super(Button,self).hoverLeaveEvent(e)
        self.__over = False
        self.update()
        
    def mousePressEvent(self,e):
        self.__callback()
        
    def boundingRect(self):
        if self.__r:
            return self.__r
        else:
            return QtCore.QRectF(0,0,0,0)
            
    def height(self):
        return self.__r.height()
        
    def width(self):
        return self.__r.width()
        
    def paint(self, painter, option, widget):
        if self.__r:
            if self.__over:
                painter.fillRect(self.__r,self.bg_over)
            else:
                painter.fillRect(self.__r,self.bg)
            
            painter.setPen(self.text_pen)
            painter.setFont(self.__font)
            painter.drawText(0,0,self.__text)
        
    def set_text(self, text):
        #if self.__m == None:
        m = QtGui.QFontMetrics(self.__font)
        self.__r = m.boundingRect(text)
        self.__r.adjust(-2,0,2,0)
        self.__text = text
        self.update()

class PreviewItem(QtGui.QGraphicsItem):
    text_bg=QtGui.QBrush(QtGui.QColor(0,0,0,150))
    text_pen=QtGui.QPen(QtGui.QColor(255,255,255))
    outline_pen_taking_picture=QtGui.QPen(QtGui.QColor(255,0,0),3)
    def __init__(self,width,height):
        super(PreviewItem,self).__init__()
        self.__width = width
        self.__height = height
        self.__image = None
        self.__image_name = None
        self.__image_rect = self.boundingRect()
        self.__m = None
        self.__taking_picture = False
        self.__show_count_down = False
        self.__count_down = 0
        self.__show_arrow = False
        self.setZValue(0)
        self.__arrow = QtGui.QPixmap('data/arrow.png')
        
    def height(self):
        return self.__height
        
    def width(self):
        return self.__width
        
    def boundingRect(self):
        return QtCore.QRectF(0,0,self.__width,self.__height)
        
    def paint(self, painter, option, widget):
        if self.__image:
            painter.drawImage(self.__image_rect,self.__image)
        if self.__image_name:
            self.__r.moveTo(self.__width-self.__r.width(),
                          self.__height-self.__r.height()-2)
            painter.fillRect(self.__r,self.text_bg)
            painter.setPen(self.text_pen)
            painter.font().setPixelSize(12)
            painter.drawText(self.__r,self.__image_name)
            
        if self.__taking_picture:
            painter.setPen(self.outline_pen_taking_picture)
            painter.drawRect(self.boundingRect())
            
        if self.__show_arrow:
            painter.drawPixmap(self.__width-self.__arrow.width(),self.__height/2-self.__arrow.height()/2,self.__arrow)
            
        if self.__show_count_down:
            f = painter.font()
            size = 400
            f.setPixelSize(size)
            m = QtGui.QFontMetrics(f)
            painter.setFont(f)
            count_down_str = str(self.__count_down)
            painter.drawText(self.__width/2-m.width(count_down_str)/2,self.__height/2+m.height()/4,count_down_str)


    def set_image(self,image):
        self.__image = image
        self.update()
        
    def set_image_name(self, image_name):
        if self.__m == None:
            self.__m = QtGui.QFontMetrics(self.scene().font())
        self.__r = self.__m.boundingRect(self.__image_name)
        self.__r.adjust(-2,-2,2,2)
        self.__image_name = image_name
        self.update()
        
    def get_image_name(self):
        return self.__image_name
        
    def count_down_started(self):
        self.__taking_picture = True
        self.__image_name = 'Vorschau'
        
    def count_down_changed(self, n):
        self.__count_down = n
        if self.__count_down <= Config.show_count_down:
            if self.__count_down <= 1:
                self.__show_arrow = True
            self.__show_count_down = True
            self.update()

    def pic_taken(self,name):
        self.__taking_picture = False
        self.__show_count_down = False
        self.__show_arrow = False
        self.update()

class Scene(QtGui.QGraphicsScene):
    take_pic = QtCore.Signal()
    print_pic = QtCore.Signal(str)
    def __init__(self,slide_show,camera,printer):
        super(Scene,self).__init__()
        self.__button_timer = QtCore.QTimer.singleShot(1000*Config.button_hide_time, self.__hide_buttons)
        self.__slide_show = slide_show
        self.__camera = camera
        self.__printer = printer
        self.__preview_item = None
        self.__take_pic_button = None
        self.__print_pic_button = None
        self.__camera.new_preview_image.connect(self.__update_preview)
        self.__slide_show.show_image.connect(self.__update_preview)

    def _take_pic(self):
        self.take_pic.emit()
        
    def _print_pic(self):
        if self.__preview_item:
            image_name = self.__preview_item.get_image_name()
            if image_name == None:
                return
            self.print_pic.emit(image_name)
        
    def __update_preview(self,image):
        if self.__preview_item==None:
            self.__preview_item = PreviewItem(image.width(),image.height())
            self.__camera.count_down_changed.connect(self.__preview_item.count_down_changed)
            self.__camera.count_down_started.connect(self.__preview_item.count_down_started)
            self.__camera.pic_taken.connect(self.__preview_item.pic_taken)
            self.__slide_show.show_image_name.connect(self.__preview_item.set_image_name)
            self.addItem(self.__preview_item)
            self.__take_pic_button = Button('Foto aufnehmen', self._take_pic)
            self.addItem(self.__take_pic_button)
            self.__print_pic_button = Button('Foto drucken', self._print_pic)
            self.addItem(self.__print_pic_button)
            self.__take_pic_button.setPos(50,self.__preview_item.height()-6)
            self.__print_pic_button.setPos(50 +20+ self.__take_pic_button.width(),self.__preview_item.height()-6)
        self.__preview_item.set_image(image)
        
    def __hide_buttons(self):
        if self.__take_pic_button:
            self.__take_pic_button.hide()
        if self.__print_pic_button:
            self.__print_pic_button.hide()
    def mouseMoveEvent(self, e):
        if self.__take_pic_button and not self.__take_pic_button.isVisible():
            self.__take_pic_button.show()
        if self.__print_pic_button and not self.__print_pic_button.isVisible():
            self.__print_pic_button.show()
        self.__button_timer = QtCore.QTimer.singleShot(1000*Config.button_hide_time, self.__hide_buttons)
        super(Scene,self).mouseMoveEvent(e)
        

class GraphicsView(QtGui.QGraphicsView):
    exit_app = QtCore.Signal()
    def __init__(self,parent):
        super(GraphicsView,self).__init__(parent=parent)
        self.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.black, QtCore.Qt.SolidPattern))
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.setMouseTracking(True)
        
    def setScene(self, scene):
        scene.sceneRectChanged.connect(self.__fit_view)
        super(GraphicsView,self).setScene(scene)
        self.__fit_view(scene.sceneRect())
        
    def __fit_view(self, scene_rect):
        self.fitInView(scene_rect,QtCore.Qt.KeepAspectRatio)
        
    def resizeEvent(self, e):
        super(GraphicsView,self).resizeEvent(e)
        scene = self.scene()
        if scene:
            self.__fit_view(scene.sceneRect())
            
    def keyPressEvent(self, e):
        super(GraphicsView,self).keyPressEvent(e)
        if e.key() == QtCore.Qt.Key_Print:
            self.scene()._print_pic()
        elif e.key() == QtCore.Qt.Key_Space:
            self.scene()._take_pic()
        elif e.key() == QtCore.Qt.Key_Escape:
            self.exit_app.emit()
        
class Widget(QtGui.QWidget):
    def __init__(self,slide_show,camera,printer,parent=None):
        super(Widget,self).__init__(parent=parent)
        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.setStyleSheet("background-color:grey;")
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.grapicsView = GraphicsView(self)
        self.grapicsView.setScene(Scene(slide_show,camera,printer))
        layout.addWidget(self.grapicsView)
        
