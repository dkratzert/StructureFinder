#!/usr/bin/env python

import sys
import math

from PyQt5 import Qt3DCore, QtCore
from PyQt5 import Qt3DExtras
from PyQt5 import Qt3DInput
from PyQt5 import Qt3DRender
from PyQt5.QtCore import *
from PyQt5.QtGui import QVector3D, QGuiApplication


class OrbitTransformController(Qt3DCore.QTransform):
    targetChanged = pyqtSignal(int)
    radiuschanged = pyqtSignal(int)
    angleChanged = pyqtSignal(int)

    def __init__(self, transform):
        super().__init__()
        self.m_target = None
        self.m_radius = 1
        self.m_angle = 0
        self.m_matrix = transform.matrix()

    def setTarget(self, target):
        if self.m_target != target:
            self.m_target = target
            self.targetChanged.emit(target)

    def target(self):
        return self.m_target

    def setRadius(self, radius):
        if not QtCore.qFuzzyCompare(radius, self.m_radius):
            self.m_radius = radius
            self.updateMatrix()
            self.targetChanged.emit(radius)

    def radius(self):
        return self.m_radius

    def updateMatrix(self):
        self.m_matrix.setToIdentity()
        self.m_matrix.rotate(self.m_angle, QVector3D(0.0, 1.0, 0.0))
        self.m_matrix.translate(self.m_radius, 0.0, 0.0)
        self.m_target.setMatrix(self.m_matrix)

    def setAngle(self, angle):
        print('###angle')
        if not QtCore.qFuzzyCompare(angle):
            self.m_angle = angle
            self.updateMatrix()
            self.angleChanged.emit(angle)

    def angle(self):
        print('###angle2')
        return self.m_angle


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
    print('###rotation: ###')
    sphereRotateTransformAnimation = QtCore.QPropertyAnimation(sphereTransform)
    sphereRotateTransformAnimation.setTargetObject(controller)
    sphereRotateTransformAnimation.setPropertyName(b"angle")
    sphereRotateTransformAnimation.setStartValue(0)
    sphereRotateTransformAnimation.setEndValue(360)
    sphereRotateTransformAnimation.setDuration(10000)
    sphereRotateTransformAnimation.setLoopCount(-1)
    sphereRotateTransformAnimation.Paused = 0
    sphereRotateTransformAnimation.Stopped = 0
    sphereRotateTransformAnimation.Forward = 1
    sphereRotateTransformAnimation.Backward = 0
    sphereRotateTransformAnimation.start()

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