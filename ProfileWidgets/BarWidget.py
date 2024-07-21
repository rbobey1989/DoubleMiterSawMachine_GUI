import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import math, cairo

class BarWidget(Gtk.DrawingArea):
    def __init__(self):
        super(BarWidget,self).__init__()
        
        self.bar_length = None
        self.cuts = []

        self.connect("draw", self.on_draw)    

    def update_bar(self, data):
        cuts = []
        try:
            self.bar_length = int(data[0][4])
            for row in data[1:]:
                do_cut = row[0]
                distance = int(row[6]) / self.bar_length
                angle1 = int(row[7])
                angle2 = int(row[8])
                cuts.append((do_cut, distance, angle1, angle2))
            self.cuts = cuts
        except:
            self.bar_length = None
            self.cuts = []
        self.queue_draw()
    

    def on_draw(self, widget, cr):
        # Get the width and height of the drawing area
        width = self.get_allocated_width() 
        height = self.get_allocated_height()

        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_join(cairo.LINE_JOIN_ROUND) 

        if self.bar_length == None and self.cuts == []:
        # Draw the Complete bar whithout any cuts
            cr.rectangle(0, 0, width, height)
            cr.set_source_rgb(0.23, 0.84, 0.61)
            cr.fill() 
            cr.set_source_rgb(0.06, 0.10, 0.29)
            cr.set_line_width(3)
            cr.rectangle(0, 0, width, height)
            cr.stroke()

            return          

        # Draw the cuts
        accumulated_length = 0
        last_angle2 = 0
        for do_cut, distance, angle1, angle2 in self.cuts:
            x = accumulated_length
            accumulated_length += distance * width
            cut_width_angle1 = math.tan(math.radians(90 - angle1)) * height
            cut_width_angle2 = math.tan(math.radians(90 - angle2)) * height

            if last_angle2 < 90:
                if angle1 > 90:
                    x = x + cut_width_angle1
                    accumulated_length = accumulated_length + cut_width_angle1

            if last_angle2 > 90:
                if angle1 < 90:
                    x = x - cut_width_angle2
                    accumulated_length = accumulated_length - cut_width_angle2  

            last_angle2 = angle2

            if angle1 <= 90:
                y0 = 0
                y1  = height
                x0 = x
                x1 = x + cut_width_angle1
            else:
                y0 = 0
                y1 = height
                x0 = x - cut_width_angle1
                x1 = x

            if angle2 <= 90:
                y2 = height
                y3 = 0
                x2 = accumulated_length - cut_width_angle2
                x3 = accumulated_length
            else:
                y2 = height
                y3 = 0
                x2 = accumulated_length
                x3 = accumulated_length + cut_width_angle2

            # Create a new, smaller parallelogram for the fill
            cr.new_path()
            cr.move_to(x0 , y0)
            cr.line_to(x1 , y1)
            cr.line_to(x2, y2)
            cr.line_to(x3, y3)
            cr.close_path()


            # Fill the smaller parallelogram with the appropriate color
            if do_cut:
                # Set the color to red if the cut is to be made
                cr.set_source_rgb(0.23, 0.61, 0.84)
            else:
                # Set the color to green if the cut is not to be made
                cr.set_source_rgb(0.84,0.61, 0.23)
            cr.fill()  # Fill the parallelogram

            # Draw the border
            cr.new_path()
            cr.move_to(x0, y0)            
            cr.line_to(x1, y1)
            cr.line_to(x2, y2)
            cr.line_to(x3, y3)
            cr.close_path()

            cr.set_source_rgb(0.06, 0.10, 0.29) 
            cr.set_line_width(3)  # Set the line width as needed
            cr.stroke()  # Draw the border

        if accumulated_length < width:
            cr.new_path()
            try:
                cr.move_to(x3, y3)
                cr.line_to(width, 0)
                cr.line_to(width, height)
                cr.line_to(x2, y2)
            except:
                cr.move_to(0, 0)
                cr.line_to(width, 0)
                cr.line_to(width, height)
                cr.line_to(0, height)
            cr.close_path()
            cr.set_source_rgb(0.23, 0.84, 0.61)
            cr.fill_preserve()
            cr.set_source_rgb(0.06, 0.10, 0.29)
            cr.set_line_width(3)
            cr.stroke()

# class MainWindow(Gtk.Window):
#     def __init__(self):
#         super().__init__(title="Bar Widget Demo")
#         self.set_default_size(1280, 50)
#         # Create a new BarWidget with some cuts

#         self.bar_widget = BarWidget()

#         self.add(self.bar_widget)

        



#         # Add the BarWidget to the window

#     def update_bar(self, data):
#         self.bar_widget.update_bar(data)


# # Create a new MainWindow and show it
# window = MainWindow()
# window.connect("destroy", Gtk.main_quit)
# window.show_all()
# window.update_bar([[True, 'Profile2', '6500', '', '', '', '', ''], 
#                                 [True, '', '', '1', '242', '90', '45', 'Description9'], 
#                                 [True, '', '', '1', '1000', '135', '90', 'Description10'], 
#                                 [True, '', '', '1', '1625', '135', '135', 'Description11'], 
#                                 [True, '', '', '1', '1000', '45', '45', 'Description12']])
# # Call update_bar every second
# GLib.timeout_add_seconds(1, window.update_bar, [])

# Gtk.main()