import gi, os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from DxfDataBase.DxfDataBase import DxfDataBase

class DxfExplorer(Gtk.Box):
    def __init__(self):
        super(DxfExplorer, self).__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.manufacturer_label = Gtk.Label(label="Manufacturer", name="dxfExplorerLabel")
        self.manufacturer_entry = Gtk.Entry(name="dxfExplorerEntry")
        self.set_label = Gtk.Label(label="Set", name="dxfExplorerLabel")
        self.set_entry = Gtk.Entry(name="dxfExplorerEntry")

        vbox_labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox_labels.pack_start(self.manufacturer_label,True, True, 0)
        vbox_labels.pack_end(self.set_label,True, True , 0)

        vbox_entrys = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox_entrys.pack_start(self.manufacturer_entry, False, False, 0)
        vbox_entrys.pack_end(self.set_entry, True, True, 0)

        hbox_manufacturer_set = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox_manufacturer_set.pack_start(vbox_labels, False, False, 0)
        hbox_manufacturer_set.pack_end(vbox_entrys, True, True, 0)

        vbox.pack_start(hbox_manufacturer_set, False, False, 0)

        # Create a ListStore model for the TreeView
        self.treestore = Gtk.TreeStore(bool, GdkPixbuf.Pixbuf, str, str, str)
        self.treeview = Gtk.TreeView(model=self.treestore)
        self.treeview.set_name('listTreeview')
        self.treeview.set_show_expanders(False)
        self.treeview.set_level_indentation(16)

        # Get the Gtk.TreeSelection associated with the TreeView and set the mode to multiple
        self.treeview_selection = self.treeview.get_selection()
        self.treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)

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


        # Create a TreeViewColumn for the Manufacturer Profile name
        self.treeview_column_manufacturer = Gtk.TreeViewColumn("Manufacturer")
        self.treeview.append_column(self.treeview_column_manufacturer)
        self.cellrenderertext = Gtk.CellRendererText()
        self.treeview_column_manufacturer.pack_start(self.cellrenderertext, True)
        self.treeview_column_manufacturer.add_attribute(self.cellrenderertext, "text", 2)

        # Create a TreeViewColumn for the Set Profile name
        self.treeview_column_set = Gtk.TreeViewColumn("Set")
        self.treeview.append_column(self.treeview_column_set)
        self.cellrenderertext = Gtk.CellRendererText()
        self.treeview_column_set.pack_start(self.cellrenderertext, True)
        self.treeview_column_set.add_attribute(self.cellrenderertext, "text", 3)

        # Create a TreeViewColumn for the DXF file names
        self.treeview_column_path = Gtk.TreeViewColumn("DXF Files")
        self.treeview.append_column(self.treeview_column_path)
        self.cellrenderertext = Gtk.CellRendererText()
        self.treeview_column_path.pack_start(self.cellrenderertext, True)
        self.treeview_column_path.add_attribute(self.cellrenderertext, "text", 4)

        # Create a ScrolledWindow
        self.scrolled_window = Gtk.ScrolledWindow(overlay_scrolling=False)
        self.scrolled_window.set_name('scrolled_window')
        self.scrolled_window.set_overlay_scrolling(False)
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        # Add the TreeView to the ScrolledWindow
        self.scrolled_window.add(self.treeview)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_name('hboxTreeview')
        hbox.pack_start(self.scrolled_window, True, True, 0)

        # Add the ScrolledWindow to the parent container
        vbox.pack_start(hbox, True, True, 0)

        # Create a button to find DXF files structured by Manufacturer and Set directories
        self.find_dxf_by_directories = Gtk.Button(label="DXFs by Directories", name= "dxfExplorerButton")
        self.find_dxf_by_directories.connect("clicked", self.on_find_dxf_by_directories_clicked)

        # Create a button to find DXF files
        self.find_dxf_button = Gtk.Button(label="Find DXFs", name= "dxfExplorerButton")
        self.find_dxf_button.connect("clicked", self.on_find_dxf_clicked)

        # Create a button to add DXF files
        self.add_dxf_button = Gtk.Button(label="Add DXFs",name= "dxfExplorerButton")
        self.add_dxf_button.connect("clicked", self.on_add_dxf_clicked)
        self.DxfsToBBDDList = []

        # Create a button to remove DXF files
        self.remove_dxf_button = Gtk.Button(label="Remove DXFs", name= "dxfExplorerButton")
        self.remove_dxf_button.connect("clicked", self.on_remove_dxf_clicked)

        self.label="Directory Structure Manufacturer/Set/file.dxf\nProvide the Manufacturer and Set fields to upload manually"
        self.info_bar = Gtk.InfoBar()
        self.info_bar.set_margin_top(6)
        self.info_bar.set_size_request(-1, 60)

        self.label_info = Gtk.Label(label=self.label, name="infoBarLabel")
        self.info_bar.get_content_area().pack_start(self.label_info, True, True, 0)

        self.ok_info_bar_btn = self.info_bar.add_button("OK", Gtk.ResponseType.OK)
        self.ok_info_bar_btn.set_name("infoBarOkButton")

        self.info_bar.connect("response", self.on_info_bar_response)

        self.hbox_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, homogeneous=True)
        self.hbox_buttons.pack_start(self.find_dxf_by_directories, False, False, 0)
        self.hbox_buttons.pack_start(self.find_dxf_button, False, False, 0)
        self.hbox_buttons.pack_start(self.add_dxf_button, False, False, 0)
        self.hbox_buttons.pack_start(self.remove_dxf_button, False, False, 0)

        vbox.pack_start(self.hbox_buttons, False, False, 0)
        
        self.pack_start(vbox, True, True, 0)
        
        self.pack_end(self.info_bar, False, False, 0)        


    def on_find_dxf_by_directories_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a folder",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK,
            ),
        )

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            # Get the selected folder
            folder = dialog.get_filename()

            # Check if the folder has the correct structure
            if not self.check_folder_structure(folder):
                # Show a message in the info bar
                self.show_info_warning_bar("\n!!!Error!!!!, The selected folder does not have the correct structure.")
                dialog.destroy()
                return
            
            # Iterate over the manufacturer in the folder
            for manufacturer in os.listdir(folder):
                manufacturer_path = os.path.join(folder, manufacturer)

                # Check if the manufacturer is a directory
                if os.path.isdir(manufacturer_path):
                    # Iterate over the sets in the manufacturer folder
                    for set in os.listdir(manufacturer_path):
                        set_path = os.path.join(manufacturer_path, set)

                        # Check if the set is a directory
                        if os.path.isdir(set_path):
                            # Iterate over the DXF files in the set folder
                            for dxf_file in os.listdir(set_path):
                                dxf_file_path = os.path.join(set_path, dxf_file)

                                # Check if the file is a DXF file
                                if dxf_file_path.endswith(".dxf"):
                                    # Find the manufacturer in the TreeStore

                                    self.check_if_exist_in_the_treeview_if_not_add_it(manufacturer,set,dxf_file_path)

        dialog.destroy()

    def check_folder_structure(self, folder):
        # Check if the folder contains only subfolders (manufacturers)
        if not all(os.path.isdir(os.path.join(folder, name)) for name in os.listdir(folder)):
            return False
        # Check if the subfolders (manufacturers) contain only further subfolders (sets)
        for manufacturer in os.listdir(folder):
            manufacturer_path = os.path.join(folder, manufacturer)
            if not all(os.path.isdir(os.path.join(manufacturer_path, name)) for name in os.listdir(manufacturer_path)):
                return False
            # Check if the subfolders (sets) contain only DXF files
            for set in os.listdir(manufacturer_path):
                set_path = os.path.join(manufacturer_path, set)
                if not all(name.endswith('.dxf') for name in os.listdir(set_path)):
                    return False
        # If all checks passed, the folder has the correct structure
        return True

    def on_find_dxf_clicked(self, button):

        manufacturer = self.manufacturer_entry.get_text()
        set = self.set_entry.get_text()

        if manufacturer == "" or set == "":
            # for btns in self.hbox_buttons.get_children():
            #     btns.set_sensitive(False)
            # self.label_info.set_text("!!!Error!!!!, Please provide Manufacturer and Set fields")
            # self.ok_info_bar_btn.set_visible(True)
            self.show_info_warning_bar("\n!!!Error!!!!, Please provide Manufacturer and Set fields")
            return

        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self.get_toplevel(),
            action=Gtk.FileChooserAction.OPEN,
            buttons=("Cancel", Gtk.ResponseType.CANCEL, "Open", Gtk.ResponseType.OK))
        
        # Create a filter that allows only .dxf files
        filter_dxf = Gtk.FileFilter()
        filter_dxf.set_name("DXF files")
        filter_dxf.add_pattern("*.dxf")

        # Add the filter to the dialog
        dialog.add_filter(filter_dxf)
        dialog.set_select_multiple(True)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            for filename in dialog.get_filenames():

                self.check_if_exist_in_the_treeview_if_not_add_it(manufacturer,set,filename)

        dialog.destroy()

    def check_if_exist_in_the_treeview_if_not_add_it(self,manufacturer,set,filename):
        # Find the manufacturer in the TreeStore
        manufacturer_iter = None
        for row in self.treestore:
            if row[2] == manufacturer:
                manufacturer_iter = row.iter
                break

        # If the manufacturer is not found, add it to the TreeStore
        if manufacturer_iter is None:
            manufacturer_iter = self.treestore.append(None, [True,self.checked_pixbuf, manufacturer, "", ""])

        # Find the set under the manufacturer
        set_iter = None
        for row in self.treestore[manufacturer_iter].iterchildren():
            if row[3] == set:
                set_iter = row.iter
                break

        # If the set is not found, create it under the manufacturer
        if set_iter is None:
            set_iter = self.treestore.append(manufacturer_iter, [True,self.checked_pixbuf, "", set, ""])
            
        # Check if the file is already in the ListStore
        if not any(row[4] == filename for row in self.treestore):
            self.treestore.append(set_iter,[True,
                                    self.checked_pixbuf, 
                                    "", 
                                    "",
                                    filename])
            
    def on_add_dxf_clicked(self, button):

        db = DxfDataBase()
        selected_rows = []
        model = self.treestore
        iter = model.get_iter_first()

        while iter is not None:
            if model.iter_has_child(iter):
                child_iter = model.iter_children(iter)
                while child_iter is not None:
                    if model.iter_has_child(child_iter):
                        child_child_iter = model.iter_children(child_iter)
                        while child_child_iter is not None:
                            if model.get_value(child_child_iter, 0):
                                # selected_rows.append([model.get_value(iter, 2), 
                                #                       model.get_value(child_iter, 3),
                                #                       os.path.basename(model.get_value(child_child_iter, 4)), 
                                #                       model.get_value(child_child_iter, 4)])
                                db.insert(model.get_value(iter, 2), 
                                                      model.get_value(child_iter, 3),
                                                      os.path.basename(model.get_value(child_child_iter, 4)), 
                                                      model.get_value(child_child_iter, 4))
                            child_child_iter = model.iter_next(child_child_iter)
                    child_iter = model.iter_next(child_iter)
            iter = model.iter_next(iter)

        db.close()
        #self.verify_database()


    def verify_database(self):
        db = DxfDataBase()
        self.DxfsToBBDDList = db.get_all_dxf_files()
        db.close()

        # Imprimir la lista de DXF en la base de datos
        for row in self.DxfsToBBDDList:
            print(row)


    def on_remove_dxf_clicked(self, button):
        # Get a list of TreePath for each row in the selection
        model, paths = self.treeview_selection.get_selected_rows()

        if len(paths) == 0:
            self.show_info_warning_bar("\n!!!Error!!!!, Please select a DXF file to remove")
            return

        # Convert the TreePaths to TreeIters and delete each one from the model
        for path in reversed(paths):
            iter = model.get_iter(path)
            model.remove(iter)

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



    def on_info_bar_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            self.ok_info_bar_btn.set_visible(False)
            self.label_info.set_text(self.label)
            for btns in self.hbox_buttons.get_children():
                btns.set_sensitive(True)

    def show_info_warning_bar(self, message):
        for btns in self.hbox_buttons.get_children():
            btns.set_sensitive(False)
        self.label_info.set_text(message)
        self.ok_info_bar_btn.set_visible(True)

    def get_add_dxf_button(self):
        return self.add_dxf_button
    
    def get_treestore(self):
        return self.treestore
            