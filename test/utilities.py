# coding=utf-8
"""Common functionality used by regression tests."""
import os
import sys
import math
import random
import logging
from PyQt4.QtCore import QVariant
from qgis.core import (QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsPoint,
                       QgsCoordinateReferenceSystem,
                       QgsGeometry,
                       QgsWKBTypes,
                       QgsVectorFileWriter,
                       QgsVectorLayer
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


def make_fields(field_definitions):
    """
    Convenience method for creating QGIS field definitions.

    :param field_definitions: list(dict, ...)
        Must be a list of dictionaries each dictionary must contain
        the attributes name and type assigned with string values.
        The type field provides the following choices: int, str, double,
        float, date
    :return: Qgs.Fields
        A Qgs.Fields object comprising the created field instances
    """
    types = {
        'int': QVariant.Int,
        'str': QVariant.String,
        'double': QVariant.Double,
        'float': QVariant.Double,
        'date': QVariant.Date
    }

    fields = QgsFields()
    for dic in field_definitions:
        name = dic.get('name')
        typ = dic.get('type')
        qvar = types.get(typ)
        assert name is not None and typ is not None and qvar is not None
        fields.append(QgsField(name, qvar))

    return fields


def make_test_layer(path):
    """
    Creates a test vector layer with ESRI shapefile format with point geometry.
    The layer has four fields with the following properties:
    species: str by random choice from a list (most common tree species)
    bhd: float random between 5.0 - 25.0
    volume: float calculated from bhd via bhd * pi
    random: int between 1 - 4
    Coordinate reference system of the layer is chosen randomly from the following choices:
    WGS84, WGS84/Pseudo-Mercator or WGS84/UTM zone 33
    In total the layer contains 20 features and each point is located in a circular manner
    around a center x,y coordinate. The circle center is located in Potsdam and the circle
    radius has approximately 10 meter.

    :param path: str
        Path where the test point vector layer should be stored
    :return: tuple(QgsVectorLayer, str)
        QgsVectorLayer instance of the created layer and the path where the layer was created
    """
    species = ['oak', 'fur', 'beech', 'pine', 'spruce', 'lime', 'alder', 'chestnut', 'birch', 'poplar']
    coords = [
        {
            # WGS84, unit degrees
            'epsg': 4326,
            'x': 13.0246733,
            'y': 52.4022183,
            'r': 0.5
        },
        {
            # WGS84/ UTM zone 33N, unit meter
            'epsg': 32633,
            'x': 365618.25,
            'y': 5807611.31,
            'r': 20.0
        },
        {
            # WGS 84 / Pseudo-Mercator, unit meter
            'epsg': 3857,
            'x': 1449900.0,
            'y': 6873181.0,
            'r': 20.0
        },
    ]
    fields = make_fields([
        {'name': 'species', 'type': 'str'},
        {'name': 'bhd', 'type': 'float'},
        {'name': 'volume', 'type': 'float'},
        {'name': 'random', 'type': 'int'}
    ])

    coord = random.choice(coords)
    crs = QgsCoordinateReferenceSystem()
    crs.createFromId(coord['epsg'])
    layer = QgsVectorFileWriter(path, "UTF-8", fields, QgsWKBTypes.Point, crs, "ESRI Shapefile")

    for circle_coor in circle(coord['x'], coord['y'], coord['r'], 20):
        specie = random.choice(species)
        bhd = round(random.uniform(5.0, 25.0), 2)
        volume = round(math.pi * bhd, 2)
        rand = random.randint(1, 4)

        point = QgsPoint(*circle_coor)
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPoint(point))
        feature.setAttributes([specie, bhd, volume, rand])
        layer.addFeature(feature)

    del layer  # flush to disk (suggestion by qgis cookbook)
    return QgsVectorLayer(path, 'test_layer', 'ogr'), path


def delete_layer(path):
    head, tail = os.path.split(path)
    name, ext = os.path.splitext(tail)
    path = os.path.join(head, name)

    for ext in ['.cpg', '.dbf', '.shp', '.prj', '.qpj', '.shx']:
        os.remove(path + ext)


if __name__ == '__main__':
    pass
