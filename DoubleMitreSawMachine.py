#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

import os,sys,csv

import linuxcnc
import time, subprocess

from gladevcp.core import Info, Status, Action

import hal
import hal_glib 


from ProfileWidgets.ManualProfileCutWidget import ManualProfileCutWidget
from ProfileWidgets.BarWidget import BarWidget
from ProfileWidgets.StepByStepCutWidget import StepByStepCutWidget
from ActionBtnsWidgets.ActionsBtnsWidgets import myBtnEstoptoggleAction,myBtnOnOfftoggleAction,myBtnHomeAxisAction

from CSVViewerWidget.CSVViewerWidget import CSVViewerWidget, CSVViewerEntry
from DxfViewer.DxfViewer import DxfViewer
from DxfExplorer.DxfExplorer import DxfExplorer
from LogViewer.LogViewer import LogViewer

INFO = Info()
STATUS = Status()
ACTION = Action()

class DoubleMitreMachine(Gtk.Window):

    def __init__(self,inifile):
        super().__init__()
        self.set_default_size(1920, 1080)
        # self.set_decorated(False)
        # self.fullscreen()
        self.set_border_width(0) 

        self.inifile = linuxcnc.ini(os.environ["INI_FILE_NAME"])

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('css_styles_sheets/style.css')
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.hal_component = hal.component("DoubleMitreSawMachine")

        self.update_rate_cmds = 100
        self.update_rate_gui = 100

        ### Hal Pins ###

        self.hal_pin_homing_start = self.hal_component.newpin("homing-start", hal.HAL_BIT, hal.HAL_OUT)
        self.hal_pin_homing_break_deactivate = self.hal_component.newpin("homing-break-deactivate", hal.HAL_BIT, hal.HAL_IN)

        self.hal_pin_stop_move = self.hal_component.newpin("stop-move", hal.HAL_BIT, hal.HAL_OUT)

        self.hal_pin_move_to_length = self.hal_component.newpin("move-to-length", hal.HAL_FLOAT, hal.HAL_IN)
        self.hal_pin_pos_fb = self.hal_component.newpin("pos-fb", hal.HAL_FLOAT, hal.HAL_IN)

        self.hal_pin_cut_start_manual = self.hal_component.newpin("cut-start-manual", hal.HAL_BIT, hal.HAL_OUT)
        self.hal_pin_cut_start_auto = self.hal_component.newpin("cut-start-auto", hal.HAL_BIT, hal.HAL_OUT)
        self.hal_pin_cut_start_step_slide = self.hal_component.newpin("cut-start-step-slide", hal.HAL_BIT, hal.HAL_OUT)

        self.hal_pin_cut_add = self.hal_component.newpin("cut-add", hal.HAL_BIT, hal.HAL_IO)
        self.hal_pin_free_cut_list = self.hal_component.newpin("free-cut-list", hal.HAL_BIT, hal.HAL_IO)
        #self.hal_pin_print_cut_list = self.hal_component.newpin("print-cut-list", hal.HAL_BIT, hal.HAL_IO)
        self.hal_pin_cut_list_wr = self.hal_component.newpin("cut-list-wr", hal.HAL_BIT, hal.HAL_OUT)
        self.hal_pin_cut_status = self.hal_component.newpin("cut-status", hal.HAL_U32, hal.HAL_IN)
        self.hal_pin_cut_list_pathX_to_gui = self.hal_component.newpin("list-line-pathX-to-gui", hal.HAL_U32, hal.HAL_IN)
        self.hal_pin_cut_list_pathY_to_gui = self.hal_component.newpin("list-line-pathY-to-gui", hal.HAL_U32, hal.HAL_IN)
        self.hal_pin_cut_list_path_update = self.hal_component.newpin("list-line-path-update", hal.HAL_BIT, hal.HAL_IN)

        self.hal_pin_bottom_cut_length =self.hal_component.newpin("bottom-cut-length", hal.HAL_FLOAT, hal.HAL_OUT)
        self.hal_pin_top_cut_length = self.hal_component.newpin("top-cut-length", hal.HAL_FLOAT, hal.HAL_OUT)
        self.hal_pin_cut_height = self.hal_component.newpin("height-cut-length", hal.HAL_FLOAT, hal.HAL_OUT)
        self.hal_pin_cut_left_angle = self.hal_component.newpin("cut-left-angle", hal.HAL_FLOAT, hal.HAL_OUT)
        self.hal_pin_cut_right_angle = self.hal_component.newpin("cut-right-angle", hal.HAL_FLOAT, hal.HAL_OUT)

        self.hal_pin_left_saw_blade = self.hal_component.newpin("left-saw-blade-btn", hal.HAL_BIT, hal.HAL_OUT)
        self.hal_pin_right_saw_blade = self.hal_component.newpin("right-saw-blade-btn", hal.HAL_BIT, hal.HAL_OUT)

        self.hal_pin_saw_blade_output_time = self.hal_component.newpin("saw-blade-output-time", hal.HAL_FLOAT, hal.HAL_OUT)
        self.hal_pin_number_of_cuts = self.hal_component.newpin("number-of-cuts", hal.HAL_U32, hal.HAL_IO)

        self.hal_pin_cut_complete = self.hal_component.newpin("cut-complete", hal.HAL_BIT, hal.HAL_IO)

        self.count_start_manual_pulse = [0]
        self.start_manual_pulse = [False]

        self.count_stop_pulse = [0]
        self.stop_pulse = [False]

        self.count_cut_add_pulse = [0]
        self.cut_add_pulse = [False]

        self.hal_pin_cut_status_trigger = hal_glib.GPin( self.hal_pin_cut_status)
        self.hal_pin_cut_status_trigger.connect("value-changed", self.on_cut_status_changed)

        self.hal_pin_cut_complete_trigger = hal_glib.GPin( self.hal_pin_cut_complete)
        self.hal_pin_cut_complete_trigger.connect("value-changed", self.on_cut_complete_changed)

        self.hal_pin_number_of_cuts_trigger = hal_glib.GPin( self.hal_pin_number_of_cuts)
        self.hal_pin_number_of_cuts_trigger.connect("value-changed", self.on_number_of_cuts_changed)

        self.hal_pin_cut_list_path_update_trigger = hal_glib.GPin( self.hal_pin_cut_list_path_update)
        self.hal_pin_cut_list_path_update_trigger.connect("value-changed", self.on_cut_list_path_update_changed)

        ### End Hal Pins ###

        torneiroLogo = Gtk.Image().new_from_file(filename="images/torneiro_logo.png") 

        self.ioStatusBtn = Gtk.EventBox(can_focus=True)         
        self.ioStatusBtn.add(Gtk.Image.new_from_file(filename="icons/in_out_icon.png")) 

        self.alarmsBtn = Gtk.EventBox(can_focus=True) 
        self.alarmsBtn.add(Gtk.Image.new_from_file(filename="icons/alarm_icon.png"))         

        self.settingsBtn = Gtk.EventBox(can_focus=True)  
        self.settingsBtn.add(Gtk.Image.new_from_file(filename="icons/settings_icon.png"))      

        self.exitBtn = Gtk.EventBox(can_focus=True)
        self.exitBtn.add(Gtk.Image.new_from_file(filename="icons/exit_icon.png"))         

        self.goHomePageBtn = Gtk.EventBox(can_focus=True)
        self.goHomePageBtn.add(Gtk.Image.new_from_file(filename="icons/go_home_icon.png"))  

        self.log_viewer = LogViewer()
        self.log_viewer.set_name('scrolled_window')   
        
        GLib.idle_add(lambda: self.log_viewer.set_margin_start(self.goHomePageBtn.get_allocated_width()))
        GLib.idle_add(lambda: self.log_viewer.set_margin_end(0)) 

        vBoxMainStruct = Gtk.VBox(homogeneous=False,vexpand=True)

        hBoxLogoHeader = Gtk.HBox()
        hBoxLogoHeader.pack_start(torneiroLogo,False,False,0)

##########################################################################################
#####                                                                                #####
#####       #Build Test Buttons                                                      #####
#####                                                                                #####
##########################################################################################
        self.BusyHandBtns =  Gtk.Button(name="testBtn",label="BusyHandBtns")
        self.clampsBtn =    Gtk.Button(name="testBtn",label="ClampsBtn")
        self.printListBtn = Gtk.Button(name="testBtn",label="PrintList")

        self.hal_pin_busy_hand_busy_btns = hal_glib.GPin( self.hal_component.newpin("busy-hand-btns", hal.HAL_BIT, hal.HAL_OUT))

        self.hal_pin_clamps_btn = hal_glib.GPin( self.hal_component.newpin("clamps-btn", hal.HAL_BIT, hal.HAL_OUT))

        self.hal_pin_print_cut_list_btn = hal_glib.GPin( self.hal_component.newpin("print-cut-list", hal.HAL_BIT, hal.HAL_IO))

        BusyHandBtnsLastClickTime = [0]
        ClampsBtnLastClickTime = [0]
        PrintListBtnLastClickTime = [0]

        self.BusyHandBtns.connect('button-press-event', self.on_button_press_event, self.hal_pin_busy_hand_busy_btns, BusyHandBtnsLastClickTime)
        self.BusyHandBtns.connect('button-release-event', self.on_button_release_event, self.hal_pin_busy_hand_busy_btns, BusyHandBtnsLastClickTime)

        self.clampsBtn.connect('button-press-event', self.on_button_press_event,self.hal_pin_clamps_btn, ClampsBtnLastClickTime)
        self.clampsBtn.connect('button-release-event', self.on_button_release_event,self.hal_pin_clamps_btn, ClampsBtnLastClickTime)

        self.printListBtn.connect('button-press-event', self.on_button_press_event,self.hal_pin_print_cut_list_btn, PrintListBtnLastClickTime)
        self.printListBtn.connect('button-release-event', self.on_button_release_event,self.hal_pin_print_cut_list_btn, PrintListBtnLastClickTime)

        hboxTestBtns = Gtk.HBox()
        hboxTestBtns.pack_start(self.BusyHandBtns,False,False,0)
        hboxTestBtns.pack_start(self.clampsBtn,False,False,0)
        hboxTestBtns.pack_start(self.printListBtn,False,False,0)

##########################################################################################
#####                                                                                #####
#####       #End Build Test Buttons, Erase after test                                #####
#####                                                                                #####
##########################################################################################

        hBoxLogoHeader.pack_start(hboxTestBtns,False,False,0)

        hBoxSecurityBtns = Gtk.HBox(spacing=50,homogeneous=True,name='securityBtns')

        self.eStopToggleBtn = myBtnEstoptoggleAction()

        self.onOffToggleBtn = myBtnOnOfftoggleAction()                        

        hBoxSecurityBtns.pack_start(self.eStopToggleBtn,False,False,0)
        hBoxSecurityBtns.pack_end(self.onOffToggleBtn,False,False,0)

        hBoxBtnsHeader = Gtk.HBox(spacing=50,homogeneous=True)

        hBoxBtnsHeader.pack_start(self.settingsBtn,False,False,0)
        hBoxBtnsHeader.pack_start(self.alarmsBtn,False,False,0)
        hBoxBtnsHeader.pack_start(self.ioStatusBtn,False,False,0)   

        hBoxHeader = Gtk.HBox(homogeneous=False,name='header')
        hBoxHeader.pack_start(hBoxLogoHeader,False,False,0)
        hBoxHeader.set_center_widget(hBoxSecurityBtns)
        hBoxHeader.pack_end(hBoxBtnsHeader,False,False,0)

        vBoxMainStruct.pack_start(hBoxHeader,False,True,0)  

        self.notebookPages = Gtk.Notebook(name='notebookPages',show_tabs=False,show_border=False)

        self.pages = {'main':0,'manual':1,'auto':2,'stepSlide':3,
                     'ioState':4,'alarms':5,'settings':6,'dxfExplorer':7}

        vBoxMainStruct.pack_start(self.notebookPages,False,True,0)

        vBoxFooter = Gtk.VBox()

        hBoxFooter = Gtk.HBox(name='footer')
        
        hBoxFooter.pack_start(self.goHomePageBtn,False,False,0)
        hBoxFooter.pack_start(self.log_viewer,True,True,0)
        hBoxFooter.pack_end(self.exitBtn,False,False,0)

        vBoxFooter.pack_start(hBoxFooter,False,False,0)

        vBoxMainStruct.pack_end(vBoxFooter,False,True,0)                          

##########################################################################################################################################
#####                                                                                                                                #####
#####       #Build Main Page                                                                                                         #####
#####                                                                                                                                #####
##########################################################################################################################################      


        self.homeAxisBtn = myBtnHomeAxisAction(hal_pin_homing_start = self.hal_pin_homing_start, 
                                               hal_pin_homing_break_deactivate = self.hal_pin_homing_break_deactivate)

        self.gstatModes = hal_glib.GStat()

        self.manualCuttingBtn = Gtk.EventBox(sensitive=False)
        self.manualCuttingBtn.add(Gtk.Image.new_from_file(filename="icons/manual_mode_icon.png"))                 

        self.autoCuttingBtn = Gtk.EventBox(sensitive=False)
        self.autoCuttingBtn.add(Gtk.Image.new_from_file(filename="icons/auto_mode_icon.png"))         

        self.stepSlideCuttingBtn = Gtk.EventBox(sensitive=False)   
        self.stepSlideCuttingBtn.add(Gtk.Image.new_from_file(filename="icons/step_slide_mode_icon.png")) 

        self.manageDxfBtn = Gtk.EventBox()
        self.manageDxfBtn.add(Gtk.Image.new_from_file(filename="icons/step_slide_mode_icon.png")) 

        self.gstatModes.connect('all-homed',  self.set_sensitive_btns_modes)
        self.gstatModes.connect('not-all-homed', self.unset_sensitive_btns_modes)   

        vGridMainBtns = Gtk.Grid(row_homogeneous=True,column_homogeneous=True,vexpand=True,hexpand=True)

        vGridMainBtns.add(self.homeAxisBtn)
        vGridMainBtns.attach(self.manualCuttingBtn,1,0,1,1)
        vGridMainBtns.attach(self.manageDxfBtn,2,0,1,1)
        vGridMainBtns.attach(self.autoCuttingBtn,0,1,1,1)
        vGridMainBtns.attach(self.stepSlideCuttingBtn,1,1,1,1)
        

        self.notebookPages.append_page(vGridMainBtns)       

        self.manualCuttingBtn.connect('button-press-event',self.on_manualCutting_btn_pressed)
        self.manualCuttingBtn.connect('button-release-event',self.on_manualCutting_btn_released)

        self.autoCuttingBtn.connect('button-press-event',self.on_autoCutting_btn_pressed)
        self.autoCuttingBtn.connect('button-release-event',self.on_autoCutting_btn_released)

        self.stepSlideCuttingBtn.connect('button-press-event',self.on_stepSlideCutting_btn_pressed)
        self.stepSlideCuttingBtn.connect('button-release-event',self.on_stepSlideCutting_btn_released)

        self.ioStatusBtn.connect('button-press-event',self.on_ioStatus_btn_pressed)
        self.ioStatusBtn.connect('button-release-event',self.on_ioStatus_btn_released)   

        self.alarmsBtn.connect('button-press-event',self.on_alarms_btn_pressed)
        self.alarmsBtn.connect('button-release-event',self.on_alarms_btn_released)  

        self.settingsBtn.connect('button-press-event',self.on_settings_btn_pressed)
        self.settingsBtn.connect('button-release-event',self.on_settings_btn_released)  

        self.notebookPages.connect('switch-page',self.on_switch_page)                 

        self.exitBtn.connect('button-press-event',self.on_exit_btn_pressed)
        self.exitBtn.connect('button-release-event',self.on_exit_btn_released)

        self.goHomePageBtn.connect('button-press-event',self.on_goHomePage_btn_pressed)
        self.goHomePageBtn.connect('button-release-event',self.on_goHomePage_btn_released)

        self.manageDxfBtn.connect('button-press-event',self.on_manageDxf_btn_pressed)
        self.manageDxfBtn.connect('button-release-event',self.on_manageDxf_btn_released)

##########################################################################################################################################
#####                                                                                                                                #####
#####       #Build Manual Cutting Page                                                                                                #####
#####                                                                                                                                #####
##########################################################################################################################################      

        self.inside_angles = self.inifile.find("DISPLAY", "INSIDE_ANGLES") or "unknown"
        self.custom_angles = self.inifile.find("DISPLAY", "CUSTOM_ANGLES") or "unknown"
        max_angle = self.inifile.find("DISPLAY", "MAX_ANGLE") or "unknown"
        min_angle = self.inifile.find("DISPLAY", "MIN_ANGLE") or "unknown"

        if self.custom_angles == "YES":
            max_angle = float(max_angle)
            min_angle = float(min_angle)
        elif self.custom_angles == "NO":
            if self.inside_angles == "YES":
                max_angle = 157.5
            elif self.inside_angles == "NO":
                max_angle = 90.0
            else:
                max_angle = 90.0
            min_angle = 22.5  
        else:
            max_angle = 90.0
            min_angle = 22.5      

        self.profile_max_length = self.inifile.find("DISPLAY", "PROFILE_MAX_LIMIT") or "unknown"
        self.profile_min_length = self.inifile.find("DISPLAY", "PROFILE_MIN_LIMIT") or "unknown"
        self.profile_max_height = self.inifile.find("DISPLAY", "PROFILE_MAX_HEIGHT_LIMIT") or "unknown"

        try:
            profile_max_length = float(self.profile_max_length)
        except ValueError:
            profile_max_length = 6500.0

        try:
            profile_min_length = float(self.profile_min_length)
        except ValueError:
            profile_min_length = 300.0

        try:
            profile_max_height = float(self.profile_max_height)
        except ValueError:
            profile_max_height = 300.0      

        self.manualCuttingProfileWidget = ManualProfileCutWidget(self,
                                                                 max_angle=max_angle,
                                                                 max_length=profile_max_length,
                                                                 min_length=profile_min_length)  
        
        self.last_FbPos = 0.0  

        self.dxfViewerManual = DxfViewer(manual_profile_cut_widget=self.manualCuttingProfileWidget)   
        self.manualCuttingProfileWidget.set_dxfViewer(self.dxfViewerManual)

        self.leftDiskManualBtn = Gtk.EventBox(can_focus=True)
        self.leftDiskManualBtnImage = Gtk.Image.new_from_file(filename="icons/disk_off_icon.png")
        self.leftDiskManualBtn.add(self.leftDiskManualBtnImage)

        self.playManualBtn = Gtk.EventBox(can_focus=True)
        self.playManualBtn.add(Gtk.Image.new_from_file(filename="icons/play_icon.png"))  
        self.moveCMD = False
        self.manualPremode = None

        self.stopManualBtn = Gtk.EventBox(can_focus=True,sensitive=False)
        self.stopManualBtn.add(Gtk.Image.new_from_file(filename="icons/stop_icon.png"))   

        self.angleLeftHeadManualBtn = Gtk.EventBox(can_focus=True)
        self.angleLeftHeadManualBtn.add(Gtk.Image.new_from_file(filename="icons/left_head_angle_90_icon.png"))   

        self.angleRightHeadManualBtn = Gtk.EventBox(can_focus=True)
        self.angleRightHeadManualBtn.add(Gtk.Image.new_from_file(filename="icons/right_head_angle_90_icon.png"))       

        self.rightDiskManualBtn = Gtk.EventBox(can_focus=True)
        self.rightDiskManualBtnImage = Gtk.Image.new_from_file(filename="icons/disk_off_icon.png")
        self.rightDiskManualBtn.add(self.rightDiskManualBtnImage)

        self.angleRightHeadManualState = 0
        self.angleLeftHeadManualState = 0 

        self.leftDiskState = [0]
        self.leftDiskLastClickTime = [0]

        self.rightDiskState = [0]
        self.rightDiskLastClickTime = [0]

        vboxManualCuttingProfileWidget_ManualCmdBtns = Gtk.VBox(homogeneous=False) 
        hboxManualCuttingProfileWidget = Gtk.HBox(homogeneous=False)     
        hboxManualCuttingProfileWidget.pack_start(self.manualCuttingProfileWidget,True,True,0)

        hBoxManualCmdBtns = Gtk.HBox(homogeneous=True)
        hBoxManualCmdBtns.pack_start(self.leftDiskManualBtn,False,False,0)
        hBoxManualCmdBtns.pack_start(self.playManualBtn,False,False,0)
        hBoxManualCmdBtns.pack_start(self.angleLeftHeadManualBtn,False,False,0)
        hBoxManualCmdBtns.pack_start(self.angleRightHeadManualBtn,False,False,0)
        hBoxManualCmdBtns.pack_start(self.stopManualBtn,False,False,0)
        hBoxManualCmdBtns.pack_end(self.rightDiskManualBtn,False,False,0)

        vboxManualCuttingProfileWidget_ManualCmdBtns.pack_start(hboxManualCuttingProfileWidget,True,True,0)
        vboxManualCuttingProfileWidget_ManualCmdBtns.pack_end(hBoxManualCmdBtns,False,False,0)

        hboxManualPage = Gtk.HBox(homogeneous=False)
        hboxManualPage.pack_start(self.dxfViewerManual,False, False,0)
        hboxManualPage.pack_end(vboxManualCuttingProfileWidget_ManualCmdBtns,True,True,0)

        self.notebookPages.append_page(hboxManualPage)      

        self.playManualBtn.connect('button-press-event',self.on_playManual_btn_pressed)
        self.playManualBtn.connect('button-release-event',self.on_playManual_btn_released)

        self.stopManualBtn.connect('button-press-event',self.on_stopManual_btn_pressed)
        self.stopManualBtn.connect('button-release-event',self.on_stopManual_btn_released)   

        self.angleLeftHeadManualBtn.connect('button-press-event',self.on_angleLeftHeadManual_btn_pressed)
        self.angleLeftHeadManualBtn.connect('button-release-event',self.on_angleLeftHeadManual_btn_released)   

        self.angleRightHeadManualBtn.connect('button-press-event',self.on_angleRightHeadManual_btn_pressed)
        self.angleRightHeadManualBtn.connect('button-release-event',self.on_angleRightHeadManual_btn_released)         

        self.leftDiskManualBtn.connect('button-press-event',self.on_disk_btn_pressed,self.leftDiskState,self.leftDiskLastClickTime,self.hal_pin_left_saw_blade,'left')
        self.rightDiskManualBtn.connect('button-press-event',self.on_disk_btn_pressed,self.rightDiskState,self.rightDiskLastClickTime,self.hal_pin_right_saw_blade,'right')

        self.leftDiskManualBtn.connect('button-release-event',self.on_disk_btn_released,self.leftDiskState,'left')
        self.rightDiskManualBtn.connect('button-release-event',self.on_disk_btn_released,self.rightDiskState,'right')

        self.manualCuttingProfileWidget.connect('bad-value', self.on_bad_value)

##########################################################################################################################################
#####                                                                                                                                #####
#####       #Build Auto Cutting Page                                                                                                #####
#####                                                                                                                                #####
##########################################################################################################################################      

        self.fifo_path = '/tmp/cut_list_fifo'

        if not os.path.exists(self.fifo_path):
            os.mkfifo(self.fifo_path)

        self.max_length = self.inifile.find("JOINT_0", "MAX_LIMIT") or "unknown"
        self.min_length = self.inifile.find("JOINT_0", "MIN_LIMIT") or "unknown"

        try:
            max_length = float(self.max_length)
        except ValueError:
            max_length = 4000.0

        try:
            min_length = float(self.min_length)
        except ValueError:
            min_length = 290.0

        vBoxAutoPage = Gtk.VBox(spacing=10,homogeneous=False)        

        self.openListBtn = Gtk.EventBox(can_focus=True)
        self.openListBtn.set_margin_start(10)
        self.openListBtn.add(Gtk.Image.new_from_file(filename="icons/open_cut_list_csv.png"))  

        self.saveListBtn = Gtk.EventBox(can_focus=True)
        self.saveListBtn.add(Gtk.Image.new_from_file(filename="icons/save_cut_list_csv.png"))   

        self.clearListBtn = Gtk.EventBox(can_focus=True)
        self.clearListBtn.add(Gtk.Image.new_from_file(filename="icons/clear_cut_list_csv.png")) 

        self.playListBtn = Gtk.EventBox(can_focus=True)
        self.playListBtn.add(Gtk.Image.new_from_file(filename="icons/play_icon.png"))

        self.stopListBtn = Gtk.EventBox(can_focus=True)
        self.stopListBtn.set_sensitive(False)
        self.stopListBtn.add(Gtk.Image.new_from_file(filename="icons/stop_icon.png"))

        self.leftDiskListBtn = Gtk.EventBox(can_focus=True)
        self.leftDiskListBtnImage = Gtk.Image.new_from_file(filename="icons/disk_off_icon.png")
        self.leftDiskListBtn.add(self.leftDiskListBtnImage)

        self.rightDiskListBtn = Gtk.EventBox(can_focus=True)
        self.rightDiskListBtnImage = Gtk.Image.new_from_file(filename="icons/disk_off_icon.png")
        self.rightDiskListBtn.add(self.rightDiskListBtnImage) 

        self.openListBtn.connect('button-press-event',self.on_open_btn_pressed)
        self.openListBtn.connect('button-release-event',self.on_open_btn_released)

        self.saveListBtn.connect('button-press-event',self.on_save_btn_pressed)
        self.saveListBtn.connect('button-release-event',self.on_save_btn_released)

        self.clearListBtn.connect('button-press-event',self.on_clear_btn_pressed)
        self.clearListBtn.connect('button-release-event',self.on_clear_btn_released)

        self.playListBtn.connect('button-press-event',self.on_play_btn_pressed)
        self.playListBtn.connect('button-release-event',self.on_play_btn_released)

        self.stopListBtn.connect('button-press-event',self.on_stop_btn_pressed)
        self.stopListBtn.connect('button-release-event',self.on_stop_btn_released)

        self.leftDiskListBtn.connect('button-press-event',self.on_disk_btn_pressed,self.leftDiskState,self.leftDiskLastClickTime,self.hal_pin_left_saw_blade,'left')
        self.rightDiskListBtn.connect('button-press-event',self.on_disk_btn_pressed,self.rightDiskState,self.rightDiskLastClickTime,self.hal_pin_right_saw_blade,'right')
        
        self.leftDiskListBtn.connect('button-release-event',self.on_disk_btn_released,self.leftDiskState,'left')       
        self.rightDiskListBtn.connect('button-release-event',self.on_disk_btn_released,self.rightDiskState,'right')

        hBoxAutoListBtns = Gtk.HBox(homogeneous=False)
        hBoxAutoListBtns.pack_start(self.openListBtn,False,False,0)
        hBoxAutoListBtns.pack_start(self.saveListBtn,False,False,0)
        hBoxAutoListBtns.pack_end(self.clearListBtn,False,False,0)

        self.autoFbPosEntry = CSVViewerEntry( parent=self, 
                                             num_int_digits=4, 
                                             num_decimal_digits=2,
                                             init_value=min_length,
                                             max_value=max_length,
                                             min_value=min_length)
        self.autoFbPosEntry.set_name('entryCsvFbPos')
        self.autoFbPosEntry.set_can_focus(False)
        self.autoFbPosEntry.set_sensitive(True)
        self.autoFbPosEntry.set_max_length(7)
        self.autoFbPosEntry.set_alignment(xalign=0.5)
        self.autoFbPosEntry.set_editable(False)

        hBoxAutoListCtrlBtns = Gtk.HBox(homogeneous=False)
        hBoxAutoListCtrlBtns.pack_start(self.leftDiskListBtn,False,False,0)
        hBoxAutoListCtrlBtns.pack_start(self.playListBtn,False,False,0)
        hBoxAutoListCtrlBtns.pack_start(self.stopListBtn,False,False,0)
        hBoxAutoListCtrlBtns.pack_end(self.rightDiskListBtn,False,False,0)

        hboxAutoListBtns = Gtk.HBox(homogeneous=False)
        hboxAutoListBtns.pack_start(hBoxAutoListBtns,False,False,0)
        hboxAutoListBtns.pack_start(self.autoFbPosEntry,True,True,0)
        hboxAutoListBtns.pack_end(hBoxAutoListCtrlBtns,False,False,0)
        
        self.barWidget = BarWidget()
        self.barWidget.set_size_request(-1, 35)
        self.barWidget.set_margin_start(10)
        self.barWidget.set_margin_end(10)

        vBoxAutoPage.pack_start(hboxAutoListBtns,False,False,0)
        vBoxAutoPage.pack_start(self.barWidget,True,True,0)
        vBoxAutoPage.set_child_packing(self.barWidget, False, False, 0, Gtk.PackType.START)

        # Create CSV Viewer Widget
        self.csvViewerWidget = CSVViewerWidget(barWidget=self.barWidget, 
                                               max_angle=max_angle, 
                                               min_angle=min_angle,
                                               max_length=profile_max_length,
                                               min_length=profile_min_length,
                                               max_height=profile_max_height)

        # Create Dxf Viewer Widget
        self.dxfViewerAuto = DxfViewer(csv_viewer_widget=self.csvViewerWidget)

        self.csvViewerWidget.set_dxfViewerWidget(self.dxfViewerAuto)

        hboxTreeviewDxfViewer = Gtk.HBox(spacing=10,homogeneous=False)
        hboxTreeviewDxfViewer.pack_start(self.csvViewerWidget,True,True,0)

        hboxTreeviewDxfViewer.pack_end(self.dxfViewerAuto,False,False,0)

        vBoxAutoPage.pack_start(hboxTreeviewDxfViewer,True,True,0)

        #vBoxAutoPage.pack_start(hBoxAutoListCtrlBtns,False,False,0)

        self.notebookPages.append_page(vBoxAutoPage)

##########################################################################################################################################
#####                                                                                                                                #####
#####       #Build Slide Cutting Page                                                                                                #####
#####                                                                                                                                #####
##########################################################################################################################################      

        vBoxStepByStepPage = Gtk.VBox(homogeneous=False)     

        self.wedgeCuttingProfileWidget = StepByStepCutWidget()

        vBoxStepByStepPage.pack_start(self.wedgeCuttingProfileWidget,True,True,0)

        self.playStepByStepBtn = Gtk.EventBox(can_focus=True)
        self.playStepByStepBtn.add(Gtk.Image.new_from_file(filename="icons/play_icon.png"))
        
        self.stopStepByStepBtn = Gtk.EventBox(can_focus=True)
        self.stopStepByStepBtn.set_sensitive(False)
        self.stopStepByStepBtn.add(Gtk.Image.new_from_file(filename="icons/stop_icon.png"))
        
        self.leftDiskStepByStepBtn = Gtk.EventBox(can_focus=True)
        self.leftDiskStepByStepBtn.add(Gtk.Image.new_from_file(filename="icons/disk_off_icon.png"))   

        self.angleLeftStepByStepBtn = Gtk.EventBox(can_focus=True)
        self.angleLeftStepByStepBtn.add(Gtk.Image.new_from_file(filename="icons/left_head_angle_90_icon.png"))   

        hBoxStepByStepBtns = Gtk.HBox(homogeneous=True)
        hBoxStepByStepBtns.pack_start(self.leftDiskStepByStepBtn,False,False,0)
        hBoxStepByStepBtns.pack_start(self.angleLeftStepByStepBtn,False,False,0)
        hBoxStepByStepBtns.pack_start(self.playStepByStepBtn,False,False,0)
        hBoxStepByStepBtns.pack_end(self.stopStepByStepBtn,False,False,0)

        vBoxStepByStepPage.pack_end(hBoxStepByStepBtns,False,False,0)

        self.notebookPages.append_page(vBoxStepByStepPage)

##########################################################################################################################################
#####                                                                                                                                #####
#####       #Build I/O Status Page                                                                                               #####
#####                                                                                                                                #####
##########################################################################################################################################

        self.ioStatusPage = Gtk.Box()
        self.ioStatusPage.set_border_width(10)
        self.ioStatusPage.add(Gtk.Label(label="I/O Status Page!."))
        self.notebookPages.append_page(self.ioStatusPage)

##########################################################################################################################################
#####                                                                                                                                #####
#####       #Build Alarms Codes Page                                                                                               #####
#####                                                                                                                                #####
##########################################################################################################################################

        self.alarmCodesPage = Gtk.Box()
        self.alarmCodesPage.set_border_width(10)
        self.alarmCodesPage.add(Gtk.Label(label="Alarms Codes Page!."))
        self.notebookPages.append_page(self.alarmCodesPage)         

##########################################################################################################################################
#####                                                                                                                                #####
#####       #Build Settings Page                                                                                               #####
#####                                                                                                                                #####
##########################################################################################################################################

        self.settingsPage = Gtk.Box()
        self.settingsPage.set_border_width(10)
        self.settingsPage.add(Gtk.Label(label="Settings Page!."))
        self.notebookPages.append_page(self.settingsPage) 

##########################################################################################################################################
#####                                                                                                                                #####
#####       #Build Manage Dxf Page                                                                                               #####
#####                                                                                                                                #####
##########################################################################################################################################

        self.manageDxfPage = Gtk.Box()
        self.manageDxfPage.set_border_width(10)

        self.dxfExplorer = DxfExplorer()

        self.manageDxfPage.add(self.dxfExplorer)
        self.notebookPages.append_page(self.manageDxfPage) 

        self.update_cmds_timer = GLib.timeout_add(self.update_rate_cmds, self.on_update_cmds_timeout)
        self.update_gui_timer = GLib.timeout_add(self.update_rate_gui, self.on_update_gui_timeout)

        self.add(vBoxMainStruct)

        self.hal_component.ready()

##########################################################################################################################################
#####                                                                                                                                #####
#####       Main Page Logic Develop                                                                                                 #####
#####                                                                                                                                #####
##########################################################################################################################################


    def on_manualCutting_btn_pressed(self,widget,event):
        child = widget.get_child()    
        child.set_from_file(filename="icons/manual_mode_icon_pressed.png")

    def on_manualCutting_btn_released(self,widget,event):
        self.notebookPages.set_current_page(self.pages['manual'])
        child = widget.get_child() 
        child.set_from_file(filename="icons/manual_mode_icon.png")     

    def on_autoCutting_btn_pressed(self,widget,event):
        child = widget.get_child()
        child.set_from_file(filename="icons/auto_mode_icon_pressed.png")

    def on_autoCutting_btn_released(self,widget,event):
        self.notebookPages.set_current_page(self.pages['auto']) 
        child = widget.get_child() 
        child.set_from_file(filename="icons/auto_mode_icon.png")         

    def on_stepSlideCutting_btn_pressed(self,widget,event):
        child = widget.get_child()
        child.set_from_file(filename="icons/step_slide_mode_icon_pressed.png")        

    def on_stepSlideCutting_btn_released(self,widget,event):
        self.notebookPages.set_current_page(self.pages['stepSlide']) 
        child = widget.get_child() 
        child.set_from_file(filename="icons/step_slide_mode_icon.png")   

    def set_sensitive_btns_modes(self,gstat):
        LogViewer().emit('public-msg', 'info', 'Info: All Axes Homed...')
        self.manualCuttingBtn.set_sensitive(True)
        self.autoCuttingBtn.set_sensitive(True)
        self.stepSlideCuttingBtn.set_sensitive(True)

    def unset_sensitive_btns_modes(self,gstat,joint):
        LogViewer().emit('public-msg', 'warning', 'Warning: %s Axis Not Homed...' % joint)
        self.manualCuttingBtn.set_sensitive(False)
        self.autoCuttingBtn.set_sensitive(False)
        self.stepSlideCuttingBtn.set_sensitive(False) 

    def on_ioStatus_btn_pressed(self,widget,event):
        widget.grab_focus()
        child = widget.get_child()
        child.set_from_file(filename="icons/in_out_icon_pressed.png")        

    def on_ioStatus_btn_released(self,widget,event):
        self.notebookPages.set_current_page(self.pages['ioState']) 
        child = widget.get_child() 
        child.set_from_file(filename="icons/in_out_icon.png") 

    def on_alarms_btn_pressed(self,widget,event):
        widget.grab_focus()
        child = widget.get_child()
        child.set_from_file(filename="icons/alarm_icon_pressed.png")        

    def on_alarms_btn_released(self,widget,event):
        self.notebookPages.set_current_page(self.pages['alarms']) 
        child = widget.get_child() 
        child.set_from_file(filename="icons/alarm_icon.png") 

    def on_settings_btn_pressed(self,widget,event):
        widget.grab_focus()
        child = widget.get_child()
        child.set_from_file(filename="icons/settings_icon_pressed.png")        

    def on_settings_btn_released(self,widget,event):
        self.notebookPages.set_current_page(self.pages['settings']) 
        child = widget.get_child() 
        child.set_from_file(filename="icons/settings_icon.png") 
          
    def on_goHomePage_btn_pressed(self,widget,event):
        widget.grab_focus()
        child = widget.get_child()
        child.set_from_file(filename="icons/go_home_icon_pressed.png")        

    def on_goHomePage_btn_released(self,widget,event):
        self.notebookPages.set_current_page(self.pages['main']) 
        child = widget.get_child() 
        child.set_from_file(filename="icons/go_home_icon.png") 

    def on_manageDxf_btn_pressed(self,widget,event):
        child = widget.get_child()
        child.set_from_file(filename="icons/step_slide_mode_icon_pressed.png")

    def on_manageDxf_btn_released(self,widget,event):
        self.notebookPages.set_current_page(self.pages['dxfExplorer'])
        child = widget.get_child()
        child.set_from_file(filename="icons/step_slide_mode_icon.png")

    def on_switch_page(self,notebook, page, page_num):
        if notebook == self.notebookPages:
            if page_num == self.pages['main']:
                # self.notebookFooter.set_current_page(0)
                self.goHomePageBtn.set_visible(False)
                self.exitBtn.set_visible(True)
                self.log_viewer.set_margin_start(self.goHomePageBtn.get_allocated_width())
                self.log_viewer.set_margin_end(0)
            else:
                # self.notebookFooter.set_current_page(1)
                self.goHomePageBtn.set_visible(True)
                self.exitBtn.set_visible(False)
                self.log_viewer.set_margin_end(self.exitBtn.get_allocated_width())
                self.log_viewer.set_margin_start(0)

    def init_visible_goHomePageBtn_and_exitBtn(self):
        self.goHomePageBtn.set_visible(False)
        self.exitBtn.set_visible(True)

    def on_exit_btn_pressed(self,widget,event):
        child = widget.get_child()
        child.set_from_file(filename="icons/exit_icon_pressed.png")  

    def on_exit_btn_released(self,widget,event):
        try:
            self.hal_component.exit()
        except RuntimeError:
            pass  # HAL component is already closed
        GLib.source_remove(self.update_cmds_timer)
        GLib.source_remove(self.update_gui_timer)
        Gtk.main_quit()

##########################################################################################################################################
#####                                                                                                                                #####
#####       Manual Mode Logic Develop                                                                                                #####
#####                                                                                                                                #####
##########################################################################################################################################

    def on_playManual_btn_pressed(self,widget,event):
        widget.grab_focus()
        child = widget.get_child()
        child.set_from_file(filename="icons/play_icon_pressed.png")   


    def on_playManual_btn_released(self,widget,event): 
        child = widget.get_child() 
        child.set_from_file(filename="icons/play_icon.png")

        if self.manualCuttingProfileWidget.get_numberOfCuts() < 1:
            LogViewer().emit('public-msg', 'warning', 'Warning: Number of Cuts is Zero...')
            return
        
        self.stopManualBtn.set_sensitive(True)
        self.playManualBtn.set_sensitive(False)
        self.angleRightHeadManualBtn.set_sensitive(False)
        self.angleLeftHeadManualBtn.set_sensitive(False)
        self.manualCuttingProfileWidget.set_sensitive(False)
        self.settingsBtn.set_sensitive(False)
        self.alarmsBtn.set_sensitive(False)
        self.ioStatusBtn.set_sensitive(False)
        self.goHomePageBtn.set_sensitive(False)
        self.dxfViewerManual.set_sensitive(False)

        self.hal_pin_bottom_cut_length.set(self.manualCuttingProfileWidget.get_bottomLengthProfile())
        self.hal_pin_top_cut_length.set(self.manualCuttingProfileWidget.get_topLengthProfile())
        self.hal_pin_cut_height.set(self.manualCuttingProfileWidget.get_heightProfile())
        self.hal_pin_cut_left_angle.set(self.manualCuttingProfileWidget.get_leftAngleProfile())
        self.hal_pin_cut_right_angle.set(self.manualCuttingProfileWidget.get_rightAngleProfile())
        self.hal_pin_saw_blade_output_time.set(self.manualCuttingProfileWidget.get_timeOutDisk()*1000)  # convert to ms
        self.hal_pin_number_of_cuts.set(self.manualCuttingProfileWidget.get_numberOfCuts())

        self.start_manual_pulse = [True]

    def on_stopManual_btn_pressed(self,widget,event):
        widget.grab_focus()
        child = widget.get_child()
        child.set_from_file(filename="icons/stop_icon_pressed.png")        

    def on_stopManual_btn_released(self,widget,event): 

        child = widget.get_child() 
        child.set_from_file(filename="icons/stop_icon.png")  

        self.stopManualBtn.set_sensitive(False)
        self.playManualBtn.set_sensitive(True)
        self.angleRightHeadManualBtn.set_sensitive(True)
        self.angleLeftHeadManualBtn.set_sensitive(True)  
        self.manualCuttingProfileWidget.set_sensitive(True) 
        self.settingsBtn.set_sensitive(True)
        self.alarmsBtn.set_sensitive(True)
        self.ioStatusBtn.set_sensitive(True)
        self.goHomePageBtn.set_sensitive(True)
        self.dxfViewerManual.set_sensitive(True)

        self.StopMove()

    def on_angleLeftHeadManual_btn_pressed(self,widget,event):
        widget.grab_focus()
        angleHeadManualState = {'90':0,'45':1,'135':2,'angle':3}
        child = widget.get_child()
        if self.angleLeftHeadManualState == angleHeadManualState['90']:
            child.set_from_file(filename="icons/left_head_angle_90_icon_pressed.png")
        elif self.angleLeftHeadManualState == angleHeadManualState['45']:
            child.set_from_file(filename="icons/left_head_angle_45_icon_pressed.svg")
        elif self.angleLeftHeadManualState == angleHeadManualState['135']:
            child.set_from_file(filename="icons/left_head_angle_135_icon_pressed.svg") 
        elif self.angleLeftHeadManualState == angleHeadManualState['angle']:
            child.set_from_file(filename="icons/left_head_angle_variable_icon_pressed.svg")       

    def on_angleLeftHeadManual_btn_released(self,widget,event): 
        child = widget.get_child() 
        self.manualCuttingProfileWidget.get_leftAngleProfileEntry().set_can_focus(False)
        angleHeadManualState = {'90':0,'45':1,'135':2,'angle':3}
        if self.angleLeftHeadManualState == angleHeadManualState['90']:
            child.set_from_file(filename="icons/left_head_angle_45_icon.svg")
            self.manualCuttingProfileWidget.get_leftAngleProfileEntry().set_text('%.2f'%45)
            self.manualCuttingProfileWidget.emit('update-value', self.manualCuttingProfileWidget.get_leftAngleProfileEntry(), 45)            
            self.angleLeftHeadManualState = angleHeadManualState['45']
        elif self.angleLeftHeadManualState == angleHeadManualState['45']:
            if self.inside_angles == "YES":
                child.set_from_file(filename="icons/left_head_angle_135_icon.svg") 
                self.manualCuttingProfileWidget.get_leftAngleProfileEntry().set_text('%.2f'%135)
                self.manualCuttingProfileWidget.emit('update-value', self.manualCuttingProfileWidget.get_leftAngleProfileEntry(), 135)
                self.angleLeftHeadManualState = angleHeadManualState['135'] 
            else:
                child.set_from_file(filename="icons/left_head_angle_variable_icon.svg") 
                self.manualCuttingProfileWidget.get_leftAngleProfileEntry().set_can_focus(True)
                self.angleLeftHeadManualState = angleHeadManualState['angle']
        elif self.angleLeftHeadManualState == angleHeadManualState['135']:
            child.set_from_file(filename="icons/left_head_angle_variable_icon.svg") 
            self.manualCuttingProfileWidget.get_leftAngleProfileEntry().set_can_focus(True)
            self.angleLeftHeadManualState = angleHeadManualState['angle']
        elif self.angleLeftHeadManualState == angleHeadManualState['angle']:
            child.set_from_file(filename="icons/left_head_angle_90_icon.svg")
            self.manualCuttingProfileWidget.get_leftAngleProfileEntry().set_text('%.2f'%90)
            self.manualCuttingProfileWidget.emit('update-value', self.manualCuttingProfileWidget.get_leftAngleProfileEntry(), 90)
            self.angleLeftHeadManualState = angleHeadManualState['90'] 

    def on_angleRightHeadManual_btn_pressed(self,widget,event):
        widget.grab_focus()
        angleHeadManualState = {'90':0,'45':1,'135':2,'angle':3}
        child = widget.get_child()
        if self.angleRightHeadManualState == angleHeadManualState['90']:
            child.set_from_file(filename="icons/right_head_angle_90_icon_pressed.svg")
        elif self.angleRightHeadManualState == angleHeadManualState['45']:
            child.set_from_file(filename="icons/right_head_angle_45_icon_pressed.svg") 
        elif self.angleRightHeadManualState == angleHeadManualState['135']:
            child.set_from_file(filename="icons/right_head_angle_135_icon_pressed.svg")
        elif self.angleRightHeadManualState == angleHeadManualState['angle']:
            child.set_from_file(filename="icons/right_head_angle_variable_icon_pressed.svg")              

    def on_angleRightHeadManual_btn_released(self,widget,event): 
        child = widget.get_child()
        self.manualCuttingProfileWidget.get_rightAngleProfileEntry().set_can_focus(False) 
        angleHeadManualState = {'90':0,'45':1,'135':2,'angle':3}
        if self.angleRightHeadManualState == angleHeadManualState['90']:
            child.set_from_file(filename="icons/right_head_angle_45_icon.svg")
            self.manualCuttingProfileWidget.get_rightAngleProfileEntry().set_text('%.2f'%45)
            self.manualCuttingProfileWidget.emit('update-value', self.manualCuttingProfileWidget.get_rightAngleProfileEntry(), 45)             
            self.angleRightHeadManualState = angleHeadManualState['45']
        elif self.angleRightHeadManualState == angleHeadManualState['45']:
            if self.inside_angles == "YES":
                child.set_from_file(filename="icons/right_head_angle_135_icon.svg")
                self.manualCuttingProfileWidget.get_rightAngleProfileEntry().set_text('%.2f'%135)
                self.manualCuttingProfileWidget.emit('update-value', self.manualCuttingProfileWidget.get_rightAngleProfileEntry(), 135)
                self.angleRightHeadManualState = angleHeadManualState['135']
            else:
                child.set_from_file(filename="icons/right_head_angle_variable_icon.svg")
                self.manualCuttingProfileWidget.get_rightAngleProfileEntry().set_can_focus(True)
                self.angleRightHeadManualState = angleHeadManualState['angle']
        elif self.angleRightHeadManualState == angleHeadManualState['135']:
            child.set_from_file(filename="icons/right_head_angle_variable_icon.svg") 
            self.manualCuttingProfileWidget.get_rightAngleProfileEntry().set_can_focus(True)
            self.angleRightHeadManualState = angleHeadManualState['angle'] 
        elif self.angleRightHeadManualState == angleHeadManualState['angle']:
            child.set_from_file(filename="icons/right_head_angle_90_icon.svg")
            self.manualCuttingProfileWidget.get_rightAngleProfileEntry().set_text('%.2f'%90)
            self.manualCuttingProfileWidget.emit('update-value', self.manualCuttingProfileWidget.get_rightAngleProfileEntry(), 90)            
            self.angleRightHeadManualState = angleHeadManualState['90']   


    def on_disk_btn_pressed(self,widget,event,state,lastClickTime,hal_pin,side):
        currentClickTime = event.time
        if currentClickTime - lastClickTime[0] > 300:
            widget.grab_focus()
            diskState = {'off':0,'on':1}
            if state[0] == diskState['off']:
                if side == 'left':
                    self.leftDiskManualBtnImage.set_from_file(filename="icons/disk_off_icon_pressed.png")
                    self.leftDiskListBtnImage.set_from_file(filename="icons/disk_off_icon_pressed.png")
                elif side == 'right':
                    self.rightDiskManualBtnImage.set_from_file(filename="icons/disk_off_icon_pressed.png")
                    self.rightDiskListBtnImage.set_from_file(filename="icons/disk_off_icon_pressed.png")
                state[0] = diskState['on']
                hal_pin.set(True)
            elif state[0] == diskState['on']:
                if side == 'left':
                    self.leftDiskManualBtnImage.set_from_file(filename="icons/disk_on_icon_pressed.png")
                    self.leftDiskListBtnImage.set_from_file(filename="icons/disk_on_icon_pressed.png")
                elif side == 'right':
                    self.rightDiskManualBtnImage.set_from_file(filename="icons/disk_on_icon_pressed.png")
                    self.rightDiskListBtnImage.set_from_file(filename="icons/disk_on_icon_pressed.png")
                state[0] = diskState['off']
                hal_pin.set(False)
            lastClickTime[0] = currentClickTime


    def on_disk_btn_released(self,widget,event,state,side):
            diskState = {'off':0,'on':1}
            if state[0] == diskState['off']:
                if side == 'left':
                    self.leftDiskManualBtnImage.set_from_file(filename="icons/disk_off_icon.png")
                    self.leftDiskListBtnImage.set_from_file(filename="icons/disk_off_icon.png")
                elif side == 'right':
                    self.rightDiskManualBtnImage.set_from_file(filename="icons/disk_off_icon.png")
                    self.rightDiskListBtnImage.set_from_file(filename="icons/disk_off_icon.png")
            elif state[0] == diskState['on']:
                if side == 'left':
                    self.leftDiskManualBtnImage.set_from_file(filename="icons/disk_on_icon.png")
                    self.leftDiskListBtnImage.set_from_file(filename="icons/disk_on_icon.png")
                elif side == 'right':
                    self.rightDiskManualBtnImage.set_from_file(filename="icons/disk_on_icon.png")
                    self.rightDiskListBtnImage.set_from_file(filename="icons/disk_on_icon.png")

    def on_bad_value(self, widget, value):
        if value == True:
            self.playManualBtn.set_sensitive(False)
            LogViewer().emit('public-msg', 'warning', 'Warning: Bad Value...')
        else:    
            self.playManualBtn.set_sensitive(True)

##########################################################################################################################################
#####                                                                                                                                #####
#####       Automatic Mode Logic Develop                                                                                             #####
#####                                                                                                                                #####
##########################################################################################################################################
    def on_open_btn_pressed(self, widget, event):

        child = widget.get_child()
        child.set_from_file(filename="icons/open_cut_list_csv_pressed.png")

    def on_open_btn_released(self, widget, event):

        if self.csvViewerWidget.get_treestore() is not None and len(self.csvViewerWidget.get_treestore()) > 0:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, "CSV Viewer Widget")
            dialog.format_secondary_text("Do you want to save the changes to the current CSV file?")
            dialog.get_style_context().add_class("dialog")
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                resp = self.csvViewerWidget.on_save_csv_list()
                if resp == Gtk.ResponseType.CANCEL:
                    return

        child = widget.get_child()
        child.set_from_file(filename="icons/open_cut_list_csv.png")

        fileChooserDialog = Gtk.FileChooserDialog("Por favor elige un archivo", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        fileChooserDialog.get_style_context().add_class("dialog")
        
        response = fileChooserDialog.run()
        if response == Gtk.ResponseType.OK:
            self.csvViewerWidget.get_treestore().clear()
            if self.csvViewerWidget.validate_csv_format(fileChooserDialog.get_filename()):
                LogViewer().emit('public-msg', 'info', 'Info: "The file: ' + fileChooserDialog.get_filename() + 'has the correct CSV format.')
                self.csvViewerWidget.load_csv(fileChooserDialog.get_filename())

        fileChooserDialog.destroy()

    def on_save_btn_pressed(self, widget, event):
        child = widget.get_child()
        child.set_from_file(filename="icons/save_cut_list_csv_pressed.png")

    def on_save_btn_released(self, widget, event):
        child = widget.get_child()
        child.set_from_file(filename="icons/save_cut_list_csv.png")

        self.csvViewerWidget.on_save_csv_list()

    def on_clear_btn_pressed(self, widget, event):
        child = widget.get_child()
        child.set_from_file(filename="icons/clear_cut_list_csv_pressed.png")
    
    def on_clear_btn_released(self, widget, event):
        child = widget.get_child()
        child.set_from_file(filename="icons/clear_cut_list_csv.png")

        self.csvViewerWidget.clear_csv()
        self.barWidget.update_bar([])
        self.dxfViewerAuto.clear_dxf()

    def on_play_btn_pressed(self, widget, event):
        child = widget.get_child()
        child.set_from_file(filename="icons/play_icon_pressed.png")

    def on_play_btn_released(self, widget, event):
        child = widget.get_child()
        child.set_from_file(filename="icons/play_icon.png")

        selected_rows = self.csvViewerWidget.get_selected_child_rows()

        if len(selected_rows) == 0:
            LogViewer().emit('public-msg', 'warning', 'Warning: No row selected...')
            return

        self.openListBtn.set_sensitive(False)
        self.saveListBtn.set_sensitive(False)
        self.clearListBtn.set_sensitive(False)
        self.playListBtn.set_sensitive(False)
        self.stopListBtn.set_sensitive(True)
        self.dxfViewerAuto.set_sensitive(False)
        self.goHomePageBtn.set_sensitive(False)
        self.csvViewerWidget.set_sensitive_btns(False)

        data = ''

        for iter in selected_rows:
            row, path = iter
            pathX = str(path[0]) 
            pathY = str(path[1])
            top_cut_length = self.csvViewerWidget.get_treestore().get_value(row, 8)
            bottom_cut_length = self.csvViewerWidget.get_treestore().get_value(row, 9)
            cut_height = self.csvViewerWidget.get_treestore().get_value(row, 10)
            cut_left_angle = self.csvViewerWidget.get_treestore().get_value(row, 11)
            cut_right_angle = self.csvViewerWidget.get_treestore().get_value(row, 12)
            data += f'{top_cut_length} {bottom_cut_length} {cut_height} {cut_left_angle} {cut_right_angle} {pathX} {pathY}\n'

        process = subprocess.Popen(['halstreamer'], stdin=subprocess.PIPE)
        process.communicate(input=data.encode())

        self.hal_pin_cut_start_auto.set(True)

    def on_stop_btn_pressed(self, widget, event):
        child = widget.get_child()
        child.set_from_file(filename="icons/stop_icon_pressed.png")

    def on_stop_btn_released(self, widget, event):
        child = widget.get_child()
        child.set_from_file(filename="icons/stop_icon.png")

        self.openListBtn.set_sensitive(True)
        self.saveListBtn.set_sensitive(True)
        self.clearListBtn.set_sensitive(True)
        self.playListBtn.set_sensitive(True)
        self.stopListBtn.set_sensitive(False)
        self.dxfViewerAuto.set_sensitive(True)
        self.goHomePageBtn.set_sensitive(True)
        self.csvViewerWidget.set_sensitive_btns(True)

        self.stop_pulse = [True]

    def on_cut_list_path_update_changed(self, hal_pin, data=None):
        if self.hal_pin_cut_list_path_update.get():            
            pathX = self.hal_pin_cut_list_pathX_to_gui.get()
            pathY = self.hal_pin_cut_list_pathY_to_gui.get()
            print(f'Path: {pathX}, {pathY}')
            self.csvViewerWidget.show_current_line_cut(f'{pathX}:{pathY}')
            self.hal_pin_cut_list_path_update.set(False)

##########################################################################################################################################
#####                                                                                                                                #####
#####       Positioning Logic Develop                                                                                             #####
#####                                                                                                                                #####
##########################################################################################################################################

    def on_button_press_event(self, button, event, hal_pin, lastClickTime):
        hal_pin.set(True)

    def on_button_release_event(self, button, event, hal_pin, lastClickTime):
        hal_pin.set(False)

    def pulse_on_hal_pin(self, widget, pulse, count_pulse, delay_counts, hal_pin):

        if pulse[0] == True:
            hal_pin.set(True)
            count_pulse[0] += 1
            if count_pulse[0] == delay_counts[0]:
                hal_pin.set(False)
                count_pulse[0] = 0
                pulse[0] = False

    def on_cut_status_changed(self, hal_pin, data=None):
        status = hal_pin.get()
        self.handle_cut_status(status)
    
    def on_cut_complete_changed(self, hal_pin, data=None):
        if hal_pin.get() == 1:

            # if self.manualCuttingProfileWidget.get_numberOfCuts() > 0: 
            #     self.manualCuttingProfileWidget.set_numberOfCuts(self.manualCuttingProfileWidget.get_numberOfCuts() - 1)
            #     self.hal_pin_number_of_cuts.set(self.manualCuttingProfileWidget.get_numberOfCuts())

            if self.manualCuttingProfileWidget.get_numberOfCuts() - 1 <= 0:
                self.stopManualBtn.get_child().set_from_file(filename="icons/stop_icon.png")
                self.stopManualBtn.set_sensitive(False)
                self.playManualBtn.set_sensitive(True)
                self.angleRightHeadManualBtn.set_sensitive(True)
                self.angleLeftHeadManualBtn.set_sensitive(True)  
                self.manualCuttingProfileWidget.set_sensitive(True) 
                self.settingsBtn.set_sensitive(True)
                self.alarmsBtn.set_sensitive(True)
                self.ioStatusBtn.set_sensitive(True)
                self.goHomePageBtn.set_sensitive(True)
                
                self.StopMove()
                
            hal_pin.set(False)

    def on_number_of_cuts_changed(self, hal_pin, data=None):
        self.manualCuttingProfileWidget.set_numberOfCuts(hal_pin.get())
        
    def StopMove(self):
        # c = linuxcnc.command()
        # c.abort()
        # c.wait_complete()
        self.stop_pulse = [True]

    def handle_cut_status(self, status):
        switcher = {
            0: lambda: LogViewer().emit('public-msg', 'info', 'Info: Ready To Start A Cutting Cycle ...'),
            1: lambda: LogViewer().emit('public-msg', 'info', 'Info: Press Busy Hands Buttons For Move...'),
            2: lambda: LogViewer().emit('public-msg', 'info', 'Info: Position Profile and Close Clamps...'),
            3: lambda: LogViewer().emit('public-msg', 'info', 'Info: Cut Complete...'),
            4: lambda: LogViewer().emit('public-msg', 'info', 'Info: Short Cut...'),
            5: lambda: LogViewer().emit('public-msg', 'info', 'Info: Normal Cut...'),
            6: lambda: LogViewer().emit('public-msg', 'info', 'Info: Long Cut...'),
            7: lambda: LogViewer().emit('public-msg', 'info', 'Info: Press Busy Hands Buttons For Cut...'),
            8: lambda: LogViewer().emit('public-msg', 'info', 'Info: Close Clamps ...'),
            9: lambda: LogViewer().emit('public-msg', 'info', 'Info: Opened Clamps ...'),
            10: lambda: LogViewer().emit('public-msg', 'info', 'Info: Positioning Head Angles...'),
            11: lambda: LogViewer().emit('public-msg', 'info', 'Info: There Are No Pieces To Cut...'),
            12: lambda: LogViewer().emit('public-msg', 'info', 'Info: Turn On Some Saw Blade and Press Busy Hands Buttons For Cut...'),
            13: lambda: LogViewer().emit('public-msg', 'info', 'Info: Cut Only Left Saw Blade...'),
            14: lambda: LogViewer().emit('public-msg', 'info', 'Info: Cut Only Right Saw Blade...'),
            15: lambda: LogViewer().emit('public-msg', 'info', 'Info: Cut Both Saw Blades...'),
            16: lambda: LogViewer().emit('public-msg', 'info', 'Info: Saw Blade Output Time Controlled By Time...'),
            17: lambda: LogViewer().emit('public-msg', 'info', 'Info: Saw Blade Output Time Controlled By User...'),
            18: lambda: LogViewer().emit('public-msg', 'info', 'Info: Turn On Right Saw Blade and Press Busy Hands Buttons For Cut...'),
            19: lambda: LogViewer().emit('public-msg', 'info', 'Info: Turn On Left Saw Blade and Press Busy Hands Buttons For Cut...'),
            20: lambda: LogViewer().emit('public-msg', 'info', 'Info: Cut Only Right Saw Blade For Short Cut...'),
            21: lambda: LogViewer().emit('public-msg', 'info', 'Info: Press Busy Hands Buttons For Move To Recover Length Long Cut...'),
            23: lambda: LogViewer().emit('public-msg', 'info', 'Info: Cut List Cmpleted...'),
        }
        # Obtener la función correspondiente al estado
        func = switcher.get(status, lambda: LogViewer().emit('public-msg', 'info', 'Info: Estado desconocido...'))
        # Llamar a la función
        func()

    def on_update_cmds_timeout(self): 

        self.pulse_on_hal_pin(None, self.start_manual_pulse, self.count_start_manual_pulse, [2], self.hal_pin_cut_start_manual)
        self.pulse_on_hal_pin(None, self.stop_pulse, self.count_stop_pulse, [2], self.hal_pin_stop_move)

        return True
    
    def on_update_gui_timeout(self):

        pos_fb_value = self.hal_pin_pos_fb.get()
        if self.last_FbPos != pos_fb_value:
            self.manualCuttingProfileWidget.set_FbPos(pos_fb_value)
            self.autoFbPosEntry.set_text('%.*f'%(self.autoFbPosEntry.get_num_decimal_digits(),pos_fb_value))
            self.last_FbPos = pos_fb_value

        # e = linuxcnc.error_channel()
        # error = e.poll()

        # if error:
        #     kind, text = error
        #     text = text.replace('\n', '. ')
        #     if kind in (linuxcnc.NML_ERROR, linuxcnc.OPERATOR_ERROR):
        #         typus = "error"
        #     else:
        #         typus = "info"
        #     LogViewer().emit('public-msg', typus, typus+': '+text)

        return True

    def postgui(self):
        postgui_halfile = self.inifile.find("HAL", "POSTGUI_HALFILE")
        return postgui_halfile,sys.argv[2]

     
def main():
    Gdk.threads_init()
    if len(sys.argv) > 2 and sys.argv[1] == '-ini':
        print("2", sys.argv[2])
        win = DoubleMitreMachine(sys.argv[2])
    else:
        win = DoubleMitreMachine()

    postgui_halfile,ini_file = win.postgui()
    print("DoubleMitreMachine postgui filename:",postgui_halfile)

    if postgui_halfile:
        res = os.spawnvp(os.P_WAIT, "halcmd", ["halcmd", "-i",ini_file,"-f", postgui_halfile])
        if res: raise SystemExit(res)    

    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    win.init_visible_goHomePageBtn_and_exitBtn()

    Gtk.main()      

if __name__ == '__main__':
    main()