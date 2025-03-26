#!/usr/bin/env python3

"""
Version basée sur GTK 2 :
    Auteur :      thuban (thuban@yeuxdelibad.net)  
    licence :     GNU General Public Licence v3
    Dépendances : python-gtk2

Version basée sur GTK 3 :
    Auteur :      Fedian4012 (francois.fedian.4012@free.fr)
    licence :     GNU General Public Licence v3
    Dépendances : python3-pygobject, python3-pyyaml

Description : Permet de copier rapidement des morceaux de texte prédéfinis

"""

from gi.repository import Gtk
import yaml

class CopColl:
    def __init__(self, config_file):
        self.config = self.load_config_file(config_file)
        self.create_window()

    def load_config_file(self, file):
        """Charge le fichier de configuration YAML"""
        try:
            with open(file, "r") as config_file:
                config = yaml.safe_load(config_file)
        except FileNotFoundError:
            config = {
                "E-mail association Aciah": "aciah@free.fr"
            }
        return config

    def create_window(self):
        """Crée la fenêtre principale et affiche la config dans l'UI"""
        window = Gtk.Window()
        window.set_title("CopColl")
        window.set_default_size(400, 300)

        # Crée une boîte verticale (Box moderne avec GTK3)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Affiche les informations de la config dans la fenêtre
        self.show_config_in_window(vbox)

        # Ajoute la boîte contenant les widgets à la fenêtre
        window.add(vbox)

        # Affiche la fenêtre
        window.show_all()

        # Gère l'événement de fermeture de la fenêtre
        window.connect('delete-event', self.close_application)

    def show_config_in_window(self, vbox):
        """Affiche la configuration dans la fenêtre"""
        # Crée un label pour chaque élément de la config
        for key, value in self.config.items():
            config_label = Gtk.Label(label=f"{key}: {value}")
            vbox.pack_start(config_label, True, True, 0)

    def close_application(self, widget=None, event=None, data=None):
        """Ferme l'application"""
        Gtk.main_quit()

def main():   
    # Crée une instance de CopColl et lance l'application
    copcoll = CopColl("config.yml")

    # Démarre la boucle principale de GTK
    Gtk.main()

if __name__ == "__main__":
    main()
