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

class CopColl:
    def __init__(self):
        self.create_window()

    def create_window(self):
        # Crée la fenêtre principale
        window = Gtk.Window()
        window.set_title("CopColl avec Label et Button")
        window.set_default_size(400, 300)

        # Crée une boîte verticale (VBox) pour contenir les widgets
        vbox = Gtk.VBox(spacing=10)

        # Crée un label et un bouton
        label = Gtk.Label(label='Bienvenue sur CopColl')
        button = Gtk.Button(label="Fermer la fenêtre")

        # Connecte le bouton à une fonction pour fermer la fenêtre
        button.connect("clicked", self.close_application)

        # Ajoute le label et le bouton à la boîte verticale
        vbox.pack_start(label, True, True, 0)
        vbox.pack_start(button, True, True, 0)

        # Ajoute la boîte à la fenêtre
        window.add(vbox)

        # Affiche la fenêtre
        window.show_all()

        # Gère l'événement de fermeture de la fenêtre (pour le bouton de la fenêtre)
        window.connect('delete-event', self.close_application)

    def close_application(self, widget=None, event=None, data=None):
        Gtk.main_quit()

# Crée une instance de CopColl et lance l'application
copcoll = CopColl()

# Démarre la boucle principale de GTK
Gtk.main()
