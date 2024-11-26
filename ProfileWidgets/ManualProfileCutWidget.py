#!/usr/bin/env python

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk, Gdk, GObject
import cairo,math

from .EntryWithNumpad import EntryNumpad,BubbleNumpad
from .EntryWithNumpad import myAlign



class ManualProfileCutWidget(Gtk.Overlay):
    __gsignals__ = {
        'update-value': (GObject.SignalFlags.RUN_FIRST, None, (EntryNumpad,float)),
        'bad-value': (GObject.SignalFlags.RUN_FIRST, None, (bool,))
    }
    def __init__(
        self, 
        parent,
        height_prof : float = 0.15, 
        height_arrow :  float = 0.7,
        width_arrow :  float = 1.5,
        y_offset :  float = 0.425,
        x_offset :  float = 0.24,
        padding_line :  float = 0.15,
        length_width :  float = 0.25,
        height_bubble_numpad : float = 0.50, 
        width_bubble_numpad : float = 0.175,
        min_length : float = 240.00,
        max_length : float = 6500.00,            
        min_angle: float = 22.5,
        max_angle: float = 157.5,
        max_height: float = 300.0
        ):
        super(ManualProfileCutWidget, self).__init__() 

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
        self.max_height = max_height

        self.lefTipAngle = 90
        self.rightTipAngle = 90
        self.topLengthProfile = 1000
        self.bottomLengthProfile = 1000
        self.heightProfile = 100
        self.timeOutDisk = 5
        self.numberOfCuts = 1

        self.focusTopLengthProfile = True
        self.focusBottomLengthProfile = False 

        self.dxfViewer = None

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

        self.topLengthProfileEntry = EntryNumpad(self,
                                                 label='entryTopLengths',
                                                 h_align_entry= myAlign.CENTER,
                                                 v_align_entry= myAlign.START,
                                                 h_align_bubbleNumpad=Gtk.ArrowType.LEFT,
                                                 v_align_bubbleNumpad=Gtk.ArrowType.DOWN,
                                                 num_int_digits=4,
                                                 num_decimal_digits=1, 
                                                 init_value=self.topLengthProfile                                                
                                                 )
        self.topLengthProfileEntry.set_name('entryWithNumpadManualWidget')
        self.topLengthProfileEntry.set_max_length(7)
        self.topLengthProfileEntry.set_alignment(xalign=0.5)
        self.topLengthProfileEntry.set_halign(Gtk.Align.CENTER)
        self.topLengthProfileEntry.set_valign(Gtk.Align.START)

        self.add_overlay(self.topLengthProfileEntry)

        self.hboxLeftAngleProfile = Gtk.HBox(can_focus=False)
        self.hboxLeftAngleProfile.set_halign(Gtk.Align.START)
        self.hboxLeftAngleProfile.set_valign(Gtk.Align.CENTER)

        self.varLeftAngleProfileLabel = Gtk.Label(label='β\u2081',can_focus=False)
        self.varLeftAngleProfileLabel.set_name('labelIdicatorsEntryWithNumpadManualWidget')        

        self.leftAngleProfileEntry = EntryNumpad(self,
                                                 label= 'entryLeftAngle',
                                                 h_align_entry= myAlign.START,
                                                 v_align_entry= myAlign.CENTER,                                                 
                                                 h_align_bubbleNumpad=Gtk.ArrowType.RIGHT,
                                                 v_align_bubbleNumpad=Gtk.ArrowType.DOWN,
                                                 num_int_digits=3,
                                                 num_decimal_digits=1,
                                                 init_value=self.lefTipAngle                                                                                     
                                                 )
        self.leftAngleProfileEntry.set_name('entryWithNumpadManualWidget')
        self.leftAngleProfileEntry.set_can_focus(False)
        self.leftAngleProfileEntry.set_max_length(7)
        self.leftAngleProfileEntry.set_alignment(xalign=0.5)
        self.hboxLeftAngleProfile.pack_start(self.varLeftAngleProfileLabel,True,True,0) 
        self.hboxLeftAngleProfile.pack_start(self.leftAngleProfileEntry,True,True,0)       
        self.add_overlay(self.hboxLeftAngleProfile)
     
        self.bottomLengthProfileEntry = EntryNumpad(self,
                                                    label='entryBottomLength',
                                                    h_align_entry= myAlign.CENTER,
                                                    v_align_entry= myAlign.END,                                                    
                                                    h_align_bubbleNumpad=Gtk.ArrowType.RIGHT,
                                                    v_align_bubbleNumpad=Gtk.ArrowType.UP,
                                                    num_int_digits=4,
                                                    num_decimal_digits=1,
                                                    init_value=self.bottomLengthProfile
                                                    )                                               
        self.bottomLengthProfileEntry.set_name('entryWithNumpadManualWidget')
        self.bottomLengthProfileEntry.set_max_length(7)
        self.bottomLengthProfileEntry.set_alignment(xalign=0.5)
        self.bottomLengthProfileEntry.set_halign(Gtk.Align.CENTER)
        self.bottomLengthProfileEntry.set_valign(Gtk.Align.END)
        self.add_overlay(self.bottomLengthProfileEntry)  

        self.hboxRightAngleProfile = Gtk.HBox(can_focus=False)
        self.hboxRightAngleProfile.set_halign(Gtk.Align.END)
        self.hboxRightAngleProfile.set_valign(Gtk.Align.CENTER)

        self.varRightAngleProfileLabel = Gtk.Label(label='β\u2082',can_focus=False)
        self.varRightAngleProfileLabel.set_name('labelIdicatorsEntryWithNumpadManualWidget')  
     
        self.rightAngleProfileEntry = EntryNumpad(self,
                                                  label='entryRightAngle',
                                                  h_align_entry= myAlign.END,
                                                  v_align_entry= myAlign.CENTER,                                                  
                                                  h_align_bubbleNumpad=Gtk.ArrowType.LEFT,
                                                  v_align_bubbleNumpad=Gtk.ArrowType.DOWN,
                                                  num_int_digits=3,
                                                  num_decimal_digits=1,
                                                  init_value=self.rightTipAngle                                                  
                                                  )                                               
        self.rightAngleProfileEntry.set_name('entryWithNumpadManualWidget')
        self.rightAngleProfileEntry.set_can_focus(False)
        self.rightAngleProfileEntry.set_max_length(7)
        self.rightAngleProfileEntry.set_alignment(xalign=0.5)
        self.hboxRightAngleProfile.add(self.rightAngleProfileEntry)
        self.hboxRightAngleProfile.pack_start(self.varRightAngleProfileLabel,True,True,0)
        self.add_overlay(self.hboxRightAngleProfile)     

        self.hboxHeightProfile = Gtk.HBox(can_focus=False)
        self.hboxHeightProfile.set_halign(Gtk.Align.START)
        self.hboxHeightProfile.set_valign(Gtk.Align.END)

        self.varHeightProfileLabel = Gtk.Label(label='h',can_focus=False)
        self.varHeightProfileLabel.set_name('labelIdicatorsEntryWithNumpadManualWidget')

        self.HeightProfileEntry = EntryNumpad(self,
                                                  label='entryHeightProfile',
                                                  h_align_entry= myAlign.START,
                                                  v_align_entry= myAlign.END,                                                  
                                                  h_align_bubbleNumpad=Gtk.ArrowType.RIGHT,
                                                  v_align_bubbleNumpad=Gtk.ArrowType.UP,
                                                  num_int_digits=3,
                                                  num_decimal_digits=1,
                                                  init_value=self.heightProfile                                                  
                                                  )                                               
        self.HeightProfileEntry.set_name('entryWithNumpadManualWidget')
        self.HeightProfileEntry.set_can_focus(True)
        self.HeightProfileEntry.set_max_length(7)
        self.HeightProfileEntry.set_alignment(xalign=0.5)
        self.hboxHeightProfile.add(self.varHeightProfileLabel)
        self.hboxHeightProfile.pack_start(self.HeightProfileEntry,True,True,0)
        self.add_overlay(self.hboxHeightProfile) 

        self.hboxNumberOfCuts = Gtk.HBox(can_focus=False)
        self.hboxNumberOfCuts.set_halign(Gtk.Align.END)
        self.hboxNumberOfCuts.set_valign(Gtk.Align.END)

        self.varNumberOfCutsLabel = Gtk.Label(label='u',can_focus=False)
        self.varNumberOfCutsLabel.set_name('labelIdicatorsEntryWithNumpadManualWidget')

        self.NumberOfCutsEntry = EntryNumpad(self,
                                                  label='entryNumberOfCuts',
                                                  h_align_entry= myAlign.END,
                                                  v_align_entry= myAlign.MIDDLE_END,                                                  
                                                  h_align_bubbleNumpad=Gtk.ArrowType.LEFT,
                                                  v_align_bubbleNumpad=Gtk.ArrowType.UP,
                                                  num_int_digits=3,
                                                  num_decimal_digits=0,
                                                  init_value=self.numberOfCuts                                                
                                                  )                                               
        self.NumberOfCutsEntry.set_name('entryWithNumpadManualWidget')
        self.NumberOfCutsEntry.set_can_focus(True)
        self.NumberOfCutsEntry.set_max_length(7)
        self.NumberOfCutsEntry.set_alignment(xalign=0.5)
        self.hboxNumberOfCuts.add(self.NumberOfCutsEntry)
        self.hboxNumberOfCuts.pack_start(self.varNumberOfCutsLabel,True,True,0) 
        self.add_overlay(self.hboxNumberOfCuts)

        self.hboxTimeOutDisk = Gtk.HBox(can_focus=False)
        self.hboxTimeOutDisk.set_halign(Gtk.Align.END)
        self.hboxTimeOutDisk.set_valign(Gtk.Align.END)

        self.varTimeOutDiskLabel = Gtk.Label(label='s',can_focus=False)
        self.varTimeOutDiskLabel.set_name('labelIdicatorsEntryWithNumpadManualWidget')

        self.TimeOutDiskEntry = EntryNumpad(self,
                                                  label='entryTimeOutDisk',
                                                  h_align_entry= myAlign.END,
                                                  v_align_entry= myAlign.END,                                                  
                                                  h_align_bubbleNumpad=Gtk.ArrowType.LEFT,
                                                  v_align_bubbleNumpad=Gtk.ArrowType.UP,
                                                  num_int_digits=3,
                                                  num_decimal_digits=1,
                                                  init_value=self.timeOutDisk                                                                                           
                                                  )                                               
        self.TimeOutDiskEntry.set_name('entryWithNumpadManualWidget')
        self.TimeOutDiskEntry.set_can_focus(True)
        self.TimeOutDiskEntry.set_max_length(7)
        self.TimeOutDiskEntry.set_alignment(xalign=0.5)
        self.hboxTimeOutDisk.add(self.TimeOutDiskEntry)
        self.hboxTimeOutDisk.pack_start(self.varTimeOutDiskLabel,True,True,0)
        self.add_overlay(self.hboxTimeOutDisk)

        self.FbPosEntry = EntryNumpad(self,
                                                  label='fbPos',
                                                  h_align_entry= myAlign.END,
                                                  v_align_entry= myAlign.START,                                                  
                                                  h_align_bubbleNumpad=Gtk.ArrowType.LEFT,
                                                  v_align_bubbleNumpad=Gtk.ArrowType.UP,
                                                  num_int_digits=4,
                                                  num_decimal_digits=1,
                                                  init_value=0                                                                                            
                                                  )                                               
        self.FbPosEntry.set_name('entryWithNumpadManualWidget')
        self.FbPosEntry.set_can_focus(False)
        self.FbPosEntry.set_max_length(7)
        self.FbPosEntry.set_alignment(xalign=0.5)
        self.FbPosEntry.set_halign(Gtk.Align.END)
        self.FbPosEntry.set_valign(Gtk.Align.START)
        self.add_overlay(self.FbPosEntry)        


    def set_lefTipAngle(self,angle):
        self.lefTipAngle = angle    

    def get_leftAngleProfile(self):
        return self.lefTipAngle    

    def get_leftAngleProfileEntry(self):
        return self.leftAngleProfileEntry
    
    def get_HeightProfileEntry(self):
        return self.HeightProfileEntry

    def set_rightTipAngle(self,angle):
        self.rightTipAngle = angle  
    
    def get_rightAngleProfile(self):
        return self.rightTipAngle

    def get_rightAngleProfileEntry(self):
        return self.rightAngleProfileEntry

    def set_topLengthProfile(self,length):
        self.topLengthProfile = length  

    def get_topLengthProfile(self):
        return self.topLengthProfile      

    def set_bottomLengthProfile(self,length):
        self.bottomLengthProfile = length 

    def get_bottomLengthProfile(self):
        return self.bottomLengthProfile

    def set_heightProfile(self,length):
        self.heightProfile = length

    def get_heightProfile(self):
        return self.heightProfile

    def set_FbPos(self,length):
        self.FbPosEntry.set_text('%.*f'%(self.FbPosEntry.get_num_decimal_digits(),length))

    def set_timeOutDisk(self,time):
        self.timeOutDisk = time

    def get_timeOutDisk(self):
        return self.timeOutDisk
    
    def set_numberOfCuts(self,cuts):
        self.numberOfCuts = cuts
        self.NumberOfCutsEntry.set_text('%.*f'%(self.NumberOfCutsEntry.get_num_decimal_digits(),self.numberOfCuts))

    def get_numberOfCuts(self):
        return self.numberOfCuts

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
            font-size: """+ str(int(PADDING_LINE*0.6)) +"""px;
            background-color: white;
            caret-color:      white;
            border-width:     4px;
            box-shadow: 5px 5px 5px 5px rgba(0, 0, 0, 0.5);
            border-radius: 2px;
        }

        #labelIdicatorsEntryWithNumpadManualWidget {
            font-size: """+ str(int(PADDING_LINE*0.6)) +"""px;
            color: white;
            text-shadow: 2px 2px 4px #000000;
        }
        """).encode()
        self.provider.load_from_data(css) 

        
        self.topLengthProfileEntry.set_size_request(width=LENGTH_WIDTH,height=int(PADDING_LINE)) 
        self.topLengthProfileEntry.set_margin_top(PADDING_LINE-self.topLengthProfileEntry.get_allocated_height()/2)

        self.leftAngleProfileEntry.set_size_request(width=LENGTH_WIDTH/2,height=int(PADDING_LINE)) 
        self.hboxLeftAngleProfile.set_margin_left(2.2*PADDING_LINE - 
                                                  self.leftAngleProfileEntry.get_allocated_width()/2 - 
                                                  self.varLeftAngleProfileLabel.get_allocated_width())
        self.hboxLeftAngleProfile.set_spacing(PADDING_LINE/8)
        
        self.bottomLengthProfileEntry.set_size_request(width=LENGTH_WIDTH,height=int(PADDING_LINE))
        self.bottomLengthProfileEntry.set_margin_bottom(PADDING_LINE-self.bottomLengthProfileEntry.get_allocated_height()/2)        

        self.rightAngleProfileEntry.set_size_request(width=LENGTH_WIDTH/2,height=int(PADDING_LINE)) 
        self.hboxRightAngleProfile.set_margin_right(2.2*PADDING_LINE - 
                                                    self.rightAngleProfileEntry.get_allocated_width()/2 -
                                                    self.varRightAngleProfileLabel.get_allocated_width())
        self.hboxRightAngleProfile.set_spacing(PADDING_LINE/8)

        self.HeightProfileEntry.set_size_request(width=LENGTH_WIDTH/2,height=int(PADDING_LINE)) 
        self.hboxHeightProfile.set_margin_left(2.2*PADDING_LINE - 
                                               self.HeightProfileEntry.get_allocated_width()/2 - 
                                               self.varHeightProfileLabel.get_allocated_width())
        self.hboxHeightProfile.set_margin_bottom(PADDING_LINE-self.HeightProfileEntry.get_allocated_height()/2)       
        self.hboxHeightProfile.set_spacing(PADDING_LINE/8)

        self.NumberOfCutsEntry.set_size_request(width=LENGTH_WIDTH/2,height=int(PADDING_LINE))
        self.hboxNumberOfCuts.set_margin_right(2.2*PADDING_LINE - 
                                               self.NumberOfCutsEntry.get_allocated_width()/2 -
                                               self.varNumberOfCutsLabel.get_allocated_width())
        self.hboxNumberOfCuts.set_margin_bottom(HEIGHT/4 + PADDING_LINE/2-self.NumberOfCutsEntry.get_allocated_height()/2)
        self.hboxNumberOfCuts.set_spacing(PADDING_LINE/8)

        self.TimeOutDiskEntry.set_size_request(width=LENGTH_WIDTH/2,height=int(PADDING_LINE))
        self.hboxTimeOutDisk.set_margin_right(2.2*PADDING_LINE - 
                                              self.TimeOutDiskEntry.get_allocated_width()/2 - 
                                              self.varTimeOutDiskLabel.get_allocated_width())
        self.hboxTimeOutDisk.set_margin_bottom(PADDING_LINE-self.TimeOutDiskEntry.get_allocated_height()/2)
        self.hboxTimeOutDisk.set_spacing(PADDING_LINE/8)

        self.FbPosEntry.set_size_request(width=int(LENGTH_WIDTH*0.65),height=int(PADDING_LINE))
        self.FbPosEntry.set_margin_right(2.2*PADDING_LINE - 
                                        self.FbPosEntry.get_allocated_width()/1.75)
        self.FbPosEntry.set_margin_top(PADDING_LINE-self.FbPosEntry.get_allocated_height()/2)
        


        ctx.set_source_rgb(0.23, 0.61, 0.84)
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
        ctx.set_source_rgb(0.06, 0.10, 0.29)
        ctx.stroke()

        if self.focusTopLengthProfile:
            ctx.move_to(WIDTH/2 - WIDTH_ARROW/4, HEIGHT/2 + HEIGHT_ARROW/2)
            ctx.line_to(WIDTH/2 - WIDTH_ARROW/4, HEIGHT/2)
            ctx.line_to(WIDTH/2 - WIDTH_ARROW/2, HEIGHT/2)
            ctx.line_to(WIDTH/2, HEIGHT/2 - HEIGHT_ARROW/2)
            ctx.line_to(WIDTH/2  + WIDTH_ARROW/2, HEIGHT/2)
            ctx.line_to(WIDTH/2  + WIDTH_ARROW/4, HEIGHT/2)
            ctx.line_to(WIDTH/2  + WIDTH_ARROW/4, HEIGHT/2 + HEIGHT_ARROW/2)
            ctx.set_source_rgb(0.96, 1.00, 0.97)
            ctx.close_path()
            ctx.fill_preserve()
            ctx.set_source_rgb(0.42, 0.46, 0.49)
            ctx.stroke()   

        if self.focusBottomLengthProfile:
            ctx.move_to(WIDTH/2 - WIDTH_ARROW/4, HEIGHT/2 - HEIGHT_ARROW/2)
            ctx.line_to(WIDTH/2 - WIDTH_ARROW/4, HEIGHT/2)
            ctx.line_to(WIDTH/2 - WIDTH_ARROW/2, HEIGHT/2)
            ctx.line_to(WIDTH/2, HEIGHT/2 + HEIGHT_ARROW/2)
            ctx.line_to(WIDTH/2  + WIDTH_ARROW/2, HEIGHT/2)
            ctx.line_to(WIDTH/2  + WIDTH_ARROW/4, HEIGHT/2)
            ctx.line_to(WIDTH/2  + WIDTH_ARROW/4, HEIGHT/2 - HEIGHT_ARROW/2)
            ctx.set_source_rgb(0.96, 1.00, 0.97)
            ctx.close_path()
            ctx.fill_preserve()
            ctx.set_source_rgb(0.42, 0.46, 0.49)
            ctx.stroke()              

        if self.lefTipAngle <= 90:
            ctx.move_to(X_OFFSET, Y_OFFSET - PADDING_LINE)
            ctx.line_to(X_OFFSET, PADDING_LINE) 
        else:
            ctx.move_to(math.tan(math.radians(90+self.lefTipAngle))*HEIGHT_PROF+X_OFFSET, Y_OFFSET - PADDING_LINE)
            ctx.line_to(math.tan(math.radians(90+self.lefTipAngle))*HEIGHT_PROF+X_OFFSET, PADDING_LINE)  

        ctx.line_to(((WIDTH-2*X_OFFSET) - LENGTH_WIDTH)/2 + X_OFFSET, PADDING_LINE)

        if self.rightTipAngle <= 90:
            ctx.move_to(WIDTH-X_OFFSET, Y_OFFSET - PADDING_LINE)
            ctx.line_to(WIDTH-X_OFFSET, PADDING_LINE) 
        else:
            ctx.move_to(WIDTH-math.tan(math.radians(90+self.rightTipAngle))*HEIGHT_PROF-X_OFFSET, Y_OFFSET - PADDING_LINE)
            ctx.line_to(WIDTH-math.tan(math.radians(90+self.rightTipAngle))*HEIGHT_PROF-X_OFFSET, PADDING_LINE)

        ctx.line_to(WIDTH- X_OFFSET - ((WIDTH-2*X_OFFSET) - LENGTH_WIDTH)/2, PADDING_LINE) 

        if self.lefTipAngle <= 90:
            ctx.move_to(math.tan(math.radians(90-self.lefTipAngle))*HEIGHT_PROF+X_OFFSET, HEIGHT_PROF + Y_OFFSET + PADDING_LINE)   
            ctx.line_to(math.tan(math.radians(90-self.lefTipAngle))*HEIGHT_PROF+X_OFFSET, HEIGHT - PADDING_LINE) 
        else:
            ctx.move_to(X_OFFSET, HEIGHT_PROF + Y_OFFSET + PADDING_LINE)   
            ctx.line_to(X_OFFSET, HEIGHT - PADDING_LINE)             
            
        ctx.line_to(WIDTH/2 - LENGTH_WIDTH/2,HEIGHT - PADDING_LINE)

        if self.rightTipAngle <= 90:
            ctx.move_to(WIDTH-math.tan(math.radians(90-self.rightTipAngle))*HEIGHT_PROF-X_OFFSET,HEIGHT_PROF + Y_OFFSET + PADDING_LINE)
            ctx.line_to(WIDTH-math.tan(math.radians(90-self.rightTipAngle))*HEIGHT_PROF-X_OFFSET, HEIGHT - PADDING_LINE) 
        else:
            ctx.move_to(WIDTH-X_OFFSET,HEIGHT_PROF + Y_OFFSET + PADDING_LINE)
            ctx.line_to(WIDTH-X_OFFSET, HEIGHT - PADDING_LINE)             

        ctx.line_to(WIDTH/2 + LENGTH_WIDTH/2,  HEIGHT - PADDING_LINE)

        ctx.set_source_rgb(0.96, 1.00, 0.97)
        ctx.set_line_width(4)
        ctx.set_dash([14,6])
        
        ctx.stroke()                         

    def on_button_press(self, widget, event):

        height = widget.get_allocated_height()
        width = widget.get_allocated_width()

        widget.grab_focus()

        HEIGHT = height 
        WIDTH = width 
        HEIGHT_PROF = height*self.height_prof 
        HEIGHT_ARROW =  HEIGHT_PROF*self.height_arrow
        WIDTH_ARROW = HEIGHT_ARROW/self.width_arrow 

        if event.get_button()[1] == 1:
                   
            if event.x >= (WIDTH - WIDTH_ARROW)/2 and event.x <= (WIDTH + WIDTH_ARROW)/2: 
                if event.y >= (HEIGHT - HEIGHT_ARROW)/2 and event.y <= (HEIGHT + HEIGHT_ARROW)/2:
                    self.focusTopLengthProfile = not(self.focusTopLengthProfile)
                    self.focusBottomLengthProfile = not(self.focusTopLengthProfile)                                                                           
            self.queue_draw()

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
            if widget.get_parent().get_h_align_entry() == myAlign.START:
                if widget.get_h_align() == Gtk.ArrowType.RIGHT:
                    allocation.x = PADDING_LINE + LENGTH_WIDTH/2                
            elif widget.get_parent().get_h_align_entry() == myAlign.CENTER:
                if widget.get_h_align() == Gtk.ArrowType.RIGHT:
                    allocation.x = WIDTH/2 + LENGTH_WIDTH/2
                elif widget.get_h_align() == Gtk.ArrowType.LEFT:
                    allocation.x = WIDTH/2 - LENGTH_WIDTH/2 - WIDTH_BUBBLE_NUMPAD 
            elif widget.get_parent().get_h_align_entry() == myAlign.END:
                if widget.get_h_align() == Gtk.ArrowType.LEFT:
                    allocation.x = WIDTH - PADDING_LINE - LENGTH_WIDTH/2 - WIDTH_BUBBLE_NUMPAD           

            if widget.get_parent().get_v_align_entry() == myAlign.START:
                if widget.get_v_align() == Gtk.ArrowType.DOWN:
                    allocation.y = PADDING_LINE
            elif widget.get_parent().get_v_align_entry() == myAlign.CENTER:
                if widget.get_v_align() == Gtk.ArrowType.UP:
                    allocation.y = HEIGHT/2 - HEIGHT_BUBBLE_NUMPAD
                if widget.get_v_align() == Gtk.ArrowType.DOWN:
                    allocation.y = HEIGHT/2
            elif widget.get_parent().get_v_align_entry() == myAlign.END:
                if widget.get_v_align() == Gtk.ArrowType.UP:                    
                    allocation.y = HEIGHT - PADDING_LINE - HEIGHT_BUBBLE_NUMPAD
            elif widget.get_parent().get_v_align_entry() == myAlign.MIDDLE_END:
                if widget.get_v_align() == Gtk.ArrowType.UP:                    
                    allocation.y = HEIGHT - (HEIGHT/4 + PADDING_LINE/2) - HEIGHT_BUBBLE_NUMPAD
            allocation.width = WIDTH_BUBBLE_NUMPAD
            allocation.height = HEIGHT_BUBBLE_NUMPAD 
            return True
        else:
            return False
        
        
    def on_update_value(self,widget,entry, value):
        if entry == self.leftAngleProfileEntry or entry == self.rightAngleProfileEntry:
            set_tipAngle = lambda e,v: self.set_lefTipAngle(v) if e == self.leftAngleProfileEntry else self.set_rightTipAngle(v)
            get_tipAngle = lambda e: self.lefTipAngle if e == self.leftAngleProfileEntry else self.rightTipAngle
            if entry.get_text():
                if value > self.max_angle: 
                    set_tipAngle(entry,self.max_angle)
                    entry.set_text('%.*f'%(entry.get_num_decimal_digits(),self.max_angle))
                elif value < self.min_angle:
                    set_tipAngle(entry,self.min_angle)                
                    entry.set_text('%.*f'%(entry.get_num_decimal_digits(),self.min_angle))
                else: 
                    set_tipAngle(entry,value)
            else:
                entry.set_text('%.*f'%(entry.get_num_decimal_digits(),get_tipAngle(entry)))   
        elif entry == self.topLengthProfileEntry or entry == self.bottomLengthProfileEntry:            
            set_sideLength = lambda e,v: self.set_topLengthProfile(v) if e == self.topLengthProfileEntry else self.set_bottomLengthProfile(v)
            get_sideLength = lambda e: self.topLengthProfile if e == self.topLengthProfileEntry else self.bottomLengthProfile
            if entry.get_text():
                if value > self.max_length:
                    set_sideLength(entry,self.max_length)
                    entry.set_text('%.*f'%(entry.get_num_decimal_digits(),self.max_length))
                elif value < self.min_length:
                    set_sideLength(entry,self.min_length)
                    entry.set_text('%.*f'%(entry.get_num_decimal_digits(),self.min_length))
                else:
                    set_sideLength(entry,value)
            else:
                entry.set_text('%.*f'%(entry.get_num_decimal_digits(),get_sideLength(entry)))
        elif entry == self.HeightProfileEntry:
            if value > self.max_height:
                value = self.max_height
            self.set_heightProfile(value)
            self.dxfViewer.emit('clear-dxf')
            entry.set_text('%.*f'%(entry.get_num_decimal_digits(),self.heightProfile))
        elif entry == self.TimeOutDiskEntry:
            self.set_timeOutDisk(value)
            entry.set_text('%.*f'%(entry.get_num_decimal_digits(),self.timeOutDisk))
        elif entry == self.NumberOfCutsEntry:
            self.set_numberOfCuts(value)
            entry.set_text('%.*f'%(entry.get_num_decimal_digits(),self.numberOfCuts))

        self.topLengthProfile,self.bottomLengthProfile = self.updateLengths()

        if any([self.topLengthProfile < self.min_length,self.bottomLengthProfile < self.min_length]):
            self.bottomLengthProfileEntry.get_style_context().add_class('entry-font-red')
            self.topLengthProfileEntry.get_style_context().add_class('entry-font-red')
            self.HeightProfileEntry.get_style_context().add_class('entry-font-red')
            self.leftAngleProfileEntry.get_style_context().add_class('entry-font-red')
            self.rightAngleProfileEntry.get_style_context().add_class('entry-font-red')
            self.emit('bad-value',True)
        else:
            entry.get_style_context().remove_class('entry-font-red')
            self.bottomLengthProfileEntry.get_style_context().remove_class('entry-font-red')
            self.topLengthProfileEntry.get_style_context().remove_class('entry-font-red')
            self.HeightProfileEntry.get_style_context().remove_class('entry-font-red')
            self.leftAngleProfileEntry.get_style_context().remove_class('entry-font-red')
            self.rightAngleProfileEntry.get_style_context().remove_class('entry-font-red')
            self.emit('bad-value',False)
                                                                        
        self.queue_draw()  

    def updateLengths(self): 
        if self.focusTopLengthProfile == True:
            bottomLengthProfile = self.topLengthProfile - self.heightProfile*(1/math.tan(math.radians(self.lefTipAngle))+1/math.tan(math.radians(self.rightTipAngle)))
            bottomLengthProfileStr = '%.*f'%(self.bottomLengthProfileEntry.get_num_decimal_digits(),bottomLengthProfile)
            self.bottomLengthProfile = float(bottomLengthProfileStr)
            self.bottomLengthProfileEntry.set_text(bottomLengthProfileStr)
        elif self.focusBottomLengthProfile == True:
            topLengthProfile = self.bottomLengthProfile + self.heightProfile*(1/math.tan(math.radians(self.lefTipAngle))+1/math.tan(math.radians(self.rightTipAngle)))
            topLengthProfileStr = '%.*f'%(self.topLengthProfileEntry.get_num_decimal_digits(),topLengthProfile)
            self.topLengthProfile = float(topLengthProfileStr)
            self.topLengthProfileEntry.set_text(topLengthProfileStr)

        return self.topLengthProfile,self.bottomLengthProfile
    
    def set_dxfViewer(self,dxfViewer):
        self.dxfViewer = dxfViewer


