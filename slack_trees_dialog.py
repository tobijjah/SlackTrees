# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SlackTreesDialog
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
import os
from event import Signal
from PyQt4 import QtGui, uic
from PyQt4.QtGui import QMessageBox
from qgis.utils import showPluginHelp


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'slack_trees_dialog_base.ui'))


class SlackTreesDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(SlackTreesDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use auto connect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.signals = Signal('GUI EVENTS')

        self.setupUi(self)
        self._layer_fields()
        self.attach_events()

    def attach_events(self):
        self.InputMapLayerComboBox.layerChanged.connect(self._layer_fields)
        self.HelpButton.clicked.connect(self._open_help)
        self.OutputBrowseButton.clicked.connect(self._output_dialog)
        self.OkButton.clicked.connect(self._ok)

    def _layer_fields(self):
        current_layer = self.InputMapLayerComboBox.currentLayer()
        self.ExcludeFieldComboBox.setLayer(current_layer)

    def _open_help(self):
        pass

    def _output_dialog(self):
        pass

    def _ok(self):
        if self.InputMapLayerComboBox.currentLayer() is not None and self.OutputLIneEdit.text() != '':
            kwargs = {}
            self.signals.fire('OK', **kwargs)
        else:
            layer_miss = 'No input layer specified'
            out_path_miss = 'Please specify output shapefile'
            msg = layer_miss if self.InputMapLayerComboBox.currentLayer() is None else out_path_miss
            self.warn_user(msg)


    def _update_progressbar(self, progress):
        self.ProgressBar.setValue(progress)

    def warn_user(self, msg):
        QMessageBox.warning(self, 'An error occurred', msg)

    def critical_user(self, msg):
        QMessageBox.critical(self, 'An critical error occurred', msg)
