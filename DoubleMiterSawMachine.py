import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,Gdk

from ProfileWidgets.ManualProfileCutWidget import ManualProfileCutWidget


windowHeight = 1080
windowWidth = 1920
buttonsWidth = 150
buttonsHeight = 150
torneiroLogoWidth = 300
torneiroLogoHeight = 150

class MyWindow(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_default_size(windowWidth,windowHeight)
        # self.set_decorated(False)
        # self.fullscreen()
        self.set_border_width(0)


        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('css_styles_sheets/style.css')
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

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

        hBoxBtnsHeader = Gtk.HBox(spacing=50,homogeneous=True)

        hBoxBtnsHeader.pack_start(self.settingsBtn,False,False,0)
        hBoxBtnsHeader.pack_start(self.alarmsBtn,False,False,0)
        hBoxBtnsHeader.pack_start(self.ioStatusBtn,False,False,0)   

        hBoxHeader = Gtk.HBox(homogeneous=False,name='header')
        hBoxHeader.pack_start(hBoxLogoHeader,False,False,0)
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

        self.manualCuttingBtn = Gtk.EventBox()
        self.manualCuttingBtn.add(Gtk.Image.new_from_file(filename="icons/manual_mode_icon.png"))                 

        self.autoCuttingBtn = Gtk.EventBox()
        self.autoCuttingBtn.add(Gtk.Image.new_from_file(filename="icons/auto_mode_icon.png"))         

        self.stepSlideCuttingBtn = Gtk.EventBox()   
        self.stepSlideCuttingBtn.add(Gtk.Image.new_from_file(filename="icons/step_slide_mode_icon.png"))              

        hBoxMainBtns = Gtk.HBox(homogeneous=True)

        hBoxMainBtns.pack_start(self.manualCuttingBtn,False,False,0)
        hBoxMainBtns.pack_start(self.autoCuttingBtn,False,False,0)
        hBoxMainBtns.pack_start(self.stepSlideCuttingBtn,False,False,0)

        self.notebookPages.append_page(hBoxMainBtns)

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

        self.playManualBtn = Gtk.EventBox(can_focus=True)
        self.playManualBtn.add(Gtk.Image.new_from_file(filename="icons/play_icon.png"))  

        self.stopManualBtn = Gtk.EventBox(can_focus=True)
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

        self.add(vBoxMainStruct)


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

    def on_stopManual_btn_pressed(self,widget,event):
        widget.grab_focus()
        child = widget.get_child()
        child.set_from_file(filename="icons/stop_icon_pressed.png")        

    def on_stopManual_btn_released(self,widget,event): 
        child = widget.get_child() 
        child.set_from_file(filename="icons/stop_icon.png")        

    def on_angleLeftHeadManual_btn_pressed(self,widget,event):
        widget.grab_focus()
        angleHeadManualState = {'90':0,'45':1,'angle':2}
        child = widget.get_child()
        if self.angleLeftHeadManualState == angleHeadManualState['90']:
            child.set_from_file(filename="icons/left_head_angle_90_icon_pressed.png")
        elif self.angleLeftHeadManualState == angleHeadManualState['45']:
            child.set_from_file(filename="icons/left_head_angle_45_icon_pressed.svg") 
        elif self.angleLeftHeadManualState == angleHeadManualState['angle']:
            child.set_from_file(filename="icons/left_head_angle_variable_icon_pressed.svg")       

    def on_angleLeftHeadManual_btn_released(self,widget,event): 
        child = widget.get_child() 
        self.manualCuttingProfileWidget.get_leftAngleProfileEntry().set_can_focus(False)
        angleHeadManualState = {'90':0,'45':1,'angle':2}
        if self.angleLeftHeadManualState == angleHeadManualState['90']:
            child.set_from_file(filename="icons/left_head_angle_45_icon.svg")
            self.manualCuttingProfileWidget.get_leftAngleProfileEntry().set_text('%.2f'%45)
            self.manualCuttingProfileWidget.emit('update-value', self.manualCuttingProfileWidget.get_leftAngleProfileEntry(), 45)            
            self.angleLeftHeadManualState = angleHeadManualState['45']
        elif self.angleLeftHeadManualState == angleHeadManualState['45']:
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
        angleHeadManualState = {'90':0,'45':1,'angle':2}
        child = widget.get_child()
        if self.angleRightHeadManualState == angleHeadManualState['90']:
            child.set_from_file(filename="icons/right_head_angle_90_icon_pressed.svg")
        elif self.angleRightHeadManualState == angleHeadManualState['45']:
            child.set_from_file(filename="icons/right_head_angle_45_icon_pressed.svg") 
        elif self.angleRightHeadManualState == angleHeadManualState['angle']:
            child.set_from_file(filename="icons/right_head_angle_variable_icon_pressed.svg")              

    def on_angleRightHeadManual_btn_released(self,widget,event): 
        child = widget.get_child()
        self.manualCuttingProfileWidget.get_rightAngleProfileEntry().set_can_focus(False) 
        angleHeadManualState = {'90':0,'45':1,'angle':2}
        if self.angleRightHeadManualState == angleHeadManualState['90']:
            child.set_from_file(filename="icons/right_head_angle_45_icon.svg")
            self.manualCuttingProfileWidget.get_rightAngleProfileEntry().set_text('%.2f'%45)
            self.manualCuttingProfileWidget.emit('update-value', self.manualCuttingProfileWidget.get_rightAngleProfileEntry(), 45)             
            self.angleRightHeadManualState = angleHeadManualState['45']
        elif self.angleRightHeadManualState == angleHeadManualState['45']:
            child.set_from_file(filename="icons/right_head_angle_variable_icon.svg") 
            self.manualCuttingProfileWidget.get_rightAngleProfileEntry().set_can_focus(True)
            self.angleRightHeadManualState = angleHeadManualState['angle'] 
        elif self.angleRightHeadManualState == angleHeadManualState['angle']:
            child.set_from_file(filename="icons/right_head_angle_90_icon.svg")
            self.manualCuttingProfileWidget.get_rightAngleProfileEntry().set_text('%.2f'%90)
            self.manualCuttingProfileWidget.emit('update-value', self.manualCuttingProfileWidget.get_rightAngleProfileEntry(), 90)            
            self.angleRightHeadManualState = angleHeadManualState['90']


    def on_switch_page(self,notebook, page, page_num):
        if notebook == self.notebookPages:
            if page_num != self.pages['main']:
                self.notebookFooter.set_current_page(1)
            else:
                self.notebookFooter.set_current_page(0)

    def on_exit_btn_pressed(self,widget,event):
        child = widget.get_child()
        child.set_from_file(filename="icons/exit_icon_pressed.png")  

    def on_exit_btn_released(self,widget,event):
        Gtk.main_quit()        

win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()

Gtk.main()