#!/usr/bin/env python

import sys
import math

from PyQt5 import Qt3DCore, QtCore, QtWidgets
from PyQt5 import Qt3DExtras
from PyQt5 import Qt3DInput
from PyQt5 import Qt3DRender
#from PyQt5.Qt3DRender.QPickEvent import RightButton
from PyQt5.Qt3DCore import QEntity
from PyQt5.Qt3DRender import QPointLight
from PyQt5.QtCore import *
from PyQt5.QtGui import QGuiApplication, QQuaternion, QVector3D, QColor

"""
TODO:
- Add atom class
- use fancy textures
- use symmetry
"""


class OrbitTransformController(Qt3DCore.QComponent):
    targetChanged = pyqtSignal(int)
    radiuschanged = pyqtSignal(int)
    angleChanged = pyqtSignal()

    def __init__(self, parent, target=None, radius=0, angle=0):
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
        """
        material = Qt3DExtras.QPhongAlphaMaterial(rootEntity)
        material.setAmbient(QColor('gray'))
        # Torus:
        cylinderEntity = Qt3DCore.QEntity(rootEntity)
        cylinderMesh = Qt3DExtras.QCylinderMesh()
        cylinderMesh.setRadius(0.21)
        cylinderMesh.setLength(10)
        cylinderMesh.setRings(100)
        cylinderMesh.setSlices(20)
        cylinderTransform = Qt3DCore.QTransform()
        cylinderTransform.setScale3D(QVector3D(1, 1, 1.0))
        cylinderTransform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(-1, -1, 0), 25.0))
        cylinderEntity.addComponent(cylinderMesh)
        cylinderEntity.addComponent(cylinderTransform)
        cylinderEntity.addComponent(material)
        """
        """
        C1    1    0.090610   -0.303414    0.513850
        F1    3    0.045281   -0.252567    0.561932
        F2    3    0.129932   -0.463873    0.548990
        F3    3    0.055789   -0.388160    0.454486
        """
        mid = QVector3D(0.0, 0.0, 0.0)
        rootEntity = Qt3DCore.QEntity()
        multvec = QVector3D(2, 2, 2)
        cololist = ['gray', 'red', 'blue', 'gray', 'green', 'green', 'green', 'green']
        #atlist = [QVector3D(0.0906, -0.3034, 0.5138), QVector3D(0.0452, -0.2525, 0.5619), QVector3D(0.1299, -0.4638, 0.5489),
        #          QVector3D(0.0557, -0.3881, 0.4544)]
        atlist = "2.85359    2.63232    0.48588; 2.01243    2.18253    1.10514; 0.92388    1.60218    1.87814; " \
                 "0.20347   -1.99886    9.07608; -0.70305   -1.66389    9.92535; 0.78718   -3.05595    9.69676; " \
                 "-0.23894   -2.55716    8.02754"
        atlist = atlist.split(';')
        atlist = [QVector3D(*[float(x) for x in i.split()]) for i in atlist]
        mid = mid * (-1.0 / len(atlist))
        """
        #C1
        self.add_sphere(rootEntity, QVector3D(0.0906, -0.3034, 0.5138)*multvec, 'gray')
        #F1
        self.add_sphere(rootEntity, QVector3D(0.0452, -0.2525, 0.5619)*multvec, 'red')
        #F2
        self.add_sphere(rootEntity, QVector3D(0.1299, -0.4638, 0.5489)*multvec, 'blue')
        #F3
        """
        for n, at in enumerate(atlist):
            at = at*multvec
            self.add_sphere(rootEntity, at, cololist[n])
            self.add_bond(rootEntity, at, atlist[0]*multvec, 'gray')
        return rootEntity

    def add_bond(self, rootEntity, pos1, pos2, color):
        """
        https://github.com/GarageGames/Qt/blob/master/qt-5/qt3d/examples/qt3d/custom-mesh-cpp/main.cpp
        """
        material = Qt3DExtras.QPhongMaterial(rootEntity)
        material.setAmbient(QColor('gray'))
        # Torus:
        cylinderEntity = Qt3DCore.QEntity(rootEntity)
        cylinderMesh = Qt3DExtras.QCylinderMesh()
        cylinderMesh.setRadius(0.2)
        cylinderMesh.setLength(20)
        cylinderMesh.setRings(100)
        cylinderMesh.setSlices(20)
        cylinderTransform = Qt3DCore.QTransform()
        cylinderTransform.setScale3D(QVector3D(1, 1, 1.0))
        cylinderTransform.setTranslation(pos1)
        cylinderTransform.setRotation(QQuaternion.fromAxisAndAngle(pos2, 25.0))
        cylinderEntity.addComponent(cylinderMesh)
        cylinderEntity.addComponent(cylinderTransform)
        cylinderEntity.addComponent(material)

    def add_sphere(self, rootEntity, position, colour):
        """ 
        :type position: QVector3D
        :type colour: string
        """
        # F3:
        material = Qt3DExtras.QPhongMaterial(rootEntity)
        material.setAmbient(QColor(colour))
        sphereEntity = Qt3DCore.QEntity(rootEntity)
        sphereMesh = Qt3DExtras.QSphereMesh()
        # sphereMesh
        sphereMesh.setRadius(1)
        print('##1')
        sphereTransform = Qt3DCore.QTransform(sphereMesh)
        #controller = OrbitTransformController(sphereTransform)
        #controller.setTarget(sphereTransform)
        sphereTransform.setTranslation(position)
        print('rad:')
        # controller.setRadius(1.0)
        print('##2')
        sphereEntity.addComponent(sphereTransform)
        sphereEntity.addComponent(sphereMesh)
        sphereEntity.addComponent(material)
        #sphereTransform.matrix().setToIdentity()

    def event(self, event):
        handled = QtWidgets.QOpenGLWidget.event(event)
        self.update()
        return handled

    def mousePressEvent(self, event):
        button = 0
        if event.button == "Qt::LeftButton":
          button = 1
        if event.button == "Qt::MiddleButton":
          button = 2
        if event.button == Qt.RightButton:
          button = 3
        return self.getEventQueue().mouseButtonPress(event.x(), event.y(), button)


if __name__ == '__main__':
    ###################################################
    app = QGuiApplication(sys.argv)
    view = Qt3DExtras.Qt3DWindow()
    s = MyScene()
    rootEntity = s.createScene()
    print('#scene')
    # // Camera
    camera = view.camera()
    lens = Qt3DRender.QCameraLens()
    #camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
    lens.setOrthographicProjection(-50, 50.0, -50.0, 50.0, -1.0, 500.0)
    camera.setUpVector(QVector3D(0, 1.0, 0))
    camera.setPosition(QVector3D(0, 0, 100.0))  # Entfernung
    camera.setViewCenter(QVector3D(0, 0, 0))
    #camera.setfieldOfView = 45
    #print(camera.fieldOfView())
    print('#camera')
    # // For camera controls
    camController = Qt3DExtras.QOrbitCameraController(rootEntity)
    camController.setLinearSpeed(-30.0)
    camController.setLookSpeed(-480.0)
    camController.setCamera(camera)
    #camController.setZoomInLimit(1)
    lightEntity = QEntity(rootEntity)
    light = QPointLight(lightEntity)
    light.setColor(QColor("white"))
    light.setIntensity(0.5)
    lightEntity.addComponent(light)
    lightTransform = Qt3DCore.QTransform(lightEntity)
    lightTransform.setTranslation(QVector3D(0.5, 0.5, 0))
    #lightEntity.addComponent(lightTransform)
    view.setRootEntity(rootEntity)

    print('view#')
    view.show()
    app.exec()


"""
// assume:
// atoms with x, y, z coordinates (Angstrom) and elementSymbol
// bonds with pointers/references to atoms at ends
// table of colors for elementTypes
// find limits of molecule in molecule coordinates as xMin, yMin, xMax, yMax
scale = min(xScreenMax/(xMax-xMin), yScreenMax/(yMax-yMin))
xOffset = -xMin * scale; yOffset = -yMin * scale
for (bond in $bonds) {
  atom0 = bond.getAtom(0)
  atom1 = bond.getAtom(1)
  x0 = xOffset+atom0.getX()*scale; y0 = yOffset+atom0.getY()*scale // (1)
  x1 = xOffset+atom1.getX()*scale; y1 = yOffset+atom1.getY()*scale // (2)
  x1 = atom1.getX();  y1 = atom1.getY()
  drawLine (bondcolor, x0, y0, x1, y1)
}
for atom in atoms:
    x = xOffset+atom.getX()*scale
    y = yOffset+atom.getY()*scale
    z = atom.getZ()*scale
Note that this assumes the origin is in the bottom left corner of the screen, 
with Y up the screen. Many graphics systems have the origin at the top left, 
with Y down the screen. In this case the lines (1) and (2) should have the y 
coordinate generation as:

 y0 = yScreenMax -(yOffset+atom0.getY()*scale) // (1)
 y1 = yScreenMax -(yOffset+atom1.getY()*scale) // (2)

C1    1    0.090610   -0.303414    0.513850
F1    3    0.045281   -0.252567    0.561932
F2    3    0.129932   -0.463873    0.548990
F3    3    0.055789   -0.388160    0.454486

"""