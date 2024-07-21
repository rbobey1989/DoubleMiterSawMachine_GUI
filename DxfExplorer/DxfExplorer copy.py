import gi, os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class DxfExplorer(Gtk.Box):
    def __init__(self):
        super(DxfExplorer, self).__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.manufacturer_label = Gtk.Label(label="Manufacturer")
        self.manufacturer_entry = Gtk.Entry()
        self.set_label = Gtk.Label(label="Set")
        self.set_entry = Gtk.Entry()

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
        self.treestore = Gtk.TreeStore(bool, str, str, str)
        self.treeview = Gtk.TreeView(model=self.treestore)

        # Get the Gtk.TreeSelection associated with the TreeView and set the mode to multiple
        self.treeview_selection = self.treeview.get_selection()
        self.treeview_selection.set_mode(Gtk.SelectionMode.MULTIPLE)

        # Create a TreeViewColumn with a CellRendererToggle for the checkboxes
        self.checkbox_colum = Gtk.TreeViewColumn("Select")
        self.treeview.append_column(self.checkbox_colum)
        self.cellrenderertoggle = Gtk.CellRendererToggle()
        self.checkbox_colum.pack_start(self.cellrenderertoggle, True)
        self.checkbox_colum.add_attribute(self.cellrenderertoggle, "active", 0)

        # Create a TreeViewColumn for the Manufacturer Profile name
        self.treeview_column_manufacturer = Gtk.TreeViewColumn("Manufacturer")
        self.treeview.append_column(self.treeview_column_manufacturer)
        self.cellrenderertext = Gtk.CellRendererText()
        self.treeview_column_manufacturer.pack_start(self.cellrenderertext, True)
        self.treeview_column_manufacturer.add_attribute(self.cellrenderertext, "text", 1)

        # Create a TreeViewColumn for the Set Profile name
        self.treeview_column_set = Gtk.TreeViewColumn("Set")
        self.treeview.append_column(self.treeview_column_set)
        self.cellrenderertext = Gtk.CellRendererText()
        self.treeview_column_set.pack_start(self.cellrenderertext, True)
        self.treeview_column_set.add_attribute(self.cellrenderertext, "text", 2)

        # Create a TreeViewColumn for the DXF file names
        self.treeview_column_path = Gtk.TreeViewColumn("DXF Files")
        self.treeview.append_column(self.treeview_column_path)
        self.cellrenderertext = Gtk.CellRendererText()
        self.treeview_column_path.pack_start(self.cellrenderertext, True)
        self.treeview_column_path.add_attribute(self.cellrenderertext, "text", 3)

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
        self.find_dxf_by_directories = Gtk.Button(label="DXFs by Directories")
        self.find_dxf_by_directories.connect("clicked", self.on_find_dxf_by_directories_clicked)

        # Create a button to find DXF files
        self.find_dxf_button = Gtk.Button(label="Find DXFs")
        self.find_dxf_button.connect("clicked", self.on_find_dxf_clicked)

        # Create a button to add DXF files
        self.add_dxf_button = Gtk.Button(label="Add DXFs")
        # self.add_dxf_button.connect("clicked", self.on_add_dxf_clicked)

        # Create a button to remove DXF files
        self.remove_dxf_button = Gtk.Button(label="Remove DXFs")
        self.remove_dxf_button.connect("clicked", self.on_remove_dxf_clicked)

        self.label="Directory Structure Manufacturer/Set/file.dxf\nProvide the Manufacturer and Set fields to upload manually"
        self.info_bar = Gtk.InfoBar()
        self.info_bar.set_margin_top(6)
        self.info_bar.set_size_request(-1, 60)

        self.label_info = Gtk.Label(label=self.label)
        self.info_bar.get_content_area().pack_start(self.label_info, True, True, 0)

        self.ok_info_bar_btn = self.info_bar.add_button("OK", Gtk.ResponseType.OK)

        self.info_bar.connect("response", self.on_info_bar_response)

        # Connect the CellRendererToggle to the callback function
        self.cellrenderertoggle.connect("toggled", self.on_checkbox_toggled)

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
                self.show_info_warning_bar("!!!Error!!!!, The selected folder does not have the correct structure.")
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
            self.show_info_warning_bar("!!!Error!!!!, Please provide Manufacturer and Set fields")
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
            if row[1] == manufacturer:
                manufacturer_iter = row.iter
                break

        # If the manufacturer is not found, add it to the TreeStore
        if manufacturer_iter is None:
            manufacturer_iter = self.treestore.append(None, [True, manufacturer, "", ""])

        # Find the set under the manufacturer
        set_iter = None
        for row in self.treestore[manufacturer_iter].iterchildren():
            if row[2] == set:
                set_iter = row.iter
                break

        # If the set is not found, create it under the manufacturer
        if set_iter is None:
            set_iter = self.treestore.append(manufacturer_iter, [True, "", set, ""])
            
        # Check if the file is already in the ListStore
        if not any(row[3] == filename for row in self.treestore):
            self.treestore.append(set_iter,[True, 
                                    "", 
                                    "",
                                    filename])
            

    # def on_add_dxf_clicked(self, button):
    #     pass

    def on_remove_dxf_clicked(self, button):
        # Get a list of TreePath for each row in the selection
        model, paths = self.treeview_selection.get_selected_rows()

        if len(paths) == 0:
            # for btns in self.hbox_buttons.get_children():
            #     btns.set_sensitive(False)
            # self.label_info.set_text("!!!Error!!!!, Please select a DXF file to remove")
            # self.ok_info_bar_btn.set_visible(True)
            self.show_info_warning_bar("!!!Error!!!!, Please select a DXF file to remove")
            return

        # Convert the TreePaths to TreeIters and delete each one from the model
        for path in reversed(paths):
            iter = model.get_iter(path)
            model.remove(iter)

    def on_checkbox_toggled(self, widget, path):
        iter = self.treestore.get_iter(path)

        # Value
        value = not self.treestore.get_value(iter, 0)

        # Change the checkbox of the parent
        self.treestore.set_value(iter, 0, value)

        if not self.treestore.iter_has_child(iter):

            if value:
                # If child is checked, check the parents
                parent_iter = self.treestore.iter_parent(iter)
                while parent_iter is not None:
                    self.treestore.set_value(parent_iter, 0, value)
                    parent_iter = self.treestore.iter_parent(parent_iter)
            else:
                # If all child is unchecked, uncheck the parents
                parent_iter = self.treestore.iter_parent(iter)
                while parent_iter is not None:
                    if any(row[0] for row in self.treestore[parent_iter].iterchildren()):
                        break
                    self.treestore.set_value(parent_iter, 0, value)
                    parent_iter = self.treestore.iter_parent(parent_iter)
            return

        # If we reach this point, the iter has children, so we change their checkboxes
        child_index = 0
        while True:
            child_iter = self.treestore.iter_nth_child(iter, child_index)
            if child_iter is None:
                break  # No more children

            self.treestore.set_value(child_iter, 0, value)  # Change the checkbox of the set

            grandchild_index = 0
            while True:
                grandchild_iter = self.treestore.iter_nth_child(child_iter, grandchild_index)
                if grandchild_iter is None:
                    break  # No more grandchildren

                self.treestore.set_value(grandchild_iter, 0, value)  # Change the checkbox of the dxf file

                grandchild_index += 1

            child_index += 1

        # If the iter has parent and the value its true, we change the parent checkbox
        if value:
            parent_iter = self.treestore.iter_parent(iter)
            while parent_iter is not None:
                self.treestore.set_value(parent_iter, 0, value)
                parent_iter = self.treestore.iter_parent(parent_iter)
        else:
            # If all child is unchecked, uncheck the parents
            parent_iter = self.treestore.iter_parent(iter)
            while parent_iter is not None:
                if any(row[0] for row in self.treestore[parent_iter].iterchildren()):
                    break
                self.treestore.set_value(parent_iter, 0, value)
                parent_iter = self.treestore.iter_parent(parent_iter)

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
            