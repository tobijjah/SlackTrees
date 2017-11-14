# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SlackTrees
                                 A QGIS plugin
 A plugin to determine trees to mount a Slackline
                             -------------------
        begin                : 2017-11-14
        copyright            : (C) 2017 by Tobias Seydewitz
        email                : tobi.seyde@gmail.com
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
    """Load SlackTrees class from file SlackTrees.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .slack_trees import SlackTrees
    return SlackTrees(iface)
