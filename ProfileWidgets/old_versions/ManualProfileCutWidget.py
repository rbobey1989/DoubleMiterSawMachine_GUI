import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk,Gdk
import cairo,math

class ManualProfileCutWidget(Gtk.DrawingArea):
    def __init__(self, parent):
      
        self.par = parent
        super(ManualProfileCutWidget, self).__init__(can_focus=True) 

        self.lefTipAngle = 90
        self.rightTipAngle = 90
        self.topLengthProfile = 0
        self.bottomLengthProfile = 0
        self.heightProfile = 70

        self.maxLength = 4000
        self.minLength = 240
        self.string_length = 6  

        self.topLengthProfileString = str()
        self.focusTopLengthProfile = False

        self.bottomLengthProfileString = str()
        self.focusBottomLengthProfile = False       

        self.connect("draw", self.on_draw)
        self.connect("state-flags-changed",self.on_state_flags_changed)
        self.connect("button-press-event", self.on_button_press)
        self.connect("key-press-event",self.on_key_press)
        self.set_events(self.get_events() |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.KEY_PRESS_MASK)
        
    def set_lefTipAngle(self,angle):
        self.lefTipAngle = angle 
        self.update_length_profile_string_and_value('top')
        # self.update_length_profile_string_and_value('bottom')         
    

    def set_rightTipAngle(self,angle):
        self.rightTipAngle = angle  
        self.update_length_profile_string_and_value('top')
        # self.update_length_profile_string_and_value('bottom')                 

    def on_draw(self, widget, event):        

        ctx = self.get_window().cairo_create()
        
        geom = self.get_window().get_geometry()       

        HEIGHT_PROF = geom.height*0.2  
        Y_OFFSET = geom.height*0.4 
        X_OFFSET = geom.width*0.1 
        HEIGHT = geom.height 
        WIDTH = geom.width  
        PADDING_LINE = geom.height*0.15 
        LENGTH_WIDTH = geom.width*0.25       

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
                self.topLengthProfile = self.bottomLengthProfile + math.tan(math.radians(90 - self.lefTipAngle))*self.heightProfile + math.tan(math.radians(90 - self.rightTipAngle))*self.heightProfile                
                self.topLengthProfileString = str(round(self.topLengthProfile,2)) 
                if self.topLengthProfileString[self.topLengthProfileString.rfind('.'):].__len__()<=2:
                    self.topLengthProfileString += '0'
        elif side == 'top':
            if self.topLengthProfileString:                
                self.topLengthProfileString,self.topLengthProfile = self.format_length_string(self.topLengthProfileString) 
                self.bottomLengthProfile = self.topLengthProfile - math.tan(math.radians(90 - self.lefTipAngle))*self.heightProfile - math.tan(math.radians(90 - self.rightTipAngle))*self.heightProfile             
                self.bottomLengthProfileString = str(round(self.bottomLengthProfile,2))
                if self.bottomLengthProfileString[self.bottomLengthProfileString.rfind('.'):].__len__()<=2:
                    self.bottomLengthProfileString += '0'                         

    def on_state_flags_changed(self,widget, flags): 
        self.update_length_profile_string_and_value('top')
        self.update_length_profile_string_and_value('bottom')
        self.queue_draw()                              

    def on_button_press(self, w, event):
        """When a button is pressed, the location gets stored and the canvas
        gets updated.
        """
        geom = self.get_window().get_geometry()

        self.grab_focus()

        HEIGHT = geom.height 
        WIDTH = geom.width  
        PADDING_LINE = geom.height*0.15 
        LENGTH_WIDTH = geom.width*0.25  
        if event.get_button()[1] == 1:
            if event.x >= (WIDTH - LENGTH_WIDTH)/2 and event.x <= (WIDTH + LENGTH_WIDTH)/2:
                if event.y >= 0 and event.y <= 2*PADDING_LINE:
                    self.focusTopLengthProfile = True
                    self.focusBottomLengthProfile = False 
                    self.update_length_profile_string_and_value('bottom')
                elif event.y >= HEIGHT-2*PADDING_LINE and event.y <= WIDTH:
                    self.focusTopLengthProfile = False
                    self.focusBottomLengthProfile = True 
                    self.update_length_profile_string_and_value('top')                                       
                self.queue_draw()  

    def validate_length_profile_string(self,ls,e):
        if e.string == '.':
            if ls.__contains__('.') or ls.__len__() == 0:
                return ls
            if ls.__len__() <= 3:
                self.string_length = ls.__len__()+2                                        
        elif not(ls.__contains__('.')) and ls.__len__() > 3 and not(e.string == '\b') and int(ls) != self.maxLength:
            ls += '.'
        elif e.string == '0' and ls.__len__() == 0:
            return ls

        if e.string == '\b':
            ls = ls[:-1]
            if not(ls.__contains__('.')):
                self.string_length = 6
        elif ls.__len__() <= self.string_length:
            if ls.__len__() >= 2 and not(ls.__contains__('.')) and not(e.string == '.'): 
                if int(ls[0:3] + e.string) == self.maxLength :
                    self.string_length = ls.__len__()
                    ls = ls[0:3] + e.string                                        
                    return ls                
                elif int(ls[0:3] + e.string) > self.maxLength :
                    self.string_length = ls.__len__()+2
                    ls += '.'                    
                    return ls

            if ls.rfind('.') != -1:
                if ls[ls.rfind('.')+1:].__len__() >= 2: 
                    return ls
            ls += e.string 

        return ls                              

    def on_key_press(self, w, event):

        if event.string == '\r':    
            self.update_length_profile_string_and_value('top')
            self.update_length_profile_string_and_value('bottom')                                         

        if event.string.isnumeric() == True or event.string == '.' or event.string == '\b':
            if self.focusTopLengthProfile == True:                      
                self.topLengthProfileString = self.validate_length_profile_string(self.topLengthProfileString,event)                                          
            elif self.focusBottomLengthProfile == True: 
                self.bottomLengthProfileString = self.validate_length_profile_string(self.bottomLengthProfileString,event)            
            
        self.queue_draw()


class PyApp(Gtk.Window): 

    def __init__(self):
        super(PyApp, self).__init__(can_focus=False)
        
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



        

        
        

        