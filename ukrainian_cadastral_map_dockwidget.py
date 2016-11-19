# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UkrainianCadastralMapDockWidget
                                 A QGIS plugin
 This plugin adds support Ukrainian Public Cadastral Map
                             -------------------
        begin                : 2016-11-13
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Roman Rukavchuk
        email                : gram@e-mail.ua
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
import public_map_layers
import get_obj_info
import check_scale


from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal, Qt
from qgis.utils import iface
from qgis.core import QgsMapLayer
from qgis.gui import QgsMessageBar

# global variables for changing back to previous tool that user used
prev_tool = None
cur_tool = None

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ukrainian_cadastral_map_dockwidget_base.ui'))


class UkrainianCadastralMapDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(UkrainianCadastralMapDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.activateButton.clicked.connect(self.activate)
        self.deactivateButton.clicked.connect(self.deactivate)
        self.connectButton.clicked.connect(self.connect_raster)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def activate(self):
        global cur_tool, prev_tool
        # TODO: change cursor. It doesnt want to use custom cursor
        # http://imasdemase.com/en/programacion-2/cursor-personalizado-en-plugin-qgis/
        current_layer = iface.mapCanvas().currentLayer()
        if current_layer:
            if current_layer.type() == QgsMapLayer.RasterLayer:
                if current_layer.customProperty("layer_id") is not None:
                    self.activateButton.setEnabled(False)
                    prev_tool = iface.mapCanvas().mapTool()
                    cur_tool = get_obj_info.GetObjectInfo(iface.mapCanvas())
                    cur_tool.setCursor(QtGui.QCursor(Qt.WhatsThisCursor))
                    iface.mapCanvas().setMapTool(cur_tool)
                else:
                    iface.messageBar().pushMessage("Error", "Current layer {} is a wrong layer".format(current_layer.name()),
                                                   level=QgsMessageBar.CRITICAL)
            else:
                iface.messageBar().pushMessage("Error", "Current layer {} is a not a raster layer"
                                           .format(current_layer.name()), level=QgsMessageBar.CRITICAL)
        else:
            iface.messageBar().pushMessage("Error", "There is no layers",level=QgsMessageBar.CRITICAL)

    def deactivate(self):
        global cur_tool, prev_tool
        self.activateButton.setEnabled(True)
        if cur_tool:
            iface.mapCanvas().setMapTool(prev_tool)
            cur_tool = None

    def connect_raster(self):
        layer_id = self.layer_id.currentIndex()
        new_layer = public_map_layers.PublicMapLayers(layer_id)
        new_layer.connect_to_pcm()
        new_layer.check_crs()
        check_scale.check_scale()