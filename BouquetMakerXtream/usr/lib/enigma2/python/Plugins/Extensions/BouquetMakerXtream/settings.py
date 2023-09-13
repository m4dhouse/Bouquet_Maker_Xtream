#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import _
from .plugin import skin_directory, cfg
from .bouquetStaticText import StaticText

from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import config, configfile, getConfigListEntry, ConfigText, ConfigSelection, ConfigYesNo
from Components.Pixmap import Pixmap
from Screens.InputBox import PinInput
from Screens.MessageBox import MessageBox
from Screens.LocationBox import LocationBox
from Screens.Screen import Screen
from Screens import Standby
from Tools.BoundFunction import boundFunction

import os


class ProtectedScreen:
    def __init__(self):
        if self.isProtected():
            self.onFirstExecBegin.append(boundFunction(self.session.openWithCallback, self.pinEntered, PinInput, pinList=[cfg.adultpin.value], triesEntry=cfg.retries.adultpin, title=_("Please enter the correct pin code"), windowTitle=_("Enter pin code")))

    def isProtected(self):
        return (config.plugins.BouquetMakerXtream.adult.value)

    def pinEntered(self, result):
        if result is None:
            self.closeProtectedScreen()
        elif not result:
            self.session.openWithCallback(self.closeProtectedScreen, MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR)

    def closeProtectedScreen(self, result=None):
        self.close(None)


class BouquetMakerXtream_Settings(ConfigListScreen, Screen, ProtectedScreen):
    ALLOW_SUSPEND = True

    def __init__(self, session):
        Screen.__init__(self, session)

        if cfg.adult.getValue() is True:
            ProtectedScreen.__init__(self)

        self.session = session

        skin_path = os.path.join(skin_directory, cfg.skin.getValue())
        skin = os.path.join(skin_path, "settings.xml")
        if os.path.exists("/var/lib/dpkg/status"):
            skin = os.path.join(skin_path, "DreamOS/settings.xml")

        with open(skin, "r") as f:
            self.skin = f.read()

        self.setup_title = (_("Main Settings"))

        self.onChangedEntry = []

        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)

        self["key_red"] = StaticText(_("Back"))
        self["key_green"] = StaticText(_("Save"))
        self["information"] = StaticText("")

        self["VKeyIcon"] = Pixmap()
        self["VKeyIcon"].hide()
        self["HelpWindow"] = Pixmap()
        self["HelpWindow"].hide()

        self["actions"] = ActionMap(["BouquetMakerXtreamActions"], {
            "cancel": self.cancel,
            "red": self.cancel,
            "green": self.save,
            "ok": self.ok,
        }, -2)

        self.initConfig()
        self.onLayoutFinish.append(self.__layoutFinished)

    def clear_caches(self):
        try:
            os.system("echo 1 > /proc/sys/vm/drop_caches")
            os.system("echo 2 > /proc/sys/vm/drop_caches")
            os.system("echo 3 > /proc/sys/vm/drop_caches")
        except:
            pass

    def __layoutFinished(self):
        self.setTitle(self.setup_title)

    def cancel(self, answer=None):

        if answer is None:
            if self["config"].isChanged():
                self.session.openWithCallback(self.cancel, MessageBox, _("Really close without saving settings?"))
            else:
                self.close()
        elif answer:
            for x in self["config"].list:
                x[1].cancel()

            self.close()
        return

    def save(self):

        if cfg.adult.value is True and (cfg.adultpin.value == 0 or cfg.adultpin.value == 0000 or cfg.adultpin.value == 1111 or cfg.adultpin.value == 1234):
            self.session.open(MessageBox, _("Please change default parental pin.\n\nPin cannot be 0000, 1111 or 1234"), MessageBox.TYPE_WARNING)
            return
        else:
            if self["config"].isChanged():
                for x in self["config"].list:
                    x[1].save()
                cfg.save()
                configfile.save()

                if self.org_main != cfg.main.getValue() or self.org_wakeup != cfg.wakeup.getValue() or self.location != cfg.location.getValue() or self.locallocation != cfg.locallocation.getValue():
                    self.changedFinished()
            self.clear_caches()
            self.close()

    def changedFinished(self):
        self.session.openWithCallback(self.ExecuteRestart, MessageBox, _("You need to restart the GUI") + "\n" + _("Do you want to restart now?"), MessageBox.TYPE_YESNO)
        self.close()

    def ExecuteRestart(self, result):
        if result:
            Standby.quitMainloop(3)
        else:
            self.close()

    def initConfig(self):
        # print("*** init config ***")
        # self.cfg_skin = getConfigListEntry(_("Select skin"), cfg.skin)
        self.cfg_location = getConfigListEntry(_("playlists.txt location"), cfg.location)
        self.cfg_locallocation = getConfigListEntry(_("Local M3U File location"), cfg.locallocation)
        self.cfg_position = getConfigListEntry(_("Bouquet placement"), cfg.position)
        # self.cfg_timeout = getConfigListEntry(_("Server timeout (seconds)"), cfg.timeout)
        self.cfg_livetype = getConfigListEntry(_("Default LIVE stream type"), cfg.livetype)
        self.cfg_vodtype = getConfigListEntry(_("Default VOD/SERIES stream type"), cfg.vodtype)
        self.cfg_adult = getConfigListEntry(_("BouquetMakerXtream parental control"), cfg.adult)
        self.cfg_adultpin = getConfigListEntry(_("BouquetMakerXtream parental pin"), cfg.adultpin)
        self.cfg_main = getConfigListEntry(_("Show in main menu"), cfg.main)

        self.cfg_skipplaylistsscreen = getConfigListEntry(_("Skip playlist selection screen if only 1 playlist"), cfg.skipplaylistsscreen)

        self.cfg_autoupdate = getConfigListEntry(_("Automatic live bouquet update"), cfg.autoupdate)
        self.cfg_wakeup = getConfigListEntry(_("Automatic live update start time"), cfg.wakeup)

        self.cfg_catchup = getConfigListEntry(_("Prefix Catchup channels"), cfg.catchup)
        self.cfg_catchupprefix = getConfigListEntry(_("Select Catchup prefix symbol"), cfg.catchupprefix)
        self.cfg_catchupstart = getConfigListEntry(_("Margin before catchup (mins)"), cfg.catchupstart)
        self.cfg_catchupend = getConfigListEntry(_("Margin after catchup (mins)"), cfg.catchupend)

        self.cfg_groups = getConfigListEntry(_("Group bouquets into its own folder"), cfg.groups)

        self.org_main = cfg.main.getValue()
        self.org_wakeup = cfg.wakeup.getValue()

        self.org_main = cfg.main.getValue()
        self.org_wakeup = cfg.wakeup.getValue()
        self.location = cfg.location.getValue()
        self.locallocation = cfg.location.getValue()

        self.createSetup()

    def createSetup(self):
        self.list = []
        # self.list.append(self.cfg_skin)
        self.list.append(self.cfg_location)
        self.list.append(self.cfg_locallocation)
        # self.list.append(self.cfg_timeout)
        self.list.append(self.cfg_skipplaylistsscreen)
        # self.list.append(self.cfg_position)
        self.list.append(self.cfg_autoupdate)

        if cfg.autoupdate.value is True:
            self.list.append(self.cfg_wakeup)

        self.list.append(self.cfg_livetype)
        self.list.append(self.cfg_vodtype)

        self.list.append(self.cfg_groups)

        self.list.append(self.cfg_catchup)
        if cfg.catchup.value is True:
            self.list.append(self.cfg_catchupprefix)

        self.list.append(self.cfg_catchupstart)
        self.list.append(self.cfg_catchupend)

        self.list.append(self.cfg_adult)

        if cfg.adult.value is True:
            self.list.append(self.cfg_adultpin)

        self.list.append(self.cfg_main)

        self["config"].list = self.list
        self["config"].l.setList(self.list)
        self.handleInputHelpers()

    def handleInputHelpers(self):
        from enigma import ePoint
        currConfig = self["config"].getCurrent()

        if currConfig is not None:
            if isinstance(currConfig[1], ConfigText):
                if "VKeyIcon" in self:
                    try:
                        self["VirtualKB"].setEnabled(True)
                    except:
                        pass

                    try:
                        self["virtualKeyBoardActions"].setEnabled(True)
                    except:
                        pass
                    self["VKeyIcon"].show()

                if "HelpWindow" in self and currConfig[1].help_window and currConfig[1].help_window.instance is not None:
                    helpwindowpos = self["HelpWindow"].getPosition()
                    currConfig[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))

            else:
                if "VKeyIcon" in self:
                    try:
                        self["VirtualKB"].setEnabled(False)
                    except:
                        pass

                    try:
                        self["virtualKeyBoardActions"].setEnabled(False)
                    except:
                        pass
                    self["VKeyIcon"].hide()

    def changedEntry(self):
        self.item = self["config"].getCurrent()
        for x in self.onChangedEntry:
            x()

        try:
            if isinstance(self["config"].getCurrent()[1], ConfigYesNo) or isinstance(self["config"].getCurrent()[1], ConfigSelection):
                self.createSetup()
        except:
            pass

    def getCurrentEntry(self):
        return self["config"].getCurrent() and self["config"].getCurrent()[0] or ""

    def getCurrentValue(self):
        return self["config"].getCurrent() and str(self["config"].getCurrent()[1].getText()) or ""

    def ok(self):
        sel = self["config"].getCurrent()[1]
        if sel and sel == cfg.location:
            self.openDirectoryBrowser(cfg.location.value, "location")

        elif sel and sel == cfg.locallocation:
            self.openDirectoryBrowser(cfg.locallocation.value, "locallocation")
        else:
            pass

    def openDirectoryBrowser(self, path, cfgitem):
        if cfgitem == "location":
            try:
                self.session.openWithCallback(
                    self.openDirectoryBrowserCB,
                    LocationBox,
                    windowTitle=_("Choose Directory:"),
                    text=_("Choose directory"),
                    currDir=str(path),
                    bookmarks=config.movielist.videodirs,
                    autoAdd=True,
                    editDir=True,
                    inhibitDirs=["/bin", "/boot", "/dev", "/home", "/lib", "/proc", "/run", "/sbin", "/sys", "/usr", "/var"])
            except Exception as e:
                print(e)

        elif cfgitem == "locallocation":
            try:
                self.session.openWithCallback(
                    self.openDirectoryBrowserCB2,
                    LocationBox,
                    windowTitle=_("Choose Directory:"),
                    text=_("Choose directory"),
                    currDir=str(path),
                    bookmarks=config.movielist.videodirs,
                    autoAdd=True,
                    editDir=True,
                    inhibitDirs=["/bin", "/boot", "/dev", "/home", "/lib", "/proc", "/run", "/sbin", "/sys", "/usr", "/var"])
            except Exception as e:
                print(e)

    def openDirectoryBrowserCB(self, path):
        if path is not None:
            cfg.location.setValue(path)
        return

    def openDirectoryBrowserCB2(self, path):
        if path is not None:
            cfg.locallocation.setValue(path)
        return
