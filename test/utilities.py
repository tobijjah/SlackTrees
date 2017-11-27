# coding=utf-8
"""Common functionality used by regression tests."""
import os
import sys
import math
import logging
from qgis.core import (QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsPoint,
                       QgsCoordinateReferenceSystem,
                       QgsGeometry,
                       QgsWKBTypes
                       )


LOGGER = logging.getLogger('QGIS')
QGIS_APP = None  # Static variable used to hold hand to running QGIS app
CANVAS = None
PARENT = None
IFACE = None


def get_qgis_app():
    """ Start one QGIS application to test against.

    :returns: Handle to QGIS app, canvas, iface and parent. If there are any
        errors the tuple members will be returned as None.
    :rtype: (QgsApplication, CANVAS, IFACE, PARENT)

    If QGIS is already running the handle to that app will be returned.
    """
    try:
        from PyQt4 import QtGui, QtCore
        from qgis.core import QgsApplication
        from qgis.gui import QgsMapCanvas
        from qgis_interface import QgisInterface
    except ImportError:
        return None, None, None, None

    global QGIS_APP  # pylint: disable=W0603
    global PARENT  # pylint: disable=W0603
    global CANVAS  # pylint: disable=W0603
    global IFACE  # pylint: disable=W0603

    if QGIS_APP is None:
        gui_flag = True  # All test will run qgis in gui mode
        # noinspection PyPep8Naming
        QGIS_APP = QgsApplication(sys.argv, gui_flag)
        # Make sure QGIS_PREFIX_PATH is set in your env if needed!
        QGIS_APP.initQgis()
        s = QGIS_APP.showSettings()
        LOGGER.debug(s)

    if PARENT is None:
        # noinspection PyPep8Naming
        PARENT = QtGui.QWidget()

    if CANVAS is None:
        # noinspection PyPep8Naming
        CANVAS = QgsMapCanvas(PARENT)
        CANVAS.resize(QtCore.QSize(400, 400))

    if IFACE is None:
        # QgisInterface is a stub implementation of the QGIS plugin interface
        # noinspection PyPep8Naming
        IFACE = QgisInterface(CANVAS)

    return QGIS_APP, CANVAS, IFACE, PARENT


def circle(x_center, y_center, radius, res=10):
    """
    Generator function for computing circle x,y coordinates from
    a radius and the provided x and y circle center coordinates.

    :param x_center: int, float
        X center of the circle
    :param y_center: int, float
        Y center of the circle
    :param radius: int, float
        Circle radius
    :param res: int
        Changes the total number of coordinates which
        should be computed. Default is ten.
    :return: tuple
        Computed x and y coordinate
    """
    step = 2 / float(res)

    for i in range(res):
        part = i * step
        x = x_center + radius * math.cos(part * math.pi)
        y = y_center + radius * math.sin(part * math.pi)
        yield round(x, 6), round(y, 6)


def make_layer():
    fields = QgsFields()
    fields.append(QgsField(''))


if __name__ == '__main__':
    """
    lat/y 52.0
    long/x 13.0
    """
    get_qgis_app()