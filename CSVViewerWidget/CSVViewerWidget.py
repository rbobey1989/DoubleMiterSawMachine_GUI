import gi
import csv
import re
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

class CSVViewerWidget(Gtk.Box):
    def __init__(self, barWidget=None, dxfViewerWidget=None):
        super(CSVViewerWidget, self).__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.barWidget = barWidget
        self.dxfViewerWidget = dxfViewerWidget

        hboxList = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.treeview = Gtk.TreeView()
        self.treeview.set_name('listTreeview')
        self.treestore = Gtk.TreeStore(bool, GdkPixbuf.Pixbuf,str, str, str, str, str, str, str, str, str)  # Adjusted
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
        profileFields = ['Manufacturer','Set','Code', 'Bar Length', 'Bar Num', 'Length', 'Right Angle', 'Left Angle', 'Description']
        for i, field in enumerate(profileFields):
            # Create a CellRendererText for editable cells
            renderer_text = Gtk.CellRendererText()
            renderer_text.set_property("editable", True)           
           
            renderer_text.connect("edited", lambda widget, path, text, column=i+1: self.on_cell_edited(widget, path, text, column))
            column = Gtk.TreeViewColumn(field, renderer_text, text=i+2)  # Adjust the text index for the added checkbox
            self.treeview.append_column(column)

        # Create the ScrolledWindow
        scrolled_window = Gtk.ScrolledWindow(overlay_scrolling=False)
        scrolled_window.set_name('scrolled_window')
        scrolled_window.set_overlay_scrolling(False)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        scrolled_window.add(self.treeview)

        hboxList.pack_start(scrolled_window, True, True, 0)

        self.pack_start(hboxList, True, True, 0)

    def validate_csv_format(self,filename):
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) != 10:  # Check the number of columns
                    print(f'number of columns error: {len(row)}')
                    print('number of columns error')
                    return False
                if not row[0].lower() in ['true', 'false']:  # Check the type of column 1
                    print('first field error')
                    return False
                if not (isinstance(row[1], str) or row[1] == ''):  # Check the type of column 2
                    print('second field error')
                    return False
                if not (isinstance(row[2], str) or row[2] == ''):  # Check the type of column 3
                    print('third field error')
                    return False
                if not (isinstance(row[3], str) or row[3] == ''):  # Check the type of column 4
                    print('fourth field error')
                    return False
                if not (self.is_float(row[4]) or row[4] == ''):  # Check the type of column 3
                    print('third field error')
                    return False
                if not (row[5].isdigit() or row[5] == ''):  # Check the type of column 4
                    return False
                if not (self.is_float(row[6]) or row[6] == ''):  # Check the type of column 5
                    return False
                if not (self.is_float(row[7]) or row[7] == ''):  # Check the type of column 6
                    return False
                if not (self.is_float(row[8]) or row[8] == ''):  # Check the type of column 7
                    return False
                if not (isinstance(row[9], str) or row[9] == ''):  # Check the type of column 8
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
            writer.writerow(row)

            # If the row has children, write them as well
            if tree.iter_has_child(child_iter):
                self.write_rows(writer, tree, child_iter)

            # Move to the next sibling of the current row
            child_iter = tree.iter_next(child_iter)

    def load_csv(self, filename):

        self.treestore.clear()
        self.barWidget.update_bar([])

        with open(filename, 'r') as f:
            reader = csv.reader(f)
            parent = None

            for row in reader:
                row[0] = row[0] == 'True'  # Adjusted
                pixbuf = self.checked_pixbuf if row[0] else self.unchecked_pixbuf
                if row[1]:
                    parent = self.treestore.append(None, [row[0], pixbuf, row[1], row[2], row[3], row[4], '', '', '', '', ''])  # Adjusted
                else:
                    self.treestore.append(parent, [row[0], pixbuf, '', '', '', '', row[5], row[6], row[7], row[8], row[9]])  # Adjusted

    def on_row_clicked(self, widget, event):
        if event.button == 1:  # left mouse button
            path_info = self.treeview.get_path_at_pos(int(event.x), int(event.y))
            if path_info is not None:
                path, col, cell_x, cell_y = path_info
                cell_area = self.treeview.get_cell_area(path, col)
                if col == self.treeview.get_column(0):
                    if cell_area.x <= cell_x <= cell_area.x + cell_area.width:
                        # Divide the column in two parts
                        if cell_x <= cell_area.x + cell_area.width / 2:
                            # Get the model and iter from the path
                            model = self.treeview.get_model()
                            iter = model.get_iter(path)
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
            else:
                self.treeview.get_selection().unselect_all()
                self.barWidget.update_bar([])
                self.dxfViewerWidget.clear_dxf()

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
                for i in range(self.treestore.iter_n_children(iter)):
                    child_iter = self.treestore.iter_nth_child(iter, i)
                    self.treestore[child_iter][0] = self.treestore[iter][0]
                    if self.treestore[child_iter][0]:
                        self.treestore[child_iter][1] = self.checked_pixbuf
                    else:
                        self.treestore[child_iter][1] = self.unchecked_pixbuf
            else:
                # This is a child row, so update the parent row if necessary
                parent_iter = self.treestore.iter_parent(iter)
                if parent_iter is not None:
                    all_selected = any(self.treestore[self.treestore.iter_nth_child(parent_iter, i)][0] for i in range(self.treestore.iter_n_children(parent_iter)))
                    self.treestore[parent_iter][0] = all_selected
                    if self.treestore[parent_iter][0]:
                        self.treestore[parent_iter][1] = self.checked_pixbuf
                    else:
                        self.treestore[parent_iter][1] = self.unchecked_pixbuf

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
                bar_num_column = self.get_column_number_by_name(treeview, "Bar Num")

                # Get the bar number of the child row
                row_bar_num = model.get_value(iter, bar_num_column)
                

                # Get all rows with the same bar number that are children of the same parent
                rows_with_same_bar_num = self.get_rows_by_bar_num(model, parent_iter, bar_num_column, row_bar_num)
                
                if self.barWidget != None:
                    self.barWidget.update_bar(rows_with_same_bar_num)

                if self.dxfViewerWidget != None:
                    self.dxfViewerWidget.update_dxf(rows_with_same_bar_num)

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
                if row[0]:
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