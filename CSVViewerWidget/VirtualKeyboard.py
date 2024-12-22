import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

class VirtualKeyboard(Gtk.Grid):
    __gsignals__ = {
        'key-pressed': (GObject.SignalFlags.RUN_FIRST, None, (str,))
    }

    def __init__(self):
        super().__init__()
        self.set_row_spacing(5)
        self.set_column_spacing(5)
        self.shift = False
        self.create_keys()

    def create_keys(self):
        keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'Backspace'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M',',', '.'],
            ['Accept','Space','Cancel']
        ]

        hboxs = []

        for row_index, row in enumerate(keys):
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            if row_index == 1:
                hbox.pack_start(Gtk.Box(), False, False, 25/2)  # Half button offset
                hbox.pack_end(Gtk.Box(), False, False, 60)
            elif row_index == 2:
                hbox.pack_start(Gtk.Box(), False, False, 50/2)  # Full button offset
                hbox.pack_end(Gtk.Box(), False, False, 110)  # Full button offset
            elif row_index == 3:
                hbox.pack_start(Gtk.Box(), False, False, 25/2)  # No offset
                hbox.pack_end(Gtk.Box(), False, False, 50)  # No offset

            for key in row:
                button = Gtk.Button(label=key,name='treeviewButton', can_focus=False)
                button.set_hexpand(True)
                button.set_vexpand(True)
                if key == 'Space':
                    button.set_size_request(600*1.2, 50)  # Make the space button longer
                    button.connect("clicked", self.on_key_clicked)
                    hbox.pack_start(Gtk.Box(), True, True, 0)  # Center the space button
                    hbox.pack_start(button, False, False, 0)
                    hbox.pack_start(Gtk.Box(), True, True, 0)  # Center the space button
                else:
                    button.set_size_request(120, 50)  # Set uniform size for other buttons
                    button.connect("clicked", self.on_key_clicked)
                    hbox.pack_start(button, False, False, 0)

            self.attach(hbox, 0, row_index, 1, 1)
            hboxs.append(hbox)

        # Add the Enter button spanning multiple rows
        enter_button = Gtk.Button(label='Clear',name='treeviewButton',can_focus=False)
        enter_button.set_size_request(100, 100)  # Adjust size as needed
        enter_button.connect("clicked", self.on_key_clicked)

        enter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        enter_box.pack_end(enter_button, False, False, 5)

        self.attach_next_to(enter_box, self.get_child_at(0,0) ,Gtk.PositionType.BOTTOM, width=1, height=2)

    def on_key_clicked(self, button):
        key = button.get_label()
        if key == 'Shift':
            self.shift = not self.shift
        elif key == 'Backspace':
            self.emit('key-pressed', 'Backspace')
        elif key == 'Enter':
            self.emit('key-pressed', 'Enter')
        elif key == 'Space':
            self.emit('key-pressed', ' ')
        else:
            if self.shift:
                key = key.upper()
            else:
                key = key.lower()
            self.emit('key-pressed', key)

# class MainWindow(Gtk.Window):
#     def __init__(self):
#         super().__init__(title="Virtual Keyboard")
#         self.set_border_width(10)
#         #self.set_default_size(600, 300)

#         vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
#         self.add(vbox)

#         self.entry = Gtk.Entry()
#         vbox.pack_start(self.entry, False, False, 0)

#         self.keyboard = VirtualKeyboard()
#         vbox.pack_start(self.keyboard, True, True, 0)

#         self.keyboard.connect("key-pressed", self.on_key_pressed)

#     def on_key_pressed(self, widget, key):
#         current_text = self.entry.get_text()
#         if key == 'Backspace':
#             self.entry.set_text(current_text[:-1])
#         elif key == 'Enter':
#             self.entry.set_text(current_text + '\n')
#         else:
#             self.entry.set_text(current_text + key)

# win = MainWindow()
# win.connect("destroy", Gtk.main_quit)
# win.show_all()
# Gtk.main()