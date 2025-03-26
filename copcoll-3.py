#!/usr/bin/env python
# -*- coding:Utf-8 -*- 


"""
Version basée sur GTK 2 :
    Auteur :      thuban (thuban@yeuxdelibad.net)  
    licence :     GNU General Public Licence v3
    Dépendances : python-gtk2

Version basée sur GTK 3 :
    Auteur :      Fedian4012 (francois.fedian.4012@free.fr)
    licence :     GNU General Public Licence v3
    Dépendances : python-gtk3

Description : Permet de copier rapidement des morceaux de texte prédéfinis

"""

from gi.repository import Gtk
import yaml

window = Gtk.Window()
window.set_title("CopColl")
window.set_default_size(400,300)
label = Gtk.Label(label='Bienvenue sur CopColl')
window.add(label)
window.show_all()
window.connect('delete-event', Gtk.main_quit)
Gtk.main()