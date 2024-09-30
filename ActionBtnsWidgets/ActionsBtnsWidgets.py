#!/usr/bin/env python

import gi
# gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import hal
import hal_glib 

from gladevcp.hal_actions import EMC_ToggleAction_ESTOP,EMC_ToggleAction_Power,EMC_Action_Home, EMC_Action_UnHome,EMC_Action_Stop
from hal_glib import GStat
from LogViewer.LogViewer import LogViewer


class myBtnEstoptoggleAction(Gtk.EventBox):   
    def __init__(self):
        super(myBtnEstoptoggleAction,self).__init__()
        self.EstopToggleAction = EMC_ToggleAction_ESTOP()
        self.EstopToggleAction._hal_init()
        self.gstat = GStat()
        
        self.add(Gtk.Image.new_from_file(filename="icons/estop_icon_pressed.png"))

        self.connect('button-press-event',self.on_button_press_event)
        # self.gstat.connect('state-estop', lambda w: self.get_child().set_from_file(filename="icons/estop_icon_pressed.png"))
        # self.gstat.connect('state-estop-reset', lambda w: self.get_child().set_from_file(filename="icons/estop_icon.png"))
        self.gstat.connect('state-estop', self.on_state_estop)
        self.gstat.connect('state-estop-reset', self.on_state_estop_reset)


    def on_button_press_event(self, widget, event):
        self.EstopToggleAction.emit("activate")
        return True
    
    def on_state_estop(self, widget):
        LogViewer().emit('public-msg', 'warning', 'Warning: Estop Activate...')
        self.get_child().set_from_file(filename="icons/estop_icon_pressed.png")

    def on_state_estop_reset(self, widget):
        LogViewer().emit('public-msg', 'info', 'Info: Estop Deactivate...')
        self.get_child().set_from_file(filename="icons/estop_icon.png")

    
class myBtnOnOfftoggleAction(Gtk.EventBox):  
    def __init__(self):
        super(myBtnOnOfftoggleAction,self).__init__(sensitive=False)
        self.PowerToggleAction = EMC_ToggleAction_Power()
        self.PowerToggleAction._hal_init()
        self.gstat = GStat()

        self.add(Gtk.Image.new_from_file(filename="icons/power_off_icon.png"))

        self.connect('button-press-event',self.on_button_press_event)       
        self.connect('button-release-event',self.on_button_release_event)

        # self.gstat.connect('state-estop', lambda w: self.set_sensitive(False))
        # self.gstat.connect('state-estop-reset', lambda w: self.set_sensitive(True))
        # self.gstat.connect('state-on', lambda w: self.get_child().set_from_file(filename="icons/power_on_icon.png"))
        # self.gstat.connect('state-off', lambda w: self.get_child().set_from_file(filename="icons/power_off_icon.png"))

        self.gstat.connect('state-estop', self.on_state_estop)
        self.gstat.connect('state-estop-reset', self.on_state_estop_reset)
        self.gstat.connect('state-on', self.on_state_on)
        self.gstat.connect('state-off', self.on_state_off)

    def on_button_press_event(self, widget, event):
        if self.PowerToggleAction.machine_on():
            self.get_child().set_from_file(filename="icons/power_on_icon_pressed.png")
        else:
            self.get_child().set_from_file(filename="icons/power_off_icon_pressed.png")
        return True
    
    def on_button_release_event(self, widget, event):
        self.PowerToggleAction.emit("activate")
        return True
    
    def on_state_estop(self, widget):
        self.set_sensitive(False)

    def on_state_estop_reset(self, widget):
        self.set_sensitive(True)

    def on_state_on(self, widget):
        LogViewer().emit('public-msg', 'info', 'Info: Power On...')
        self.get_child().set_from_file(filename="icons/power_on_icon.png")

    def on_state_off(self, widget):
        LogViewer().emit('public-msg', 'info', 'Info: Power Off...')
        self.get_child().set_from_file(filename="icons/power_off_icon.png")
    
class myBtnHomeAxisAction(Gtk.EventBox):  
    def __init__(self, hal_pin_homing_start, hal_pin_homing_break_deactivate):
        super(myBtnHomeAxisAction,self).__init__(sensitive=False)
        self.HomeAxisAction = EMC_Action_Home()
        self.HomeAxisAction._hal_init()
        self.gstat = GStat()
        self.hal_pin_homing_start = hal_pin_homing_start
        self.hal_pin_homing_break_deactivate = hal_pin_homing_break_deactivate


        self.hal_pin_homing_break_deactivate_trigger = hal_glib.GPin(self.hal_pin_homing_break_deactivate)
        self.hal_pin_homing_break_deactivate_trigger.connect("value-changed", self.on_hal_pin_homing_break_deactivate)

        self.add(Gtk.Image.new_from_file(filename="icons/zero_axis_icon.png"))

        self.connect('button-press-event',self.on_button_press_event, self.hal_pin_homing_start)
        self.connect('button-release-event',self.on_button_release_event)

        self.gstat.connect('state-off', lambda w: self.set_sensitive(False))
        self.gstat.connect('state-estop', lambda w: self.set_sensitive(False))

        # self.gstat.connect('interp-idle', lambda w: self.set_sensitive(self.HomeAxisAction.machine_on()))
        # self.gstat.connect('interp-run', lambda w: self.set_sensitive(False))

        self.gstat.connect('interp-idle', self.on_interp_idle)
        self.gstat.connect('interp-run', self.on_interp_run)

    def on_button_press_event(self, widget, event, hal_pin_homing_start):
        LogViewer().emit('public-msg', 'warning', 'Referencing Axis...')
        hal_pin_homing_start.set(1)
        #self.HomeAxisAction.emit("activate")
        self.get_child().set_from_file(filename="icons/zero_axis_icon_pressed.png") 
        return True
    
    def on_button_release_event(self, widget, event):
        self.get_child().set_from_file(filename="icons/zero_axis_icon.png")
        return True
    
    def on_interp_idle(self, widget):
        self.set_sensitive(self.HomeAxisAction.machine_on())

    def on_interp_run(self, widget):
        self.set_sensitive(False)

    def on_hal_pin_homing_break_deactivate(self, hal_pin, data=None):
        if hal_pin.get():
            self.HomeAxisAction.emit("activate")
            self.hal_pin_homing_start.set(0)

    
class myBtnMainPage(Gtk.EventBox):  
    def __init__(self):
        super(myBtnMainPage,self).__init__(sensitive=False)
        self.gstat = GStat()

        self.gstat.connect('state-off', lambda w: self.set_sensitive(False))
        self.gstat.connect('state-estop', lambda w: self.set_sensitive(False))        

  