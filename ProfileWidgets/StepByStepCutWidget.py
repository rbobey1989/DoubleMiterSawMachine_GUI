import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject

import os, json

from .EntryWithNumpad import EntryNumpad, BubbleNumpad, myAlign


class StepByStepCutWidget(Gtk.Overlay):
    __gsignals__ = {
        'update-value': (GObject.SignalFlags.RUN_FIRST, None, (EntryNumpad,float)),
    }
    def __init__(
            self,
            y_offset :  float = 0.15,
            x_offset :  float = 0.30,
            length_width :  float = 0.25,
            padding_line :  float = 0.10,
            height_bubble_numpad : float = 0.50, 
            width_bubble_numpad : float = 0.175,
            rows : int = 5,
            min_length : float = 290.00,
            max_length : float = 4000.00):
        super(StepByStepCutWidget,self).__init__()



        self.y_offset = y_offset
        self.x_offset = x_offset
        self.length_width = length_width
        self.padding_line = padding_line
        self.height_bubble_numpad = height_bubble_numpad 
        self.width_bubble_numpad  = width_bubble_numpad   
        self.rows = rows
        self.min_length = min_length
        self.max_length = max_length
        self.time_out_disk = 0

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
            label.set_name('labelIdicatorsStepByStepCutWidgeButton')
            label.set_valign(Gtk.Align.START)
            self.add_overlay(label)

        self.colNumbers = [Gtk.Label(label=str(i+1), halign=Gtk.Align.START) for i in range(self.rows)]

        for i, label in enumerate(self.colNumbers):
            label.set_name('labelIdicatorsStepByStepCutWidgeButton')
            label.set_valign(Gtk.Align.START)
            self.add_overlay(label)

        self.checkButtons = [Gtk.ToggleButton(halign=Gtk.Align.START, 
                                              hexpand=True, vexpand= True,
                                              name='checkToggleButton') for i in range(self.rows)]
        

        for i, checkButton in enumerate(self.checkButtons):
            checkButton.set_valign(Gtk.Align.START)
            checkButton.set_halign(Gtk.Align.END)
            self.add_overlay(checkButton)

        self.rowStartListEntry = EntryNumpad(self,
                                            label='entryRowStartList',
                                            h_align_entry= myAlign.CENTER,
                                            v_align_entry= myAlign.START,
                                            h_align_bubbleNumpad=Gtk.ArrowType.RIGHT,
                                            v_align_bubbleNumpad=Gtk.ArrowType.DOWN,
                                            num_int_digits=1,
                                            num_decimal_digits=0, 
                                            init_value=1,                                               
                                            )
        self.rowStartListEntry.set_name('entryWithNumpadManualWidget')
        self.rowStartListEntry.set_can_focus(True)
        self.rowStartListEntry.set_max_length(1)
        self.rowStartListEntry.set_alignment(xalign=0.5)
        self.rowStartListEntry.set_halign(Gtk.Align.START)

        self.labelArrowStartToEndList = Gtk.Label(label=' --> ')
        self.labelArrowStartToEndList.set_name('labelIdicatorsStepByStepCutWidgeButton')

        self.rowEndListEntry = EntryNumpad(self,
                                            label='entryRowEndList',
                                            h_align_entry= myAlign.CENTER,
                                            v_align_entry= myAlign.START,
                                            h_align_bubbleNumpad=Gtk.ArrowType.RIGHT,
                                            v_align_bubbleNumpad=Gtk.ArrowType.DOWN,
                                            num_int_digits=1,
                                            num_decimal_digits=0, 
                                            init_value=1,                                               
                                            )
        self.rowEndListEntry.set_name('entryWithNumpadManualWidget')
        self.rowEndListEntry.set_can_focus(True)
        self.rowEndListEntry.set_max_length(1)
        self.rowEndListEntry.set_alignment(xalign=0.5)
        self.rowEndListEntry.set_halign(Gtk.Align.START)

        self.hBoxRowStartEndList = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                            halign=Gtk.Align.START,
                                            valign=Gtk.Align.START)
        
        self.hBoxRowStartEndList.pack_start(self.rowStartListEntry, True, True, 0)
        self.hBoxRowStartEndList.pack_start(self.labelArrowStartToEndList, True, True, 0)
        self.hBoxRowStartEndList.pack_start(self.rowEndListEntry, True, True, 0)

        self.add_overlay(self.hBoxRowStartEndList)

        self.restartChecksBtn = Gtk.EventBox(valign=Gtk.Align.START,
                                            halign=Gtk.Align.START)
        self.restartChecksBtn.add(Gtk.Image.new_from_file(filename='icons/restart_checks_of_complete_rows.png'))
        self.restartChecksBtn.connect('button-press-event', self.on_restartChecksBtn_press)
        self.restartChecksBtn.connect('button-release-event', self.on_restartChecksBtn_release)

        self.add_overlay(self.restartChecksBtn)

        self.restarWholeList = Gtk.EventBox(valign=Gtk.Align.START,
                                            halign=Gtk.Align.START)
        self.restarWholeList.add(Gtk.Image.new_from_file(filename='icons/restart_whole_list.png'))
        self.restarWholeList.connect('button-press-event', self.on_restarWholeList_press)
        self.restarWholeList.connect('button-release-event', self.on_restarWholeList_release)

        self.add_overlay(self.restarWholeList)

        self.labelCountProcessedCuts = Gtk.Label(label='#')
        self.labelCountProcessedCuts.set_name('labelIdicatorsStepByStepCutWidgeButton')

        self.countProcessedCutsEntry = EntryNumpad(self,
                                                    label='entryCountProcessedCuts',
                                                    h_align_entry= myAlign.CENTER,
                                                    v_align_entry= myAlign.START,
                                                    h_align_bubbleNumpad=Gtk.ArrowType.RIGHT,
                                                    v_align_bubbleNumpad=Gtk.ArrowType.DOWN,
                                                    num_int_digits=4,
                                                    num_decimal_digits=0, 
                                                    init_value=0,                                               
                                                    )
        self.countProcessedCutsEntry.set_name('entryWithNumpadManualWidget')
        self.countProcessedCutsEntry.set_can_focus(False)
        self.countProcessedCutsEntry.set_max_length(4)
        self.countProcessedCutsEntry.set_alignment(xalign=0.5)

        self.hBoxCountProcessedCuts = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                                                halign=Gtk.Align.END,
                                                valign=Gtk.Align.START)
        self.hBoxCountProcessedCuts.pack_start(self.labelCountProcessedCuts, True, True, 0)
        self.hBoxCountProcessedCuts.pack_start(self.countProcessedCutsEntry, True, True, 0)
        self.add_overlay(self.hBoxCountProcessedCuts)

        self.targetPosEntry = EntryNumpad(self,
                                            label='entryTargetPos',
                                            h_align_entry= myAlign.CENTER,
                                            v_align_entry= myAlign.START,
                                            h_align_bubbleNumpad=Gtk.ArrowType.LEFT,
                                            v_align_bubbleNumpad=Gtk.ArrowType.UP,
                                            num_int_digits=2,
                                            num_decimal_digits=1, 
                                            init_value=0,                                               
                                            )
        self.targetPosEntry.set_name('entryWithNumpadManualWidget')
        self.targetPosEntry.set_can_focus(True)
        self.targetPosEntry.set_max_length(4)
        self.targetPosEntry.set_alignment(xalign=0.5)
        self.targetPosEntry.set_halign(Gtk.Align.END)
        self.targetPosEntry.set_valign(Gtk.Align.END)
        self.add_overlay(self.targetPosEntry)

        self.FbPosEntry = EntryNumpad(self,
                                    label='fbPos',
                                    h_align_entry= myAlign.END,
                                    v_align_entry= myAlign.START,                                                  
                                    h_align_bubbleNumpad=Gtk.ArrowType.LEFT,
                                    v_align_bubbleNumpad=Gtk.ArrowType.DOWN,
                                    num_int_digits=4,
                                    num_decimal_digits=1,
                                    init_value=0                                                                                            
                                    )                                               
        self.FbPosEntry.set_name('entryWithNumpadManualWidget')
        self.FbPosEntry.set_can_focus(False)
        self.FbPosEntry.set_max_length(7)
        self.FbPosEntry.set_alignment(xalign=0.5)
        self.FbPosEntry.set_halign(Gtk.Align.END)
        self.FbPosEntry.set_valign(Gtk.Align.END)
        self.add_overlay(self.FbPosEntry)  

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
                                        num_int_digits=4,
                                        num_decimal_digits=1, 
                                        init_value=0.0,                                               
                                        )
            PiecesEntry.set_name('entryWithNumpadManualWidget')
            PiecesEntry.set_can_focus(True)
            PiecesEntry.set_max_length(7)
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

        #labelIdicatorsStepByStepCutWidgeButton {
            font-size: """+ str(entry_height*0.6) +"""px;
            color: white;
            text-shadow: 2px 2px 4px #000000;
        }

        #checkToggleButton {
            background: #FFFFFF;
            border-width:     4px;
            border-radius: 2px;
            border-color: #D4CFCB;
            box-shadow: 5px 5px 5px 5px rgba(0, 0, 0, 0.5);
            border-radius: 2px;
        }

        #checkToggleButton:checked {
            background: rgb(233, 11, 11);
            border-width:     4px;
            border-radius: 2px;
            border-color: #D4CFCB;
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
            checkButton.set_size_request(width=entry_height*1/4, height=entry_height*1/4)
            checkButton.set_margin_top(int(Y_OFFSET + row_height*(i+1/2) - checkButton.get_allocated_height()/2))
            checkButton.set_margin_right(X_OFFSET - checkButton.get_allocated_width()*2)

        self.restartChecksBtn.set_margin_top(HEIGHT/2)
        self.restartChecksBtn.set_margin_left(WIDTH/16)

        self.restarWholeList.set_margin_top(int(HEIGHT/2 + self.restartChecksBtn.get_allocated_height()*(1.25)))
        self.restarWholeList.set_margin_left(WIDTH/16)

        self.hBoxRowStartEndList.set_size_request(width=int(LENGTH_WIDTH*3/4), height=entry_height)
        self.hBoxRowStartEndList.set_margin_top(int(Y_OFFSET + row_height*(1/2) - entry_height/2))
        self.hBoxRowStartEndList.set_margin_left(X_OFFSET/16)

        self.hBoxCountProcessedCuts.set_size_request(width=LENGTH_WIDTH/2, height=entry_height)
        self.hBoxCountProcessedCuts.set_margin_top(int(Y_OFFSET + row_height*(1/2) - entry_height/2))
        self.hBoxCountProcessedCuts.set_margin_right(X_OFFSET/16)

        self.FbPosEntry.set_size_request(width=LENGTH_WIDTH/2, height=entry_height)
        self.FbPosEntry.set_margin_bottom(int(Y_OFFSET + row_height*(1/2) - entry_height))
        self.FbPosEntry.set_margin_right(X_OFFSET/16)

        self.targetPosEntry.set_size_request(width=LENGTH_WIDTH/2, height=entry_height)
        self.targetPosEntry.set_margin_bottom(int(Y_OFFSET + row_height*(1+1/2) - entry_height))
        self.targetPosEntry.set_margin_right(X_OFFSET/16)

    def on_button_press(self, widget, event):
        widget.grab_focus()

    def on_restartChecksBtn_press(self, widget, event):
        child = widget.get_child()
        child.set_from_file(filename='icons/restart_checks_of_complete_rows_pressed.png')

    def on_restartChecksBtn_release(self, widget, event):
        child = widget.get_child()
        child.set_from_file(filename='icons/restart_checks_of_complete_rows.png')
        for i, checkButton in enumerate(self.checkButtons):
            if checkButton.get_active():
                self.checkButtons[i].set_active(False)

    def on_restarWholeList_press(self, widget, event):
        child = widget.get_child()
        child.set_from_file(filename='icons/restart_whole_list_pressed.png')

    def on_restarWholeList_release(self, widget, event):
        child = widget.get_child()
        child.set_from_file(filename='icons/restart_whole_list.png')

        self.rowStartListEntry.set_text('1')
        self.rowEndListEntry.set_text('1')
        self.countProcessedCutsEntry.set_text('0')

        for i, (length_entry, pieces_entry, processed_pieces_entry) in enumerate(self.entries):
            length_entry.set_text('0.0')
            pieces_entry.set_text('0.0')
            processed_pieces_entry.set_text('0')
            self.checkButtons[i].set_active(False)

    def find_entry_index(self, entry):
        for i, row in enumerate(self.entries):
            for j, col in enumerate(row):
                if entry == col:
                    return (i, j)
        return None
    
    def update_row(self, rows, qty, check):
        self.entries[rows][2].set_text(str(qty))
        self.checkButtons[rows].set_active(check)

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

        row_height = int((HEIGHT-Y_OFFSET)/ self.rows)
        entry_height = int(row_height*(1-self.padding_line - 0.2))
        
        if isinstance(widget, BubbleNumpad):
            indexTable = self.find_entry_index(widget.get_parent())
            otherEntries = [self.rowStartListEntry,
                            self.rowEndListEntry,
                            self.targetPosEntry]

            if indexTable is not None:
            
                if widget.get_parent().get_halign() == Gtk.Align.START:
                    allocation.x = X_OFFSET - WIDTH_BUBBLE_NUMPAD
                elif widget.get_parent().get_halign() == Gtk.Align.CENTER:
                    allocation.x = (WIDTH + widget.get_parent().get_allocated_width())/2
                else:
                    allocation.x = WIDTH - X_OFFSET 

                allocation.y = Y_OFFSET + indexTable[0]*int((HEIGHT-Y_OFFSET)/ self.rows) + int((HEIGHT-Y_OFFSET)/ self.rows)/2
                if widget.get_parent().get_v_align_bubbleNumpad() == Gtk.ArrowType.UP:
                    allocation.y -= HEIGHT_BUBBLE_NUMPAD

                allocation.width = WIDTH_BUBBLE_NUMPAD
                allocation.height = HEIGHT_BUBBLE_NUMPAD    

            elif widget.get_parent() in otherEntries:
                if widget.get_parent() == self.rowStartListEntry:
                    allocation.x = X_OFFSET/16 + self.rowStartListEntry.get_allocated_width()
                    allocation.y = Y_OFFSET + widget.get_parent().get_allocated_height()/2
                elif widget.get_parent() == self.rowEndListEntry:
                    allocation.x = X_OFFSET/16 + self.rowStartListEntry.get_allocated_width() + self.labelArrowStartToEndList.get_allocated_width() + self.rowEndListEntry.get_allocated_width()
                    allocation.y = Y_OFFSET + widget.get_parent().get_allocated_height()/2
                elif widget.get_parent() == self.targetPosEntry:
                    allocation.x = WIDTH - (X_OFFSET/16 + self.targetPosEntry.get_allocated_width()) - WIDTH_BUBBLE_NUMPAD
                    allocation.y = HEIGHT - int(Y_OFFSET + row_height*(1+1/2) - entry_height) - HEIGHT_BUBBLE_NUMPAD
                

                allocation.width = WIDTH_BUBBLE_NUMPAD
                allocation.height = HEIGHT_BUBBLE_NUMPAD 

            else:
                return False
            
            return True
        else:
            return False

        
    def on_update_value(self,widget,entry, value):
        if entry == self.rowStartListEntry:
            value = int(value)
            if value > self.rows:
                self.rowStartListEntry.set_text(str(self.rows))
                self.rowEndListEntry.set_text(str(self.rows))
            elif value < 1:
                self.rowStartListEntry.set_text('1')
            elif value > int(self.rowEndListEntry.get_text()):
                self.rowStartListEntry.set_text(str(value))
                self.rowEndListEntry.set_text(str(value))
            else:
                self.rowStartListEntry.set_text(str(value))
        elif entry == self.rowEndListEntry:
            value = int(value)
            if value > self.rows:
                self.rowEndListEntry.set_text(str(self.rows))
            elif value < 1:
                self.rowEndListEntry.set_text('1')
                self.rowStartListEntry.set_text('1')
            elif value < int(self.rowStartListEntry.get_text()):
                self.rowStartListEntry.set_text(str(value))
                self.rowEndListEntry.set_text(str(value))
            else:
                self.rowEndListEntry.set_text(str(value))
        elif self.find_entry_index(entry):
            max_values = ['%.*f'%(entry.get_num_decimal_digits(),self.max_length), 
                          '%.*f'%(entry.get_num_decimal_digits(),self.max_length), 
                          '999']
            min_values = ['%.*f'%(entry.get_num_decimal_digits(),self.min_length), 
                          '0', 
                          '0']
            index = self.find_entry_index(entry)
            if index is not None:
                for i,max_value in enumerate(max_values):
                    if entry == self.entries[index[0]][i]:
                        if value > float(max_value):
                            entry.set_text(max_value)
                        elif value < float(min_values[i]):
                            entry.set_text(min_values[i])
                        else:
                            if i != 2:
                                entry.set_text('%.*f'%(entry.get_num_decimal_digits(),value))
                            else:   
                                entry.set_text(str(int(value)))
        elif entry == self.targetPosEntry:
            if value > 99.9:
                self.targetPosEntry.set_text('99.9')
                self.time_out_disk = 99.9
            elif value < 0:
                self.targetPosEntry.set_text('0.0')
                self.time_out_disk = 0
            else:
                self.targetPosEntry.set_text('%.*f'%(entry.get_num_decimal_digits(),value))
                self.time_out_disk = value
        
        self.save_data_values()

    def get_time_out_disk(self):
        return self.time_out_disk

    def set_FbPos(self,length):
        self.FbPosEntry.set_text('%.*f'%(self.FbPosEntry.get_num_decimal_digits(),length))

    def load_data_values(self):
        stepByStepData_dir = 'stepByStepCutData'
        file_path = os.path.join(stepByStepData_dir, 'stepByStepCutData.json')

        if not os.path.exists(file_path):
            return

        with open(file_path, 'r') as file:
            data = json.load(file)
        
        self.rowStartListEntry.set_text(str(data['start_row']))
        self.rowEndListEntry.set_text(str(data['end_row']))
        self.countProcessedCutsEntry.set_text(str(data['global_processed_pieces']))

        for i, row_data in enumerate(data['table']):
            length_entry, pieces_entry, processed_pieces_entry = self.entries[i]
            length_entry.set_text(str(row_data['length']))
            pieces_entry.set_text(str(row_data['pieces']))
            processed_pieces_entry.set_text(str(row_data['processed_pieces']))
            self.checkButtons[i].set_active(row_data['button_state'])

    def save_data_values(self):
        stepByStepData_dir = 'stepByStepCutData'
        file_path = os.path.join(stepByStepData_dir, 'stepByStepCutData.json')

        if not os.path.exists(stepByStepData_dir):
            os.makedirs(stepByStepData_dir)

        data = {
            'table': [],
            'start_row': int(self.rowStartListEntry.get_text()),
            'end_row': int(self.rowEndListEntry.get_text()),
            'global_processed_pieces': int(self.countProcessedCutsEntry.get_text())
        }

        for i, row in enumerate(self.entries):
            length_entry, pieces_entry, processed_pieces_entry = row
            data['table'].append({
                'length': float(length_entry.get_text()),
                'pieces': float(pieces_entry.get_text()),
                'processed_pieces': int(processed_pieces_entry.get_text()),
                'button_state': self.checkButtons[i].get_active()
            })

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def get_entries(self):
        return self.entries
    
    def get_rowStartListEntry(self):
        return self.rowStartListEntry
    
    def get_rowEndListEntry(self):
        return self.rowEndListEntry
    
    def get_checkRows(self):
        return self.checkButtons
    
    def set_checkRow(self, checkBtn):
        self.checkButtons[checkBtn].set_active(True)

    def get_countProcessedCutsEntry(self):
        return int(self.countProcessedCutsEntry.get_text())
    
    def set_countProcessedCutsEntry(self, value):
        if value > 9999:
            self.countProcessedCutsEntry.set_text('0')
        elif value < 0:
            self.countProcessedCutsEntry.set_text('0')
        else:
            self.countProcessedCutsEntry.set_text('%d'%(value))




        

