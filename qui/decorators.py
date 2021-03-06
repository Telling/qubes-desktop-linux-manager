#!/usr/bin/env python3
''' Decorators wrap a `qui.models.PropertiesModel` in a class
containing helpful representation methods.
'''
# pylint: disable=wrong-import-position,import-error

import qubesadmin
import gi  # isort:skip
gi.require_version('Gtk', '3.0')  # isort:skip
from gi.repository import Gtk, Pango  # isort:skip



class PropertiesDecorator():
    ''' Base class for all decorators '''

    # pylint: disable=too-few-public-methods

    def __init__(self, obj, margins=(5, 5)) -> None:
        self.obj = obj
        self.margin_left = margins[0]
        self.margin_right = margins[1]
        super(PropertiesDecorator, self).__init__()

    def set_margins(self, widget):
        ''' Helper for setting the default margins on a widget '''
        widget.set_margin_left(self.margin_left)
        widget.set_margin_right(self.margin_right)


class DomainDecorator(PropertiesDecorator):
    ''' Useful methods for domain data representation '''

    def __init__(self, vm: qubesadmin.vm.QubesVM, margins=(5, 5)) -> None:
        super(DomainDecorator, self).__init__(vm, margins)
        self.vm = vm

    def name(self):
        label = Gtk.Label(self.vm.name, xalign=0)
        self.set_margins(label)
        return label

    def memory(self, memory=0) -> Gtk.Label:
        label = Gtk.Label(
            str(int(memory / 1024)) + ' MB', xalign=0)
        self.set_margins(label)
        label.set_sensitive(False)
        return label

    def icon(self) -> Gtk.Image:
        ''' Returns a `Gtk.Image` containing the colored lock icon '''
        try:
            # this is a temporary, emergency fix for unexecpected conflict with
            # qui-devices rewrite
            icon = self.vm.icon
        except AttributeError:
            icon = self.vm.label.icon
        icon_vm = Gtk.IconTheme.get_default().load_icon(
            icon, 16, 0)
        icon_img = Gtk.Image.new_from_pixbuf(icon_vm)
        return icon_img

    def netvm(self) -> Gtk.Label:
        netvm = self.vm.netvm
        if netvm is None:
            label = Gtk.Label('No', xalign=0)
        else:
            label = Gtk.Label(netvm.name, xalign=0)

        self.set_margins(label)
        return label


def device_hbox(device) -> Gtk.Box:
    ''' Returns a :class:`Gtk.Box` containing the device name & icon.. '''
    if device.devclass == 'block':
        icon = 'drive-removable-media'
    elif device.devclass == 'mic':
        icon = 'audio-input-microphone'
    elif device.devclass == 'usb':
        icon = 'generic-usb'
    else:
        icon = 'emblem-important'
    dev_icon = create_icon(icon)

    name_label = Gtk.Label(xalign=0)
    name = "{}:{} - {}".format(device.backend_domain, device.ident,
                               device.description)
    if device.attachments:
        name_label.set_markup('<b>{} ({})</b>'.format(
            name, ", ".join([vm for vm in device.attachments])))
    else:
        name_label.set_text(name)
    name_label.set_max_width_chars(64)
    name_label.set_ellipsize(Pango.EllipsizeMode.END)

    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    hbox.pack_start(name_label, True, True, 0)
    hbox.pack_start(dev_icon, False, True, 0)
    return hbox


def device_domain_hbox(vm, attached: bool) -> Gtk.Box:
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

    # hbox.pack_start(label, True, True, 5)

    if attached:
        eject_icon = create_icon('media-eject')
        hbox.pack_start(eject_icon, False, False, 5)
    else:
        add_icon = create_icon('list-add')
        hbox.pack_start(add_icon, False, False, 5)

    name = Gtk.Label(xalign=0)
    if attached:
        name.set_markup('<b>{}</b>'.format(vm.vm_name))
    else:
        name.set_text(vm.vm_name)

    hbox.pack_start(name, True, True, 5)
    return hbox


def create_icon(name) -> Gtk.Image:
    ''' Create an icon from string '''
    icon_dev = Gtk.IconTheme.get_default().load_icon(name, 16, 0)
    return Gtk.Image.new_from_pixbuf(icon_dev)
