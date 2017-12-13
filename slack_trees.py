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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from slack_trees_dialog import SlackTreesDialog
from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsFeature,
                       QgsGeometry,
                       QgsMessageLog)
import os.path
import re


class SlackTrees:
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
        self.actions = []
        self.menu = self.tr(u'&SlackTrees')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'SlackTrees')
        self.toolbar.setObjectName(u'SlackTrees')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

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
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            pass

    def _get_features(self, field_name, operator, const):
        attr_idx = self.layer.fieldNameIndex(field_name)

        if attr_idx > -1:
            for feature in self._get_filtered_features(attr_idx, operator, const):
                yield feature
        else:
            for feature in self._get_unfiltered_features():
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

    # TODO refactor local variable QgsCoordinateTransform from layer.crs to WGS84
    # TODO refactor finish error message
    def _reproject_features(self, feature_generator):
        if not self._valid_bounds():
            msg = 'Layer bounds {} {} spanning multiple  coordinates systems'
            raise ValueError(msg)

        layer_crs = self.layer.crs()

        # yield features without re-projecting them if layer has already crs WGS84/UTM
        if bool(re.match(r'.*(?:326|327)\d{2}', layer_crs.authid())):
            for feature in feature_generator:
                yield feature

        # re-project to WGS84/UTM if layer has WGS84 and yield
        elif layer_crs == self.__class__.WGS84:
            bounds = self._bounding_box()
            epsg = self._latlon_to_epsg(bounds.boundingBox().xMinimum(),
                                        bounds.boundingBox().yMinimum())
            dst_crs = QgsCoordinateReferenceSystem(epsg)
            transform = QgsCoordinateTransform(self.__class__.WGS84, dst_crs)

            for feature in feature_generator:
                yield self._reproject_feature(feature, crs_transform=transform)

        # re-project to WGS84 and WGS84/UTM if layer other crs and yield
        else:
            for feature in feature_generator:
                feature = self._reproject_feature(feature, layer_crs, self.__class__.WGS84)

                epsg = self._latlon_to_epsg(feature.geometry().boundingBox().xMinimum(),
                                            feature.geometry().boundingBox().yMinimum())
                dst_crs = QgsCoordinateReferenceSystem(epsg)

                yield self._reproject_feature(feature, self.__class__.WGS84, dst_crs)

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
