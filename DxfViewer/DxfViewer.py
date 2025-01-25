import ezdxf
from ezdxf import bbox
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration
import matplotlib.pyplot as plt
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas

from DxfDataBase.DxfDataBase import DxfDataBase
from ProfileWidgets.ManualProfileCutWidget import ManualProfileCutWidget
from CSVViewerWidget.CSVViewerWidget import CSVViewerWidget

import math

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk

class DxfViewer(Gtk.Box):
    __gsignals__ = {
        "update-dimensions-dxf-manual-widget": (GObject.SignalFlags.RUN_FIRST, None, (ManualProfileCutWidget, float, float)),
        "update-dimensions-dxf-csv-viewer-widget": (GObject.SignalFlags.RUN_FIRST, None, (CSVViewerWidget, float, float)),
        "clear-dxf": (GObject.SignalFlags.RUN_FIRST, None, ())
    }
    def __init__(self, hide_buttons=False, hide_edits=False, manual_profile_cut_widget=None, csv_viewer_widget=None):
        super(DxfViewer, self).__init__()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('css_styles_sheets/DXFViewerstyle.css')
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)        


        self.hide_buttons = hide_buttons
        self.hide_edits = hide_edits


        self.width_profile = 0
        self.height_profile = 0

        self.manual_profile_cut_widget = manual_profile_cut_widget
        self.csv_viewer_widget = csv_viewer_widget

        if self.manual_profile_cut_widget != None:
            self.connect("update-dimensions-dxf-manual-widget", self.on_update_dimensions_dxf_in_manual_widget)
            self.connect("clear-dxf", self.on_clear_dxf)
        
        if self.csv_viewer_widget != None:
            self.connect("update-dimensions-dxf-csv-viewer-widget", self.on_update_dimensions_dxf_in_csv_widget)
            self.connect("clear-dxf", self.on_clear_dxf)

        self.added_entities = []  # Initialize the list of added entities
        self.frame_percent_offset = 0.125

        # Create a combobox to select Manufacturers
        manufacturer_combobox_label = Gtk.Label(label="Manufacturers", name="DXFViewerLabel")
        self.manufacturer_combobox = Gtk.ComboBoxText(name="DXFViewerCombobox")

        # Create a combobox to select Sets
        set_combobox_label = Gtk.Label(label="Sets", name="DXFViewerLabel")
        self.set_combobox = Gtk.ComboBoxText(name="DXFViewerCombobox")

        # Create a combobox to select code of DXF files
        code_combobox_label = Gtk.Label(label="DXF Files", name="DXFViewerLabel")
        self.code_combobox = Gtk.ComboBoxText(name="DXFViewerCombobox")

        self.manufacturer_combobox.connect("changed", self.on_manufacturer_changed)
        self.set_combobox.connect("changed", self.on_set_changed)
        self.code_combobox.connect("changed", self.on_code_changed)

        self.update_manufacturer_combo()

        # Create a vertical box layout and add the labels
        vbox_labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox_labels.pack_start(manufacturer_combobox_label, True, False, 0)
        vbox_labels.pack_start(set_combobox_label, True, False, 0)
        vbox_labels.pack_start(code_combobox_label, True, False, 0)

        # Create a vertical box layout and add the comboboxes
        vbox_comboboxes = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox_comboboxes.pack_start(self.manufacturer_combobox, False,False, 0)
        vbox_comboboxes.pack_start(self.set_combobox, False, False, 0)
        vbox_comboboxes.pack_start(self.code_combobox, False, False, 0)

        # Create a horizontal box layout and add the labels and comboboxes
        hbox_labels_comboboxes = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox_labels_comboboxes.pack_start(vbox_labels, False, False, 0)
        hbox_labels_comboboxes.pack_start(vbox_comboboxes, True, True, 0)

        # Create a new DXF document.
        self.doc = ezdxf.new()
        self.doc_to_show = None

        # Create a new Matplotlib figure and a new subplot
        self.fig, self.ax = plt.subplots()

        # Create a rendering context.
        self.ctx = RenderContext(self.doc)

        # Create a MatplotlibBackend object.
        self.out = MatplotlibBackend(self.ax)

        self.config = Configuration().defaults()

        self.config = self.config.with_changes(
            min_lineweight=2
            )      

        # Create a new Matplotlib canvas and add it to the GTK window
        self.canvas = FigureCanvas(self.fig)

        # Create 'open','rot' and 'mirror' buttons
        # open_button = Gtk.Button(label="Open")
        self.rot_rigth_button = Gtk.Button(label="RotR", name="DXFViewerButton")
        self.rot_left_button = Gtk.Button(label="RotL", name="DXFViewerButton")
        self.x_inv_button = Gtk.Button(label="XInv", name="DXFViewerButton")
        self.y_inv_button = Gtk.Button(label="YInv", name="DXFViewerButton")
        self.clear_button = Gtk.Button(label="Clear", name="DXFViewerButton")

        # Connect the buttons to their respective callback functions
        # open_button.connect("clicked", self.on_open_clicked)
        self.rot_rigth_button.connect("clicked", self.on_rot_rigth_clicked)
        self.rot_left_button.connect("clicked", self.on_rot_left_clicked)
        self.x_inv_button.connect("clicked", self.on_x_invert)
        self.y_inv_button.connect("clicked", self.on_y_invert)
        self.clear_button.connect("clicked", self.on_clear_dxf)

        # Create a vertical box layout and add the canvas and buttons
        vboxcanvasbtns = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vboxcanvasbtns.pack_start(self.canvas, True, True, 0)
        hboxbtns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)

        if not self.hide_buttons:
            # hboxbtns.pack_start(open_button, False, False, 0)
            hboxbtns.pack_start(self.rot_rigth_button, False, False, 0)
            hboxbtns.pack_start(self.rot_left_button, False, False, 0)
            hboxbtns.pack_start(self.x_inv_button, False, False, 0)
            hboxbtns.pack_start(self.y_inv_button, False, False, 0)
            hboxbtns.pack_start(self.clear_button, False, False, 0)
        else:
            self.canvas.set_size_request( 400, -1)
        vboxcanvasbtns.pack_start(hboxbtns, False, False, 0)

        # Create a vertical box layout and add the labels,comboboxes,canvas and buttons
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        if not self.hide_edits:
            self.vbox.pack_start(hbox_labels_comboboxes, False, False, 0)

        self.vbox.pack_end(vboxcanvasbtns, True, True, 0)

        self.add(self.vbox)

        # Draw the frames
        self.draw_frames()

    def update_manufacturer_combo(self):
        # Create a new instance of DxfDataBase
        db = DxfDataBase()

        # Get all the manufacturers from the database
        manufacturers = db.get_all_manufacturers()
        for manufacturer in manufacturers:
            self.manufacturer_combobox.append_text(manufacturer[0])

        # Close the database connection
        db.close()

    def on_manufacturer_changed(self, combobox):
        # Create a new instance of DxfDataBase
        db = DxfDataBase()

        # Get the selected manufacturer
        manufacturer = combobox.get_active_text()

        # Get all the sets for the selected manufacturer
        sets = db.get_sets_by_manufacturer(manufacturer)
        self.set_combobox.remove_all()
        for set in sets:
            self.set_combobox.append_text(set[0])

        # Close the database connection
        db.close()

    def on_set_changed(self, combobox):
        # Create a new instance of DxfDataBase
        db = DxfDataBase()

        # Get the selected manufacturer
        manufacturer = self.manufacturer_combobox.get_active_text()

        # Get the selected set
        set = combobox.get_active_text()

        # Get all the DXF files for the selected set
        dxf_files = db.get_codes_by_manufacturer_and_set(manufacturer, set)
        self.code_combobox.remove_all()
        for dxf_file in dxf_files:
            self.code_combobox.append_text(dxf_file[0])

        # Close the database connection
        db.close()

    def on_code_changed(self, combobox):
        # Create a new instance of DxfDataBase
        db = DxfDataBase()

        # Get the selected manufacturer
        manufacturer = self.manufacturer_combobox.get_active_text()

        # Get the selected set
        set = self.set_combobox.get_active_text()

        # Get the selected code
        code = combobox.get_active_text()

        # Check if the manufacturer, set, and code are not None
        if manufacturer == None or set == None or code == None:
            return

        # Get the path of the DXF file
        path = db.get_dxf_file(manufacturer, set, code)

        # Close the database connection
        db.close()

        # Draw the DXF file
        self.draw_dxf(path)

    def update_frames(self):

        # Get the dimensions of the axes
        xmin, xmax = self.ax.get_xlim()
        ymin, ymax = self.ax.get_ylim()

        # Define Vertices of the Frame
        frame_vertices = [
            (xmin, ymax),
            (xmin, ymin),
            (xmax, ymin),
            (xmax, self.frame_percent_offset*ymax),
            (self.frame_percent_offset*xmax, self.frame_percent_offset*ymax),
            (self.frame_percent_offset*xmax, ymax),
            (xmin, ymax)
        ]

        # Create a hatch within the frame
        hatch = self.doc.modelspace().add_hatch(color=14)

        # Add a path to the hatch
        edge_path = hatch.paths.add_edge_path()
        for i in range(len(frame_vertices) - 1):
            edge_path.add_line(frame_vertices[i], frame_vertices[i + 1])

        # Set the pattern of the hatch
        hatch.set_pattern_fill(name='SOLID', scale=0.1, color=8)

        # Remove the ticks from the axes
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        # Remove the box around the plot
        self.ax.set_frame_on(False)

    def draw_frames(self):

        self.ax.clear()

        self.update_frames()

        # Render the entities in the modelspace
        Frontend(self.ctx, self.out,self.config).draw_layout(self.doc.modelspace(), finalize=True)

        # Force Matplotlib to redraw the figure immediately
        self.ax.figure.canvas.draw()

    def draw_dxf(self, filename):

        self.add_entities(filename)
        self.render_draw_and_emit_signals()

    def render_draw_and_emit_signals(self):
        
        #Render the entities in the modelspace
        Frontend(self.ctx, self.out, self.config).draw_layout(self.doc.modelspace(),finalize=False)

        # # Force Matplotlib to redraw the figure immediately
        self.ax.figure.canvas.draw()

        if self.manual_profile_cut_widget != None:
            self.emit("update-dimensions-dxf-manual-widget", self.manual_profile_cut_widget, self.width_profile, self.height_profile)
        
        if self.csv_viewer_widget != None:
            self.emit("update-dimensions-dxf-csv-viewer-widget", self.csv_viewer_widget, self.width_profile, self.height_profile)


    def add_entities(self, filename):
        # Load the new DXF file
        self.doc_to_show = ezdxf.readfile(filename)

        # Clear the current axes
        self.ax.clear()

        xmin, ymin, zmin =  self.doc_to_show.header["$EXTMIN"]
        xmax, ymax, zmax =  self.doc_to_show.header["$EXTMAX"]

        self.width_profile = (xmax - xmin)
        self.height_profile = (ymax - ymin)

        max_length = max(xmax - xmin, ymax - ymin)

        xmin /= max_length
        xmax /= max_length
        ymin /= max_length
        ymax /= max_length

        # Rotate and redraw the added entities
        for e in self.added_entities:
            # Remove the entity from the modelspace
            self.doc.modelspace().delete_entity(e)

        for entity in self.doc_to_show.modelspace():
            # Create a copy of the entity
            entity_copy = entity.copy()

            entity_copy.scale_uniform(0.8/max_length)

            entity_copy.translate(self.frame_percent_offset, self.frame_percent_offset, 0)

            # Change the color of the entity
            entity_copy.dxf.set('color', 10)

            self.doc.modelspace().add_entity(entity_copy)

            # Add the entity to the list of added entities
            self.added_entities.append(entity_copy)

  
    def clear_dxf(self):
        # Clear the current axes
        self.ax.clear()

        for e in self.added_entities:
            # Remove the entity from the modelspace
            self.doc.modelspace().delete_entity(e)

        
        if self.doc_to_show is not None:
            self.doc_to_show.modelspace().delete_all_entities()

        # Clear the list of added entities
        self.added_entities = []

        self.width_profile = 0
        self.height_profile = 0

        #Render the entities in the modelspace
        Frontend(self.ctx, self.out, self.config).draw_layout(self.doc.modelspace(),finalize=False)

        # Force Matplotlib to redraw the figure immediately
        self.ax.figure.canvas.draw()


    # def on_open_clicked(self, button):
    #     # Create a new instance of DxfDataBase
    #     db = DxfDataBase()

    #     # Get the selected manufacturer, set, and code
    #     manufacturer = self.manufacturer_combobox.get_active_text()
    #     set = self.set_combobox.get_active_text()
    #     code = self.code_combobox.get_active_text()

    #     # Check if the manufacturer, set, and code are not None
    #     if manufacturer == None or set == None or code == None:
    #         return

    #     # Get the path of the DXF file
    #     path = db.get_dxf_file(manufacturer, set, code)

    #     # Close the database connection
    #     db.close()

    #     # Draw the DXF file
    #     self.draw_dxf(path)

    def update_dxf(self, data):
        # Create a new instance of DxfDataBase
        db = DxfDataBase()

        try:
            manufacturer = data[0]
            set = data[1]
            code = data[2]
            rotation = data[3]
            if data[4] == '✔':
                x_invert = ('x', -1)
            else:
                x_invert = None

            if data[5] == '✔':
                y_invert = ('y', -1)
            else:
                y_invert = None    
        except:
            print("Error No DXF data to Show")

        # Check if the manufacturer, set, and code are not None
        if manufacturer == None or set == None or code == None:
            return
        
        # Get the path of the DXF file
        path = db.get_dxf_file(manufacturer, set, code)

        # Close the database connection
        db.close()

        #self.draw_dxf(path)
        self.add_entities(path)
        self.transform_entities(rotation)
        self.transform_entities(x_invert)
        self.transform_entities(y_invert)

        self.render_draw_and_emit_signals()
        
    def on_rot_rigth_clicked(self, button):

        if self.csv_viewer_widget != None:
            model, iter = self.csv_viewer_widget.get_active_row()

            if (model, iter) == (None, None):
                return

            value = model.get_value(iter, 13)

            value = int(value) - 90

            if value == -360:
                value = 0

            model.set_value(iter, 13, str(value))

        self.transform_entities("-90")
        self.render_draw_and_emit_signals()
            

    def on_rot_left_clicked(self, button):

        if self.csv_viewer_widget != None:
            model, iter = self.csv_viewer_widget.get_active_row()

            if (model, iter) == (None, None):
                return

            value = model.get_value(iter, 13)

            value = int(value) + 90

            if value == 360:
                value = 0

            model.set_value(iter, 13, str(value))

        self.transform_entities("90")
        self.render_draw_and_emit_signals()

    def on_x_invert(self, button):

        if self.csv_viewer_widget != None:
            model, iter = self.csv_viewer_widget.get_active_row()

            if (model, iter) == (None, None):
                return

            value = model.get_value(iter, 14)

            if value == '✔':
                value = ' '
            elif value == ' ':
                value = '✔'

            model.set_value(iter, 14, value)

        self.transform_entities(("x", -1))
        self.render_draw_and_emit_signals()

    def on_y_invert(self, button):  

        if self.csv_viewer_widget != None:
            model, iter = self.csv_viewer_widget.get_active_row()
            
            if (model, iter) == (None, None):
                return

            value = model.get_value(iter, 15)

            if value == '✔':
                value = ' '
            elif value == ' ':
                value = '✔'

            model.set_value(iter, 15, value)

        self.transform_entities(("y", -1))
        self.render_draw_and_emit_signals()

    def transform_entities(self, transformation):
        if self.added_entities == []:
            return

        # Clear the current axes
        self.ax.clear()
        
        # Get the bounding box of the modelspace
        xmin, ymin, zmin = self.doc_to_show.header["$EXTMIN"]
        xmax, ymax, zmax = self.doc_to_show.header["$EXTMAX"]
        # Calculate the center of the bounding box
        xcenter, ycenter, zcenter = (xmin + xmax) / 2, (ymin + ymax) / 2, 0

        # Calculate the maximum dimension
        max_length = max(xmax - xmin, ymax - ymin)

        xmin /= max_length
        xmax /= max_length
        ymin /= max_length
        ymax /= max_length

        # Rotate and redraw the added entities
        for e in self.added_entities:
            # Remove the entity from the modelspace
            self.doc.modelspace().delete_entity(e)


        for e in self.doc_to_show.modelspace():
             # move to origin
            e.translate(-xcenter,-ycenter,-zcenter)

            if transformation == "0":
                # no transformation
                pass
            if transformation == "90":
                # rotate about Z-axis 
                e.rotate_z(math.radians(90))
            elif transformation == "-90":
                # rotate about Z-axis 
                e.rotate_z(math.radians(-90))
            elif transformation == "180":
                # rotate about Z-axis 
                e.rotate_z(math.radians(180))
            elif transformation == "-180":
                # rotate about Z-axis 
                e.rotate_z(math.radians(-180))
            elif transformation == "270":
                # rotate about Z-axis 
                e.rotate_z(math.radians(270))
            elif transformation == "-270":
                # rotate about Z-axis 
                e.rotate_z(math.radians(-270))
            elif transformation == ('x', -1):
                # invert X-axis 
                e.scale(-1,1,1)
            elif transformation == ('y', -1):
                # invert Y-axis 
                e.scale(1,-1,1)

            # move back to original position
            e.translate(xcenter,ycenter,zcenter)  

        # Calculate the new bounding box after rotation
        cache = bbox.Cache()
        new_extmin, new_extmax = bbox.extents(self.doc_to_show.modelspace(), cache=cache)
        new_extmin = new_extmin.round(10)
        new_extmax = new_extmax.round(10)

        # Update the header variables
        self.doc_to_show.header["$EXTMIN"] = new_extmin
        self.doc_to_show.header["$EXTMAX"] = new_extmax

        self.width_profile = (new_extmax[0] - new_extmin[0])
        self.height_profile = (new_extmax[1] - new_extmin[1])

        for entity in self.doc_to_show.modelspace():
            # Create a copy of the entity
            entity_copy = entity.copy()

            # Move back to original position
            entity_copy.translate(-new_extmin.x, -new_extmin.y, 0)

            entity_copy.scale_uniform(0.8/max_length)
            
            entity_copy.translate(self.frame_percent_offset, self.frame_percent_offset, 0)

            # Change the color of the entity
            entity_copy.dxf.set('color', 10)

            self.doc.modelspace().add_entity(entity_copy)

            # Add the entity to the list of added entities
            self.added_entities.append(entity_copy)

    def check_units(self):
        # Get the insertion units of the document
        units = self.doc.header.get('$INSUNITS', 0)

        # Map the unit codes to their names
        units_map = {
            0: 'Unspecified',
            1: 'Inches',
            2: 'Feet',
            3: 'Miles',
            4: 'Millimeters',
            5: 'Centimeters',
            6: 'Meters',
            7: 'Kilometers',
            8: 'Microinches',
            9: 'Mils',
            10: 'Yards',
            11: 'Angstroms',
            12: 'Nanometers',
            13: 'Microns',
            14: 'Decimeters',
            15: 'Decameters',
            16: 'Hectometers',
            17: 'Gigameters',
            18: 'Astronomical units',
            19: 'Light years',
            20: 'Parsecs',
        }

        # Get the name of the units
        units_name = units_map.get(units, 'Unknown')

        print(f"The units of the document are: {units_name}")
    
    def on_update_dimensions_dxf_in_manual_widget(self, widget, manual_profile_cut, width, height):
        entry_height_profile = manual_profile_cut.get_HeightProfileEntry()
        manual_profile_cut.set_heightProfile(height)
        entry_height_profile.set_text('%.*f'%(entry_height_profile.get_num_decimal_digits(),manual_profile_cut.get_heightProfile()))
        manual_profile_cut.updateLengths()
        manual_profile_cut.queue_draw()

    def set_csv_viewer_widget(self, csv_viewer_widget):
        self.csv_viewer_widget = csv_viewer_widget

    def on_update_dimensions_dxf_in_csv_widget(self, widget, csv_viewer_widget, width, height):
        model, iter = csv_viewer_widget.get_active_row()
        
        if (model, iter) == (None, None):
            return
        
        if model.get_value(iter, 2) == '' or model.get_value(iter, 3) == '' or model.get_value(iter, 4) == '':
            model.set_value(iter, 10, f'{height:.2f}')

        if model.get_value(iter, 7) == ' ⬆ ':
            right_opposite_leg = math.tan(math.pi/2 - math.radians(float(model.get_value(iter, 12)))) * height
            left_opposite_leg = math.tan(math.pi/2 - math.radians(float(model.get_value(iter, 11)))) * height
            bottom_length = float(model.get_value(iter, 8)) - right_opposite_leg - left_opposite_leg
            model.set_value(iter, 9, f'{bottom_length:.2f}')
        elif model.get_value(iter, 7) == ' ⬇ ':
            right_opposite_leg = math.tan(math.pi/2 - math.radians(float(model.get_value(iter, 12)))) * height
            left_opposite_leg = math.tan(math.pi/2 - math.radians(float(model.get_value(iter, 11)))) * height
            top_length = float(model.get_value(iter, 9)) + right_opposite_leg + left_opposite_leg
            model.set_value(iter, 8, f'{top_length:.2f}')

    def on_clear_dxf(self, widget):
        self.manufacturer_combobox.set_active(-1)
        self.set_combobox.set_active(-1)
        self.code_combobox.set_active(-1)
        self.clear_dxf()

    def get_active_manufacturer_set_code(self):
        manufacturer = self.manufacturer_combobox.get_active_text()
        set = self.set_combobox.get_active_text()
        code = self.code_combobox.get_active_text()

        return manufacturer, set, code
    
    def set_sensitive_comboboxes_and_buttons(self, sensitive):
        self.manufacturer_combobox.set_sensitive(sensitive)
        self.set_combobox.set_sensitive(sensitive)
        self.code_combobox.set_sensitive(sensitive)
        self.rot_rigth_button.set_sensitive(sensitive)
        self.rot_left_button.set_sensitive(sensitive)
        self.x_inv_button.set_sensitive(sensitive)
        self.y_inv_button.set_sensitive(sensitive)
        self.clear_button.set_sensitive(sensitive)

        
        
