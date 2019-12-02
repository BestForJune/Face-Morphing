#######################################################
#   Author:     Yanjun Chen
#   email:      chen2620@purdue.edu
#   ID:         ee364f21
#   Date:       11.27
#######################################################

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from MorphingGUI import *
from Morphing import *
from PIL import Image, ImageQt

class MorphingApp(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MorphingApp, self).__init__(parent)
        self.setupUi(self)

        #initial state
        self.txtAlpha.setText('0.0')
        self.btnBlend.setDisabled(True)
        self.chkTriangle.setDisabled(True)
        self.txtAlpha.setDisabled(True)

        #useful variables
        self.imgright = None
        self.imgleft = None
        self.leftscene = QGraphicsScene()
        self.rightscene = QGraphicsScene()
        self.blendscene = QGraphicsScene()
        self.alpha = 0
        self.originalpoint = -1
        self.endpoint = -1
        self.leftPointClick = False
        self.rightPointClick = False
        self.presist = False
        self.deleteleft = False
        self.deleteright = False
        self.refresh = False
        self.update = False
        self.leftTriangles = []
        self.rightTriangles = []
        self.rightPointArrs = []
        self.leftPointArrs = []
        self.blendcheck = False

        #connect widgets
        self.btnStart.clicked.connect(self.loadImageleftHandler)
        self.btnEnd.clicked.connect(self.loadImagerightHandler)
        self.chkTriangle.stateChanged.connect(self.showTriangle)
        self.sliAlpha.valueChanged.connect(self.sliderValueChange)
        self.btnBlend.pressed.connect(self.blend)
        self.graStart.mousePressEvent = self.leftImgClicked
        self.graEnd.mousePressEvent = self.rightImgClicked
        self.mousePressEvent = self.Clicked
        self.keyPressEvent = self.KeyPressed

    def Clicked(self, event):
        if self.leftPointClick is False or self.rightPointClick is False:
            return
        self.leftPointClick = False
        self.rightPointClick = False
        self.updateTXTFile()

    def updateTXTFile(self):
        fpstart = open(self.filePathleft+'.points.txt', 'w')
        fpend = open(self.filePathright + '.points.txt', 'w')
        #for i, ele in enumerate(self.leftPointArrs[self.originalpoint + 1:]):
        for i, ele in enumerate(self.leftPointArrs):
            fpstart.write('%.1f %.1f\n'%(ele[0] * (self.xleft / 480), ele[1] * (self.yleft / 360)))
            fpend.write('%.1f %.1f\n'%(self.rightPointArrs[i][0] * (self.xright / 480), self.rightPointArrs[i][1] * (self.yright / 360)))
        fpstart.close()
        fpend.close()
        self.rightscene.addEllipse(QRectF(self.rightPointArrs[len(self.rightPointArrs)-1][0], self.rightPointArrs[len(self.rightPointArrs)-1][1], 7, 7), brush=QBrush(Qt.blue))
        self.leftscene.addEllipse(QRectF(self.leftPointArrs[len(self.leftPointArrs)-1][0], self.leftPointArrs[len(self.leftPointArrs)-1][1], 7, 7), brush=QBrush(Qt.blue))
        self.endpoint = len(self.leftPointArrs) - 1
        if (len(self.rightPointArrs) >= 3):
            self.leftTriangles, self.rightTriangles = self.newLoadTriangles(np.array(self.leftPointArrs), np.array(self.rightPointArrs))
            if self.chkTriangle.isChecked():
                self.update = True
                self.originalpoint = -1
                self.imgright = None
                self.loadImageleft()
                self.loadImageright()

    def KeyPressed(self, event):
        if (event.key() == Qt.Key_Backspace):
            self.deleteleft = True
            self.deleteright = True
            if self.leftPointClick and not self.rightPointClick:
                self.leftPointClick = False
                self.leftPointArrs = self.leftPointArrs[:-1]
                self.deleteright = False
                self.originalpoint = -1
                self.loadImageleft()
            elif self.rightPointClick:
                self.rightPointClick = False
                self.rightPointArrs = self.rightPointArrs[:-1]
                self.deleteleft = False
                self.originalpoint = -1
                self.loadImageright()
            else:
                self.deleteleft = False
                self.deleteright = False

    def leftImgClicked(self, event):
        if self.leftPointClick and self.rightPointClick is False:
            return
        if self.leftPointClick and self.rightPointClick:
            self.leftPointClick = False
            self.rightPointClick = False
            self.updateTXTFile()

        #get point selected by the user
        x,y = (self.graStart.mapToScene(event.pos()).x(), self.graStart.mapToScene(event.pos()).y())
        if x < 0 or y < 0: #invalid point
            return

        self.leftPointArrs.append([round(x - 3, 1),round(y - 3,1)])
        self.leftPointClick = True
        lenth = len(self.leftPointArrs)
        self.leftscene.addEllipse(QRectF(self.leftPointArrs[lenth - 1][0], self.leftPointArrs[lenth - 1][1], 7, 7),
                                  brush=QBrush(Qt.green))

    def rightImgClicked(self, event):
        if self.leftPointClick and self.rightPointClick:
            return
        if self.leftPointClick is False:
            return

        #get point selected by the user
        x,y = (self.graEnd.mapToScene(event.pos()).x(), self.graEnd.mapToScene(event.pos()).y())
        if x < 0 or y < 0: #invalid point
            return

        self.rightPointArrs.append([round(x - 3, 1),round(y - 3,1)])
        self.rightPointClick = True
        lenth = len(self.rightPointArrs)
        self.rightscene.addEllipse(QRectF(self.rightPointArrs[lenth - 1][0], self.rightPointArrs[lenth - 1][1], 7, 7),
                                  brush=QBrush(Qt.green))

    def loadImageleftHandler(self):
        filePath, _ = QFileDialog.getOpenFileName(self, caption='Choose Image ...', filter="Image files (*.png *.jpg)")
        if not filePath:
            return
        self.filePathleft = filePath
        self.leftPointClick = False
        self.originalpoint = -1
        self.endpoint = -1
        self.leftPointArrs = []
        self.rightPointArrs = []
        self.leftTriangles = []
        self.rightTriangles = []
        self.loadImageleft()

    def loadImageleft(self):
        self.yleft = np.shape(imageio.imread(self.filePathleft))[0]
        self.xleft = np.shape(imageio.imread(self.filePathleft))[1]

        self.imgleft = QPixmap(self.filePathleft).scaledToWidth(480-2)
        self.imgleft = QPixmap(self.filePathleft).scaledToHeight(360-2)
        leftImg = Image.open(self.filePathleft).resize([480, 360])
        try:
            self.leftImg = np.uint8(np.array(leftImg.getdata()).reshape(leftImg.size[1], leftImg.size[0]))
        except:
            self.leftImg = np.uint8(np.array(leftImg.getdata()).reshape(leftImg.size[1], leftImg.size[0], 3))
        self.leftscene.addPixmap(self.imgleft)
        self.graStart.setScene(self.leftscene)
        if self.imgleft and self.imgright:
            self.loadPoint()

    def loadImagerightHandler(self):
        filePath, _ = QFileDialog.getOpenFileName(self, caption='Choose Image ...', filter="Image files (*.png *.jpg)")
        if not filePath:
            return
        self.filePathright = filePath
        self.rightPointClick = False
        self.originalpoint = -1
        self.endpoint = -1
        self.leftPointArrs = []
        self.rightPointArrs = []
        self.leftTriangles = []
        self.rightTriangles = []
        self.loadImageright()

    def loadImageright(self):
        self.yright = np.shape(imageio.imread(self.filePathright))[0]
        self.xright = np.shape(imageio.imread(self.filePathright))[1]
        self.imgright = QPixmap(self.filePathright).scaledToWidth(480-2)
        self.imgright = QPixmap(self.filePathright).scaledToHeight(360-2)
        rightImg = Image.open(self.filePathright).resize([480,360])
        try:
            self.rightImg = np.uint8(np.array(rightImg.getdata()).reshape(rightImg.size[1], rightImg.size[0]))
        except:
            self.rightImg = np.uint8(np.array(rightImg.getdata()).reshape(rightImg.size[1], rightImg.size[0], 3))
        self.rightscene.addPixmap(self.imgright)
        self.graEnd.setScene(self.rightscene)
        if self.imgleft and self.imgright:
            self.loadPoint()

    def loadPoint(self):
        try:
            leftPointArrs = np.loadtxt(self.filePathleft + '.txt', dtype="float64")
            rightPointArrs = np.loadtxt(self.filePathright + '.txt', dtype="float64")

            arr = []
            for point in leftPointArrs:
                arr.append([point[0]/(self.xleft / 475), point[1]/(self.yleft / 355)])
                self.originalpoint += 1
                self.leftscene.addEllipse(QRectF(point[0]/(self.xleft / 470), point[1]/(self.yleft / 350), 7, 7), brush=QBrush(Qt.red))
            if self.leftPointArrs == []:
                self.leftPointArrs = arr

            arry = []
            for point in rightPointArrs:
                arry.append([point[0] / (self.xright / 475), point[1] / (self.yright / 355)])
                self.rightscene.addEllipse(QRectF(point[0]/(self.xright / 470), point[1]/(self.yright / 350), 7, 7), brush=QBrush(Qt.red))
            if self.rightPointArrs == []:
                self.rightPointArrs = arry

            if self.endpoint != -1 and (self.endpoint != len(leftPointArrs) - 1 or self.endpoint != len(rightPointArrs) - 1):
                (self.leftTriangles, self.rightTriangles) = self.newLoadTriangles(np.array(self.leftPointArrs[:self.endpoint + 1]), np.array(self.rightPointArrs[:self.endpoint + 1]))
            else:
                (self.leftTriangles, self.rightTriangles) = self.newLoadTriangles(np.array(self.leftPointArrs), np.array(self.rightPointArrs))
            #if self.originalpoint != len(self.leftPointArrs) - 1:
            self.loadadditionpoint()

            self.graStart.fitInView(QGraphicsScene.itemsBoundingRect(self.leftscene), Qt.KeepAspectRatio)
            self.graStart.setScene(self.leftscene)
            self.graEnd.fitInView(QGraphicsScene.itemsBoundingRect(self.rightscene), Qt.KeepAspectRatio)
            self.graEnd.setScene(self.rightscene)
        except IOError:
            self.loadadditionpoint()
        finally:
            self.btnBlend.setDisabled(False)
            self.chkTriangle.setDisabled(False)
            self.txtAlpha.setDisabled(False)

    def loadadditionpoint(self):
        if self.refresh:
            lenth = len(self.leftPointArrs)
            if lenth > 0 and self.endpoint != lenth - 1 and self.originalpoint != lenth - 1:
                for point in self.leftPointArrs[self.originalpoint + 1:-1]:
                    self.leftscene.addEllipse(QRectF(point[0], point[1], 7, 7), brush=QBrush(Qt.blue))
                self.leftscene.addEllipse(QRectF(self.leftPointArrs[lenth - 1][0], self.leftPointArrs[lenth - 1][1], 7, 7), brush=QBrush(Qt.green))
            elif self.endpoint == lenth - 1:
                for point in self.leftPointArrs[self.originalpoint + 1:]:
                    self.leftscene.addEllipse(QRectF(point[0], point[1], 7, 7), brush=QBrush(Qt.blue))

            lenth = len(self.rightPointArrs)
            if lenth > 0 and self.endpoint != lenth - 1 and self.originalpoint != lenth - 1:
                for point in self.rightPointArrs[self.originalpoint + 1:-1]:
                    self.rightscene.addEllipse(QRectF(point[0], point[1], 7, 7), brush=QBrush(Qt.blue))
                self.rightscene.addEllipse(QRectF(self.rightPointArrs[lenth - 1][0], self.rightPointArrs[lenth - 1][1], 7, 7),brush=QBrush(Qt.green))
            elif self.endpoint == lenth - 1:
                for point in self.rightPointArrs[self.originalpoint + 1:]:
                    self.rightscene.addEllipse(QRectF(point[0], point[1], 7, 7), brush=QBrush(Qt.blue))
            self.refresh = False

        if self.update:
            lenth = len(self.leftPointArrs)
            for point in self.leftPointArrs[self.originalpoint + 1:-1]:
                self.leftscene.addEllipse(QRectF(point[0], point[1], 7, 7), brush=QBrush(Qt.blue))
            self.leftscene.addEllipse(QRectF(self.leftPointArrs[lenth - 1][0], self.leftPointArrs[lenth - 1][1], 7, 7),
                                      brush=QBrush(Qt.blue))

            lenth = len(self.rightPointArrs)
            for point in self.rightPointArrs[self.originalpoint + 1:-1]:
                self.rightscene.addEllipse(QRectF(point[0], point[1], 7, 7), brush=QBrush(Qt.blue))
            self.rightscene.addEllipse(
                QRectF(self.rightPointArrs[lenth - 1][0], self.rightPointArrs[lenth - 1][1], 7, 7),
                brush=QBrush(Qt.blue))
            self.update = False

        if self.deleteleft:
            for point in self.leftPointArrs[self.originalpoint + 1:]:
                self.leftscene.addEllipse(QRectF(point[0], point[1], 7, 7), brush=QBrush(Qt.blue))
            #print(self.leftPointArrs[self.originalpoint+1:])
            #print(self.originalpoint)
            #print(len(self.leftPointArrs))
            self.deleteleft = False

        if self.deleteright:
            for point in self.rightPointArrs[self.originalpoint + 1:]:
                self.rightscene.addEllipse(QRectF(point[0], point[1], 7, 7), brush=QBrush(Qt.blue))
            #print(self.rightPointArrs[self.originalpoint + 1:])
            #print(self.originalpoint)
            #print(len(self.rightPointArrs))
            self.deleteright = False

        if self.chkTriangle.isChecked():
            self.showTriangle()

    def showTriangle(self):
        if not self.imgleft and not self.imgright: return
        if self.chkTriangle.isChecked():
            if self.originalpoint != -1 and self.originalpoint == len(self.leftPointArrs) - 1:
                for t in self.leftTriangles:
                    p = t.vertices
                    # add each of the 3 lines in the triangle separately
                    self.leftscene.addLine(p[0][0], p[0][1], p[1][0], p[1][1], QPen(QBrush(Qt.red), 1.0))
                    self.leftscene.addLine(p[1][0], p[1][1], p[2][0], p[2][1], QPen(QBrush(Qt.red), 1.0))
                    self.leftscene.addLine(p[2][0], p[2][1], p[0][0], p[0][1], QPen(QBrush(Qt.red), 1.0))
                for t in self.rightTriangles:
                    p = t.vertices
                    # add each of the 3 lines in the triangle separately
                    self.rightscene.addLine(p[0][0], p[0][1], p[1][0], p[1][1], QPen(QBrush(Qt.red), 1.0))
                    self.rightscene.addLine(p[1][0], p[1][1], p[2][0], p[2][1], QPen(QBrush(Qt.red), 1.0))
                    self.rightscene.addLine(p[2][0], p[2][1], p[0][0], p[0][1], QPen(QBrush(Qt.red), 1.0))
            elif self.originalpoint == -1:
                for t in self.leftTriangles:
                    p = t.vertices
                    # add each of the 3 lines in the triangle separately
                    self.leftscene.addLine(p[0][0], p[0][1], p[1][0], p[1][1], QPen(QBrush(Qt.blue), 1.0))
                    self.leftscene.addLine(p[1][0], p[1][1], p[2][0], p[2][1], QPen(QBrush(Qt.blue), 1.0))
                    self.leftscene.addLine(p[2][0], p[2][1], p[0][0], p[0][1], QPen(QBrush(Qt.blue), 1.0))
                for t in self.rightTriangles:
                    p = t.vertices
                    # add each of the 3 lines in the triangle separately
                    self.rightscene.addLine(p[0][0], p[0][1], p[1][0], p[1][1], QPen(QBrush(Qt.blue), 1.0))
                    self.rightscene.addLine(p[1][0], p[1][1], p[2][0], p[2][1], QPen(QBrush(Qt.blue), 1.0))
                    self.rightscene.addLine(p[2][0], p[2][1], p[0][0], p[0][1], QPen(QBrush(Qt.blue), 1.0))
            else:
                for t in self.leftTriangles:
                    p = t.vertices
                    # add each of the 3 lines in the triangle separately
                    self.leftscene.addLine(p[0][0], p[0][1], p[1][0], p[1][1], QPen(QBrush(Qt.cyan), 1.0))
                    self.leftscene.addLine(p[1][0], p[1][1], p[2][0], p[2][1], QPen(QBrush(Qt.cyan), 1.0))
                    self.leftscene.addLine(p[2][0], p[2][1], p[0][0], p[0][1], QPen(QBrush(Qt.cyan), 1.0))
                for t in self.rightTriangles:
                    p = t.vertices
                    # add each of the 3 lines in the triangle separately
                    self.rightscene.addLine(p[0][0], p[0][1], p[1][0], p[1][1], QPen(QBrush(Qt.cyan), 1.0))
                    self.rightscene.addLine(p[1][0], p[1][1], p[2][0], p[2][1], QPen(QBrush(Qt.cyan), 1.0))
                    self.rightscene.addLine(p[2][0], p[2][1], p[0][0], p[0][1], QPen(QBrush(Qt.cyan), 1.0))
        else:
            self.leftscene.clear()
            self.rightscene.clear()
            self.refresh = True
            self.originalpoint = -1
            self.imgright = None
            self.loadImageleft()
            self.loadImageright()

    def sliderValueChange(self):
        self.alpha = round(float(self.sliAlpha.value()) / 20.0, 2)
        self.txtAlpha.setText('{:.2f}'.format(self.alpha))
        if self.blendcheck:
            self.newblend()

    def blend(self):
        self.blendcheck = not self.blendcheck
        self.newblend()

    def newblend(self):
        try:
            morpher = Morpher(self.leftImg, self.leftTriangles, self.rightImg, self.rightTriangles)
            result = morpher.getImageAtAlpha(self.alpha)
        except:
            morpher = ColorMorpher(self.leftImg, self.leftTriangles, self.rightImg, self.rightTriangles)
            result = morpher.getImageAtAlpha(self.alpha)
        # Image.fromarray(result).show()
        result = ImageQt.ImageQt(Image.fromarray(result))
        graph = QPixmap()
        graph.convertFromImage(result)
        self.blendscene.addPixmap(graph)
        self.graBlend.setScene(self.blendscene)
        self.graBlend.fitInView(QGraphicsScene.itemsBoundingRect(self.blendscene), Qt.KeepAspectRatio)


    def newLoadTriangles(self, leftPointArr, rightPointArr):
        endindex = Delaunay(rightPointArr).simplices  # generate triangle
        leftTriangles = [Triangle(n) for n in leftPointArr[endindex]]
        rightTriangles = [Triangle(n) for n in rightPointArr[endindex]]
        return (leftTriangles, rightTriangles)


if __name__ == "__main__":
    currentApp = QApplication(sys.argv)
    currentForm = MorphingApp()

    currentForm.show()
    currentApp.exec_()
