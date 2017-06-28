# -*- coding: utf-8 -*-
"""
Created on 03.06.2017

 ----------------------------------------------------------------------------
* "THE BEER-WARE LICENSE" (Revision 42):
* <daniel.kratzert@uni-freiburg.de> wrote this file. As long as you retain this 
* notice you can do whatever you want with this stuff. If we meet some day, and 
* you think this stuff is worth it, you can buy me a beer in return.
* ----------------------------------------------------------------------------

@author: Daniel Kratzert
"""
from math import cos, radians, sqrt, sin
import numpy as np


def vol_unitcell(a, b, c, al, be, ga):
    """
    calculates the volume of a unit cell
    :type a: float
    :type b: float
    :type c: float
    :type al: float
    :type be: float
    :type ga: float
    
    >>> v = vol_unitcell(2, 2, 2, 90, 90, 90)
    >>> print(v)
    8.0
    """
    ca, cb, cg = cos(radians(al)), cos(radians(be)), cos(radians(ga))
    v = a * b * c * sqrt(1 + 2 * ca * cb * cg - ca ** 2 - cb ** 2 - cg ** 2)
    return v


class A(object):
    """
    orthogonalization matrix
    e.g. converts fractional coordinates to cartesian coodinates

    >>> cell = (10.5086, 20.9035, 20.5072, 90, 94.13, 90)
    # fractional to cartesian:
    >>> coord = np.matrix((-0.186843,   0.282708,   0.526803))
    >>> A = A(cell).orthogonal_matrix
    >>> A*coord.reshape(3, 1)
    matrix([[ -2.74150542],
            [  5.90958668],
            [ 10.7752007 ]])
    # cartesian to fractional:
    >>> coord = [[-2.74150542399906], [5.909586678], [10.7752007008937]]
    >>> cartcoord = np.matrix(coord)
    >>> A**-1*cartcoord
    matrix([[-0.186843],
            [ 0.282708],
            [ 0.526803]])
    """

    def __init__(self, cell):
        self.a, self.b, self.c, alpha, beta, gamma = cell
        self.V = vol_unitcell(self.a, self.b, self.c, alpha, beta, gamma)
        self.alpha = radians(alpha)
        self.beta = radians(beta)
        self.gamma = radians(gamma)

    @property
    def orthogonal_matrix(self):
        """
        Converts von fractional to cartesian.
        Invert the matrix to do the opposite.
        """
        Am = np.matrix([[self.a, self.b * cos(self.gamma), self.c * cos(self.beta)],
                         [0, self.b * sin(self.gamma),
                          (self.c * (cos(self.alpha) - cos(self.beta) * cos(self.gamma)) / sin(self.gamma))],
                         [0, 0, self.V / (self.a * self.b * sin(self.gamma))]])
        return Am