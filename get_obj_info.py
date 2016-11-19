# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GetObjInfo
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
import urllib
import json
import check_scale
import qgis.utils
import BeautifulSoup
from PyQt4.QtCore import QSizeF
from PyQt4.QtGui import QTextDocument
from qgis.gui import QgsMapTool, QgsMessageBar, QgsTextAnnotationItem
from qgis.utils import iface
from qgis.core import QgsCoordinateTransform, QgsCoordinateReferenceSystem, QgsPoint


class GetObjectInfo(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.x = None
        self.y = None
        self.x_map = None
        self.y_map = None
        self.zoom = None
        self.request = None
        self.response = None
        self.act_layer = None
        self.zoom_levels = {8531: 16, 17062: 15, 34124: 14, 68248: 13, 136496: 12, 272992: 11, 545984: 10,
                            1091968: 9, 2183936: 8, 4367872: 7, 8735744: 6}

    def canvasReleaseEvent(self, event):
        check_scale.check_scale()
        x = event.pos().x()
        y = event.pos().y()
        coord_ext = self.canvas.getCoordinateTransform()
        coord = coord_ext.toMapCoordinates(x, y)
        self.x_map = coord[0]
        self.y_map = coord[1]
        current_crs_id = iface.mapCanvas().mapRenderer().destinationCrs().authid()
        # TODO: fix for correct work send request for other CRS than EPSG:3857
        if current_crs_id != 'EPSG:3857':
            crsSrc = QgsCoordinateReferenceSystem(int(current_crs_id.split(":")[1]))
            crsDest = QgsCoordinateReferenceSystem(3857)
            xform = QgsCoordinateTransform(crsSrc, crsDest)
            point = QgsPoint(*coord)
            coord = xform.transform(point)
        self.x = coord[1]
        self.y = coord[0]
        self.zoom = self.get_zoom()
        self.act_layer = self.canvas.currentLayer().customProperty("layer_name")
        self.form_request()
        self.send_request()
        self.parse_response()

    def choose_nearest_scale(self, current_scale, zoom_levels):
        """
        Chose the nearest typical scale of current scale
        :param current_scale: scale of map canvas
        :param zoom_levels: zoom levels in dictionary form
        :return: zoom in
        """
        scale_temp = float("inf")
        scale = current_scale
        zoom = 16
        for i in zoom_levels.keys():
            if abs(i - current_scale) < scale_temp:
                scale_temp = abs(i - current_scale)
                zoom = zoom_levels[i]
                scale = i
        #iface.mapCanvas().zoomScale(scale)
        return zoom

    def get_zoom(self):
        """
        Get zoom for request to server
        :return: typical scale for correct request to server
        """
        current_scale = int(round(self.canvas.scale()))
        if current_scale in self.zoom_levels.keys():
            return self.zoom_levels[current_scale]
        else:
            #iface.messageBar().pushMessage("Warning", "For accuracity you should use one of the standart scales."
            #                                          "Standart scales are in help.", level=QgsMessageBar.WARNING)
            return self.choose_nearest_scale(current_scale, self.zoom_levels)

    def form_request(self):
        self.request = "http://map.land.gov.ua/kadastrova-karta/getobjectinfo?x={}&y={}&zoom={}&actLayers[]={}".format(
            self.x, self.y, self.zoom, self.act_layer)

    def send_request(self):
        self.response = urllib.urlopen(self.request)

    def parse_response(self):
        names = {"dilanka": "Ділянка", "ikk": "ІКК", "obl": "Область", "rajonunion": "Район", "grunt": "Ґрунти",
                 "dilanka_arch": "Ділянка (архівна)", "restriction": "Обмеження", "cnap": "ЦНАД"}
        text = ""
        scene = self.canvas.scene()
        annotation = QgsTextAnnotationItem(self.canvas)
        annotation.setMapPosition(QgsPoint(self.x_map, self.y_map))
        # Starting from 2.14
        # TODO: check and fix bug for previous versions
        if qgis.utils.QGis.QGIS_VERSION_INT < 20140:
            iface.messageBar().pushMessage("Warning", "For correct transformation annotations between CRS please use"
                                                      " version 2.14 or later", level=QgsMessageBar.WARNING)
        # This delete annotation if we used other CRS than defined when we use OTF
        # if qgis.utils.QGis.QGIS_VERSION_INT >= 20140:
        #     annotation.setMapPositionCrs(QgsCoordinateReferenceSystem(3857))
        annotation.setActive(True)
        # fixes bug when response starts not with JSON object
        # http://map.land.gov.ua/kadastrova-karta/getobjectinfo?x=6201535.76141&y=2477307.1863&zoom=16&actLayers[]=kadastr_arch
        response_read = self.response.read()
        if not response_read.startswith("{"):
            response_read = "{" + response_read.split("{")[-1]
        json_obj = json.loads(response_read)
        for k, v in json_obj.items():
            if k == "pusto":
                annotation.setFrameSize(QSizeF(100, 20))
                annotation.setDocument(QTextDocument("Data is empty"))
                scene.addItem(annotation)
                self.canvas.refresh()
                return
            if iface.mapCanvas().currentLayer().customProperty("layer_id") == 0:
                annotation.setFrameSize(QSizeF(200, 300))
            elif iface.mapCanvas().currentLayer().customProperty("layer_id") == 1:
                annotation.setFrameSize(QSizeF(200, 100))
            elif iface.mapCanvas().currentLayer().customProperty("layer_id") == 2:
                annotation.setFrameSize(QSizeF(200, 300))
            else:
                annotation.setFrameSize(QSizeF(200, 250))
            title = names.get(k, u"Noname")
            text += title.decode("utf-8") + "\n"
            html_parsed = BeautifulSoup.BeautifulSoup(v)
            for i in html_parsed:
                for j in i.findAll("li"):
                    write_text = ""
                    t = (j.contents[0].string, j.contents[1])
                    if t[0]:
                        write_text += t[0]
                        if isinstance(t[1], BeautifulSoup.Tag):
                            write_text += " " + t[1].text
                        else:
                            write_text += " " + t[1]
                        text += write_text + "\n"
            #     for j in i.findAll(text=True):
            #         j = str(j)
            #         if j.startswith("&") or j.startswith("Замовити") or j.startswith("Інформація про право власності"):
            #             continue
            #         text += j.decode("utf-8") + " "
            # text += "\n"
        annotation.setDocument(QTextDocument(text))
        scene.addItem(annotation)
        self.canvas.refresh()
