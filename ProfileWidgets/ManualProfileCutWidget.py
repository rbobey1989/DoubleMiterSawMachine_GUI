import gi, re

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk,Gdk
import cairo,math

from .EntryWithNumpad import EntryNumpad,BubbleNumpad

class ManualProfileCutWidget(Gtk.Overlay):
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
        length_width :  float = 0.25,
        height_bubble_numpad : float = 0.60, 
        width_bubble_numpad : float = 0.20
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

        self.drawingArea = Gtk.DrawingArea(can_focus=True,focus_on_click=True)

        self.drawingArea.set_events(
            self.drawingArea.get_events()   |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.KEY_PRESS_MASK
            )

        self.drawingArea.connect("draw", self.on_draw)
        self.drawingArea.connect("focus-out-event",self.on_focus_out_event)
        self.drawingArea.connect("focus-in-event",self.on_focus_in_event)        
        self.drawingArea.connect("button-press-event", self.on_button_press)
        self.drawingArea.connect("key-press-event",self.on_key_press)

        self.connect('get-child-position',self.on_get_child_position)

        self.add_overlay(self.drawingArea)         
        
        screen = Gdk.Screen.get_default()
        self.provider = Gtk.CssProvider()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, self.provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )       
        
        self.topLengthProfileEntry = EntryNumpad(self,
                                                 label='entryLengthsTop',
                                                 h_align_bubbleNumpad=Gtk.ArrowType.RIGHT,
                                                 v_align_bubbleNumpad=Gtk.ArrowType.DOWN)
        self.topLengthProfileEntry.set_name(name='entryLengths')
        self.topLengthProfileEntry.set_max_length(7)
        self.topLengthProfileEntry.set_alignment(xalign=0.5)
        self.topLengthProfileEntry.set_halign(Gtk.Align.CENTER)
        self.topLengthProfileEntry.set_valign(Gtk.Align.START)
        self.add_overlay(self.topLengthProfileEntry)
     
        self.bottomLengthProfileEntry = EntryNumpad(self,
                                                    label='entryLengthsBottom',
                                                    h_align_bubbleNumpad=Gtk.ArrowType.RIGHT,
                                                    v_align_bubbleNumpad=Gtk.ArrowType.UP)                                               
        self.bottomLengthProfileEntry.set_name(name='entryLengths')
        self.bottomLengthProfileEntry.set_max_length(7)
        self.bottomLengthProfileEntry.set_alignment(xalign=0.5)
        self.bottomLengthProfileEntry.set_halign(Gtk.Align.CENTER)
        self.bottomLengthProfileEntry.set_valign(Gtk.Align.END)
        self.add_overlay(self.bottomLengthProfileEntry)       
        
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
        #entryLengths {
            font-size: """+ str(int(PADDING_LINE*0.8)) +"""px
        }
        """).encode()
        self.provider.load_from_data(css) 

        
        self.topLengthProfileEntry.set_size_request(width=LENGTH_WIDTH,height=int(PADDING_LINE)) 
        self.topLengthProfileEntry.set_margin_top(PADDING_LINE-self.topLengthProfileEntry.get_allocated_height()/2)


        self.bottomLengthProfileEntry.set_size_request(width=LENGTH_WIDTH,height=int(PADDING_LINE))
        self.bottomLengthProfileEntry.set_margin_bottom(PADDING_LINE-self.bottomLengthProfileEntry.get_allocated_height()/2)        
                   
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
                   
            if widget.get_h_align() == Gtk.ArrowType.RIGHT:
                allocation.x = WIDTH/2 + LENGTH_WIDTH/2
            elif widget.get_h_align() == Gtk.ArrowType.LEFT:
                allocation.x = WIDTH/2 - LENGTH_WIDTH/2 - WIDTH_BUBBLE_NUMPAD  
            
            if widget.get_v_align() == Gtk.ArrowType.DOWN:
                allocation.y = PADDING_LINE
            elif widget.get_v_align() == Gtk.ArrowType.UP:
                allocation.y = HEIGHT - PADDING_LINE - HEIGHT_BUBBLE_NUMPAD

            allocation.width = WIDTH_BUBBLE_NUMPAD
            allocation.height = HEIGHT_BUBBLE_NUMPAD 
            return True
        else:
            return False