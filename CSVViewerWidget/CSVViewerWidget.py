import gi
import csv
import re
import math
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
from LogViewer.LogViewer import LogViewer
from DxfDataBase.DxfDataBase import DxfDataBase
from .VirtualKeyboard import VirtualKeyboard

class CSVViewerWidget(Gtk.Notebook):
    def __init__(self, barWidget=None, max_angle = 90, min_angle = 22.5, max_length = 6500, min_length = 240, max_height = 300):
        super(CSVViewerWidget, self).__init__(show_tabs=False,show_border=False)

        self.barWidget = barWidget
        self.dxfViewerWidget = None
        self.max_angle = max_angle
        self.min_angle = min_angle
        self.max_length = max_length
        self.min_length = min_length
        self.max_height = max_height

        self.csvViewerWidgetPages = {'mainCutListPage': 0, 'addCutCsvListPage': 1}
        self.set_current_page(self.csvViewerWidgetPages['mainCutListPage'])

        vboxCutList = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vboxAppendCut = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,homogeneous=True)

        # Create  a Title Bar
        self.titleBar = Gtk.Entry(editable=False, can_focus=False)
        self.titleBar.set_name('titleBar')
        self.titleBar.set_property('xalign', 0.5)

        self.titleBar.connect("focus-out-event", self.on_focus_out_event_title_bar)

        hboxList = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hboxList.set_name('hboxTreeview')

        self.treeview = Gtk.TreeView()
        self.treeview.set_name('listTreeview')
        self.treestore = Gtk.TreeStore(bool, 
                                       GdkPixbuf.Pixbuf,
                                       str, str, str, str, 
                                       str, str, str, str, 
                                       str, str, str, str, 
                                       str, str, str) #, str)  # Adjusted
        self.treeview.set_model(self.treestore)
        self.treeview.set_show_expanders(False)
        self.treeview.set_level_indentation(16)
        # Connect the signal handler to the 'cursor-changed' signal
        self.treeview.connect("cursor-changed", self.on_cursor_changed)

        # Add a CellRendererToggle for the checkbox
        renderer_pixbuf_check = Gtk.CellRendererPixbuf()
        self.checked_pixbuf = GdkPixbuf.Pixbuf.new_from_file("icons/check_icon.png")
        self.unchecked_pixbuf = GdkPixbuf.Pixbuf.new_from_file("icons/uncheck_icon.png")
        
        # Add a CellRendererPixbuf for the expander
        renderer_pixbuf_expander = Gtk.CellRendererPixbuf()
        self.expand_pixbuf = GdkPixbuf.Pixbuf.new_from_file("icons/expand_icon.png")
        self.collapse_pixbuf = GdkPixbuf.Pixbuf.new_from_file("icons/collapse_icon.png")

        self.treeview.connect("button-press-event", self.on_row_clicked)

        column_pixbuf = Gtk.TreeViewColumn("")

        # Add both CellRendererPixbuf to the column
        column_pixbuf.pack_start(renderer_pixbuf_expander, False)
        column_pixbuf.pack_start(renderer_pixbuf_check, False)
        
        # Set the pixbuf attribute of the CellRendererPixbuf to the appropriate columns of the model
        column_pixbuf.add_attribute(renderer_pixbuf_check, "pixbuf", 1)
        column_pixbuf.add_attribute(renderer_pixbuf_expander, "pixbuf", 1)

        def cell_func(column, cell, model, iter, data):
            # Check if the row has children
            if model.iter_has_child(iter):
                # Get the path of the current row
                path = model.get_path(iter)
                # Check if the row is expanded
                if self.treeview.row_expanded(path):
                    # If the row is expanded, set the pixbuf to the collapse icon
                    cell.set_property('pixbuf', self.collapse_pixbuf)
                else:
                    # If the row is not expanded, set the pixbuf to the expand icon
                    cell.set_property('pixbuf', self.expand_pixbuf)
            else:
                # If the row does not have children, do not show the pixbuf
                cell.set_property('pixbuf', None)

        # Set the cell function for the renderer_pixbuf_expander
        column_pixbuf.set_cell_data_func(renderer_pixbuf_expander, cell_func)
        
        self.treeview.append_column(column_pixbuf)

        # Create a TreeViewColumn for each field
        self.profileFields = ['Manufacturer',
                              'Set',
                              'Code', 
                              'Bar Length', 
                              'Bar Num', 
                              '   ', 
                              'Top Length', 
                              'Bottom Length', 
                              'Heigth', 
                              'Left Angle', 
                              'Right Angle',
                              'Rotation',
                              'X Invert',
                              'Y Invert', 
                              'Description']
        for i, field in enumerate(self.profileFields):
            # Create a CellRendererText for editable cells
            renderer_text = Gtk.CellRendererText()
            renderer_text.set_property('xalign', 0.5)
            #renderer_text.set_property("editable", True)           
           
            #renderer_text.connect("edited", lambda widget, path, text, column=i+1: self.on_cell_edited(widget, path, text, column))
            column = Gtk.TreeViewColumn(field, renderer_text, text=i+2)  # Adjust the text index for the added checkbox
            self.treeview.append_column(column)

        # Create the ScrolledWindow
        scrolled_window = Gtk.ScrolledWindow(overlay_scrolling=False)
        scrolled_window.set_name('scrolled_window')
        scrolled_window.set_overlay_scrolling(False)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        scrolled_window.add(self.treeview)

        hboxList.pack_start(scrolled_window, True, True, 0)

        self.newCsvListBtn = Gtk.Button(label="New Cut List", name='treeviewButton')
        self.addProfileCsvListBtn = Gtk.Button(label="*Add Profile", name='treeviewButton')
        self.addCutCsvListBtn = Gtk.Button(label="Add Cut", name='treeviewButton')
        self.delLineCsvListBtn = Gtk.Button(label="Del Line", name='treeviewButton')
        self.clearCsvListBtn = Gtk.Button(label="Del List", name='treeviewButton')

        self.newCsvListBtn.connect("clicked", self.on_new_csv_list)
        self.addProfileCsvListBtn.connect("clicked", self.on_add_profile_csv_list)
        self.addCutCsvListBtn.connect("clicked", self.on_add_cut_csv_list)
        self.delLineCsvListBtn.connect("clicked", self.on_del_line_csv_list)
        self.clearCsvListBtn.connect("clicked", self.on_clear_csv)

        hboxTreeViewBtns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=True)
        hboxTreeViewBtns.pack_start(self.newCsvListBtn, False, True, 0)
        hboxTreeViewBtns.pack_start(self.addProfileCsvListBtn, False, True, 0)
        hboxTreeViewBtns.pack_start(self.addCutCsvListBtn, False, True, 0)
        hboxTreeViewBtns.pack_start(self.delLineCsvListBtn, False, True, 0)
        hboxTreeViewBtns.pack_start(self.clearCsvListBtn, False, True, 0)

        vboxCutList.pack_start(hboxTreeViewBtns, False, True, 0)
        vboxCutList.pack_start(self.titleBar, False, True, 0)
        vboxCutList.pack_start(hboxList, True, True, 0)

        self.append_page(vboxCutList)

        self.virtualKeyboard = VirtualKeyboard()
        self.virtualKeyboard.connect("key-pressed", self.on_key_pressed)

        self.entryWithFocus = None

        barNumberLabel = Gtk.Label(label='Bar Number', name='labelIdicatorsEntryCsvCutData')
        self.barNumberEntry = CSVViewerEntry( parent=self, 
                                             num_int_digits=4, 
                                             num_decimal_digits=0,
                                             init_value=1,
                                             max_value=9999, 
                                             min_value=0)
        self.barNumberEntry.set_name('entryCsvCutData')
        self.barNumberEntry.set_max_length(4)
        self.barNumberEntry.set_alignment(xalign=0.5)
        self.barNumberEntry.set_editable(False)

        topLengthLabel = Gtk.Label(label='Top Length', name='labelIdicatorsEntryCsvCutData')
        self.topLengthEntry = CSVViewerEntry( parent=self, 
                                             num_int_digits=4, 
                                             num_decimal_digits=2,
                                             init_value=1000.00,
                                             max_value=self.max_length,
                                             min_value=self.min_length)
        self.topLengthEntry.set_name('entryCsvCutData')
        self.topLengthEntry.set_sensitive(True)
        self.topLengthEntry.set_max_length(7)
        self.topLengthEntry.set_alignment(xalign=0.5)
        self.topLengthEntry.set_editable(False)
        self.topLengthEntry.connect("update-value", self.on_update_value_entry)

        bottomLengthLabel = Gtk.Label(label='Bottom Length', name='labelIdicatorsEntryCsvCutData')
        self.bottomLengthEntry = CSVViewerEntry( parent=self,
                                                num_int_digits=4,
                                                num_decimal_digits=2,
                                                init_value=1000.00,
                                                max_value=self.max_length,
                                                min_value=self.min_length)
        self.bottomLengthEntry.set_name('entryCsvCutData')
        self.bottomLengthEntry.set_sensitive(False)
        self.bottomLengthEntry.set_max_length(7)
        self.bottomLengthEntry.set_alignment(xalign=0.5)
        self.bottomLengthEntry.set_editable(False)
        self.bottomLengthEntry.connect("update-value", self.on_update_value_entry)

        heightLabel = Gtk.Label(label='Height', name='labelIdicatorsEntryCsvCutData')
        self.heightEntry = CSVViewerEntry( parent=self,
                                          num_int_digits=3,
                                          num_decimal_digits=2,
                                          init_value=100.00,
                                          max_value=self.max_height,
                                          min_value=0)
        self.heightEntry.set_name('entryCsvCutData')
        self.heightEntry.set_max_length(6)
        self.heightEntry.set_alignment(xalign=0.5)
        self.heightEntry.set_editable(False)
        self.heightEntry.connect("update-value", self.on_update_value_entry)

        rightAngleLabel = Gtk.Label(label='Right Angle', name='labelIdicatorsEntryCsvCutData')
        self.rightAngleEntry = CSVViewerEntry( parent=self,
                                              num_int_digits=3,
                                              num_decimal_digits=2,
                                              init_value=90.00,
                                              max_value=self.max_angle,
                                              min_value=self.min_angle)
        self.rightAngleEntry.set_name('entryCsvCutData')
        self.rightAngleEntry.set_max_length(6)
        self.rightAngleEntry.set_alignment(xalign=0.5)
        self.rightAngleEntry.set_editable(False)
        self.rightAngleEntry.connect("update-value", self.on_update_value_entry)

        leftAngleLabel = Gtk.Label(label='Left Angle', name='labelIdicatorsEntryCsvCutData')
        self.leftAngleEntry = CSVViewerEntry( parent=self,
                                              num_int_digits=3,
                                              num_decimal_digits=2,
                                              init_value=90.00,
                                              max_value=self.max_angle,
                                              min_value=self.min_angle)
        self.leftAngleEntry.set_name('entryCsvCutData')
        self.leftAngleEntry.set_max_length(6)
        self.leftAngleEntry.set_alignment(xalign=0.5)
        self.leftAngleEntry.set_editable(False)
        self.leftAngleEntry.connect("update-value", self.on_update_value_entry)

        self.changeTopLengthCheckBtn = Gtk.ToggleButton(label='⬆',name='treeviewButton')
        self.changeTopLengthCheckBtn.set_active(True)

        self.changeBottomLengthCheckBtn = Gtk.ToggleButton(label='⬇',name='treeviewButton')
        self.changeBottomLengthCheckBtn.set_active(False)

        self.changeTopLengthCheckBtn.connect("toggled", self.on_change_length_reference, self.changeBottomLengthCheckBtn, 'top')
        self.changeBottomLengthCheckBtn.connect("toggled", self.on_change_length_reference, self.changeTopLengthCheckBtn, 'bottom')

        DescriptionLabel = Gtk.Label(label='Description', name='labelIdicatorsEntryCsvCutData')
        self.DescriptionEntry = Gtk.Entry(name = 'entryCsvCutData')
        self.DescriptionEntry.set_editable(False)
        self.DescriptionEntry.connect("focus-in-event", self.on_focus_in_event_description)
        self.DescriptionEntry.connect("focus-out-event", self.on_focus_out_event_description)
        
        gridCutData = Gtk.Grid()
        gridCutData.set_column_spacing(20)
        gridCutData.set_row_spacing(30)
        gridCutData.set_margin_top(10)
        gridCutData.set_margin_bottom(10)
        gridCutData.set_margin_start(20)
        gridCutData.set_margin_end(10)
        
        gridCutData.attach(barNumberLabel, 0, 0, 1, 1)
        gridCutData.attach(self.barNumberEntry, 1, 0, 1, 1)

        gridCutData.attach(heightLabel, 0, 1, 1, 1)
        gridCutData.attach(self.heightEntry, 1, 1, 1, 1)

        gridCutData.attach(topLengthLabel, 2, 0, 1, 1)
        hBoxTopLength = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        hBoxTopLength.pack_start(self.topLengthEntry, True, True, 0)
        hBoxTopLength.pack_end(self.changeTopLengthCheckBtn, False, True, 0)
        gridCutData.attach(hBoxTopLength, 3, 0, 1, 1)

        gridCutData.attach(bottomLengthLabel, 2, 1, 1, 1)
        hBoxBottomLength = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        hBoxBottomLength.pack_start(self.bottomLengthEntry, True, True, 0)
        hBoxBottomLength.pack_end(self.changeBottomLengthCheckBtn, False, True, 0)
        gridCutData.attach(hBoxBottomLength, 3, 1, 1, 1)

        gridCutData.attach(rightAngleLabel, 4, 0, 1, 1)
        gridCutData.attach(self.rightAngleEntry, 5, 0, 1, 1)

        gridCutData.attach(leftAngleLabel, 4, 1, 1, 1)
        gridCutData.attach(self.leftAngleEntry, 5, 1, 1, 1) 

        gridCutData.attach(DescriptionLabel, 0, 2, 1, 1)
        gridCutData.attach(self.DescriptionEntry, 1, 2, 6, 1)

        vboxAppendCut.pack_start(gridCutData, True, True, 0)
        vboxAppendCut.pack_start(self.virtualKeyboard, True, True, 0)

        self.append_page(vboxAppendCut, Gtk.Label(label='Profile List'))

    def validate_csv_format(self,filename):
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            bar_lengths = {}
            sub_list = (0,0)

            for index,row in enumerate(reader):
                if len(row) != len(self.profileFields)+1:  # Check the number of columns
                    LogViewer().emit('public-msg', 'error', 'cantidad campos self.profileFields: ' + str(len(self.profileFields)) + ' y row: '+ str(len(row)))
                    LogViewer().emit('public-msg', 'error', 'Error: Number Of Columns Error At Row ' + str(index + 1) + ': '+ str(len(row)))
                    return False
                if not row[0].lower() in ['true', 'false']:  # Check the type of column 1
                    LogViewer().emit('public-msg', 'error', 'Error: First Field Error At Row ' + str(index + 1) + ': '+ row[0])
                    return False
                if not (isinstance(row[1], str) or row[1] == ''):  # Check the type of column 2
                    LogViewer().emit('public-msg', 'error', 'Error: Second Field Error At Row ' + str(index + 1) + ': '+ row[1])
                    return False
                if not (isinstance(row[2], str) or row[2] == ''):  # Check the type of column 3
                    LogViewer().emit('public-msg', 'error', 'Error: Third Field Error At Row ' + str(index + 1) + ': '+ row[2])
                    return False
                if not (isinstance(row[3], str) or row[3] == ''):  # Check the type of column 4
                    LogViewer().emit('public-msg', 'error', 'Error: Fourth Field Error At Row ' + str(index + 1) + ': '+ row[3])
                    return False
                if not (self.is_float(row[4]) or row[4] == ''):  # Check the type of column 5
                    LogViewer().emit('public-msg', 'error', 'Error: Fifth Field Error At Row ' + str(index + 1) + ': '+ row[4])
                    return False
                else:
                    if row[4] != '':
                        sub_list = (sub_list[0]+1,float(row[4]))
                        if sub_list not in bar_lengths:
                            bar_lengths[sub_list] = {}
                if not (row[5].isdigit() or row[5] == ''):  # Check the type of column 6
                    LogViewer().emit('public-msg', 'error', 'Error: Sixth Field Error At Row ' + str(index + 1) + ': '+ row[5])
                    return False
                else:
                    if row[5] != '':
                        if row[5] not in bar_lengths[sub_list]:
                            bar_lengths[sub_list][row[5]] = 0
                        bar_lengths[sub_list][row[5]] += float(row[7])
                        if bar_lengths[sub_list][row[5]] > sub_list[1]:
                            LogViewer().emit('public-msg', 'error', 'Error: Bar Length Error At Row ' + str(index + 1) + ' Bar: '+ row[5]+ ', '+ str(bar_lengths[sub_list][row[5]]) + ' > ' + str(sub_list[1]))
                            return False
                if not (row[6].lower() in ['top','bottom'] or row[6] == '') :  # Check the type of column 7
                    LogViewer().emit('public-msg', 'error', 'Error: Seventh Field Error At Row ' + str(index + 1) + ': '+ row[6])
                    return False
                if not (self.is_float(row[7]) or row[7] == ''):  # Check the type of column 8
                    LogViewer().emit('public-msg', 'error', 'Error: Eighth Field Error At Row ' + str(index + 1) + ': '+ row[7])
                    return False
                if not (self.is_float(row[8]) or row[8] == ''):  # Check the type of column 9
                    LogViewer().emit('public-msg', 'error', 'Error: Ninth Field Error At Row ' + str(index + 1) + ': '+ row[8])
                    return False
                if not (self.is_float(row[9]) or row[9] == ''):  # Check the type of column 10
                    LogViewer().emit('public-msg', 'error', 'Error: Tenth Field Error At Row ' + str(index + 1) + ': '+ row[9])
                    return False
                if not (self.is_float(row[10]) or row[10] == ''):  # Check the type of column 11
                    LogViewer().emit('public-msg', 'error', 'Error: Eleventh Field Error At Row ' + str(index + 1) + ': '+ row[10])
                    return False
                else:
                    if row[10] != '':
                        if float(row[10]) > self.max_angle or float(row[10]) < self.min_angle:
                            LogViewer().emit('public-msg', 'error', 'Error: Eleventh Field Error At Row ' + str(index + 1) + ': '+ row[10] + ' > ' + str(self.max_angle) + ' or ' + row[10] + ' < ' + str(self.min_angle))
                            return False
                if not (self.is_float(row[11]) or row[11] == ''):  # Check the type of column 12
                    LogViewer().emit('public-msg', 'error', 'Error: Twelfth Field Error At Row ' + str(index + 1) + ': '+ row[11])
                    return False
                else:
                    if row[11] != '':
                        if float(row[11]) > self.max_angle or float(row[11]) < self.min_angle:
                            LogViewer().emit('public-msg', 'error', 'Error: Twelfth Field Error At Row ' + str(index + 1) + ': '+ row[11] + ' > ' + str(self.max_angle) + ' or ' + row[11] + ' < ' + str(self.min_angle))
                            return False
                if not (row[12] in ['0','90','180','270','-90','-180','-270'] or row[12] == ''): # Check the type of column 13
                    LogViewer().emit('public-msg', 'error', 'Error: Thirteenth Field Error At Row ' + str(index + 1) + ': '+ row[12])
                    return False
                if not (row[13] in ['0','1'] or row[13] == ''): # Check the type of column 14
                    LogViewer().emit('public-msg', 'error', 'Error: Fourteenth Field Error At Row ' + str(index + 1) + ': '+ row[13])
                    return False
                if not (row[14] in ['0','1'] or row[14] == ''): # Check the type of column 15
                    LogViewer().emit('public-msg', 'error', 'Error: Fifteenth Field Error At Row ' + str(index + 1) + ': '+ row[14])
                    return False
                if not (isinstance(row[15], str) or row[15] == ''):  # Check the type of column 11
                    LogViewer().emit('public-msg', 'error', 'Error: Seventeenth Field Error At Row ' + str(index + 1) + ': '+ row[15])
                    return False
                
        return True

    def is_float(self,value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def write_rows(self, writer, tree, parent=None):
        # Get an iterator to the first child of parent
        if parent is None:
            child_iter = tree.get_iter_first()
        else:
            child_iter = tree.iter_children(parent)

        # Iterate over all children of parent
        while child_iter is not None:
            # Write the row to the CSV 
            row = [tree.get_value(child_iter, i) for i in range(tree.get_n_columns())]
            row.pop(1)  # Remove the GdkPixbuf.Pixbuf from the row

            if row[6] == ' ⬆ ': # Replace the visual arrow representation of the row 6 to 'TOP' or 'BOTTOM' values
                row[6] = 'TOP'
            elif row[6] == ' ⬇ ':
                row[6] = 'BOTTOM'

            if row[13] == '✔': # Replace the visual check representation of the row 13 to '1' or '0' values
                row[13] = '1'
            else:
                row[13] = '0'

            if row[14] == '✔': # Replace the visual check representation of the row 14 to '1' or '0' values
                row[14] = '1'
            else:
                row[14] = ''

            writer.writerow(row)

            # If the row has children, write them as well
            if tree.iter_has_child(child_iter):
                self.write_rows(writer, tree, child_iter)

            # Move to the next sibling of the current row
            child_iter = tree.iter_next(child_iter)

    def load_csv(self, filename):

        self.treestore.clear()
        self.barWidget.update_bar([])

        file_name = os.path.basename(filename)
        self.titleBar.set_text(file_name)

        with open(filename, 'r') as f:
            reader = csv.reader(f)
            parent = None

            db = DxfDataBase()
            current_height = 0
            current_width = 0

            for index,row in enumerate(reader):
                row[0] = row[0].lower() == 'true'  # Adjusted
                pixbuf = self.checked_pixbuf if row[0] else self.unchecked_pixbuf
                if row[1] or (row[1].lower() == 'define' and row[2].lower() == 'by' and row[3].lower() == 'user'):
                    if not (row[1].lower() == 'define' and row[2].lower() == 'by' and row[3].lower() == 'user'):
                        current_height, current_width = db.get_code_dimensions(row[1], row[2], row[3])
                        if current_height is None:
                            manufacturers = db.get_all_manufacturers()
                            if row[1] not in [manufacturer[0] for manufacturer in manufacturers]:
                                LogViewer().emit('public-msg', 'error', 'Error: Has not provided a valid manufacturer at ROW: ' + str(index + 1))
                                self.treestore.clear()
                                db.close()
                                return
                            
                            sets = db.get_sets_by_manufacturer(row[1])
                            if row[2] not in [set[0] for set in sets]:
                                LogViewer().emit('public-msg', 'error', 'Error: Has not provided a valid set at ROW: ' + str(index + 1))
                                self.treestore.clear()
                                db.close()
                                return
                            
                            codes = db.get_codes_by_manufacturer_and_set(row[1], row[2])
                            if row[3] not in [code[0] for code in codes]:
                                LogViewer().emit('public-msg', 'error', 'Error: Has not provided a valid code at ROW: ' + str(index + 1))
                                self.treestore.clear()
                                db.close()
                                return


                            LogViewer().emit('public-msg', 'error', 'Error: An error occurred while trying to get the dimensions of the dxf file at ROW: ' + str(index + 1))
                            self.treestore.clear()
                            db.close()
                            return
                    else:
                        row[1] = 'DEFINE'
                        row[2] = 'BY'
                        row[3] = 'USER'
                        
                    parent = self.treestore.append(None, [row[0], pixbuf, row[1], row[2], row[3], row[4], '', '', '', '', '', '', '', '', '', '', ''])  # Adjusted
                else:
                    top_length = float(row[7]) if row[7] else None
                    bottom_length = float(row[8]) if row[8] else None
                    height = float(row[9]) if row[9] else None
                    left_angle = float(row[10]) if row[10] else None
                    right_angle = float(row[11]) if row[11] else None 
                    
                    if height is None:
                        LogViewer().emit('public-msg', 'warning', 'Warning: Height Obtained From DXF file at ROW: ' + str(index + 1) + ', Height Value: '+ f'{current_height:.2f}')
                        row[9] = f'{current_height:.2f}'
                        height = current_height

                    if right_angle is None or left_angle is None:
                        LogViewer().emit('public-msg', 'error', 'Error: The angles of the heads cannot be undefined at ROW: ' + str(index + 1))
                        self.treestore.clear()
                        db.close()
                        return

                    if top_length is None and bottom_length is None:
                        LogViewer().emit('public-msg', 'error', 'Error: The TOP and BOTTOM length cannot both be undefined at ROW: ' + str(index + 1))
                        self.treestore.clear()
                        db.close()
                        return
                    
                    if top_length is None:
                        right_opposite_leg = math.tan(math.pi/2 - math.radians(right_angle)) * height
                        left_opposite_leg = math.tan(math.pi/2 - math.radians(left_angle)) * height
                        top_length = right_opposite_leg + left_opposite_leg + bottom_length
                        row[7] = f'{top_length:.2f}'

                    if bottom_length is None:
                        right_opposite_leg = math.tan(math.pi/2 - math.radians(right_angle)) * height
                        left_opposite_leg = math.tan(math.pi/2 - math.radians(left_angle)) * height
                        bottom_length = top_length - right_opposite_leg - left_opposite_leg
                        row[8] = f'{bottom_length:.2f}'

                    if row[6].lower() == 'top':
                        visual_row_6 = ' ⬆ '
                    elif row[6].lower() == 'bottom':
                        visual_row_6 = ' ⬇ '

                    if row[12] == '':
                        row[12] = '0'

                    if row[13] == '' or row[13] == '0':
                        row[13] = ' '
                    elif row[13] == '1':
                        row[13] = '✔'

                    if row[14] == '' or row[14] == '0':
                        row[14] = ' '
                    elif row[14] == '1':
                        row[14] = '✔'

                    # if row[15] == '':
                    #     row[15] = '0'

                    self.treestore.append(parent, [row[0], pixbuf, '', '', '', '', row[5], visual_row_6, row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15]]) #, row[16]])  # Adjusted

            db.close()

    def clear_csv(self):
        if self.treestore is not None and len(self.treestore) > 0:
            dialog = Gtk.MessageDialog(self.get_toplevel_window(), 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, "CSV Viewer Widget")
            dialog.format_secondary_text("Do you want to save the changes to the current CSV file?")
            dialog.get_style_context().add_class('dialog')
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                resp = self.on_save_csv_list()
                if resp == Gtk.ResponseType.CANCEL:
                    return
            else:
                self.treestore.clear()
                self.titleBar.set_text('')
                if self.barWidget != None:
                    self.barWidget.update_bar([])
                if self.dxfViewerWidget != None:
                    self.dxfViewerWidget.clear_dxf()


    def on_row_clicked(self, widget, event):
        if event.button == 1:  # left mouse button
            path_info = self.treeview.get_path_at_pos(int(event.x), int(event.y))
            if path_info is not None:
                path, col, cell_x, cell_y = path_info
                cell_area = self.treeview.get_cell_area(path, col)
                # Get the model and iter from the path
                model = self.treeview.get_model()
                iter = model.get_iter(path)
                if col == self.treeview.get_column(0) and event.type == Gdk.EventType.BUTTON_PRESS:
                    if cell_area.x <= cell_x <= cell_area.x + cell_area.width:
                        # Divide the column in two parts
                        if cell_x <= cell_area.x + cell_area.width / 2:
                            # Check if the row has children
                            if model.iter_has_child(iter):
                                # Check if the row is expanded
                                if self.treeview.row_expanded(path):
                                    # If the row is expanded, collapse it
                                    self.treeview.collapse_row(path)
                                else:
                                    # If the row is not expanded, expand it
                                    self.treeview.expand_row(path, False)
                        else:
                            self.on_row_activated(widget, path, col)
                elif col == self.treeview.get_column(6) and event.type == Gdk.EventType._2BUTTON_PRESS:
                    if model.iter_parent(iter) is not None:
                        if model.get_value(iter, 7) == ' ⬆ ':
                            model.set_value(iter, 7, ' ⬇ ')
                        elif model.get_value(iter, 7) == ' ⬇ ':
                            model.set_value(iter, 7, ' ⬆ ')
            else:
                self.treeview.get_selection().unselect_all()
                self.barWidget.update_bar([])
                # self.dxfViewerWidget.clear_dxf()

    def on_row_activated(self, widget, path, column):
        # Get the column index
        column_index = self.treeview.get_columns().index(column)

        # Only toggle the checkbox if the first column was clicked
        if column_index == 0:
            # Toggle the state of the clicked cell
            self.treestore[path][0] = not self.treestore[path][0]

            # Update the GdkPixbuf.Pixbuf based on the new state
            if self.treestore[path][0]:
                self.treestore[path][1] = self.checked_pixbuf
            else:
                self.treestore[path][1] = self.unchecked_pixbuf

            # Get an iterator to the row
            iter = self.treestore.get_iter(path)

            if self.treestore.iter_has_child(iter):
                # This is a parent row, so update all child rows
                self.update_children(iter, self.treestore[path][0], self.treestore[path][1])

                    # Get the parent iterator
            parent_iter = self.treestore.iter_parent(iter)

            # If the row has a parent and all siblings are in the desired state, set the parent to the desired state
            while parent_iter:
                if self.are_all_children(parent_iter, self.treestore[path][0]):
                    self.treestore[parent_iter][0] = self.treestore[path][0]
                    self.treestore[parent_iter][1] = self.treestore[path][1]
                parent_iter = self.treestore.iter_parent(parent_iter)

    def update_children(self, parent_iter, new_state, new_pixbuf):
        for i in range(self.treestore.iter_n_children(parent_iter)):
            child_iter = self.treestore.iter_nth_child(parent_iter, i)
            self.treestore[child_iter][0] = new_state
            self.treestore[child_iter][1] = new_pixbuf
            if self.treestore.iter_has_child(child_iter):
                self.update_children(child_iter, new_state, new_pixbuf)

    def are_all_children(self, parent_iter, state):
        for i in range(self.treestore.iter_n_children(parent_iter)):
            child_iter = self.treestore.iter_nth_child(parent_iter, i)
            if self.treestore[child_iter][0] != state:  # If the child's state is not the desired state
                return False
            if self.treestore.iter_has_child(child_iter):  # If the child has children
                if not self.are_all_children(child_iter, state):  # If any grandchild's state is not the desired state
                    return False
        return True

    def on_cell_edited(self, cell, path, new_text, column):
        # Convert the path to a Gtk.TreeIter
        iter = self.treestore.get_iter(path)

        # Validate the new text
        if column == 1 and not re.match(r'^(true|false)$', new_text.lower()):
            print("Error: La columna 1 debe ser un booleano (True o False).")
        elif column == 2 and not re.match(r'^\w+$', new_text):
            print("Error: La columna 2 debe ser una cadena.")
        elif column in [3, 5, 6, 7] and not re.match(r'^\d+(\.\d+)?$', new_text):
            print(f"Error: La columna {column} debe ser un número de punto flotante.")
        elif column == 4 and not re.match(r'^\d+$', new_text):
            print("Error: La columna 4 debe ser un número entero.")
        else:
            # If the new text is valid, update the model
            self.treestore.set_value(iter, column + 1, new_text)

    def on_cursor_changed(self, treeview):
        # Get the currently selected row
        selection = treeview.get_selection()
        (model, iter) = selection.get_selected()

        # If a row is selected
        if iter is not None:
            # Get the parent of the selected row
            parent_iter = model.iter_parent(iter)

            # If the selected row has a parent
            if parent_iter is not None:
                # Get the column number of the bar number
                #bar_num_column = self.get_column_number_by_name(treeview, "Bar Num")

                # Get the bar number of the child row
                row_bar_num = model.get_value(iter, 6)
                

                # Get all rows with the same bar number that are children of the same parent
                rows_with_same_bar_num = self.get_rows_by_bar_num(model, parent_iter, 6, row_bar_num)

                if self.barWidget != None:
                    self.barWidget.update_bar(rows_with_same_bar_num)

                if self.dxfViewerWidget != None:
                    if rows_with_same_bar_num[0][1].lower() == 'define' and rows_with_same_bar_num[0][2].lower() == 'by' and rows_with_same_bar_num[0][3].lower() == 'user':
                        self.dxfViewerWidget.clear_dxf()
                    else:
                        self.dxfViewerWidget.update_dxf(rows_with_same_bar_num[0][1:4] + 
                                                        [model.get_value(iter, 13), 
                                                        model.get_value(iter, 14),
                                                        model.get_value(iter, 15)])
            else:
                if self.barWidget != None:
                    self.barWidget.update_bar([])
                # if self.dxfViewerWidget != None:
                #     self.dxfViewerWidget.clear_dxf()

    def get_rows_by_bar_num(self, model, parent_iter, bar_num_column, bar_num):
        # Create a list to store the rows with the given bar number
        rows_with_same_bar_num = []

        # Get the parent row
        parent_row = model[parent_iter][:]
        parent_row.pop(1)
        # Insert the parent row at the beginning of the list
        rows_with_same_bar_num.append(parent_row)

        # Get the number of children of the parent row
        n_children = model.iter_n_children(parent_iter)

        # Iterate over all children of the parent row
        for i in range(n_children):
            # Get the Gtk.TreeIter for the current child row
            child_iter = model.iter_nth_child(parent_iter, i)

            # Get the bar number of the child row
            row_bar_num = model.get_value(child_iter, bar_num_column)            

            # If the bar number of the child row is the same as the given bar number, add the row to the list
            if row_bar_num == bar_num:
                # Get the row as a list of column values
                row = [model.get_value(child_iter, j) for j in range(model.get_n_columns())]
                # if row[0]:
                #     row.pop(1)
                #     rows_with_same_bar_num.append(row)

                row.pop(1)
                rows_with_same_bar_num.append(row)

        return rows_with_same_bar_num
    
    def get_column_number_by_name(self, treeview, column_name):
        # Get the Gtk.TreeViewColumn objects for all columns in the model
        columns = treeview.get_columns()

        # Iterate over all columns
        for i, column in enumerate(columns):
            # If the title of the column is the same as the given column name, return the column number
            if column.get_title() == column_name:
                return i + 1

        # If no column with the given name is found, return None
        return None
    
    def get_treestore(self):
        return self.treestore
    
    def get_active_row(self):
        selection = self.treeview.get_selection()
        model, iter = selection.get_selected()

        if iter is not None:
            return model, iter
        
        return None, None
    
    def get_selected_child_rows(self):

        selected_rows = []
        model = self.treestore
        iter = model.get_iter_first()

        while iter is not None:
            if model.iter_has_child(iter):
                child_iter = model.iter_children(iter)
                while child_iter is not None:
                    if model.get_value(child_iter, 0):
                        path = model.get_path(child_iter)
                        selected_rows.append((child_iter, path))
                    child_iter = model.iter_next(child_iter)
            iter = model.iter_next(iter)

        return selected_rows
    
    def show_current_line_cut(self, pathIterStr):
        if pathIterStr is not None:
            pathIter = Gtk.TreePath.new_from_string(pathIterStr)
            
            if pathIter.get_depth() > 1:
                parentIter = pathIter.copy()
                parentIter.up()
                self.treeview.expand_row(parentIter, False)
            
            self.treeview.set_cursor(pathIter, self.treeview.get_column(0), True)

    
    def set_dxfViewerWidget(self, dxfViewerWidget):
        self.dxfViewerWidget = dxfViewerWidget

    def on_focus_out_event_title_bar(self, widget, event):
        widget.set_can_focus(False)
        if widget.get_text() == '':
            widget.set_text('Untitled.csv')
        elif widget.get_text()[-4:] != '.csv' :
            widget.set_text(widget.get_text() + '.csv')
        widget.set_editable(False)
        
    def on_new_csv_list(self, widget):
        # if self.treestore is not None and len(self.treestore) > 0:
        #     dialog = Gtk.MessageDialog(self.get_toplevel_window(), 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, "CSV Viewer Widget")
        #     dialog.format_secondary_text("Do you want to save the changes to the current CSV file?")
        #     dialog.get_style_context().add_class('dialog')
        #     response = dialog.run()
        #     dialog.destroy()
        #     if response == Gtk.ResponseType.YES:
        #         resp = self.on_save_csv_list()
        #         if resp == Gtk.ResponseType.CANCEL:
        #             return
        self.clear_csv()
        self.titleBar.set_editable(True)
        self.titleBar.set_can_focus(True)
        self.titleBar.grab_focus()

    def get_toplevel_window(self):
        widget = self
        while not isinstance(widget, Gtk.Window):
            widget = widget.get_parent()
            if widget is None:
                break
        return widget
    
    def on_save_csv_list(self):
        if self.treestore is None or len(self.treestore) == 0:
            LogViewer().emit('public-msg', 'warning', 'Warning: There is no data to save.')
            return Gtk.ResponseType.CANCEL
        
        dialog = Gtk.FileChooserDialog("Por favor elige un archivo", self.get_toplevel_window(),
        Gtk.FileChooserAction.SAVE,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.get_style_context().add_class('dialog')
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            with open(dialog.get_filename(), 'w') as f:
                writer = csv.writer(f)
                self.write_rows(writer, self.get_treestore())
        else:
            dialog.destroy()
            return Gtk.ResponseType.CANCEL   
        
        dialog.destroy()

        return Gtk.ResponseType.OK

    def on_add_profile_csv_list(self, widget):
        if self.dxfViewerWidget != None:
            manufacturer, set, code = self.dxfViewerWidget.get_active_manufacturer_set_code()
            if manufacturer != None and set != None and code != None:
                self.treestore.append(None, [True, self.checked_pixbuf, manufacturer, set, code, '6500', '', '', '', '', '', '', '', '', '', '', ''])
            else:
                self.treestore.append(None, [True, self.checked_pixbuf, 'DEFINE', 'BY', 'USER', '6500', '', '', '', '', '', '', '', '', '', '', ''])
                LogViewer().emit('public-msg', 'warning', 'Warning: No manufacturer, set or code selected.')

    def on_add_cut_csv_list(self, widget):
        model, iter = self.get_active_row()
        top_bar_used = 0
        bottom_bar_used = 0
        if model is not None and iter is not None:
            if model[iter][2:5] != ['', '', '']:
                db = DxfDataBase()
                current_height, current_width = db.get_code_dimensions(model[iter][2], model[iter][3], model[iter][4])
                db.close()
                
                if current_height is not None:
                    self.heightEntry.set_text(f'{current_height:.2f}')

                self.barNumberEntry.set_init_value()
                self.topLengthEntry.set_init_value()
                self.bottomLengthEntry.set_init_value()
                self.heightEntry.set_init_value()
                self.leftAngleEntry.set_init_value()
                self.rightAngleEntry.set_init_value()

                self.set_current_page(self.csvViewerWidgetPages['addCutCsvListPage'])
            
    def on_key_pressed(self, widget, key):

        model, iter = self.get_active_row()

        if key == 'cancel':
            self.set_current_page(self.csvViewerWidgetPages['mainCutListPage'])
            return
        elif key == 'accept':

            space, bar_number = self.has_enough_space(float(self.topLengthEntry.get_text()), float(self.bottomLengthEntry.get_text()))

            self.treestore.append(iter, [True, self.checked_pixbuf, 
                                         '', '', '', '', 
                                         bar_number, 
                                         ' ⬆ ' if self.changeTopLengthCheckBtn.get_active() else ' ⬇ ',
                                         self.topLengthEntry.get_text(),
                                         self.bottomLengthEntry.get_text(), 
                                         self.heightEntry.get_text(),
                                         self.leftAngleEntry.get_text(), 
                                         self.rightAngleEntry.get_text(),  
                                         '0', 
                                         '', 
                                         '', 
                                         self.DescriptionEntry.get_text()]) 
            self.sort_treestore_by_bar_number() 
            
            self.treestore.emit('row-changed', self.treestore.get_path(iter), iter)
            self.set_current_page(self.csvViewerWidgetPages['mainCutListPage'])
            return


        if self.entryWithFocus is None:
            print('entryWithFocus is None')
            return
        else:
            if key == 'Backspace':
                self.entryWithFocus.set_text(self.entryWithFocus.get_text()[:-1])
            elif key == 'clear':
                print('clear')
                self.entryWithFocus.set_text('')
            else: 
                self.entryWithFocus.set_text(self.entryWithFocus.get_text() + key)

    def has_enough_space(self, new_cut_top_length, new_cut_bottom_length):
        
        model, iter = self.get_active_row()
        total_bar_length = float(model[iter][5])  # Suponiendo que la longitud total de la barra está en la columna 5

        others_numbers_bars = []

        # Calcular la longitud utilizada en la barra específica
        used_top_length = 0
        used_bottom_length = 0

        bar_number = None

        if model.iter_has_child(iter):
            child_iter = model.iter_children(iter)
            # last_child_iter = child_iter
            while child_iter is not None:
                if model.get_value(child_iter, 6) == self.barNumberEntry.get_text():
                    used_top_length += float(model.get_value(child_iter, 8))
                    used_bottom_length += float(model.get_value(child_iter, 9))
                    # last_child_iter = child_iter
                else:
                    others_numbers_bars.append(model.get_value(child_iter, 6))
                child_iter = model.iter_next(child_iter)
            
            if self.barNumberEntry.get_text() not in others_numbers_bars:
                bar_number = self.barNumberEntry.get_text()            
        else:
            bar_number = self.barNumberEntry.get_text()

        # Verificar si hay suficiente espacio para el nuevo corte
        if ((total_bar_length - used_top_length) >= new_cut_top_length) and ((total_bar_length - used_bottom_length) >= new_cut_bottom_length):
            return True, bar_number

        for bar in others_numbers_bars:
            used_top_length = 0
            used_bottom_length = 0
            child_iter = model.iter_children(iter)
            while child_iter is not None:
                if model.get_value(child_iter, 6) == bar:
                    used_top_length += float(model.get_value(child_iter, 8))
                    used_bottom_length += float(model.get_value(child_iter, 9))
                child_iter = model.iter_next(child_iter)

            if ((total_bar_length - used_top_length) >= new_cut_top_length) and ((total_bar_length - used_bottom_length) >= new_cut_bottom_length):
                return True, bar
            
        others_numbers_bars.append(bar_number)
        int_others_numbers_bars = [int(bar) for bar in others_numbers_bars]
        return False, str(max(int_others_numbers_bars) + 1)
    
    def sort_treestore_by_bar_number(self):
        
        model, iter = self.get_active_row()

        if model.iter_has_child(iter):
            data = []
            child_iter = model.iter_children(iter)
            while child_iter is not None:
                row_data = [model.get_value(child_iter, i) for i in range(model.get_n_columns())]
                data.append(row_data)
                child_iter = model.iter_next(child_iter)

            data.sort(key=lambda x: int(x[6]))

            # Limpiar las filas hijas del padre seleccionado
            while model.iter_has_child(iter):
                child_iter = model.iter_children(iter)
                model.remove(child_iter)

            for row_data in data:
                model.append(iter, row_data)

    def on_focus_in_event_description(self, widget, event):
        self.entryWithFocus = widget

    def on_focus_out_event_description(self, widget, event):
        self.entryWithFocus = None

    def set_entry_with_focus(self, entry):
        self.entryWithFocus = entry

    def get_entry_with_focus(self):
        return self.entryWithFocus
    
    def on_change_length_reference(self, button, otherButton, name):
        if button.get_active():
            otherButton.set_active(False)
            if name == 'top':
                self.bottomLengthEntry.set_sensitive(False)
                self.topLengthEntry.set_sensitive(True)
            elif name == 'bottom':
                self.topLengthEntry.set_sensitive(False)
                self.bottomLengthEntry.set_sensitive(True)

    def on_update_value_entry(self, entry):
        
        try:
            height = float(self.heightEntry.get_text())
            left_angle = float(self.leftAngleEntry.get_text())
            right_angle = float(self.rightAngleEntry.get_text())
            top_length = float(self.topLengthEntry.get_text())
            bottom_length = float(self.bottomLengthEntry.get_text())
        except ValueError:
            height = self.heightEntry.get_init_value()
            left_angle = self.leftAngleEntry.get_init_value()
            right_angle = self.rightAngleEntry.get_init_value()
            top_length = self.topLengthEntry.get_init_value()
            bottom_length = self.bottomLengthEntry.get_init_value()

        if self.changeTopLengthCheckBtn.get_active():
            bottomLengthProfile = top_length - height*(1/math.tan(math.radians(left_angle))+1/math.tan(math.radians(right_angle)))
            bottomLengthProfileStr = '%.*f'%(self.bottomLengthEntry.get_num_decimal_digits(),bottomLengthProfile)
            # self.bottomLengthProfile = float(bottomLengthProfileStr)
            self.bottomLengthEntry.set_text(bottomLengthProfileStr)
        elif self.changeBottomLengthCheckBtn.get_active():
            topLengthProfile = bottom_length + height*(1/math.tan(math.radians(left_angle))+1/math.tan(math.radians(right_angle)))
            topLengthProfileStr = '%.*f'%(self.topLengthEntry.get_num_decimal_digits(),topLengthProfile)
            # self.topLengthProfile = float(topLengthProfileStr)
            self.topLengthEntry.set_text(topLengthProfileStr)

    def on_del_line_csv_list(self, widget):
        model, iter = self.get_active_row()
        if model is not None and iter is not None:
            model.remove(iter)


    def on_clear_csv(self, widget):
        self.clear_csv()

    def set_sensitive_btns(self, state):
        self.newCsvListBtn.set_sensitive(state)          
        self.addProfileCsvListBtn.set_sensitive(state)   
        self.addCutCsvListBtn.set_sensitive(state)       
        self.delLineCsvListBtn.set_sensitive(state)      
        self.clearCsvListBtn.set_sensitive(state) 
        self.treeview.set_sensitive(state)







class CSVViewerEntry(Gtk.Entry,Gtk.Editable): 
    __gsignals__ = {
        'update-value': (GObject.SignalFlags.RUN_FIRST, None, ())
    }
        
    def __init__(
        self,
        parent = None,
        num_int_digits : int = 4,
        num_decimal_digits : int = 2,    
        init_value: float = 0,
        max_value: float = 9999.99,
        min_value: float = 0.0
        ):
        super(CSVViewerEntry,self).__init__() 

        self.parent = parent
        self.num_int_digits = num_int_digits - 1
        self.num_decimal_digits = num_decimal_digits
        self.init_value = init_value
        self.max_value = max_value
        self.min_value = min_value

        self.set_text('%.*f'%(self.num_decimal_digits,self.init_value))

        self.connect('focus-in-event',self.on_focus_in_event)
        self.connect('focus-out-event',self.on_focus_out_event)

        self.focusOutState = False
    
    def custom_get_parent(self):
        return self.parent
    
    def get_num_decimal_digits(self):
        return self.num_decimal_digits
    
    def get_init_value(self):
        return self.init_value

    def on_focus_in_event(self, widget, event):
        self.custom_get_parent().set_entry_with_focus(widget)

    def set_init_value(self):
        self.set_text('%.*f'%(self.num_decimal_digits,self.init_value))
    
    def on_focus_out_event(self, widget, event):
        try:
            value = float(widget.get_text())
        except ValueError:
            if widget.get_text() == '':
                value = self.min_value

        if value < self.min_value:
            widget.set_text('%.*f'%(self.num_decimal_digits,self.min_value))
        elif value > self.max_value:
            widget.set_text('%.*f'%(self.num_decimal_digits,self.max_value))
        else:
            widget.set_text('%.*f'%(self.num_decimal_digits,value))

        self.emit('update-value')

        self.custom_get_parent().set_entry_with_focus(None)
        
    def validate_float_string(self,input_string):
        if self.num_decimal_digits != 0:
            pattern = r"^([1-9]\d{{0,{}}}|0)(\.|\.\d{{1,{}}})?$".format(self.num_int_digits,self.num_decimal_digits)
        else:
            pattern = r"^([1-9]\d{{0,{}}}|0)?$".format(self.num_int_digits)
        return re.match(pattern, input_string)    

    def do_insert_text(self, new_text, length, position):
        
        validate_float_string = self.validate_float_string(new_text)

        if validate_float_string:
            self.get_buffer().insert_text(position, new_text, length)
            return position + length

        self.get_buffer().insert_text(position, new_text[:-1], length-1)
        return position


# class MainWindow(Gtk.Window):
#     def __init__(self):
#         super().__init__()

#         self.set_title("CSV TreeView")
#         self.set_default_size(800, 600)

#         vboxmain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

#         hboxBtns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

#         self.open_button = Gtk.Button(label="Abrir")
#         self.open_button.connect("clicked", self.on_open_clicked)
#         hboxBtns.pack_start(self.open_button, False, True, 0)

#         self.save_button = Gtk.Button(label="Guardar")
#         self.save_button.connect("clicked", self.on_save_clicked)
#         hboxBtns.pack_start(self.save_button, False, True, 0)

#         self.delete_button = Gtk.Button(label="Suprimir")
#         self.delete_button.connect("clicked", self.on_delete_clicked)
#         hboxBtns.pack_start(self.delete_button, False, True, 0)

#         vboxmain.pack_start(hboxBtns, False, True, 0)

#         self.csv_viewer = CSVViewerWidget()

#         vboxmain.pack_start(self.csv_viewer, True, True, 0)

#         self.add(vboxmain)

#     def main(self):
#         self.connect("destroy", Gtk.main_quit)
#         self.show_all()
#         Gtk.main()

#     def on_open_clicked(self, widget):
#         fileChooserDialog = Gtk.FileChooserDialog("Por favor elige un archivo", self,
#             Gtk.FileChooserAction.OPEN,
#             (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

#         response = fileChooserDialog.run()
#         if response == Gtk.ResponseType.OK:
#             self.csv_viewer.get_treestore().clear()
#             if not self.csv_viewer.validate_csv_format(fileChooserDialog.get_filename()):
#                 error_dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
#                     Gtk.ButtonsType.OK, "Error")
#                 error_dialog.format_secondary_text(
#                     f"Error: The file {fileChooserDialog.get_filename()} does not have the correct CSV format.")
#                 error_dialog.run()
#                 error_dialog.destroy()                
#             else:
#                 print(f"The file {fileChooserDialog.get_filename()} has the correct CSV format.")
#                 self.csv_viewer.load_csv(fileChooserDialog.get_filename())

#         fileChooserDialog.destroy()

#     def on_save_clicked(self, widget):
#         dialog = Gtk.FileChooserDialog("Por favor elige un archivo", self,
#             Gtk.FileChooserAction.SAVE,
#             (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

#         response = dialog.run()
#         if response == Gtk.ResponseType.OK:
#             with open(dialog.get_filename(), 'w') as f:
#                 writer = csv.writer(f)
#                 self.csv_viewer.write_rows(writer, self.csv_viewer.get_treestore())

#         dialog.destroy()

#     def on_delete_clicked(self, widget):
#         self.csv_viewer.get_treestore().clear()

# if __name__ == "__main__":
#     window = MainWindow()
#     window.main()