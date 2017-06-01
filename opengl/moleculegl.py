#!/usr/bin/env python

import sys
import math

from PyQt5 import Qt3DCore, QtCore
from PyQt5 import Qt3DExtras
from PyQt5 import Qt3DInput
from PyQt5 import Qt3DRender
from PyQt5.QtCore import *
from PyQt5.QtGui import QGuiApplication, QQuaternion, QVector3D


class OrbitTransformController(QObject):
    targetChanged = pyqtSignal(int)
    radiuschanged = pyqtSignal(int)
    angleChanged = pyqtSignal()

    def __init__(self, parent, target=None, radius=1, angle=0):
        super(OrbitTransformController, self).__init__(parent)
        print('init')
        self.m_target = target
        self.m_radius = radius
        self.m_angle = angle
        self.m_matrix = parent.matrix()
        print('hello')

    def setTarget(self, target):
        if self.m_target != target:
            self.m_target = target
            self.targetChanged.emit(target)

    def target(self):
        return self.m_target

    @pyqtSlot(bool, name='radius')
    def setRadius(self, radius):
        print('#radiuschnage')
        #if not QtCore.qFuzzyCompare(radius, self.m_radius):
        self.m_radius = radius
        self.updateMatrix()
        self.radiuschanged.emit(radius)

    def radius(self):
        return self.m_radius

    def updateMatrix(self):
        print('matrix###')
        self.m_matrix.setToIdentity()
        self.m_matrix.rotate(self.m_angle, QVector3D(1.0, 1.0, 0.0))
        #self.m_matrix.translate(self.m_radius, 0.0, 0.0)
        self.m_target.setMatrix(self.m_matrix)

    @pyqtSlot(bool, name='angle')
    def setAngle(self, angle):
        print('###angle')
        #if not QtCore.qFuzzyCompare(angle, self.m_angle):
        print('###angle##')
        self.m_angle = angle
        self.updateMatrix()
        self.angleChanged.emit()

    def angle(self):
        print('###angle2')
        return self.m_angle


class MyScene(Qt3DCore.QEntity):
    def __init__(self, *arg, **args):
        super(MyScene, self).__init__()

    def createScene(self):
        rootEntity = Qt3DCore.QEntity()
        material = Qt3DExtras.QPhongMaterial(rootEntity)
        # Torus:
        cylinderEntity = Qt3DCore.QEntity(rootEntity)
        cylinderMesh = Qt3DExtras.QCylinderMesh()
        cylinderMesh.setRadius(0.31)
        cylinderMesh.setLength(20)
        cylinderMesh.setRings(100)
        cylinderMesh.setSlices(20)
    
        cylinderTransform = Qt3DCore.QTransform()
        cylinderTransform.setScale3D(QVector3D(1, 1, 1.0))
        cylinderTransform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(-1, -1, 0), 25.0))
    
        cylinderEntity.addComponent(cylinderMesh)
        cylinderEntity.addComponent(cylinderTransform)
        cylinderEntity.addComponent(material)
    
        # Sphere:
        sphereEntity = Qt3DCore.QEntity(rootEntity)
        sphereMesh = Qt3DExtras.QSphereMesh()
        sphereMesh.setRadius(2)
        print('##1')
        sphereTransform = Qt3DCore.QTransform(sphereMesh)
        controller = OrbitTransformController(sphereTransform)
        controller.setTarget(sphereTransform)
        print('rad:')
        controller.setRadius(2.0)
        print('##2')
        sphereEntity.addComponent(sphereMesh)
        sphereEntity.addComponent(sphereTransform)
        sphereEntity.addComponent(material)
        return rootEntity



if __name__ == '__main__':
    ###################################################
    app = QGuiApplication(sys.argv)
    view = Qt3DExtras.Qt3DWindow()
    s = MyScene()
    scene = s.createScene()
    print('#scene')
    # // Camera
    camera = view.camera()
    lens = Qt3DRender.QCameraLens()
    lens.setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
    camera.setPosition(QVector3D(0, 0, 60.0))  # Entfernung
    camera.setViewCenter(QVector3D(0, 0, 0))
    print('#camera')
    # // For camera controls
    camController = Qt3DExtras.QOrbitCameraController(scene)
    camController.setLinearSpeed(50.0)
    camController.setLookSpeed(180.0)
    camController.setCamera(camera)
    view.setRootEntity(scene)
    print('view#')
    view.show()
    app.exec()
