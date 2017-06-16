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



class Molecule3D(Qt3DCore.QEntity):
    def __init__(self, *arg, **args):
        super(Molecule3D, self).__init__()
        self.mid = QVector3D(0, 0, 0)
        atlist = "2.85359    2.63232    0.48588; 2.01243    2.18253    1.10514; 0.92388    1.60218    1.87814; " \
                 "0.20347   -1.99886    9.07608; -0.70305   -1.66389    9.92535; 0.78718   -3.05595    9.69676; " \
                 "-0.23894   -2.55716    8.02754".split(';')
        self.atlist = [QVector3D(*[float(x) for x in i.split()]) for i in atlist]

    def add_atoms(self, atlist):
        """
        Adds atoms to the scene
        :type atlist: list
        """
        self.atlist = [QVector3D(x) for x in atlist]

    def create_molecule(self, color=False):
        """
        C1    6     0.20347   -1.99886    9.07608
        F1    9    -0.70305   -1.66389    9.92535
        F2    9     0.78718   -3.05595    9.69676
        F3    9    -0.23894   -2.55716    8.02754
        """
        rootEntity = Qt3DCore.QEntity()
        multvec = QVector3D(2, 2, 2)
        cololist = ['gray', 'red', 'blue', 'gray', 'green', 'green', 'green', 'green']
        xsum = 0
        ysum = 0
        zsum = 0
        for n, at in enumerate(self.atlist):
            at = at*multvec
            if color:
                self.add_sphere(rootEntity, at, cololist[n])
            else:
                self.add_sphere(rootEntity, at, 'black')
            xsum += at.x()
            ysum += at.y()
            zsum += at.z()
            #self.add_bond(rootEntity, at, at2, 'gray')
        # calculate the mid point of the atoms:
        self.mid = QVector3D(xsum / len(self.atlist), ysum / len(self.atlist), zsum / len(self.atlist))
        return rootEntity

    def add_bond(self, rootEntity, pos1, pos2, color):
        """
        This should draw bonds, but it does not work atm.
        https://github.com/GarageGames/Qt/blob/master/qt-5/qt3d/examples/qt3d/custom-mesh-cpp/main.cpp
        """
        material = Qt3DExtras.QPhongMaterial(rootEntity)
        material.setAmbient(QColor('gray'))
        # Torus:
        cylinder_entity = Qt3DCore.QEntity(rootEntity)
        cylinder_mesh = Qt3DExtras.QCylinderMesh()
        cylinder_mesh.setRadius(0.2)
        cylinder_mesh.setLength(pos1.distanceToPoint(pos2))
        cylinder_mesh.setRings(100)
        cylinder_mesh.setSlices(20)
        cylinderTransform = Qt3DCore.QTransform()
        cylinderTransform.setScale3D(QVector3D(1, 1, 1))
        cylinderTransform.setRotation(QQuaternion.fromDirection(pos2, pos1))
        cylinder_entity.addComponent(cylinder_mesh)
        cylinder_entity.addComponent(cylinderTransform)
        cylinder_entity.addComponent(material)

    def add_sphere(self, rootEntity, position, colour):
        """ 
        :type position: QVector3D
        :type colour: string
        """
        material = Qt3DExtras.QPhongMaterial(rootEntity)
        material.setAmbient(QColor(colour))
        sphere_entity = Qt3DCore.QEntity(rootEntity)
        sphere_mesh = Qt3DExtras.QSphereMesh()
        # sphere_mesh
        sphere_mesh.setRadius(0.8)
        sphere_transform = Qt3DCore.QTransform(sphere_mesh)
        sphere_transform.setTranslation(position)
        sphere_entity.addComponent(sphere_transform)
        sphere_entity.addComponent(sphere_mesh)
        sphere_entity.addComponent(material)
        sphere_transform.matrix().setToIdentity()

    def event(self, event):
        handled = QtWidgets.QOpenGLWidget.event(event)
        self.update()
        print('foo')
        return handled

    def mousePressEvent(self, event):
        button = 0
        print(event)
        if event.button == "Qt::LeftButton":
          button = 1
        if event.button == "Qt::MiddleButton":
          button = 2
        if event.button == Qt.RightButton:
          button = 3
        return self.getEventQueue().mouseButtonPress(event.x(), event.y(), button)


class Cylinder():
    def __init__(self):
        """
        """
        pass



if __name__ == '__main__':
    ###################################################
    app = QGuiApplication(sys.argv)
    view = Qt3DExtras.Qt3DWindow()
    s = Molecule3D()
    rootEntity = s.create_molecule()
    print('#scene')
    # // Camera
    camera = view.camera()
    lens = Qt3DRender.QCameraLens()
    lens.setOrthographicProjection(-50, 50.0, -50.0, 50.0, -1.0, 500.0)
    camera.setUpVector(QVector3D(0, 1.0, 0))
    camera.setPosition(QVector3D(0, 0, 80.0))  # Entfernung
    camera.setViewCenter(s.mid)
    #camera.setfieldOfView = 45
    # For camera controls:
    camController = Qt3DExtras.QOrbitCameraController(rootEntity)
    camController.setLinearSpeed(-30.0)
    camController.setLookSpeed(-480.0)
    camController.setCamera(camera)
    #camController.setZoomInLimit(1)
    lightEntity = QEntity(rootEntity)
    light = QPointLight(lightEntity)
    light.setColor(QColor(150, 150, 100))
    light.setIntensity(0.5)
    lightEntity.addComponent(light)
    lightTransform = Qt3DCore.QTransform(lightEntity)
    lightTransform.setTranslation(QVector3D(0, 0, 80.0))
    lightEntity.addComponent(lightTransform)
    view.setRootEntity(rootEntity)
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