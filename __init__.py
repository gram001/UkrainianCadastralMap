# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UkrainianCadastralMap
                                 A QGIS plugin
 This plugin adds support Ukrainian Public Cadastral Map
                             -------------------
        begin                : 2016-11-13
        copyright            : (C) 2016 by Roman Rukavchuk
        email                : gram@e-mail.ua
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load UkrainianCadastralMap class from file UkrainianCadastralMap.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ukrainian_cadastral_map import UkrainianCadastralMap
    return UkrainianCadastralMap(iface)
