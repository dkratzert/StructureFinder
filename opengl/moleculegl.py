#!/usr/bin/env python

import sys
import math

from PyQt5 import Qt3DCore, QtCore
from PyQt5 import Qt3DExtras
from PyQt5 import Qt3DInput
from PyQt5 import Qt3DRender
from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt, QObject
from PyQt5.QtGui import QColor, QOpenGLVersionProfile, QSurfaceFormat, QVector3D
from PyQt5.QtWidgets import QOpenGLWidget



class OrbitTransformController(QObject):
    targetChanged = pyqtSignal(int)
    radiuschanged = pyqtSignal(int)

    def __init__(self, transform):
        super().__init__()
        self.m_target = None
        self.m_radius = 0
        self.m_angle = 0
        self.m_matrix = transform.matrix()

    def setTarget(self, target):
        if self.m_target != target:
            self.m_target = target
            self.targetChanged.emit(target)

    def setRadius(self, radius):
        self.m_radius = radius
        self.updateMatrix()
        #self.targetChanged.emit(radius)

    def updateMatrix(self):
        self.m_matrix.setToIdentity()
        self.m_matrix.rotate(self.m_angle, QVector3D(0.0, 1.0, 0.0))
        self.m_matrix.translate(self.m_radius, 0.0, 0.0)
        self.m_target.setMatrix(self.m_matrix)


class GLWidget(QOpenGLWidget):
    #xRotationChanged = pyqtSignal(int)
    #yRotationChanged = pyqtSignal(int)
    #zRotationChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        # from old opengl code:
        ##################################################
        """
        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.lastPos = QPoint()
        self.trolltechGreen = QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.bgcolor = QColor.fromRgb(25, 25, 25, 1)
        """
        ###################################################
        view = Qt3DExtras.Qt3DWindow()
        scene = self.createScene()
        print('#scene')
        #// Camera
        camera = view.camera()
        lens = Qt3DRender.QCameraLens()
        lens.setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
        camera.setPosition(QVector3D(0, 0, 40.0))
        camera.setViewCenter(QVector3D(0, 0, 0))

        #// For camera controls
        camController = Qt3DExtras.QOrbitCameraController(scene)
        camController.setLinearSpeed(50.0)
        camController.setLookSpeed(180.0)
        camController.setCamera(camera)
        view.setRootEntity(scene)

    def createScene(self):
        rootEntity = Qt3DCore.QEntity()
        material = Qt3DExtras.QPhongMaterial(rootEntity)
        sphereEntity = Qt3DCore.QEntity(rootEntity)
        sphereMesh = Qt3DExtras.QSphereMesh()
        sphereMesh.setRadius(3)

        sphereTransform = Qt3DCore.QTransform()
        controller = OrbitTransformController(sphereTransform)
        controller.setTarget(sphereTransform)
        controller.setRadius(20.0)

        sphereEntity.addComponent(sphereMesh)
        sphereEntity.addComponent(sphereTransform)
        sphereEntity.addComponent(material)

    """
    def minimumSizeHint(self):
        return QSize(250, 250)

    def sizeHint(self):
        return QSize(450, 450)

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def initializeGL(self):
        vp = QOpenGLVersionProfile()
        vp.setVersion(2, 1)
        vp.setProfile(QSurfaceFormat.CoreProfile)
        self.gl = self.context().versionFunctions(vp)
        self.gl.initializeOpenGLFunctions()
        self.setClearColor(self.bgcolor.darker())
        self.object = self.makeObject()
        self.cube = self.make_cube()
        self.gl.glShadeModel(self.gl.GL_FLAT)
        self.gl.glEnable(self.gl.GL_DEPTH_TEST)
        #self.gl.glEnable(self.gl.GL_CULL_FACE)

    def paintGL(self):
        self.gl.glClear(
                self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)
        self.gl.glLoadIdentity()
        self.gl.glTranslated(0.0, 0.0, -10.0)
        self.gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        self.gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        self.gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        self.gl.glCallList(self.object)
        self.gl.glCallList(self.cube)

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return
        ar = width/height
        self.gl.glViewport(0, 0, width, height)
        #self.gl.glViewport((width - side) // 2, (height - side) // 2, side, side)
        self.gl.glMatrixMode(self.gl.GL_PROJECTION)
        self.gl.glLoadIdentity()
        zoom = 0.4
        if width <= height:
            self.gl.glOrtho(-zoom, zoom, zoom / ar, -zoom / ar, 4.0, 15.0)
        else:
            self.gl.glOrtho(-zoom * ar, zoom * ar, zoom, -zoom, 4.0, 15.0)
        self.gl.glMatrixMode(self.gl.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()
        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & Qt.RightButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)
        self.lastPos = event.pos()

    def makeObject(self):
        genList = self.gl.glGenLists(1)
        self.gl.glNewList(genList, self.gl.GL_COMPILE)
        self.gl.glBegin(self.gl.GL_QUADS)
        x1 = +0.06
        y1 = -0.14
        x2 = +0.14
        y2 = -0.06
        x3 = +0.08
        y3 = +0.00
        x4 = +0.30
        y4 = +0.22
        self.quad(x1, y1, x2, y2, y2, x2, y1, x1)
        self.quad(x3, y3, x4, y4, y4, x4, y3, x3)
        self.extrude(x1, y1, x2, y2)
        self.extrude(x2, y2, y2, x2)
        self.extrude(y2, x2, y1, x1)
        self.extrude(y1, x1, x1, y1)
        self.extrude(x3, y3, x4, y4)
        self.extrude(x4, y4, y4, x4)
        self.extrude(y4, x4, y3, x3)
        NumSectors = 200
        for i in range(NumSectors):
            angle1 = (i * 2 * math.pi) / NumSectors
            x5 = 0.30 * math.sin(angle1)
            y5 = 0.30 * math.cos(angle1)
            x6 = 0.20 * math.sin(angle1)
            y6 = 0.20 * math.cos(angle1)
            angle2 = ((i + 1) * 2 * math.pi) / NumSectors
            x7 = 0.20 * math.sin(angle2)
            y7 = 0.20 * math.cos(angle2)
            x8 = 0.30 * math.sin(angle2)
            y8 = 0.30 * math.cos(angle2)
            self.quad(x5, y5, x6, y6, x7, y7, x8, y8)
            self.extrude(x6, y6, x7, y7)
            self.extrude(x8, y8, x5, y5)
        self.gl.glEnd()
        self.gl.glEndList()
        return genList

    def make_cube(self):
        genList = self.gl.glGenLists(1)
        self.gl.glNewList(genList, self.gl.GL_COMPILE)
        self.gl.glBegin(self.gl.GL_QUADS)
        self.gl.glColor3f(0, 1, 0)
        # front
        self.gl.glVertex3d(0.0, 0.0, 0.0)
        self.gl.glVertex3d(0.2, 0.0, 0.0)
        self.gl.glVertex3d(0.2, 0.2, 0.0)
        self.gl.glVertex3d(0.0, 0.2, 0.0)
        # back
        self.gl.glVertex3d(0.0, 0.0, -0.2)
        self.gl.glVertex3d(0.2, 0.0, -0.2)
        self.gl.glVertex3d(0.2, 0.2, -0.2)
        self.gl.glVertex3d(0.0, 0.2, -0.2)
        # right
        self.gl.glVertex3d(0.2, 0.0, 0.0)
        self.gl.glVertex3d(0.2, 0.0, -0.2)
        self.gl.glVertex3d(0.2, 0.2, -0.2)
        self.gl.glVertex3d(0.2, 0.2, 0.0)
        # left
        self.gl.glVertex3d(0.0, 0.0, 0.0)
        self.gl.glVertex3d(0.0, 0.0, -0.2)
        self.gl.glVertex3d(0.0, 0.2, -0.2)
        self.gl.glVertex3d(0.0, 0.2, 0.0)
        # top
        self.gl.glVertex3d(0.0, 0.2, 0.0)
        self.gl.glVertex3d(0.2, 0.2, 0.0)
        self.gl.glVertex3d(0.2, 0.2, -0.2)
        self.gl.glVertex3d(0.0, 0.2, -0.2)
        # bottom
        self.gl.glVertex3d(0.0, 0.0, 0.0)
        self.gl.glVertex3d(0.2, 0.0, 0.0)
        self.gl.glVertex3d(0.2, 0.0, -0.2)
        self.gl.glVertex3d(0.0, 0.0, -0.2)
        self.gl.glEnd()
        self.gl.glEndList()
        return genList

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.setColor(self.trolltechGreen)
        self.gl.glVertex3d(x1, y1, -0.05)
        self.gl.glVertex3d(x2, y2, -0.05)
        self.gl.glVertex3d(x3, y3, -0.05)
        self.gl.glVertex3d(x4, y4, -0.05)
        self.gl.glVertex3d(x4, y4, +0.05)
        self.gl.glVertex3d(x3, y3, +0.05)
        self.gl.glVertex3d(x2, y2, +0.05)
        self.gl.glVertex3d(x1, y1, +0.05)

    def extrude(self, x1, y1, x2, y2):
        self.setColor(self.trolltechGreen.darker(250 + int(100 * x1)))
        self.gl.glVertex3d(x1, y1, +0.05)
        self.gl.glVertex3d(x2, y2, +0.05)
        self.gl.glVertex3d(x2, y2, -0.05)
        self.gl.glVertex3d(x1, y1, -0.05)

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def setClearColor(self, c):
        self.gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setColor(self, c):
        self.gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())
    """



if __name__ == '__main__':
    pass
