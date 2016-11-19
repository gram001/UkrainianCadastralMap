# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PublicMapLayers
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

from qgis.core import QgsRasterLayer, QgsMapLayerRegistry, QgsCoordinateReferenceSystem
from qgis.utils import iface
from qgis.gui import QgsMessageBar

# TODO: place it to config file
layers = [("kadastr", 0, u"Кадастровий поділ", "tileMatrixSet=kadastr-wmsc-0"),
          ("grunt", 0, u"Ґрунти", "tileMatrixSet=grunt-wmsc-1"),
          ("kadastr_arch", 0, u"Архівні ділянки", "tileMatrixSet=kadastr_arch-wmsc-3"),
          ("atu", 0, u"АТУ", "tileMatrixSet=atu-wmsc-2"),
          ("dzk:restriction", 1, u"Обмеження", "tileMatrixSet=dzk:restriction-wmsc-0"),
          ("dzk:cnap", 1, u"Місце розташування ЦНАП", "tileMatrixSet=dzk:cnap-wmsc-1"),
          ("dzk:dp_land", 1, u"Розпорядження с/г землями", "tileMatrixSet=dzk:dp_land-wmsc-2")]

url_layers = ("contextualWMSLegend=0&crs=EPSG:900913&dpiMode=7&featureCount=10&format=image/png&styles="
              "&url=http://212.26.144.110/geowebcache/service/wms?tiled%3Dtrue",
              "contextualWMSLegend=0&crs=EPSG:900913&dpiMode=7&featureCount=10&format=image/png&styles="
              "&url=http://map.land.gov.ua/geoserver/gwc/service/wms?tiled%3Dtrue")


class PublicMapLayers(QgsRasterLayer):
    # TODO: delete layer crs chose window
    def __init__(self, layer_id):
        chosen_layer = (url_layers[layers[layer_id][1]], layers[layer_id][0], layers[layer_id][3])
        self.url_to_pcm = 'url={}&layers={}&{}'.format(*chosen_layer)
        self.layer_name = layers[layer_id][2]
        self.provider = "wms"
        super(PublicMapLayers, self).__init__(self.url_to_pcm, self.layer_name, self.provider)
        self.setCustomProperty("layer_id", layer_id)
        self.setCustomProperty("layer_name", layers[layer_id][0])

    def connect_to_pcm(self):
        QgsMapLayerRegistry.instance().addMapLayer(self)

    def check_crs(self):
        # TODO: work with any crs
        crs_id = self.crs().authid()
        if crs_id != 'EPSG:3857':
            iface.messageBar().pushMessage("Error","Wrong CRS. Please use CRS EPSG:3857", level=QgsMessageBar.CRITICAL)
            #crs = QgsCoordinateReferenceSystem('EPSG:3857')
            #self.setCrs(crs)
