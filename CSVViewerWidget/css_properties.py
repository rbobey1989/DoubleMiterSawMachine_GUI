import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

treeview = Gtk.TreeView()

style_context = treeview.get_style_context()
properties = style_context.list_properties()

for property in properties:
    print('Property name:', property.name)