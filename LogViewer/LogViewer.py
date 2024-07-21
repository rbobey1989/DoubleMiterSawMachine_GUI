import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GObject
import os, datetime

class LogViewer(Gtk.ScrolledWindow, GObject.GObject):
    __gsignals__ = {
        'public-msg': (GObject.SignalFlags.RUN_FIRST, None, (str, str))
    }
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LogViewer, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    

    def __init__(self):
        super().__init__()
        if not self._initialized:
            logs_dir = 'logs'
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)

            today = datetime.date.today()
            self.log_file = os.path.join(logs_dir, f'msg_{today.strftime("%d_%m_%Y")}.log')

            self.set_overlay_scrolling(False)
            self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

            self.connect('public-msg', self.add_info_msg)

            # Create a ListBox and add it to the ScrolledWindow
            self.list_box = Gtk.ListBox()
            self.add(self.list_box)

            # Create tags for the different message types
            self.info_tag = Gtk.CssProvider()
            self.info_tag.load_from_data(b'#log_entry_row { background-color: lightblue; }')

            self.warning_tag = Gtk.CssProvider()
            self.warning_tag.load_from_data(b'#log_entry_row { background-color: yellow; }')

            self.error_tag = Gtk.CssProvider()
            self.error_tag.load_from_data(b'#log_entry_row { background-color: red; }')

            # Load the initial contents of the log file when idle
            GLib.idle_add(self.load_log_file)

            self._initialized = True

    def add_info_msg(self, widget, msg_type, msg):
        self.append_msg(msg, msg_type)

    def load_log_file(self):
        # Clear the ListBox
        for row in self.list_box.get_children():
            self.list_box.remove(row)

        # Open the log file for reading and writing, and create it if it doesn't exist
        with open(self.log_file, 'a+') as f:
            # Move the file pointer to the beginning of the file
            f.seek(0)

            # Read the contents of the log file line by line
            for line in f:
                # Determine the type of the message and the message itself
                message_type, message = line.split(":", 1)

                entry = Gtk.Entry()
                entry.set_name('log_entry_row')
                entry.set_text(message[:-1])

                # Disable editing
                entry.set_editable(False)

                # Disable cursor
                entry.set_can_focus(False)

                # Hide border
                entry.set_has_frame(False)

                # Apply the appropriate tag to the label
                if message_type == 'info':
                    Gtk.StyleContext.add_provider(entry.get_style_context(), self.info_tag, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                elif message_type == 'warning':
                    Gtk.StyleContext.add_provider(entry.get_style_context(), self.warning_tag, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                elif message_type == 'error':
                    Gtk.StyleContext.add_provider(entry.get_style_context(), self.error_tag, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

                # Add the label to a new ListBoxRow and add the row to the ListBox
                row = Gtk.ListBoxRow()
                row.set_name('log_row')
                #row.get_style_context().add_class('frame')
                row.add(entry)
                self.list_box.add(row)  # Change this line


        # Show all the new rows
        self.list_box.show_all()

        # Scroll to the last ListBoxRow
        vadjustment = self.get_vadjustment()
        GLib.idle_add(lambda: vadjustment.set_value(vadjustment.get_upper()))

    def append_msg(self, msg, msg_type):
        # Get the current date and time
        current_datetime = datetime.datetime.now()

        # Format the date and time as a string
        datetime_str = current_datetime.strftime("%d-%m-%Y %H:%M:%S")

        with open(self.log_file, 'a') as f:
            # Write the date and time, message type, and message to the log file
            f.write(f"{msg_type}:{datetime_str} {msg}\n")

        # Load the log file
        self.load_log_file()

    def get_css_property(self, widget, property_name):
        # Get the StyleContext for the widget
        style_context = widget.get_style_context()

        # Get the state for the widget
        state = style_context.get_state()

        # Get the property value
        property_value = style_context.get_property(property_name, state)

        return property_value


# class TestWindow(Gtk.Window):
#     def __init__(self):
#         super().__init__()

#         self.set_default_size(800, 600)

#         vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

#         self.log_viewer = LogViewer()

#         vbox.pack_start(self.log_viewer, True, True, 0)

#         hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
#         self.entry = Gtk.Entry()
        
#         self.add_info_button = Gtk.Button(label='Add Info')
#         self.add_warning_button = Gtk.Button(label='Add Warning')
#         self.add_error_button = Gtk.Button(label='Add Error')
        
#         self.add_info_button.connect('clicked', self.add_info_msg)
#         self.add_warning_button.connect('clicked', self.add_warning_msg)
#         self.add_error_button.connect('clicked', self.add_error_msg)
        
#         hbox.pack_start(self.entry, True, True, 0)
#         hbox.pack_end(self.add_info_button, False, False, 0)
#         hbox.pack_end(self.add_warning_button, False, False, 0)
#         hbox.pack_end(self.add_error_button, False, False, 0)

#         vbox.pack_end(hbox, False, False, 0)

#         self.add(vbox)

#         self.show_all()

#     def add_info_msg(self, button):
#         # msg = self.entry.get_text()
#         # self.log_viewer.append_msg(msg, 'info')
#         # self.entry.set_text('')
#         LogViewer().emit('public-msg', 'info', 'Info message')

#     def add_warning_msg(self, button):
#         # msg = self.entry.get_text()
#         # self.log_viewer.append_msg(msg, 'warning')
#         # self.entry.set_text('')
#         LogViewer().emit('public-msg', 'warning', 'Warning message')

#     def add_error_msg(self, button):
#         # msg = self.entry.get_text()
#         # self.log_viewer.append_msg(msg, 'error')
#         # self.entry.set_text('')
#         LogViewer().emit('public-msg', 'error', 'Error message')

#     def main(self):
#         self.connect("destroy", Gtk.main_quit)
#         self.show_all()
#         Gtk.main()

# if __name__ == "__main__":
#     window = TestWindow()
#     window.main()