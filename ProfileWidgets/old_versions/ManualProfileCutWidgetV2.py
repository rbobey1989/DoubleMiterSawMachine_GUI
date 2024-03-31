import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk,Gdk
import cairo,math

class Numpad(Gtk.Window):
    def __init__(self):
        super(Numpad, self).__init__(decorated=False)
        self.set_title("Numpad")
        self.set_size_request(200, 200)        

        char = [('1','2','3'),('4','5','6'),('7','8','9'),('.','0','<--')]
        button = Gtk.Button()

        grid = Gtk.Grid(row_homogeneous=True,column_homogeneous=True)
        for i in range(0, char.__len__()):            
            for j in range(0,char[i].__len__()):
                button = Gtk.Button(label=char[i][j])
                grid.attach(button,j,i,1,1)
                button.connect("clicked", self.numpad_clicked)

        self.add(grid)
        self.show_all()
        self.hide()

    def numpad_clicked(self,button):
        print(button.get_label())


class ManualProfileCutWidget(Gtk.DrawingArea):
    def __init__(
        self, 
        parent,
        height_prof : float = 0.2, 
        height_arrow :  float = 0.7,
        width_arrow :  float = 1.5,
        y_offset :  float = 0.4,
        x_offset :  float = 0.1,
        height_widget :  float = 1, 
        width_height :  float  = 1,
        padding_line :  float = 0.15,
        length_width :  float = 0.25    
        ):
      
        super(ManualProfileCutWidget, self).__init__(can_focus=True) 

        self.par = parent
        self.height_prof   = height_prof  
        self.height_arrow  = height_arrow 
        self.width_arrow   = width_arrow  
        self.y_offset      = y_offset     
        self.x_offset      = x_offset     
        self.padding_line  = padding_line 
        self.length_width  = length_width 

        self.lefTipAngle = 90
        self.rightTipAngle = 90
        self.topLengthProfile = 0
        self.bottomLengthProfile = 0
        self.heightProfile = 70

        self.maxLengthProfile = 6500
        self.minLength = 240
        self.string_length = 7 
        self.current_string_length = self.string_length  

        self.topLengthProfileString = str()
        self.focusTopLengthProfile = False

        self.bottomLengthProfileString = str()
        self.focusBottomLengthProfile = False  

        self.numpad = Numpad() 

        self.connect("draw", self.on_draw)
        self.connect("focus-out-event",self.on_focus_out_event)
        self.connect("focus-in-event",self.on_focus_in_event)        
        self.connect("button-press-event", self.on_button_press)
        self.connect("key-press-event",self.on_key_press)
        self.set_events(self.get_events() |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.KEY_PRESS_MASK)

        self.test_entry = Gtk.Entry(text='test')
        self.test_entry.show_all()
        
    def set_lefTipAngle(self,angle):
        self.lefTipAngle = angle
        if self.focusBottomLengthProfile: 
            self.update_length_profile_string_and_value('top')
            self.update_length_profile_string_and_value('bottom')
        if self.focusTopLengthProfile:
            self.update_length_profile_string_and_value('bottom') 
            self.update_length_profile_string_and_value('top')        
    

    def set_rightTipAngle(self,angle):
        self.rightTipAngle = angle  
        if self.focusBottomLengthProfile: 
            self.update_length_profile_string_and_value('top')
            self.update_length_profile_string_and_value('bottom')
        if self.focusTopLengthProfile:
            self.update_length_profile_string_and_value('bottom') 
            self.update_length_profile_string_and_value('top')                  

    def on_draw(self, widget, event):        

        ctx = self.get_window().cairo_create()
        
        geom = self.get_window().get_geometry()       

        HEIGHT_PROF = geom.height*self.height_prof 
        HEIGHT_ARROW =  HEIGHT_PROF*self.height_arrow
        WIDTH_ARROW = HEIGHT_ARROW/self.width_arrow
        Y_OFFSET = geom.height*self.y_offset
        X_OFFSET = geom.width*self.x_offset
        HEIGHT = geom.height 
        WIDTH = geom.width  
        PADDING_LINE = geom.height*self.padding_line
        LENGTH_WIDTH = geom.width*self.length_width       

        ctx.set_source_rgb(0.3, 0.2, 0.5)
        ctx.set_line_width(2)  
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)       
        
        #Draw Profile
        ctx.move_to(X_OFFSET, Y_OFFSET)
        ctx.line_to(math.tan(math.radians(90-self.lefTipAngle))*HEIGHT_PROF+X_OFFSET,HEIGHT_PROF+Y_OFFSET)
        ctx.line_to(WIDTH-math.tan(math.radians(90-self.rightTipAngle))*HEIGHT_PROF-X_OFFSET,HEIGHT_PROF+Y_OFFSET)
        ctx.line_to(WIDTH-X_OFFSET,Y_OFFSET)
        ctx.close_path()      
        ctx.fill_preserve()
        ctx.set_source_rgb(1.0, 0.2, 0.5)
        ctx.stroke()

        if self.focusTopLengthProfile:
            ctx.move_to(WIDTH/2 - WIDTH_ARROW/4, HEIGHT/2 + HEIGHT_ARROW/2)
            ctx.line_to(WIDTH/2 - WIDTH_ARROW/4, HEIGHT/2)
            ctx.line_to(WIDTH/2 - WIDTH_ARROW/2, HEIGHT/2)
            ctx.line_to(WIDTH/2, HEIGHT/2 - HEIGHT_ARROW/2)
            ctx.line_to(WIDTH/2  + WIDTH_ARROW/2, HEIGHT/2)
            ctx.line_to(WIDTH/2  + WIDTH_ARROW/4, HEIGHT/2)
            ctx.line_to(WIDTH/2  + WIDTH_ARROW/4, HEIGHT/2 + HEIGHT_ARROW/2)
            ctx.set_source_rgb(0.6, 0.3, 0.7)
            ctx.close_path()
            ctx.fill_preserve()
            ctx.set_source_rgb(1.0, 0.2, 0.5)
            ctx.stroke()   

        if self.focusBottomLengthProfile:
            ctx.move_to(WIDTH/2 - WIDTH_ARROW/4, HEIGHT/2 - HEIGHT_ARROW/2)
            ctx.line_to(WIDTH/2 - WIDTH_ARROW/4, HEIGHT/2)
            ctx.line_to(WIDTH/2 - WIDTH_ARROW/2, HEIGHT/2)
            ctx.line_to(WIDTH/2, HEIGHT/2 + HEIGHT_ARROW/2)
            ctx.line_to(WIDTH/2  + WIDTH_ARROW/2, HEIGHT/2)
            ctx.line_to(WIDTH/2  + WIDTH_ARROW/4, HEIGHT/2)
            ctx.line_to(WIDTH/2  + WIDTH_ARROW/4, HEIGHT/2 - HEIGHT_ARROW/2)
            ctx.set_source_rgb(0.6, 0.3, 0.7)
            ctx.close_path()
            ctx.fill_preserve()
            ctx.set_source_rgb(1.0, 0.2, 0.5)
            ctx.stroke()           

        ctx.move_to(WIDTH/2 - LENGTH_WIDTH/2, 0)
        ctx.rectangle(WIDTH/2 - LENGTH_WIDTH/2, 0, LENGTH_WIDTH, 2*PADDING_LINE)

        ctx.set_line_width(2)
        if self.is_focus() == True and self.focusTopLengthProfile == True:
            ctx.set_line_width(4)

        ctx.stroke()  

        ctx.set_line_width(2)
        if self.is_focus() == True and self.focusBottomLengthProfile == True:
            ctx.set_line_width(4)               

        ctx.move_to(WIDTH/2 - LENGTH_WIDTH/2, HEIGHT-2*PADDING_LINE)
        ctx.rectangle(WIDTH/2 - LENGTH_WIDTH/2, HEIGHT-2*PADDING_LINE, LENGTH_WIDTH, 2*PADDING_LINE) 
        
        ctx.stroke()                
               
        ctx.select_font_face("Arial",
                    cairo.FONT_SLANT_NORMAL,
                    cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(60)
        (x, y, w, h, dx, dy) = ctx.text_extents(self.topLengthProfileString)
        ctx.move_to((WIDTH - w)/2, PADDING_LINE+h/2)    
        ctx.show_text(self.topLengthProfileString) 
          
        ctx.select_font_face("Arial",
                    cairo.FONT_SLANT_NORMAL,
                    cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(60)
        (x, y, w, h, dx, dy) = ctx.text_extents(self.bottomLengthProfileString)
        ctx.move_to((WIDTH - w)/2, HEIGHT-PADDING_LINE+h/2)    
        ctx.show_text(self.bottomLengthProfileString)          

        ctx.move_to(X_OFFSET, Y_OFFSET - PADDING_LINE)
        ctx.line_to(X_OFFSET, PADDING_LINE) 
        ctx.line_to(((WIDTH-2*X_OFFSET) - LENGTH_WIDTH)/2 + X_OFFSET, PADDING_LINE) 
        ctx.move_to(WIDTH-X_OFFSET, Y_OFFSET - PADDING_LINE)
        ctx.line_to(WIDTH-X_OFFSET, PADDING_LINE) 
        ctx.line_to(WIDTH- X_OFFSET - ((WIDTH-2*X_OFFSET) - LENGTH_WIDTH)/2, PADDING_LINE)  
        ctx.move_to(math.tan(math.radians(90-self.lefTipAngle))*HEIGHT_PROF+X_OFFSET, HEIGHT_PROF + Y_OFFSET + PADDING_LINE)   
        ctx.line_to(math.tan(math.radians(90-self.lefTipAngle))*HEIGHT_PROF+X_OFFSET, HEIGHT - PADDING_LINE) 
        ctx.line_to(WIDTH/2 - LENGTH_WIDTH/2,HEIGHT - PADDING_LINE)
        ctx.move_to(WIDTH-math.tan(math.radians(90-self.rightTipAngle))*HEIGHT_PROF-X_OFFSET,HEIGHT_PROF + Y_OFFSET + PADDING_LINE)
        ctx.line_to(WIDTH-math.tan(math.radians(90-self.rightTipAngle))*HEIGHT_PROF-X_OFFSET, HEIGHT - PADDING_LINE) 
        ctx.line_to(WIDTH/2 + LENGTH_WIDTH/2,  HEIGHT - PADDING_LINE)

        ctx.set_line_width(2)
        ctx.set_dash([14,6])
        
        ctx.stroke()      

    def format_length_string(self,lengthString):                      
        if lengthString.__len__() != 0:
            if lengthString[-1] == '.':
                lengthString = lengthString[:-1] + '.00'
            if lengthString[-2:-1] == '.':
                lengthString = lengthString + '0'  
            if not(lengthString.__contains__('.')):                   
                lengthString = lengthString + '.00' 
        lengthProfile = float(lengthString)               
        return lengthString, lengthProfile
        
    
    def update_length_profile_string_and_value(self, side):
        if side == 'bottom':
            if self.bottomLengthProfileString:
                self.bottomLengthProfileString,self.bottomLengthProfile = self.format_length_string(self.bottomLengthProfileString)
                if self.bottomLengthProfile < self.minLength:
                    self.bottomLengthProfileString,self.bottomLengthProfile = self.format_length_string(str(self.minLength)) 
                    self.current_string_length = self.bottomLengthProfileString.__len__()                   
                elif self.bottomLengthProfile > self.maxLengthProfile:
                    self.bottomLengthProfileString,self.bottomLengthProfile = self.format_length_string(str(round(self.maxLengthProfile - (math.tan(math.radians(90 - self.lefTipAngle)) + math.tan(math.radians(90 - self.rightTipAngle)))*self.heightProfile,2)))
                    self.current_string_length = self.bottomLengthProfileString.__len__()
                self.topLengthProfile = self.bottomLengthProfile + math.tan(math.radians(90 - self.lefTipAngle))*self.heightProfile + math.tan(math.radians(90 - self.rightTipAngle))*self.heightProfile                
                self.topLengthProfileString = str(round(self.topLengthProfile,2)) 
                if self.topLengthProfileString[self.topLengthProfileString.rfind('.'):].__len__()<=2:
                    self.topLengthProfileString += '0'
        elif side == 'top':
            if self.topLengthProfileString:                
                self.topLengthProfileString,self.topLengthProfile = self.format_length_string(self.topLengthProfileString)
                if self.topLengthProfile < self.minLength + math.tan(math.radians(90 - self.lefTipAngle))*self.heightProfile + math.tan(math.radians(90 - self.rightTipAngle))*self.heightProfile:
                    self.topLengthProfileString,self.topLengthProfile = self.format_length_string(str(round(self.minLength + math.tan(math.radians(90 - self.lefTipAngle))*self.heightProfile + math.tan(math.radians(90 - self.rightTipAngle))*self.heightProfile,2)))
                    self.current_string_length = self.topLengthProfileString.__len__()
                elif self.topLengthProfile > self.maxLengthProfile:
                    self.topLengthProfileString,self.topLengthProfile = self.format_length_string(str(self.maxLengthProfile))
                    self.current_string_length = self.topLengthProfileString.__len__()
                self.bottomLengthProfile = self.topLengthProfile - math.tan(math.radians(90 - self.lefTipAngle))*self.heightProfile - math.tan(math.radians(90 - self.rightTipAngle))*self.heightProfile             
                self.bottomLengthProfileString = str(round(self.bottomLengthProfile,2))
                if self.bottomLengthProfileString[self.bottomLengthProfileString.rfind('.'):].__len__()<=2:
                    self.bottomLengthProfileString += '0'                         

    # def on_state_flags_changed(self,widget, flags): 
    #     print('ahora')
    #     if self.focusBottomLengthProfile: 
    #         self.update_length_profile_string_and_value('top')
    #         self.update_length_profile_string_and_value('bottom')
    #     if self.focusTopLengthProfile:
    #         self.update_length_profile_string_and_value('bottom') 
    #         self.update_length_profile_string_and_value('top')  
    #     self.queue_draw() 

    def on_focus_out_event(self,widget,event):
        print('focus out')
        if self.focusBottomLengthProfile: 
            self.update_length_profile_string_and_value('bottom')
        if self.focusTopLengthProfile:
            self.update_length_profile_string_and_value('top')  
        self.queue_draw()  

    def on_focus_in_event(self,widget,event):
        print('focus in')
        if self.focusBottomLengthProfile: 
            self.update_length_profile_string_and_value('bottom')
        if self.focusTopLengthProfile:
            self.update_length_profile_string_and_value('top')  
        self.queue_draw()         

    def on_button_press(self, w, event):
        """When a button is pressed, the location gets stored and the canvas
        gets updated.
        """
        geom = self.get_window().get_geometry()

        # self.grab_focus()

        # Gtk.Window.translate_coordinates
        X0 = geom.x
        Y0 = geom.y
        HEIGHT = geom.height 
        WIDTH = geom.width 
        PADDING_LINE = geom.height*self.padding_line 
        LENGTH_WIDTH = geom.width*self.length_width  

        if event.get_button()[1] == 1:
            self.focusTopLengthProfile = False
            self.focusBottomLengthProfile = False
            # self.numpad.hide()             
            if event.x >= (WIDTH - LENGTH_WIDTH)/2 and event.x <= (WIDTH + LENGTH_WIDTH)/2:
                if event.y >= 0 and event.y <= 2*PADDING_LINE:
                    self.focusTopLengthProfile = True
                    self.focusBottomLengthProfile = False                     
                    # self.numpad.show()
                    # self.numpad.move(X0+WIDTH/2+LENGTH_WIDTH/2,Y0)
                    self.update_length_profile_string_and_value('bottom')
                elif event.y >= HEIGHT-2*PADDING_LINE and event.y <= WIDTH:
                    self.focusTopLengthProfile = False
                    self.focusBottomLengthProfile = True 
                    # self.numpad.show()
                    # self.numpad.move(X0+WIDTH/2+LENGTH_WIDTH/2,Y0)
                    self.update_length_profile_string_and_value('top')                                                      
            self.queue_draw()
            
           

    def validate_length_profile_string(self,ls,e):
        if e.string == '.':
            if (ls.__len__() > 0 and ls.__len__() <= 4) and not(ls.__contains__('.')):
                if self.focusBottomLengthProfile == True and int(ls) < self.minLength:
                    ls = str(self.minLength)
                if self.focusTopLengthProfile == True and (int(ls) < self.minLength + math.tan(math.radians(90 - self.lefTipAngle))*self.heightProfile + math.tan(math.radians(90 - self.rightTipAngle))*self.heightProfile):
                    ls = str(round(self.minLength + math.tan(math.radians(90 - self.lefTipAngle))*self.heightProfile + math.tan(math.radians(90 - self.rightTipAngle))*self.heightProfile,2))
                    ls = self.format_length_string(ls)[0]
                    self.current_string_length = ls.__len__()
                    return ls
                ls += e.string                
                self.current_string_length = ls.__len__() + 2 
        elif e.string == '\b':
            ls = ls[:-1]
            if not(ls.__contains__('.')):
                self.current_string_length = self.string_length
        else:
            if ls.__len__() < self.current_string_length:
                ls += e.string
            if not(ls.__contains__('.')):                          
                if ls.__len__() >= self.current_string_length - 2:
                    ls = ls[:-1] + '.' + e.string
            if self.focusTopLengthProfile:
                if float(ls) > self.maxLengthProfile:        
                    ls = self.format_length_string(str(self.maxLengthProfile))[0]                                
            elif self.focusBottomLengthProfile:
                if float(ls) > self.maxLengthProfile - (math.tan(math.radians(90 - self.lefTipAngle)) + math.tan(math.radians(90 - self.rightTipAngle)))*self.heightProfile:
                    ls = self.format_length_string(str(round(self.maxLengthProfile - (math.tan(math.radians(90 - self.lefTipAngle)) + math.tan(math.radians(90 - self.rightTipAngle)))*self.heightProfile,2)))[0]
        return ls  
    
    def on_key_press(self, w, event):

        if event.string == '\r':    
            if self.focusBottomLengthProfile: 
                self.update_length_profile_string_and_value('bottom')
            if self.focusTopLengthProfile:
                self.update_length_profile_string_and_value('top')                                          

        if event.string.isnumeric() == True or event.string == '.' or event.string == '\b':
            if self.focusTopLengthProfile == True:                      
                self.topLengthProfileString = self.validate_length_profile_string(self.topLengthProfileString,event)                                          
            elif self.focusBottomLengthProfile == True: 
                self.bottomLengthProfileString = self.validate_length_profile_string(self.bottomLengthProfileString,event)            
            
        self.queue_draw()


class PyApp(Gtk.Window):
    def __init__(self):
        super(PyApp, self).__init__()
        
        self.set_title("ManualProfileCutWidget")
        self.set_size_request(1920, 400)        
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("destroy", Gtk.main_quit)

        self.cur_value = 0

        vbox = Gtk.VBox()
        
        leftscale = Gtk.HScale()
        leftscale.set_range(5, 90)
        leftscale.set_digits(0)
        leftscale.set_size_request(160, 40)
        leftscale.set_value(self.cur_value)
        leftscale.connect("value-changed", self.on_changed_left)

        rightscale = Gtk.HScale()
        rightscale.set_range(5, 90)
        rightscale.set_digits(0)
        rightscale.set_size_request(160, 40)
        rightscale.set_value(self.cur_value)
        rightscale.connect("value-changed", self.on_changed_right)        
                
        leftfix = Gtk.Fixed()
        leftfix.put(leftscale, 50, 50)

        rightfix = Gtk.Fixed()
        rightfix.put(rightscale, 50, 50)
        
        vbox.pack_start(leftfix, False, False, 0) 
        vbox.pack_start(rightfix, False, False, 0)       
        self.manualProfileCutWidget = ManualProfileCutWidget(self)
        vbox.pack_start(self.manualProfileCutWidget, True, True, 0)

        self.add(vbox)
        self.show_all()
        
    def on_changed_left(self, widget):
        self.manualProfileCutWidget.set_lefTipAngle(widget.get_value())

        self.manualProfileCutWidget.queue_draw()

    def on_changed_right(self, widget):

        self.manualProfileCutWidget.set_rightTipAngle(widget.get_value())
        self.manualProfileCutWidget.queue_draw()          

PyApp()
Gtk.main()