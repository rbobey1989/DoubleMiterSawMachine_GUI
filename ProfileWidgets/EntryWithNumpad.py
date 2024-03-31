import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject
import re,cairo

class BubbleNumpad(Gtk.Overlay):
    def __init__(self,parent,h_align,v_align):
        Gtk.Overlay.__init__(self,can_focus=True)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('css_styles_sheets/bubbleNumpadstyle.css')
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)        

        self.par = parent
        self.h_align = h_align
        self.v_align = v_align

        label = [('1','2','3'),
                 ('4','5','6'),
                 ('7','8','9'),
                 ('.','0','←')]
        
        self.drawingArea = Gtk.DrawingArea(can_focus=False)
        self.add_overlay(self.drawingArea)

        self.grid = Gtk.Grid(can_focus=False,name='bubbleNumpadGrid')
        
        for i,row in enumerate(label):
            for j,col in enumerate(row):
                button = Gtk.Button(label=col,can_focus=False,expand=True,name='bubbleNumpadButton')
                self.grid.attach(button,j,i,1,1) 
                button.connect('button-press-event',self.on_button_press_event_button)            

        self.add_overlay(self.grid)

        self.drawingArea.connect("draw", self.on_draw)
        self.connect('focus-out-event',self.on_focus_out_event)

    def get_h_align(self):
        return self.h_align 

    def get_v_align(self):
        return self.v_align  

    def on_button_press_event_button(self, widget, event):
        if widget.get_label() != '←':
            self.par.set_text(self.par.get_text() + widget.get_label())
        else:
            self.par.set_text(self.par.get_text()[:-1])        

    def on_focus_out_event(self, widget, event):
        self.par.emit('hide-numpad')

    def on_draw(self, widget, ctx):

        WIDTH = widget.get_allocated_width()
        HEIGHT = widget.get_allocated_height()
        PEAK_WIDTH = WIDTH*0.1
        PEAK_HEIGHT = HEIGHT*0.075
        X_OFFSET = WIDTH*0.05
        Y_OFFSET = HEIGHT*0.05
        BUTTON_OFFSET = ((WIDTH+HEIGHT)/2)*0.05

        H_ALIGN_POINTS = {Gtk.ArrowType.RIGHT:(X_OFFSET,WIDTH-X_OFFSET,WIDTH-X_OFFSET,X_OFFSET+PEAK_WIDTH,X_OFFSET+PEAK_WIDTH),
                        Gtk.ArrowType.LEFT:(X_OFFSET,WIDTH-X_OFFSET-PEAK_WIDTH,WIDTH-X_OFFSET-PEAK_WIDTH,WIDTH-X_OFFSET,X_OFFSET)}
        V_ALIGN_POINTS = {Gtk.ArrowType.DOWN:(Y_OFFSET,Y_OFFSET,HEIGHT-Y_OFFSET,HEIGHT-Y_OFFSET,Y_OFFSET+PEAK_HEIGHT),
                          Gtk.ArrowType.UP:(HEIGHT-Y_OFFSET,HEIGHT-Y_OFFSET,Y_OFFSET,Y_OFFSET,HEIGHT-Y_OFFSET-PEAK_HEIGHT)}

        H_ALIGN_MARGINS = {Gtk.ArrowType.RIGHT:(X_OFFSET+PEAK_WIDTH+BUTTON_OFFSET,X_OFFSET+BUTTON_OFFSET),
                        Gtk.ArrowType.LEFT:(X_OFFSET+BUTTON_OFFSET,X_OFFSET+PEAK_WIDTH+BUTTON_OFFSET)}
       
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(20) 

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
        
        # if self.h_align == Gtk.ArrowType.RIGHT and self.v_align == Gtk.ArrowType.DOWN:
        #     for i in range(0,2):
        #         ctx.move_to(X_OFFSET,Y_OFFSET)
        #         ctx.line_to(WIDTH-X_OFFSET,Y_OFFSET)
        #         ctx.line_to(WIDTH-X_OFFSET,HEIGHT-Y_OFFSET)
        #         ctx.line_to(X_OFFSET+PEAK_WIDTH,HEIGHT-Y_OFFSET)
        #         ctx.line_to(X_OFFSET+PEAK_WIDTH,Y_OFFSET+PEAK_HEIGHT)
        #         ctx.close_path() 
        #         if i == 0:
        #             ctx.set_line_join(cairo.LINE_JOIN_ROUND)      
        #             ctx.stroke()  
        #         else:
        #             ctx.fill()

        # if self.h_align == Gtk.ArrowType.RIGHT and self.v_align == Gtk.ArrowType.UP:
        #     for i in range(0,2):
        #         ctx.move_to(X_OFFSET,HEIGHT-Y_OFFSET)
        #         ctx.line_to(WIDTH-X_OFFSET,HEIGHT-Y_OFFSET)
        #         ctx.line_to(WIDTH-X_OFFSET,Y_OFFSET)
        #         ctx.line_to(X_OFFSET+PEAK_WIDTH,Y_OFFSET)
        #         ctx.line_to(X_OFFSET+PEAK_WIDTH,HEIGHT-Y_OFFSET-PEAK_HEIGHT)
        #         ctx.close_path() 
        #         if i == 0:
        #             ctx.set_line_join(cairo.LINE_JOIN_ROUND)      
        #             ctx.stroke()  
        #         else:
        #             ctx.fill()

        

        


        
        

class EntryNumpad(Gtk.Entry,Gtk.Editable):
    __gsignals__ = {
        'show-numpad': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'hide-numpad': (GObject.SignalFlags.RUN_FIRST, None, ())
    }
    def __init__(
        self,
        parent,
        label : str,
        h_align_bubbleNumpad : Gtk.ArrowType,
        v_align_bubbleNumpad : Gtk.ArrowType,     
        lower_limit : float = 240.00,
        upper_limit : float = 6500.00        
        ):
        super(EntryNumpad,self).__init__() 

        self.parent = parent
        self.label = label
        self.h_align_bubbleNumpad = h_align_bubbleNumpad
        self.v_align_bubbleNumpad = v_align_bubbleNumpad        
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit 

        self.bubbleNumpad = BubbleNumpad(self,self.h_align_bubbleNumpad,self.v_align_bubbleNumpad)
        self.bubbleNumpad.set_name(self.label+'BubbleNumpad')
        
        self.state = 0

        self.connect('show-numpad', self.show_numpad)
        self.connect('hide-numpad', self.hide_numpad) 

    def get_parent(self):
        return self.parent

   

    def do_focus_in_event(self, event):
        self.emit('show-numpad')
        return Gtk.Entry.do_focus_in_event(self, event)

    def get_child_widget_by_name(self,overlay):
        for widget in overlay.get_children():
            if isinstance(widget, BubbleNumpad) and widget.get_name() == self.bubbleNumpad.get_name():
                return widget
        return None  

    def show_numpad(self, widget):
        
        if self.get_child_widget_by_name(self.parent) == None:
            self.parent.add_overlay(self.bubbleNumpad) 
        self.bubbleNumpad.show_all()
        self.bubbleNumpad.grab_focus()           

    def hide_numpad(self, widget):     
        self.bubbleNumpad.hide()


    def validate_float_string(self,input_string, lower_limit, upper_limit):
        pattern = r'^([1-9]\d{0,3}|0)(\.|\.\d{1,2})?$'
        # return re.match(pattern, input_string) is not None and lower_limit <= float(input_string) <= upper_limit
        return re.match(pattern, input_string)    

    def do_insert_text(self, new_text, length, position):
        
        validate_float_string = self.validate_float_string(new_text,self.lower_limit,self.upper_limit)

        if validate_float_string:
            self.get_buffer().insert_text(position, new_text, length)
            return position + length

        self.get_buffer().insert_text(position, new_text[:-1], length-1)
        return position

        # validate_float_string = self.validate_float_string(new_text,self.lower_limit,self.upper_limit)

        # if new_text.__len__() <= 4 and new_text[-1] != '.' and new_text.isnumeric() and float(new_text) <= self.upper_limit:
        #     if self.get_text().__len__() == 0 and new_text == '0': 
        #         return position
        #     else:
        #         self.get_buffer().insert_text(position, new_text, length)
        #         return position + length
        # elif self.validate_float_string(new_text,self.lower_limit,self.upper_limit):
        #     self.get_buffer().insert_text(position, new_text, length)
        #     return position + length
        # else:
        #     if float(new_text) < self.lower_limit :
        #         self.get_buffer().insert_text(position, str(round(self.lower_limit,2)), length)
        #         return str(round(self.lower_limit,2)).__len__()
        #     elif float(new_text) > self.upper_limit: 
        #         self.get_buffer().insert_text(position, str(round(self.upper_limit,2)), length)
        #         return str(round(self.upper_limit,2)).__len__()
        #     # self.get_buffer().insert_text(position, new_text[-1], length)
        #     # return position + length -1
        # return position
    

# class EntryWindow(Gtk.Window):
#     def __init__(self):
#         Gtk.Window.__init__(self, title="Entry Widget Example")
#         self.set_default_size(200, 100)

           

#         button = Gtk.Button()

#         box = Gtk.VBox()

#         self.entry = EntryWithSignal(self)   

#         box.pack_start(button,True,True,10)
#         box.pack_start(self.entry,True,True,10)
#         self.add(box)


# win = EntryWindow()
# win.connect("destroy", Gtk.main_quit)
# win.show_all()
# Gtk.main()