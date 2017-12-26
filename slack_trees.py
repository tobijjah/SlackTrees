# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SlackTrees
                                 A QGIS plugin
 A plugin to determine trees to mount a Slackline
                              -------------------
        begin                : 2017-11-14
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Tobias Seydewitz
        email                : tobi.seyde@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import re
import os.path
import resources
from itertools import combinations
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from slack_trees_dialog import SlackTreesDialog
from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsFeature,
                       QgsGeometry,
                       QgsPoint)


class SlackTrees(object):
    """QGIS Plugin Implementation."""
    COMPARES = {
        '<': lambda val, const: val < const,
        '>': lambda val, const: val > const,
        '<=': lambda val, const: val <= const,
        '>=': lambda val, const: val >= const,
        '==': lambda val, const: val == const,
        '!=': lambda val, const: val != const
    }
    WGS84 = QgsCoordinateReferenceSystem(4326)

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        # locale = QSettings().value('locale/userLocale')[0:2]
        # locale_path = os.path.join(
        #     self.plugin_dir,
        #     'i18n',
        #     'SlackTrees_{}.qm'.format(locale))
        #
        # if os.path.exists(locale_path):
        #     self.translator = QTranslator()
        #     self.translator.load(locale_path)
        #
        #     if qVersion() > '4.3.3':
        #         QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.dlg = None
        self.layer = None
        self._spacing = None
        self._slack_layer = None
        self._max_distance = None
        self._min_distance = None
        self.actions = []
        self.menu = self.tr(u'&SlackTrees')

        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SlackTrees')
        self.toolbar.setObjectName(u'SlackTrees')

    @property
    def min_distance(self):
        # set hard coded min distance cap if not initialized through gui
        if self._min_distance is None:
            self.min_distance = 10.0

        return self._min_distance

    @min_distance.setter
    def min_distance(self, value):
        low = 0.0
        high = 499.0

        if value < low or value > high or not isinstance(value, (int, float)) or value > self.max_distance:
            type_err = 'Min value {} with {} is not accepted'.format(value, type(value))
            value_err = 'Min value {} must be {} < x < {}'.format(value, low, high)
            raise TypeError(type_err) if not isinstance(value, (int, float)) else ValueError(value_err)

        self._min_distance = value

    @property
    def max_distance(self):
        # set hard coded max distance cap if not initialized through gui
        if self._max_distance is None:
            self.max_distance = 50.0

        return self._max_distance

    @max_distance.setter
    def max_distance(self, value):
        low = 1.0
        high = 500.0

        if value < low or value > high or not isinstance(value, (int, float)) or value < self._min_distance:
            type_err = 'Max value {} with {} is not accepted'.format(value, type(value))
            value_err = 'Max value {} must be {} < x < {}'.format(value, low, high)
            raise TypeError(type_err) if not isinstance(value, (int, float)) else ValueError(value_err)

        self._max_distance = value

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """
        Get the translation for a string using Qt translation API.
        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString
        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('SlackTrees', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str
        :param text: Text that should be shown in menu items for this action.
        :type text: str
        :param callback: Function to be called when the action is triggered.
        :type callback: function
        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool
        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool
        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool
        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str
        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget
        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = SlackTreesDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/plugins/SlackTrees/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Find Slackline trees'),
            callback=self.run,
            parent=self.iface.mainWindow()
        )

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&SlackTrees'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    # TODO attach to layercombobox event handler (update self.layer)
    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        self.dlg.signals.connect('OK', self.controller)
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if Cancel was pressed
        if result == QFileDialog.Rejected:
            return

    def controller(self, layer=None, spacing=None, min_max=None, field=None, op=None, const=None, out=None):
        try:
            self.layer = layer
            self._spacing = spacing
            self.min_distance, self.max_distance = min_max

            feat_gen = self._get_features(field, op, const)
            rproj_gen = self._reproject_features(feat_gen)
            slacklines = self._slacklines(rproj_gen)

        except (TypeError, ValueError) as err:
            self.dlg.warn_user(str(err))
        except Exception as err:
            msg = 'Unexpected error: {}, please contact a maintainer'.format(err)
            self.dlg.critical_user(msg)

    def _get_features(self, field_name, operator, const):
        attr_idx = self.layer.fieldNameIndex(field_name)

        if attr_idx > -1:
            generator = self._get_filtered_features(attr_idx, operator, const)
        else:
            generator = self._get_unfiltered_features()

        for feature in generator:
            yield feature

    def _get_unfiltered_features(self):
        for feature in self.layer.getFeatures():
            yield feature

    def _get_filtered_features(self, attr_idx, operator, const):
        compare_func = self.__class__.COMPARES.get(operator)

        for feature in self.layer.getFeatures():
            val = feature[attr_idx]
            if compare_func(val, const):
                yield feature

    def _reproject_features(self, feature_generator):
        if not self._valid_bounds():
            bounds = self._bounding_box()
            msg = 'Bounds (xmin, ymin, xmax, ymax) = ({:f}, {:f}, {:f}, {:f}) spanning multiple coordinates systems'\
                .format(bounds.boundingBox().xMinimum(),
                        bounds.boundingBox().yMinimum(),
                        bounds.boundingBox().xMaximum(),
                        bounds.boundingBox().yMaximum())
            raise ValueError(msg)

        layer_crs = self.layer.crs()

        if bool(re.match(r'.*(?:326|327)\d{2}', layer_crs.authid())):
            wgs84_transform = None
            wgs84utm_transform = None

        elif layer_crs == self.__class__.WGS84:
            bounds = self._bounding_box()
            epsg = self._latlon_to_epsg(bounds.boundingBox().xMinimum(),
                                        bounds.boundingBox().yMinimum())
            dst_crs = QgsCoordinateReferenceSystem(epsg)

            wgs84_transform = None
            wgs84utm_transform = QgsCoordinateTransform(self.__class__.WGS84, dst_crs)

        else:
            wgs84_transform = QgsCoordinateTransform(layer_crs, self.__class__.WGS84)
            wgs84utm_transform = None

        for feature in feature_generator:
            if wgs84utm_transform is not None:
                feature = self._reproject_feature(feature, crs_transform=wgs84utm_transform)
            elif wgs84_transform is not None:
                feature = self._reproject_feature(feature, crs_transform=wgs84_transform)
                epsg = self._latlon_to_epsg(feature.geometry().boundingBox().xMinimum(),
                                            feature.geometry().boundingBox().yMinimum())
                dst_crs = QgsCoordinateReferenceSystem(epsg)
                feature = self._reproject_feature(feature, self.__class__.WGS84, dst_crs)

            yield feature

    def _slacklines(self, feature_generator):
        for fet1, fet2 in combinations(feature_generator, 2):
            geo1, geo2 = fet1.geometry(), fet2.geometry()
            point1, point2 = geo1.asPoint(), geo2.asPoint()
            attr1, attr2 = fet1.attributes(), fet2.attributes()

            distance = round(geo1.distance(geo2), 2)

            if distance < self.min_distance or distance > self.max_distance:
                continue

            out_feat = QgsFeature()
            out_line = QgsGeometry.fromPolyline([QgsPoint(point1), QgsPoint(point2)])
            out_feat.setGeometry(out_line)
            out_feat.setAttributes(attr1 + attr2 + [distance])

            yield out_feat

    def _reproject_feature(self, feature, src_crs=None, dst_crs=None, crs_transform=None):
        out_feature = QgsFeature()

        geometry = feature.geometry()
        geometry = self._reproject_geometry(geometry, src_crs, dst_crs, crs_transform)

        out_feature.setGeometry(geometry)
        out_feature.setAttributes(feature.attributes())

        return out_feature

    def _reproject_geometry(self, geometry, src_crs=None, dst_crs=None, crs_transform=None):
        if src_crs is not None and dst_crs is not None:
            transform = QgsCoordinateTransform(src_crs, dst_crs)
        else:
            assert crs_transform is not None
            transform = crs_transform

        geometry.transform(transform)

        return geometry

    def _valid_bounds(self):
        bounds = self._bounding_box()
        layer_crs = self.layer.crs()

        if layer_crs != self.__class__.WGS84:
            bounds = self._reproject_geometry(bounds, layer_crs, self.__class__.WGS84)

        bottom_left = (bounds.boundingBox().xMinimum(), bounds.boundingBox().yMinimum())
        top_right = (bounds.boundingBox().xMaximum(), bounds.boundingBox().yMaximum())

        return self._latlon_to_epsg(*bottom_left) == self._latlon_to_epsg(*top_right)

    def _bounding_box(self):
        self.layer.selectAll()
        bounds = self.layer.boundingBoxOfSelected()
        return QgsGeometry.fromRect(bounds)

    def _latlon_to_epsg(self, x, y):
        if x < -180 or x > 180 or y < -90 or y > 90:
            msg = 'lat/x {:f} and lon/y {:f} overflowing WGS84 coordinates system'.format(y, x)
            raise ValueError(msg)

        prefix = '326' if y >= 0 else '327'
        suffix = int(((x + 180) // 6) + 1)
        epsg = prefix + '{:02d}'.format(suffix)

        return int(epsg)
