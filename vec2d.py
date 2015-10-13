# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 12:04:17 2013

@author: tom
"""
import numpy as np
from math import atan2

class vec2d(object):
    """A simple 2d vector class. Supports basic arithmetics."""
    def __init__(self, x, y = None):
        #print "got x", x
        #print "got y", y
        if y == None:
            if len(x) != 2: raise ValueError('Need exactly two values to create vec2d from list.')
            y = x[1]  # -- Yes, we need to process y first.
            x = x[0]
        self.x = x
        self.y = y

    @property
    def lon(self):
        return self.x

    @lon.setter
    def lon(self, value):
        self.x = value

    @property
    def lat(self):
        return self.y

    @lat.setter
    def lat(self, value):
        self.y = value
        
    def __getitem__(self, key):
        return (self.x, self.y)[key]

    def __fixtype(self, other):
        if type(other) == type(self): return other
        return vec2d(other, other)

    def __add__(self, other):
        other = self.__fixtype(other)
        return vec2d(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        other = self.__fixtype(other)
        return vec2d(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        other = self.__fixtype(other)
        return vec2d(self.x * other.x, self.y * other.y)

    def __div__(self, other):
        other = self.__fixtype(other)
        return vec2d(self.x / other.x, self.y / other.y)

    def __str__(self):
        return "%1.7f %1.7f" % (self.x, self.y)

    def __neg__(self):
        return vec2d(-self.x, -self.y)

    def __abs__(self):
        return vec2d(abs(self.x), abs(self.y))

    def sign(self):
        return vec2d(np.sign((self.x, self.y)))

    def __lt__(self, other):
        return vec2d(self.x < other.x, self.y < other.y)

    def list(self):
        print "deprecated call to vec2d.list(). Iterate instead."
        return self.x, self.y

    def as_array(self):
        """return as numpy array"""
        return np.array((self.x, self.y))

    def __iter__(self):
        yield(self.x)
        yield(self.y)

    def swap(self):
        return vec2d(self.y, self.x)

    def int(self):
        return vec2d(int(self.x), int(self.y))

    def distance_to(self, other):
        d = self - other
        return (d.x**2 + d.y**2)**0.5

    def magnitude(self):
        return (self.x**2 + self.y**2)**0.5

    def normalize(self):
        mag = self.magnitude()
        self.x /= mag
        self.y /= mag

    def rot90ccw(self):
        return vec2d(-self.y, self.x)

    def atan2(self):
        return atan2(self.y, self.x)

if __name__ == "__main__":
    a = vec2d(1,2)
    b = vec2d(10,10)
    print "a   ", a
    print "b   ", b
    print "a+b ", a+b
    print "a-b ", a-b
    print "a+2 ", a+2
    print "a*b ", a * b
    print "a*2 ", a*2
    # print "2*a ", 2*a --> fails!
    print "a/2 ", a/2
    print "a/2.", a/2.

    print a.x, a.y
    print a.lon, a.lat
    a.lon = 4
    print a.x, a.lon

    print "a  ", a
    for i in a:
        print " y", i

