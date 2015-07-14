
from gi.repository import Gtk, Gdk, Gio, GLib

from .conf import _
from .settings import settings
from . import app_info
from . import fontlib
from . import tray


class MainWindow(Gtk.ApplicationWindow):

    _DND_URI = 0
    _DND_LIST = [Gtk.TargetEntry.new('text/uri-list', 0, _DND_URI),]

    def __init__(self, app, minimized=False):
        super().__init__(title=app_info.TITLE, application=app)

        self.connect('window-state-event', self._on_window_state_event)
        self.connect('destroy', self._on_window_destroy)

        self.drag_dest_set(
            Gtk.DestDefaults.ALL, self._DND_LIST, Gdk.DragAction.COPY)
        self.connect('drag_data_received', self._on_drag_data_received)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(box)

        main_menu = self._create_menubar()
        box.pack_start(main_menu, False, True, 0)

        self.paned = Gtk.Paned()
        self.paned.set_size_request(500, 250)
        box.pack_start(self.paned, True, True, 0)

        self.sets = fontlib.SetList()
        self.sets.load_sets()
        self.fonts = fontlib.FontList(self.sets)
        self.paned.pack1(self.sets, False, False)
        self.paned.pack2(self.fonts, True, False)

        box.show_all()

        self.tray = tray.Tray(self)

        action = Gio.SimpleAction.new_stateful(
            'minimized', None, GLib.Variant.new_boolean(not minimized))
        action.connect('activate', self._visibility_cb)
        action.connect('change_state', self._toggle_visibility_cb)
        self.add_action(action)

        try:
            if settings['window_maximized']:
                self.maximize()
            else:
                self.move(settings['window_x'], settings['window_y'])
                self.resize(
                    settings['window_width'], settings['window_height'])
        except (KeyError, TypeError):
            pass

        self.paned.set_position(
            settings.get('splitter_position', self.paned.get_position()))
        self.sets.selected_set = max(0, settings.get('selected_set', 1) - 1)

        if not minimized:
            self.show()

    def _create_menubar(self):
        ag = Gtk.AccelGroup()
        self.add_accel_group(ag)

        menubar = Gtk.MenuBar()

        # File.

        mi_file = Gtk.MenuItem.new_with_mnemonic(_('_File'))
        menubar.append(mi_file)
        file_menu = Gtk.Menu()
        mi_file.set_submenu(file_menu)

        mi_quit = Gtk.MenuItem(
            label=_('Quit'),
            action_name='app.quit')
        key, mod = Gtk.accelerator_parse('<Control>Q')
        mi_quit.add_accelerator(
            'activate', ag, key, mod, Gtk.AccelFlags.VISIBLE)
        file_menu.append(mi_quit)

        # Help.

        mi_help = Gtk.MenuItem.new_with_mnemonic(_('_Help'))
        menubar.append(mi_help)
        help_menu = Gtk.Menu()
        mi_help.set_submenu(help_menu)

        mi_about = Gtk.MenuItem(
            label=_('About'),
            action_name='app.about')
        help_menu.append(mi_about)

        return menubar

    def _visibility_cb(self, action, parameter):
        action.change_state(GLib.Variant.new_boolean(not action.get_state()))

    def _toggle_visibility_cb(self, action, state):
        if state:
            self.set_visible(True)
            self.present()
        else:
            self.set_visible(False)
        action.set_state(state)

    def _on_drag_data_received(self, widget, context, x, y, selection,
                               target, time):
        if target == self._DND_URI:
            font_set = self.fonts.font_set
            if not font_set:
                return
            paths = (GLib.filename_from_uri(uri)[0] for uri in
                     selection.get_uris() if uri.startswith('file://'))
            font_set.add_fonts(paths)

    def _on_window_state_event(self, widget, event):
        settings['window_maximized'] = bool(
            event.new_window_state & Gdk.WindowState.MAXIMIZED)

    def _on_window_destroy(self, window):
        self.sets.save_sets()
        settings['selected_set'] = self.sets.selected_set + 1
        settings['splitter_position'] = self.paned.get_position()
        settings['window_x'], settings['window_y'] = self.get_position()
        settings['window_width'], settings['window_height'] = self.get_size()
