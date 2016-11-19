# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CheckScale
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

from qgis.utils import iface
from qgis.gui import QgsMessageBar


def check_scale():
    # TODO: fix bug with the first layer doesn't change to need scale
    """
    Check correctnes of border scales. If scale < 8531 change it to 8531 and if it's > 8 735 744 change scale to it.
    :return: None
    """
    current_scale = iface.mapCanvas().scale()
    if current_scale < 8531:
        iface.messageBar().pushMessage("Warning", "You chose larger scale that map can use. Please use scale smaller"
                                                  " than 1:8 530", level=QgsMessageBar.WARNING)
        iface.mapCanvas().zoomScale(8531)
    elif current_scale > 8735744:
        iface.messageBar().pushMessage("Warning", "You chose smaller scale that map can use. Please use scale larger "
                                                  "than 1:8 735 745", level=QgsMessageBar.WARNING)
        iface.mapCanvas().zoomScale(8735744)