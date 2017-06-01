#!/usr/bin/env python

import sys
import math

from PyQt5 import Qt3DCore, QtCore
from PyQt5 import Qt3DExtras
from PyQt5 import Qt3DInput
from PyQt5 import Qt3DRender
from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt, QObject
from PyQt5.QtGui import QColor, QOpenGLVersionProfile, QSurfaceFormat, QVector3D, QGuiApplication
from PyQt5.QtOpenGL import QGLWidget
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
        if QtCore.qFuzzyCompare(radius, self.m_radius):
            self.m_radius = radius
            self.updateMatrix()
            self.targetChanged.emit(radius)

    def updateMatrix(self):
        self.m_matrix.setToIdentity()
        self.m_matrix.rotate(self.m_angle, QVector3D(0.0, 1.0, 0.0))
        self.m_matrix.translate(self.m_radius, 0.0, 0.0)
        self.m_target.setMatrix(self.m_matrix)



def createScene():
    rootEntity = Qt3DCore.QEntity()
    material = Qt3DExtras.QPhongMaterial(rootEntity)
    # Sphere:
    sphereEntity = Qt3DCore.QEntity(rootEntity)
    sphereMesh = Qt3DExtras.QSphereMesh()
    sphereMesh.setRadius(3)
    print('##1')
    sphereTransform = Qt3DCore.QTransform()
    controller = OrbitTransformController(sphereTransform)
    controller.setTarget(sphereTransform)
    controller.setRadius(5.0)
    print('##2')
    sphereEntity.addComponent(sphereMesh)
    sphereEntity.addComponent(sphereTransform)
    sphereEntity.addComponent(material)
    return rootEntity



if __name__ == '__main__':
    ###################################################
    app = QGuiApplication(sys.argv)
    view = Qt3DExtras.Qt3DWindow()
    scene = createScene()
    print('#scene')
    # // Camera
    camera = view.camera()
    lens = Qt3DRender.QCameraLens()
    lens.setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
    camera.setPosition(QVector3D(0, 0, 100.0))  # Entfernung
    camera.setViewCenter(QVector3D(0, 0, 0))
    print('#camera')
    # // For camera controls
    camController = Qt3DExtras.QOrbitCameraController(scene)
    camController.setLinearSpeed(50.0)
    camController.setLookSpeed(180.0)
    camController.setCamera(camera)
    view.setRootEntity(scene)
    print('view#')
    view.setRootEntity(scene)
    view.show()
    app.exec()