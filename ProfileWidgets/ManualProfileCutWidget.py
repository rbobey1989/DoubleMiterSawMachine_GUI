import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk, GObject
import cairo,math

from .EntryWithNumpad import EntryNumpad,BubbleNumpad

class ManualProfileCutWidget(Gtk.Overlay):
    __gsignals__ = {
        'update-value': (GObject.SignalFlags.RUN_FIRST, None, (float,EntryNumpad))
    }
    def __init__(
        self, 
        parent,
        height_prof : float = 0.2, 
        height_arrow :  float = 0.7,
        width_arrow :  float = 1.5,
        y_offset :  float = 0.4,
        x_offset :  float = 0.2,
        padding_line :  float = 0.15,
        length_width :  float = 0.25,
        height_bubble_numpad : float = 0.50, 
        width_bubble_numpad : float = 0.175,
        min_length : float = 240.00,
        max_length : float = 6500.00,            
        min_angle: float = 22.5,
        max_angle: float = 157.5    
        ):
        super(ManualProfileCutWidget, self).__init__(can_focus=True, focus_on_click=True) 

        self.par = parent
        self.height_prof   = height_prof  
        self.height_arrow  = height_arrow 
        self.width_arrow   = width_arrow  
        self.y_offset      = y_offset     
        self.x_offset      = x_offset     
        self.padding_line  = padding_line 
        self.length_width  = length_width  
        self.height_bubble_numpad = height_bubble_numpad 
        self.width_bubble_numpad  = width_bubble_numpad   
        self.min_length = min_length
        self.max_length = max_length 
        self.min_angle = min_angle
        self.max_angle = max_angle

        self.lefTipAngle = 90
        self.rightTipAngle = 90
        self.topLengthProfile = 0
        self.bottomLengthProfile = 0
        self.heightProfile = 70

        self.topLengthProfileString = str()
        self.focusTopLengthProfile = False

        self.bottomLengthProfileString = str()
        self.focusBottomLengthProfile = False 

        screen = Gdk.Screen.get_default()
        self.provider = Gtk.CssProvider()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, self.provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )       
        

        drawingArea = Gtk.DrawingArea(can_focus=True,focus_on_click=True)
        drawingArea.set_name('manualCutProfileWidgetAnimation')

        drawingArea.set_events(
            drawingArea.get_events()   |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.KEY_PRESS_MASK
            )

        drawingArea.connect("draw", self.on_draw)
        drawingArea.connect("focus-out-event",self.on_focus_out_event)
        drawingArea.connect("focus-in-event",self.on_focus_in_event)        
        drawingArea.connect("button-press-event", self.on_button_press)
        drawingArea.connect("key-press-event",self.on_key_press)

        self.add_overlay(drawingArea) 
        self.connect('get-child-position',self.on_get_child_position) 
        self.connect('update-value', self.on_update_value)       
        

        self.topLengthProfileEntry = EntryNumpad(self,
                                                 label='entryTopLengths',
                                                 h_align_bubbleNumpad=Gtk.ArrowType.LEFT,
                                                 v_align_bubbleNumpad=Gtk.ArrowType.DOWN,
                                                 num_int_digits=4,
                                                 num_decimal_digits=2                                                 
                                                 )
        self.topLengthProfileEntry.set_name('entryWithNumpadManualWidget')
        self.topLengthProfileEntry.set_max_length(7)
        self.topLengthProfileEntry.set_alignment(xalign=0.5)
        self.topLengthProfileEntry.set_halign(Gtk.Align.CENTER)
        self.topLengthProfileEntry.set_valign(Gtk.Align.START)
        self.add_overlay(self.topLengthProfileEntry)

        self.leftAngleProfileEntry = EntryNumpad(self,
                                                 label= 'entryLeftAngle',
                                                 h_align_bubbleNumpad=Gtk.ArrowType.RIGHT,
                                                 v_align_bubbleNumpad=Gtk.ArrowType.DOWN,
                                                 num_int_digits=3,
                                                 num_decimal_digits=2                                                                                     
                                                 )
        self.leftAngleProfileEntry.set_name('entryWithNumpadManualWidget')
        self.leftAngleProfileEntry.set_max_length(7)
        self.leftAngleProfileEntry.set_alignment(xalign=0.5)
        self.leftAngleProfileEntry.set_halign(Gtk.Align.START)
        self.leftAngleProfileEntry.set_valign(Gtk.Align.CENTER)
        self.add_overlay(self.leftAngleProfileEntry)
     
        self.bottomLengthProfileEntry = EntryNumpad(self,
                                                    label='entryBottomLength',
                                                    h_align_bubbleNumpad=Gtk.ArrowType.RIGHT,
                                                    v_align_bubbleNumpad=Gtk.ArrowType.UP,
                                                    num_int_digits=4,
                                                    num_decimal_digits=2)                                               
        self.bottomLengthProfileEntry.set_name('entryWithNumpadManualWidget')
        self.bottomLengthProfileEntry.set_max_length(7)
        self.bottomLengthProfileEntry.set_alignment(xalign=0.5)
        self.bottomLengthProfileEntry.set_halign(Gtk.Align.CENTER)
        self.bottomLengthProfileEntry.set_valign(Gtk.Align.END)
        self.add_overlay(self.bottomLengthProfileEntry)   
     
        self.rightAngleProfileEntry = EntryNumpad(self,
                                                  label='entryRightAngle',
                                                  h_align_bubbleNumpad=Gtk.ArrowType.LEFT,
                                                  v_align_bubbleNumpad=Gtk.ArrowType.DOWN,
                                                  num_int_digits=3,
                                                  num_decimal_digits=2                                                  
                                                  )                                               
        self.rightAngleProfileEntry.set_name('entryWithNumpadManualWidget')
        self.rightAngleProfileEntry.set_max_length(7)
        self.rightAngleProfileEntry.set_alignment(xalign=0.5)
        self.rightAngleProfileEntry.set_halign(Gtk.Align.END)
        self.rightAngleProfileEntry.set_valign(Gtk.Align.CENTER)
        self.add_overlay(self.rightAngleProfileEntry)       
        
    def set_lefTipAngle(self,angle):
        self.lefTipAngle = angle        

    def set_rightTipAngle(self,angle):
        self.rightTipAngle = angle  

    def set_topLengthProfile(self,length):
        self.topLengthProfile = length        

    def set_bottomLengthProfile(self,length):
        self.bottomLengthProfile = length   

    def on_draw(self, widget, ctx):        

        height = widget.get_allocated_height()
        width = widget.get_allocated_width()

        HEIGHT_PROF = height*self.height_prof 
        HEIGHT_ARROW =  HEIGHT_PROF*self.height_arrow
        WIDTH_ARROW = HEIGHT_ARROW/self.width_arrow
        Y_OFFSET = height*self.y_offset
        X_OFFSET = width*self.x_offset
        HEIGHT = height 
        WIDTH = width  
        PADDING_LINE = height*self.padding_line
        LENGTH_WIDTH = width*self.length_width  

        css = str("""
        #entryWithNumpadManualWidget {
            font-size: """+ str(int(PADDING_LINE*0.8)) +"""px;
            box-shadow: 5px 5px 5px 5px rgba(0, 0, 0, 0.5);
            border-radius: 5px;
        }
        """).encode()
        self.provider.load_from_data(css) 

        
        self.topLengthProfileEntry.set_size_request(width=LENGTH_WIDTH,height=int(PADDING_LINE)) 
        self.topLengthProfileEntry.set_margin_top(PADDING_LINE-self.topLengthProfileEntry.get_allocated_height()/2)

        self.leftAngleProfileEntry.set_size_request(width=LENGTH_WIDTH/2,height=int(PADDING_LINE)) 
        self.leftAngleProfileEntry.set_margin_left(PADDING_LINE/2)

        self.bottomLengthProfileEntry.set_size_request(width=LENGTH_WIDTH,height=int(PADDING_LINE))
        self.bottomLengthProfileEntry.set_margin_bottom(PADDING_LINE-self.bottomLengthProfileEntry.get_allocated_height()/2)        

        self.rightAngleProfileEntry.set_size_request(width=LENGTH_WIDTH/2,height=int(PADDING_LINE)) 
        self.rightAngleProfileEntry.set_margin_right(PADDING_LINE/2)


        ctx.set_source_rgb(0.99, 0.64, 0.07)
        ctx.set_line_width(10)  
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)   

        #Draw Profile
        if self.lefTipAngle <= 90 and self.rightTipAngle <= 90:
            ctx.move_to(X_OFFSET, Y_OFFSET)
            ctx.line_to(math.tan(math.radians(90-self.lefTipAngle))*HEIGHT_PROF+X_OFFSET,HEIGHT_PROF+Y_OFFSET)
            ctx.line_to(WIDTH-math.tan(math.radians(90-self.rightTipAngle))*HEIGHT_PROF-X_OFFSET,HEIGHT_PROF+Y_OFFSET)
            ctx.line_to(WIDTH-X_OFFSET,Y_OFFSET)
        elif self.lefTipAngle > 90 and self.rightTipAngle > 90:
            ctx.move_to(math.tan(math.radians(90+self.lefTipAngle))*HEIGHT_PROF+X_OFFSET, Y_OFFSET)
            ctx.line_to(X_OFFSET,Y_OFFSET+HEIGHT_PROF)
            ctx.line_to(WIDTH-X_OFFSET,Y_OFFSET+HEIGHT_PROF)
            ctx.line_to(WIDTH-math.tan(math.radians(90+self.rightTipAngle))*HEIGHT_PROF-X_OFFSET,Y_OFFSET)
        elif self.lefTipAngle <= 90 and self.rightTipAngle > 90:
            ctx.move_to(X_OFFSET, Y_OFFSET)
            ctx.line_to(math.tan(math.radians(90-self.lefTipAngle))*HEIGHT_PROF+X_OFFSET,HEIGHT_PROF+Y_OFFSET)
            ctx.line_to(WIDTH-X_OFFSET,Y_OFFSET+HEIGHT_PROF)
            ctx.line_to(WIDTH-math.tan(math.radians(90+self.rightTipAngle))*HEIGHT_PROF-X_OFFSET,Y_OFFSET)
        elif self.lefTipAngle > 90 and self.rightTipAngle <= 90:
            ctx.move_to(math.tan(math.radians(90+self.lefTipAngle))*HEIGHT_PROF+X_OFFSET, Y_OFFSET)
            ctx.line_to(X_OFFSET,Y_OFFSET+HEIGHT_PROF)
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

    def on_focus_out_event(self,widget,event):
        pass

    def on_focus_in_event(self,widget,event):
        pass        

    def on_button_press(self, widget, event):
        """When a button is pressed, the location gets stored and the canvas
        gets updated.
        """

        height = widget.get_allocated_height()
        width = widget.get_allocated_width()

        widget.grab_focus()

        # Gtk.Window.translate_coordinates
        # X0 = geom.x
        # Y0 = geom.y
        HEIGHT = height 
        WIDTH = width 
        PADDING_LINE = height*self.padding_line 
        LENGTH_WIDTH = width*self.length_width  

        if event.get_button()[1] == 1:
            self.focusTopLengthProfile = False
            self.focusBottomLengthProfile = False          
            if event.x >= (WIDTH - LENGTH_WIDTH)/2 and event.x <= (WIDTH + LENGTH_WIDTH)/2:
                if event.y >= 0 and event.y <= 2*PADDING_LINE:
                    self.focusTopLengthProfile = True
                    self.focusBottomLengthProfile = False                     
                elif event.y >= HEIGHT-2*PADDING_LINE and event.y <= WIDTH:
                    self.focusTopLengthProfile = False
                    self.focusBottomLengthProfile = True                                                      
            self.queue_draw()
            
    
    def on_key_press(self, w, event):
        pass

    def on_get_child_position(self, overlay, widget, allocation):
        
        width = overlay.get_allocated_width()
        height = overlay.get_allocated_height()

        HEIGHT = height 
        WIDTH = width 
        HEIGHT_BUBBLE_NUMPAD = height*self.height_bubble_numpad 
        WIDTH_BUBBLE_NUMPAD = width*self.width_bubble_numpad
        PADDING_LINE = height*self.padding_line
        LENGTH_WIDTH = width*self.length_width  

        if isinstance(widget, BubbleNumpad):  


            if widget.get_parent().get_halign() == Gtk.Align.START:
                if widget.get_h_align() == Gtk.ArrowType.RIGHT:
                    allocation.x = PADDING_LINE/2 + LENGTH_WIDTH/2                
            elif widget.get_parent().get_halign() == Gtk.Align.CENTER:
                if widget.get_h_align() == Gtk.ArrowType.RIGHT:
                    allocation.x = WIDTH/2 + LENGTH_WIDTH/2
                elif widget.get_h_align() == Gtk.ArrowType.LEFT:
                    allocation.x = WIDTH/2 - LENGTH_WIDTH/2 - WIDTH_BUBBLE_NUMPAD 
            elif widget.get_parent().get_halign() == Gtk.Align.END:
                if widget.get_h_align() == Gtk.ArrowType.LEFT:
                    allocation.x = WIDTH - PADDING_LINE/2 - LENGTH_WIDTH/2 - WIDTH_BUBBLE_NUMPAD           

            if widget.get_parent().get_valign() == Gtk.Align.START:
                if widget.get_v_align() == Gtk.ArrowType.DOWN:
                    allocation.y = PADDING_LINE
            elif widget.get_parent().get_valign() == Gtk.Align.CENTER:
                if widget.get_v_align() == Gtk.ArrowType.UP:
                    allocation.y = HEIGHT/2 - HEIGHT_BUBBLE_NUMPAD
                if widget.get_v_align() == Gtk.ArrowType.DOWN:
                    allocation.y = HEIGHT/2
            elif widget.get_parent().get_valign() == Gtk.Align.END:
                if widget.get_v_align() == Gtk.ArrowType.UP:
                    allocation.y = HEIGHT - PADDING_LINE - HEIGHT_BUBBLE_NUMPAD

            allocation.width = WIDTH_BUBBLE_NUMPAD
            allocation.height = HEIGHT_BUBBLE_NUMPAD 
            return True
        else:
            return False
        
    def on_update_value(self,widget,value,entry):
        if entry == self.leftAngleProfileEntry or entry == self.rightAngleProfileEntry:
            set_tipAngle = lambda x,y: self.set_lefTipAngle(y) if x == self.leftAngleProfileEntry else self.set_rightTipAngle(y) 
            if value > self.max_angle: 
                set_tipAngle(entry,self.max_angle)
                entry.set_text(str(round(self.max_angle,2)))
            elif value < self.min_angle:
                set_tipAngle(entry,self.min_angle)                
                entry.set_text(str(round(self.min_angle,2)))
            else: 
                set_tipAngle(entry,value)
        elif entry == self.topLengthProfileEntry or entry == self.bottomLengthProfileEntry:            
            set_sideLength = lambda x,y: self.set_topLengthProfile(y) if x == self.topLengthProfileEntry else self.set_bottomLengthProfile(y)
            if value > self.max_length:
                set_sideLength(entry,self.max_length)
                entry.set_text(str(round(self.max_length,2)))
            elif value < self.min_length:
                set_sideLength(entry,self.min_length)
                entry.set_text(str(round(self.min_length,2)))    
            else:
                set_sideLength(entry,value)