#!/usr/bin/env python

import gi
# gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from gladevcp.hal_actions import EMC_ToggleAction_ESTOP,EMC_ToggleAction_Power,EMC_Action_Home
from hal_glib import GStat


class myBtnEstoptoggleAction(Gtk.EventBox):   
    def __init__(self):
        super(myBtnEstoptoggleAction,self).__init__()
        self.EstopToggleAction = EMC_ToggleAction_ESTOP()
        self.EstopToggleAction._hal_init()
        self.gstat = GStat()
        
        self.add(Gtk.Image.new_from_file(filename="icons/estop_icon_pressed.png"))

        self.connect('button-press-event',self.on_button_press_event)
        self.gstat.connect('state-estop', lambda w: self.get_child().set_from_file(filename="icons/estop_icon_pressed.png"))
        self.gstat.connect('state-estop-reset', lambda w: self.get_child().set_from_file(filename="icons/estop_icon.png"))

    def on_button_press_event(self, widget, event):
        self.EstopToggleAction.emit("activate")
        return True
    
class myBtnOnOfftoggleAction(Gtk.EventBox):  
    def __init__(self):
        super(myBtnOnOfftoggleAction,self).__init__(sensitive=False)
        self.PowerToggleAction = EMC_ToggleAction_Power()
        self.PowerToggleAction._hal_init()
        self.gstat = GStat()

        self.add(Gtk.Image.new_from_file(filename="icons/power_off_icon.png"))

        self.connect('button-press-event',self.on_button_press_event)       
        self.connect('button-release-event',self.on_button_release_event)
        self.gstat.connect('state-estop', lambda w: self.set_sensitive(False))
        self.gstat.connect('state-estop-reset', lambda w: self.set_sensitive(True))
        self.gstat.connect('state-on', lambda w: self.get_child().set_from_file(filename="icons/power_on_icon.png"))
        self.gstat.connect('state-off', lambda w: self.get_child().set_from_file(filename="icons/power_off_icon.png"))


    def on_button_press_event(self, widget, event):
        if self.PowerToggleAction.machine_on():
            self.get_child().set_from_file(filename="icons/power_on_icon_pressed.png")
        else:
            self.get_child().set_from_file(filename="icons/power_off_icon_pressed.png")
        return True
    
    def on_button_release_event(self, widget, event):
        self.PowerToggleAction.emit("activate")
        return True
    
class myBtnHomeAxisAction(Gtk.EventBox):  
    def __init__(self):
        super(myBtnHomeAxisAction,self).__init__(sensitive=False)
        self.HomeAxisAction = EMC_Action_Home()
        self.HomeAxisAction._hal_init()
        self.gstat = GStat()

        self.add(Gtk.Image.new_from_file(filename="icons/zero_axis_icon.png"))

        self.connect('button-press-event',self.on_button_press_event)
        self.connect('button-release-event',self.on_button_release_event)

        self.gstat.connect('state-off', lambda w: self.set_sensitive(False))
        self.gstat.connect('state-estop', lambda w: self.set_sensitive(False))
        self.gstat.connect('interp-idle', lambda w: self.set_sensitive(self.HomeAxisAction.machine_on()))
        self.gstat.connect('interp-run', lambda w: self.set_sensitive(False))

    def on_button_press_event(self, widget, event):
        self.HomeAxisAction.emit("activate")
        self.get_child().set_from_file(filename="icons/zero_axis_icon_pressed.png") 
        return True
    
    def on_button_release_event(self, widget, event):
        self.get_child().set_from_file(filename="icons/zero_axis_icon.png")
        return True
    