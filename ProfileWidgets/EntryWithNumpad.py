import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject
import re,cairo

class BubbleNumpad(Gtk.Overlay):
    def __init__(
        self,
        parent,
        label,
        h_align : Gtk.ArrowType,
        v_align : Gtk.ArrowType
        ):
        super(BubbleNumpad,self).__init__(can_focus=False)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('css_styles_sheets/bubbleNumpadstyle.css')
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)        

        self.par = parent
        self.label = label
        self.h_align = h_align
        self.v_align = v_align 

        self.char = [('1','2','3'),
                 ('4','5','6'),
                 ('7','8','9'),
                 ('.','0','←')]
        
        drawingArea = Gtk.DrawingArea(can_focus=False)
        self.add_overlay(drawingArea)
        drawingArea.connect("draw", self.on_draw)

        self.grid = Gtk.Grid(name='bubbleNumpadGrid')

        for i,row in enumerate(self.char):
            for j,col in enumerate(row):
                button = Gtk.Button(label=col,expand=True,can_focus=False, name='bubbleNumpadButton')
                self.grid.attach(button,j,i,1,1) 
                button.connect("clicked", self.on_button_clicked_event)

        self.add_overlay(self.grid)

    def get_parent(self):
        return self.par
    
    def get_h_align(self):
        return self.h_align 

    def get_v_align(self):
        return self.v_align 


    
    def get_label(self):
        return self.label

    def on_button_clicked_event(self, widget):
        widget = widget.get_child() 
        if widget.get_label() != '←':
            self.par.set_text(self.par.get_text() + widget.get_label())
        else:
            self.par.set_text(self.par.get_text()[:-1]) 
 
    def on_draw(self, widget, ctx):

        WIDTH = widget.get_allocated_width()
        HEIGHT = widget.get_allocated_height()
        PEAK_WIDTH = WIDTH*0.1
        PEAK_HEIGHT = HEIGHT*0.075
        X_OFFSET = WIDTH*0.05
        Y_OFFSET = HEIGHT*0.05
        BUTTON_OFFSET = ((WIDTH+HEIGHT)/2)*0.025

        H_ALIGN_POINTS = {Gtk.ArrowType.RIGHT:(X_OFFSET,WIDTH-X_OFFSET,WIDTH-X_OFFSET,X_OFFSET+PEAK_WIDTH,X_OFFSET+PEAK_WIDTH),
                        Gtk.ArrowType.LEFT:(WIDTH-X_OFFSET,X_OFFSET,X_OFFSET,WIDTH-X_OFFSET-PEAK_WIDTH,WIDTH-X_OFFSET-PEAK_WIDTH)}
        V_ALIGN_POINTS = {Gtk.ArrowType.DOWN:(Y_OFFSET,Y_OFFSET,HEIGHT-Y_OFFSET,HEIGHT-Y_OFFSET,Y_OFFSET+PEAK_HEIGHT),
                          Gtk.ArrowType.UP:(HEIGHT-Y_OFFSET,HEIGHT-Y_OFFSET,Y_OFFSET,Y_OFFSET,HEIGHT-Y_OFFSET-PEAK_HEIGHT)}

        H_ALIGN_MARGINS = {Gtk.ArrowType.RIGHT:(X_OFFSET+PEAK_WIDTH+BUTTON_OFFSET,X_OFFSET+BUTTON_OFFSET),
                        Gtk.ArrowType.LEFT:(X_OFFSET+BUTTON_OFFSET,X_OFFSET+PEAK_WIDTH+BUTTON_OFFSET)}
       
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(10) 

        for i in range(0,2):
            ctx.move_to(H_ALIGN_POINTS[self.h_align][0],V_ALIGN_POINTS[self.v_align][0])
            ctx.line_to(H_ALIGN_POINTS[self.h_align][1],V_ALIGN_POINTS[self.v_align][1])
            ctx.line_to(H_ALIGN_POINTS[self.h_align][2],V_ALIGN_POINTS[self.v_align][2])
            ctx.line_to(H_ALIGN_POINTS[self.h_align][3],V_ALIGN_POINTS[self.v_align][3])
            ctx.line_to(H_ALIGN_POINTS[self.h_align][4],V_ALIGN_POINTS[self.v_align][4])
            ctx.close_path() 
            if i == 0:
                ctx.set_line_join(cairo.LINE_JOIN_ROUND)      
                ctx.stroke()  
            else:
                ctx.fill()  

        self.grid.set_margin_left(H_ALIGN_MARGINS[self.h_align][0])
        self.grid.set_margin_top(Y_OFFSET+BUTTON_OFFSET)
        self.grid.set_margin_right(H_ALIGN_MARGINS[self.h_align][1])
        self.grid.set_margin_bottom(Y_OFFSET+BUTTON_OFFSET)       


class EntryNumpad(Gtk.Entry,Gtk.Editable):  
    def __init__(
        self,
        parent,
        label : str,
        h_align_bubbleNumpad : Gtk.ArrowType,
        v_align_bubbleNumpad : Gtk.ArrowType,
        num_int_digits : int = 4,
        num_decimal_digits : int = 2,    
        init_value: float = 0    
        ):
        super(EntryNumpad,self).__init__() 

        self.parent = parent
        self.label = label
        self.h_align_bubbleNumpad = h_align_bubbleNumpad
        self.v_align_bubbleNumpad = v_align_bubbleNumpad      
        self.num_int_digits = num_int_digits - 1
        self.num_decimal_digits = num_decimal_digits
        self.init_value = init_value

        self.set_text('%.2f'%self.init_value)

        self.bubbleNumpad = BubbleNumpad(self,self.label+'BubbleNumpad',self.h_align_bubbleNumpad,self.v_align_bubbleNumpad)
        
        self.bubbleNumpadVisible = False 

        self.connect('focus-in-event',self.show_numpad)
        self.connect('focus-out-event',self.hide_numpad)
    
    def get_parent(self):
        return self.parent
    
    def get_label(self):
        return self.label   

    def get_child_widget_by_name(self,overlay):
        for widget in overlay.get_children():
            if isinstance(widget, BubbleNumpad) and widget.get_label() == self.bubbleNumpad.get_label():
                return widget
        return None  

    def show_numpad(self, widget, event):
        if not self.bubbleNumpadVisible:
            self.bubbleNumpadVisible = True
            if self.get_child_widget_by_name(self.parent) == None:
                self.parent.add_overlay(self.bubbleNumpad) 
            self.bubbleNumpad.show_all()   
            
          
    def hide_numpad(self, widget, event):
        if self.bubbleNumpadVisible:
            self.bubbleNumpadVisible = False 
            if self.get_text():
                value = float(self.get_text())
                self.set_text('%.2f'%value)
            else:
                value = 0
            self.parent.emit('update-value', self, value)       
            self.bubbleNumpad.hide()   
            

    def validate_float_string(self,input_string):
        pattern = r"^([1-9]\d{{0,{}}}|0)(\.|\.\d{{1,{}}})?$".format(self.num_int_digits,self.num_decimal_digits)
        return re.match(pattern, input_string)    

    def do_insert_text(self, new_text, length, position):
        
        validate_float_string = self.validate_float_string(new_text)

        if validate_float_string:
            self.get_buffer().insert_text(position, new_text, length)
            return position + length

        self.get_buffer().insert_text(position, new_text[:-1], length-1)
        return position
