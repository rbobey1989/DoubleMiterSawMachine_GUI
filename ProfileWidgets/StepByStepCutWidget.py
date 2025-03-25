import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject

from .EntryWithNumpad import EntryNumpad, BubbleNumpad, myAlign


class StepByStepCutWidget(Gtk.Overlay):
    __gsignals__ = {
        'update-value': (GObject.SignalFlags.RUN_FIRST, None, (EntryNumpad,float))
    }
    def __init__(
            self,
            y_offset :  float = 0.2,
            x_offset :  float = 0.30,
            length_width :  float = 0.25,
            padding_line :  float = 0.10,
            height_bubble_numpad : float = 0.50, 
            width_bubble_numpad : float = 0.175,
            rows : int = 5):
        super(StepByStepCutWidget,self).__init__()

        self.y_offset = y_offset
        self.x_offset = x_offset
        self.length_width = length_width
        self.padding_line = padding_line
        self.height_bubble_numpad = height_bubble_numpad 
        self.width_bubble_numpad  = width_bubble_numpad   
        self.rows = rows

        screen = Gdk.Screen.get_default()
        self.provider = Gtk.CssProvider()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, self.provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )  

        drawingArea = Gtk.DrawingArea(can_focus=True)
        drawingArea.set_name('manualCutProfileWidgetAnimation')

        drawingArea.set_events(
            drawingArea.get_events()   |
            Gdk.EventMask.BUTTON_PRESS_MASK
            )

        drawingArea.connect("draw", self.on_draw)      
        drawingArea.connect("button-press-event", self.on_button_press)

        self.add_overlay(drawingArea) 
        self.connect('get-child-position',self.on_get_child_position) 
        self.connect('update-value', self.on_update_value)  

        self.colLabels = [Gtk.Label(label='Length', halign=Gtk.Align.START),
                          Gtk.Label(label='Pieces', halign=Gtk.Align.CENTER),
                          Gtk.Label(label='Qty', halign=Gtk.Align.END)]

        for i, label in enumerate(self.colLabels):
            label.set_name('labelIdicatorsEntryWithNumpadManualWidget')
            label.set_valign(Gtk.Align.START)
            self.add_overlay(label)

        self.colNumbers = [Gtk.Label(label=str(i+1), halign=Gtk.Align.START) for i in range(self.rows)]

        for i, label in enumerate(self.colNumbers):
            label.set_name('labelIdicatorsEntryWithNumpadManualWidget')
            label.set_valign(Gtk.Align.START)
            self.add_overlay(label)

        self.checkButtons = [Gtk.ToggleButton(halign=Gtk.Align.START, 
                                              hexpand=True, vexpand= True,
                                              name='checkToggleButton') for i in range(self.rows)]

        for i, checkButton in enumerate(self.checkButtons):
            checkButton.set_valign(Gtk.Align.START)
            checkButton.set_halign(Gtk.Align.END)
            checkButton.connect('toggled', lambda btn: btn.set_label("✓") if btn.get_active() else btn.set_label(""))
            self.add_overlay(checkButton)

        self.entries = []

        for i in range(self.rows):


            if i < self.rows//2:
                vAlignBubbleNumpad = Gtk.ArrowType.DOWN
            else:
                vAlignBubbleNumpad = Gtk.ArrowType.UP

            

            LengthProfileEntry = EntryNumpad(self,
                                                label='entryTopLengths'+str(i),
                                                h_align_entry= myAlign.CENTER,
                                                v_align_entry= myAlign.START,
                                                h_align_bubbleNumpad=Gtk.ArrowType.LEFT,
                                                v_align_bubbleNumpad=vAlignBubbleNumpad,
                                                num_int_digits=4,
                                                num_decimal_digits=1, 
                                                init_value=0.0,                                               
                                                )
            LengthProfileEntry.set_name('entryWithNumpadManualWidget')
            LengthProfileEntry.set_can_focus(True)
            LengthProfileEntry.set_max_length(7)
            LengthProfileEntry.set_alignment(xalign=0.5)
            LengthProfileEntry.set_halign(Gtk.Align.START)

            PiecesEntry = EntryNumpad(self,
                                        label='entryPieces'+str(i),
                                        h_align_entry= myAlign.CENTER,
                                        v_align_entry= myAlign.START,
                                        h_align_bubbleNumpad=Gtk.ArrowType.RIGHT,
                                        v_align_bubbleNumpad=vAlignBubbleNumpad,
                                        num_int_digits=3,
                                        num_decimal_digits=0, 
                                        init_value=0.0,                                               
                                        )
            PiecesEntry.set_name('entryWithNumpadManualWidget')
            PiecesEntry.set_can_focus(True)
            PiecesEntry.set_max_length(4)
            PiecesEntry.set_alignment(xalign=0.5)
            PiecesEntry.set_halign(Gtk.Align.CENTER)

            ProcessedPiecesEntry = EntryNumpad(self,
                                                label='entryProcessedPieces'+str(i),
                                                h_align_entry= myAlign.CENTER,
                                                v_align_entry= myAlign.START,
                                                h_align_bubbleNumpad=Gtk.ArrowType.RIGHT,
                                                v_align_bubbleNumpad=vAlignBubbleNumpad,
                                                num_int_digits=3,
                                                num_decimal_digits=0, 
                                                init_value=0.0,                                               
                                                )
            ProcessedPiecesEntry.set_name('entryWithNumpadManualWidget')
            ProcessedPiecesEntry.set_can_focus(True)
            ProcessedPiecesEntry.set_max_length(4)
            ProcessedPiecesEntry.set_alignment(xalign=0.5)
            ProcessedPiecesEntry.set_halign(Gtk.Align.END)

            for entry in [LengthProfileEntry,PiecesEntry,ProcessedPiecesEntry]:
                entry.set_valign(Gtk.Align.START)

            self.add_overlay(LengthProfileEntry)
            self.add_overlay(PiecesEntry)
            self.add_overlay(ProcessedPiecesEntry)

            self.entries.append([LengthProfileEntry,PiecesEntry,ProcessedPiecesEntry])

    def on_draw(self, widget, ctx):        

        height = widget.get_allocated_height()
        width = widget.get_allocated_width()

        Y_OFFSET = int(height*self.y_offset)
        X_OFFSET = int(width*self.x_offset)
        HEIGHT = height 
        WIDTH = width  
        PADDING_LINE = height*self.padding_line
        LENGTH_WIDTH = width*self.length_width 

        row_height = int((HEIGHT-Y_OFFSET)/ self.rows)
        entry_height = int(row_height*(1-self.padding_line - 0.2))

        css = str("""
        #entryWithNumpadManualWidget {
            font-size: """+ str(entry_height*0.6) +"""px;
            background-color: white;
            caret-color:      white;
            border-width:     4px;
            box-shadow: 5px 5px 5px 5px rgba(0, 0, 0, 0.5);
            border-radius: 2px;
        }

        #labelIdicatorsEntryWithNumpadManualWidget {
            font-size: """+ str(entry_height*0.6) +"""px;
            color: white;
            text-shadow: 2px 2px 4px #000000;
        }

        #checkToggleButton {
            font-size: """ + str(entry_height * 0.3) + """px;
            background: #fff;
        }

        #checkToggleButton:checked {
            background: #fff;
            color: #000;
            font-size: """ + str(entry_height * 0.3) + """px;
        }
        """).encode()
        self.provider.load_from_data(css) 

        for i, label in enumerate(self.colLabels):
            label.set_size_request(width=LENGTH_WIDTH/2, height=entry_height)
            label.set_margin_top(Y_OFFSET - row_height/2 - label.get_allocated_height()/2)
            if i == 0:
                label.set_margin_left(X_OFFSET)
            elif i == 2:
                label.set_margin_right(X_OFFSET)

        for i, label in enumerate(self.colNumbers):
            label.set_margin_top(Y_OFFSET + row_height*(i+1/2) - label.get_allocated_height()/2)
            label.set_margin_left(X_OFFSET - label.get_allocated_width()*2)

        for i, (length_entry, pieces_entry, processed_pieces_entry) in enumerate(self.entries):
            

            length_entry.set_size_request(width=LENGTH_WIDTH/2, height=entry_height)
            length_entry.set_margin_left(X_OFFSET)

            pieces_entry.set_size_request(width=LENGTH_WIDTH/2, height=entry_height)
            
            processed_pieces_entry.set_size_request(width=LENGTH_WIDTH/2, height=entry_height)
            processed_pieces_entry.set_margin_right(X_OFFSET)

            for entry in [length_entry, pieces_entry, processed_pieces_entry]:
                entry.set_margin_top(int(Y_OFFSET + row_height*(i+1/2) - length_entry.get_allocated_height()/2))

        for i, checkButton in enumerate(self.checkButtons):
            checkButton.set_size_request(width=entry_height*3/4, height=entry_height*3/4)
            checkButton.set_margin_top(int(Y_OFFSET + row_height*(i+1/2) - checkButton.get_allocated_height()/2))
            checkButton.set_margin_right(X_OFFSET - checkButton.get_allocated_width()*2)

    def on_button_press(self, widget, event):
        widget.grab_focus()

    def find_entry_index(self, entry):
        for i, row in enumerate(self.entries):
            for j, col in enumerate(row):
                if entry == col:
                    return (i, j)
        return None

    def on_get_child_position(self, overlay, widget, allocation):
        
        width = overlay.get_allocated_width()
        height = overlay.get_allocated_height()

        HEIGHT = height 
        WIDTH = width 
        HEIGHT_BUBBLE_NUMPAD = height*self.height_bubble_numpad 
        WIDTH_BUBBLE_NUMPAD = width*self.width_bubble_numpad
        PADDING_LINE = height*self.padding_line
        LENGTH_WIDTH = width*self.length_width 
        Y_OFFSET = height*self.y_offset
        X_OFFSET = width*self.x_offset
        
        if isinstance(widget, BubbleNumpad):
            index = self.find_entry_index(widget.get_parent())
            if index is None:
                return False
            
            if widget.get_parent().get_halign() == Gtk.Align.START:
                allocation.x = X_OFFSET - WIDTH_BUBBLE_NUMPAD
            elif widget.get_parent().get_halign() == Gtk.Align.CENTER:
                allocation.x = (WIDTH + widget.get_parent().get_allocated_width())/2
            else:
                allocation.x = WIDTH - X_OFFSET 

            allocation.y = Y_OFFSET + index[0]*int((HEIGHT-Y_OFFSET)/ self.rows) + int((HEIGHT-Y_OFFSET)/ self.rows)/2
            if widget.get_parent().get_v_align_bubbleNumpad() == Gtk.ArrowType.UP:
                allocation.y -= HEIGHT_BUBBLE_NUMPAD

            allocation.width = WIDTH_BUBBLE_NUMPAD
            allocation.height = HEIGHT_BUBBLE_NUMPAD 
            return True
        else:
            return False

        
    def on_update_value(self,widget,entry, value):
        pass
