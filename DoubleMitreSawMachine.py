#!/usr/bin/env python

import gi
# gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,Gdk,GLib

import os,sys,threading,time

import linuxcnc

from gladevcp.core import Info, Status, Action
import gladevcp.drowidget

import hal
from hal_glib import GStat

from ProfileWidgets.ManualProfileCutWidget import ManualProfileCutWidget
from ActionBtnsWidgets.ActionsBtnsWidgets import myBtnEstoptoggleAction,myBtnOnOfftoggleAction,myBtnHomeAxisAction

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

        self.ini_file = os.environ["INI_FILE_NAME"]
        print(self.ini_file)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('css_styles_sheets/style.css')
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


        self.hal_component = hal.component("DoubleMitreMachine")
        self.update_rate_cmds = 100
        self.update_rate_gui = 100

        self.hal_pin_pos_fb = self.hal_component.newpin("pos-fb", hal.HAL_FLOAT, hal.HAL_IN)

        self.angleRightHeadManualState = 0
        self.angleLeftHeadManualState = 0

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

        vBoxMainStruct = Gtk.VBox(homogeneous=False,vexpand=True)

        hBoxLogoHeader = Gtk.HBox()
        hBoxLogoHeader.pack_start(torneiroLogo,False,False,0)

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
                     'ioState':4,'alarms':5,'settings':6}

        vBoxMainStruct.pack_start(self.notebookPages,False,True,0)

        vBoxFooter = Gtk.VBox()
        self.notebookFooter = Gtk.Notebook(name='footer',show_tabs=False,show_border=False)

        hBoxFooterGoHomePage = Gtk.HBox()        
        hBoxFooterExitPage = Gtk.HBox()

        hBoxFooterGoHomePage.pack_start(self.goHomePageBtn,False,False,0)
        hBoxFooterExitPage.pack_end(self.exitBtn,False,False,0)

        self.notebookFooter.append_page(hBoxFooterExitPage)
        self.notebookFooter.append_page(hBoxFooterGoHomePage)

        vBoxFooter.pack_end(self.notebookFooter,False,False,0)

        vBoxMainStruct.pack_end(vBoxFooter,False,True,0)                          

        #Build Main Page

        self.homeAxisBtn = myBtnHomeAxisAction()

        self.gstatModes = GStat()

        self.manualCuttingBtn = Gtk.EventBox(sensitive=False)
        self.manualCuttingBtn.add(Gtk.Image.new_from_file(filename="icons/manual_mode_icon.png"))                 

        self.autoCuttingBtn = Gtk.EventBox(sensitive=False)
        self.autoCuttingBtn.add(Gtk.Image.new_from_file(filename="icons/auto_mode_icon.png"))         

        self.stepSlideCuttingBtn = Gtk.EventBox(sensitive=False)   
        self.stepSlideCuttingBtn.add(Gtk.Image.new_from_file(filename="icons/step_slide_mode_icon.png"))  

        self.gstatModes.connect('all-homed',  self.set_sensitive_btns_modes)
        self.gstatModes.connect('not-all-homed', self.unset_sensitive_btns_modes)   



        vGridMainBtns = Gtk.Grid(row_homogeneous=True,column_homogeneous=True,vexpand=True,hexpand=True)

        vGridMainBtns.add(self.homeAxisBtn)
        vGridMainBtns.attach(self.manualCuttingBtn,1,0,1,1)
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

        #Build Manual Cutting Page 

        self.manualCuttingProfileWidget = ManualProfileCutWidget(self)  
        self.last_FbPos = 0.0     

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
                    
        vboxManualPage = Gtk.VBox(homogeneous=False) 
        hboxManualCuttingProfileWidget = Gtk.HBox(homogeneous=False)      
        hboxManualCuttingProfileWidget.pack_start(self.manualCuttingProfileWidget,True,True,0)

        hBoxManualCmdBtns = Gtk.HBox(homogeneous=True)
        hBoxManualCmdBtns.pack_start(self.playManualBtn,False,False,0)
        hBoxManualCmdBtns.pack_start(self.angleLeftHeadManualBtn,False,False,0)
        hBoxManualCmdBtns.pack_start(self.angleRightHeadManualBtn,False,False,0)
        hBoxManualCmdBtns.pack_end(self.stopManualBtn,False,False,0)

        vboxManualPage.pack_start(hboxManualCuttingProfileWidget,True,True,0)
        vboxManualPage.pack_end(hBoxManualCmdBtns,False,False,0)

        self.notebookPages.append_page(vboxManualPage)      

        self.playManualBtn.connect('button-press-event',self.on_playManual_btn_pressed)
        self.playManualBtn.connect('button-release-event',self.on_playManual_btn_released)

        self.stopManualBtn.connect('button-press-event',self.on_stopManual_btn_pressed)
        self.stopManualBtn.connect('button-release-event',self.on_stopManual_btn_released)   

        self.angleLeftHeadManualBtn.connect('button-press-event',self.on_angleLeftHeadManual_btn_pressed)
        self.angleLeftHeadManualBtn.connect('button-release-event',self.on_angleLeftHeadManual_btn_released)   

        self.angleRightHeadManualBtn.connect('button-press-event',self.on_angleRightHeadManual_btn_pressed)
        self.angleRightHeadManualBtn.connect('button-release-event',self.on_angleRightHeadManual_btn_released)         

        #Build Auto Cutting Page

        gridAutoPage = Gtk.Grid(row_homogeneous=True,column_homogeneous=True,vexpand=True,hexpand=True)        
        gridAutoPage.add(Gtk.Label(label="Logo"))
        gridAutoPage.attach(Gtk.Label(label="Auto Cutting Page!."),1,1,1,1)
 
        self.notebookPages.append_page(gridAutoPage)

        #Build Slide Cutting Page        

        gridStepSlidePage = Gtk.Grid(row_homogeneous=True,column_homogeneous=True,vexpand=True,hexpand=True)        
        gridStepSlidePage.add(Gtk.Label(label="Logo"))
        gridStepSlidePage.attach(Gtk.Label(label="Step and Slide Cutting Page!."),1,1,1,1)

        self.notebookPages.append_page(gridStepSlidePage)

        #Build Auto Cutting Page

        self.ioStatusPage = Gtk.Box()
        self.ioStatusPage.set_border_width(10)
        self.ioStatusPage.add(Gtk.Label(label="I/O Status Page!."))
        self.notebookPages.append_page(self.ioStatusPage)

        #Build Auto Cutting Page

        self.alarmCodesPage = Gtk.Box()
        self.alarmCodesPage.set_border_width(10)
        self.alarmCodesPage.add(Gtk.Label(label="Alarms Codes Page!."))
        self.notebookPages.append_page(self.alarmCodesPage)         

        #Build Auto Cutting Page

        self.settingsPage = Gtk.Box()
        self.settingsPage.set_border_width(10)
        self.settingsPage.add(Gtk.Label(label="Settings Page!."))
        self.notebookPages.append_page(self.settingsPage) 

        self.update_cmds_timer = GLib.timeout_add(self.update_rate_cmds, self.on_update_cmds_timeout)
        self.update_gui_timer = GLib.timeout_add(self.update_rate_gui, self.on_update_gui_timeout)

        self.add(vBoxMainStruct)

        self.hal_component.ready()

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
        self.manualCuttingBtn.set_sensitive(True)
        self.autoCuttingBtn.set_sensitive(True)
        self.stepSlideCuttingBtn.set_sensitive(True)
        print('set_sensitive_btns_modes')

    def unset_sensitive_btns_modes(self,gstat,str):
        self.manualCuttingBtn.set_sensitive(False)
        self.autoCuttingBtn.set_sensitive(False)
        self.stepSlideCuttingBtn.set_sensitive(False) 
        print('unset_sensitive_btns_modes')

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

    def on_playManual_btn_pressed(self,widget,event):
        widget.grab_focus()
        child = widget.get_child()
        child.set_from_file(filename="icons/play_icon_pressed.png")        

    def on_playManual_btn_released(self,widget,event): 
        child = widget.get_child() 
        child.set_from_file(filename="icons/play_icon.png")
        
        self.stopManualBtn.set_sensitive(True)
        self.playManualBtn.set_sensitive(False)
        self.angleRightHeadManualBtn.set_sensitive(False)
        self.angleLeftHeadManualBtn.set_sensitive(False)
        self.manualCuttingProfileWidget.set_sensitive(False)
        self.settingsBtn.set_sensitive(False)
        self.alarmsBtn.set_sensitive(False)
        self.ioStatusBtn.set_sensitive(False)
        # self.goHomePageBtn.set_sensitive(False)
        
        self.G0_X(self.manualCuttingProfileWidget.get_bottomLengthProfile())

    def G0_X(self, x):
        c = linuxcnc.command()  # Create a new instance of linuxcnc.command
        fail, self.manualPremode = ACTION.ensure_mode(linuxcnc.MODE_MDI)
        command = "G0 X%.2f" % x
        c.mdi('%s' % command)

    def StopMove(self):
        c = linuxcnc.command()
        c.abort()
        c.wait_complete() 

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
        # self.goHomePageBtn.set_sensitive(True)

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
            child.set_from_file(filename="icons/left_head_angle_135_icon.svg") 
            self.manualCuttingProfileWidget.get_leftAngleProfileEntry().set_text('%.2f'%135)
            self.manualCuttingProfileWidget.emit('update-value', self.manualCuttingProfileWidget.get_leftAngleProfileEntry(), 135)
            self.angleLeftHeadManualState = angleHeadManualState['135'] 
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
            child.set_from_file(filename="icons/right_head_angle_135_icon.svg")
            self.manualCuttingProfileWidget.get_rightAngleProfileEntry().set_text('%.2f'%135)
            self.manualCuttingProfileWidget.emit('update-value', self.manualCuttingProfileWidget.get_rightAngleProfileEntry(), 135)
            self.angleRightHeadManualState = angleHeadManualState['135']
        elif self.angleRightHeadManualState == angleHeadManualState['135']:
            child.set_from_file(filename="icons/right_head_angle_variable_icon.svg") 
            self.manualCuttingProfileWidget.get_rightAngleProfileEntry().set_can_focus(True)
            self.angleRightHeadManualState = angleHeadManualState['angle'] 
        elif self.angleRightHeadManualState == angleHeadManualState['angle']:
            child.set_from_file(filename="icons/right_head_angle_90_icon.svg")
            self.manualCuttingProfileWidget.get_rightAngleProfileEntry().set_text('%.2f'%90)
            self.manualCuttingProfileWidget.emit('update-value', self.manualCuttingProfileWidget.get_rightAngleProfileEntry(), 90)            
            self.angleRightHeadManualState = angleHeadManualState['90']   

    def on_update_cmds_timeout(self):

        # s = linuxcnc.stat()
        # s.poll()
        # in_position_flag = s.inpos  

        # if in_position_flag:
        #     print("In position")
        # else:
        #     print("Not in position")      

        return True
    
    def on_update_gui_timeout(self):

        s = linuxcnc.stat()
        s.poll()
        pos_fb_value = s.actual_position[0]
        if self.last_FbPos != pos_fb_value:
            self.manualCuttingProfileWidget.set_FbPos(pos_fb_value)
            self.last_FbPos = pos_fb_value

        return True

    def on_switch_page(self,notebook, page, page_num):
        if notebook == self.notebookPages:
            if page_num == self.pages['main']:
                self.notebookFooter.set_current_page(0)
            else:
                self.notebookFooter.set_current_page(1)

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

    def postgui(self):
        inifile = linuxcnc.ini(self.ini_file)
        postgui_halfile = inifile.find("HAL", "POSTGUI_HALFILE")
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

    Gtk.main()      

if __name__ == '__main__':
    main()