
from gettext import gettext as _
import os

from gi.repository import Gtk

from . import common
from . import app_info
from .settings import settings
from . import utils


def yesno(message, parent):
    dialog = Gtk.MessageDialog(
        parent, 0, Gtk.MessageType.QUESTION,
        Gtk.ButtonsType.YES_NO, message)
    response = dialog.run()
    dialog.destroy()
    return response == Gtk.ResponseType.YES


def about(parent):
    dialog = Gtk.AboutDialog(
        program_name=app_info.TITLE,
        logo_icon_name=app_info.ICON,
        version=app_info.VERSION,
        comments=_('Install fonts temporarily'),
        website=app_info.WEBSITE,
        website_label=app_info.WEBSITE,
        copyright=app_info.COPYRIGHT,
        license=app_info.LICENSE,

        parent=parent,
        transient_for=parent,
        destroy_with_parent=True
        )

    dialog.run()
    dialog.destroy()


def open_fonts(parent):
    font_filter = Gtk.FileFilter()
    font_filter.set_name(_('Fonts'))
    for ext in common.FONT_EXTENSIONS:
        font_filter.add_pattern(utils.ext_to_glob(ext))

    dialog = Gtk.FileChooserDialog(
        _('Choose fonts'),
        parent,
        Gtk.FileChooserAction.OPEN,
        (_('_Cancel'), Gtk.ResponseType.CANCEL,
         _('_Open'), Gtk.ResponseType.OK),
        select_multiple=True,
        )
    dialog.add_filter(font_filter)
    dialog.set_current_folder(
        settings.setdefault('last_dir', os.path.expanduser('~')))

    if dialog.run() == Gtk.ResponseType.OK:
        font_paths = dialog.get_filenames()
        settings['last_dir'] = dialog.get_current_folder()
    else:
        font_paths = []
    dialog.destroy()

    return font_paths

