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
import yaml  # Si tu veux intégrer YAML pour la configuration

class CopColl:
    def __init__(self):
        self.create_window()

    def create_window(self):
        # Crée une fenêtre principale
        window = Gtk.Window()
        window.set_title("CopColl")
        window.set_default_size(400, 300)

        # Crée un label à afficher dans la fenêtre
        label = Gtk.Label(label="Bienvenue sur CopColl")
        window.add(label)

        # Affiche tout
        window.show_all()

        # Gère l'événement de fermeture de la fenêtre
        window.connect('delete-event', self.close_application)

    def close_application(self, widget, event, data=None):
        # Ferme l'application quand l'événement de fermeture est déclenché
        Gtk.main_quit()

# Crée une instance de CopColl et lance l'application
copcoll = CopColl()

# Démarre la boucle principale de GTK
Gtk.main()