#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

'''
provides the PlugableMainWindow class
'''
import logging
import pickle
import sys

from PyQt4 import QtGui, QtCore

from lib_openmolar.common.qt4.widgets import BaseMainWindow
from lib_openmolar.common.qt4.widgets import Preference

from lib_openmolar.common.qt4.plugin_tools import PluginOptionsWidget

from lib_openmolar.common.qt4.dialogs import PreferencesDialog

class PlugableMainWindow(BaseMainWindow):
    '''
    adds a preference dialog with font and plugin options
    '''
    _preferences_dialog = None

    def __init__(self, parent=None):
        BaseMainWindow.__init__(self, parent)

        icon = QtGui.QIcon(":icons/plugins.png")
        plugin_action = QtGui.QAction(icon, _("Plugins"), self)

        self.plugin_toolbar = QtGui.QToolBar()
        '''
        A toolbar which plugins can (should?) add a QAction to
        '''
        self.plugin_toolbar.setObjectName("plugins toolbar")
        self.plugin_toolbar.toggleViewAction().setText(_("Plugins Toolbar"))

        self.plugin_toolbar.addAction(plugin_action)

        self.addToolBar(self.plugin_toolbar)
        self.loadSettings()

        plugin_action.triggered.connect(self.plugin_action_triggered)

    def loadSettings(self):
        '''
        load settings from QtCore.QSettings.
        '''
        settings = QtCore.QSettings()
        #Qt settings
        self.restoreGeometry(settings.value("geometry").toByteArray())
        self.restoreState(settings.value("windowState").toByteArray())
        statusbar_hidden = settings.value("statusbar_hidden").toBool()
        self.statusbar.setVisible(not statusbar_hidden)
        self.action_show_statusbar.setChecked(not self.statusbar.isHidden())

        font = settings.value("Font").toPyObject()
        if font:
            QtGui.QApplication.instance().setFont(font)

        toolbar_set = settings.value(
            "Toolbar", QtCore.Qt.ToolButtonTextUnderIcon).toInt()[0]
        for tb in self.toolbar_list:
            tb.setToolButtonStyle(toolbar_set)

        tiny_menu = settings.value("TinyMenu").toBool()
        if tiny_menu:
            self.menuBar().toggle_visability(True)
            self.menuBar().menu_toolbar.toggleViewAction().setChecked(True)

        qsettings = QtCore.QSettings()
        #python dict of settings
        dict_ = str(qsettings.value("settings_dict").toString())
        if dict_:
            try:
                SETTINGS.PERSISTANT_SETTINGS = pickle.loads(dict_)
            except Exception as e:
                logging.exception(
                 "exception caught loading python settings...")

        SETTINGS.ALLOW_NAKED_PLUGINS = qsettings.value(
            "allow_naked_plugins_in_home_dir")

        SETTINGS.ACTIVE_PLUGINS = set(qsettings.value(
            "active_plugins").toStringList())

        SETTINGS.main_ui = self

    def saveSettings(self):
        '''
        save settings from QtCore.QSettings
        '''
        LOGGER.debug("saving settings")
        qsettings = QtCore.QSettings()
        #Qt settings
        qsettings.setValue("geometry", self.saveGeometry())
        qsettings.setValue("windowState", self.saveState())
        qsettings.setValue("statusbar_hidden", self.statusbar.isHidden())
        qsettings.setValue("Font", self.font())
        qsettings.setValue("Toolbar", self.main_toolbar.toolButtonStyle())
        qsettings.setValue("TinyMenu", not self.menuBar().isVisible())

        # SETTINGS.PERSISTANT_SETTINGS is a python dict of non qt-specific settings.
        # unfortunately.. QVariant.toPyObject can't recreate a dictionary
        # so best to pickle this
        pickled_dict = pickle.dumps(SETTINGS.PERSISTANT_SETTINGS)
        qsettings.setValue("settings_dict", pickled_dict)

        qsettings.setValue("allow_naked_plugins_in_home_dir",
            SETTINGS.ALLOW_NAKED_PLUGINS)
        qsettings.setValue("active_plugins",
            QtCore.QStringList(list(SETTINGS.ACTIVE_PLUGINS)))

    def preferences_dialog(self):
        if self._preferences_dialog is None:
            dl = self._preferences_dialog = PreferencesDialog(self)

            plugin_icon = QtGui.QIcon(":icons/plugins.png")

            plugins_pref = Preference(_("Plugins"))
            plugins_pref.setIcon(plugin_icon)
            pl_widg = PluginOptionsWidget(self)
            plugins_pref.setWidget(pl_widg)
            dl.insert_preference_dialog(0, plugins_pref)

        return self._preferences_dialog

    def show_preferences_dialog(self):
        '''
        launch the preference dialog
        '''
        LOGGER.debug("show_preferences_dialog")
        self.preferences_dialog().exec_()

    def plugin_action_triggered(self):
        '''
        dummy function. should probably be overwritten
        '''
        LOGGER.debug("plugin action triggered")
        self.preferences_dialog().select_preference(_("Plugins"))
        self.preferences_dialog().exec_()

def _test():
    from lib_openmolar import client

    app = QtGui.QApplication([])
    app.setOrganizationName("om_test")
    app.setApplicationName("om_test")

    mw = PlugableMainWindow()
    SETTINGS.load_plugins()
    mw.main_toolbar.addAction(QtGui.QAction("Placeholder", mw))
    mw.show()
    app.exec_()

if __name__ == "__main__":
    _test()
