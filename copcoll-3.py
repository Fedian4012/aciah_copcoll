#!/usr/bin/env python3
# -*- coding:Utf-8 -*- 

"""
Version basée sur Python 2 :
    Auteur :      thuban (thuban@yeuxdelibad.net)  
    licence :     GNU General Public Licence v3
    Dépendances : python-gtk2

Version basée sur Python 3 :
    Auteur :      Fedian4012 (francois.fedian.4012@free.fr)
    licence :     GNU General Public Licence v3
    Dépendances : pygobject, pyyaml, notify2

Description : Permet de copier rapidement des morceaux de texte prédéfinis

"""

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import yaml
import notify2

class CopColl:
    def __init__(self, config_file):
        self.config = self.load_config_file(config_file)
        self.create_window()

    def load_config_file(self, file):
        """Charge le fichier de configuration YAML"""
        try:
            with open(file, "r") as config_file:
                return yaml.safe_load(config_file)
        except FileNotFoundError:
            return {
                "raccourcis": {
                    "E-mail association Aciah": {"Aciah": "aciah@free.fr"}
                }
            }

    def create_window(self):
        """Crée la fenêtre principale et affiche la config dans l'UI"""
        self.window = Gtk.Window()
        self.window.set_title("CopColl")
        self.window.set_default_size(400, 300)

        # Crée une boîte verticale
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        # Affiche les informations de la config dans la fenêtre
        self.show_config_in_window(vbox)

        # Ajoute la boîte contenant les widgets à la fenêtre
        self.window.add(vbox)  # `add()` au lieu de `set_child()`

        # Gère l'événement de fermeture de la fenêtre
        self.window.connect('delete-event', Gtk.main_quit)

        # Affiche la fenêtre
        self.window.show_all()

    def show_config_in_window(self, vbox):
        """Affiche la configuration dans la fenêtre"""
        categories_list = list(self.config.keys())

        categories_notebook = Gtk.Notebook()
        categories_notebook.set_tab_pos(Gtk.PositionType.LEFT)
        vbox.pack_start(categories_notebook, True, True, 0)  # `pack_start()` au lieu de `append()`

        for category in categories_list:
            page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            page.set_homogeneous(False)  # Empêche les boutons de prendre toute la largeur

            # Récupération des données sous chaque catégorie
            category_data = self.config[category]
            for sub_key, sub_value in category_data.items():
                # Crée un bouton avec la clé comme libellé
                button = Gtk.Button(label=sub_key)

                # Connecte l'événement de clic à la fonction set_clipboard avec la valeur à copier
                button.connect("clicked", lambda widget, text=str(sub_value): self.set_clipboard(text))

                # Ajoute une marge de 10 px tout autour du bouton
                # Pour ceux qui se demandent, il n'y a pas d'attribut margin pour les quatre côtés à la fois comme en CSS
                button.set_margin_start(10)
                button.set_margin_end(10) 
                button.set_margin_bottom(10)
                button.set_margin_top(10)

                # Fixe une taille raisonnable pour les boutons
                button.set_size_request(200, -1)  # Ajuste la largeur des boutons, la hauteur s'adaptera

                # Ajoute le bouton au conteneur
                page.pack_start(button, False, False, 0)

            # Crée un label pour le titre de l'onglet
            label = Gtk.Label(label=category)
            categories_notebook.append_page(page, label)

    def notify(self, message, title="Texte copié"):
        """Affiche une notification avec notify2"""
        # Initialise la connexion avec le système de notification
        notify2.init("CopColl Notification")

        # Crée une notification
        notification = notify2.Notification(title, message)

        # Affiche la notification
        notification.show()

    def set_clipboard(self, text):
        """Met un texte défini dans le presse-papiers"""
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)
        clipboard.store()

        # Affiche la notification via notify2
        self.notify(f"Le texte \"{text}\" a été copié dans le presse-papiers.")
        

def main():
    """Lance l'application GTK 3"""
    app = CopColl("config.yml")
    Gtk.main()

if __name__ == "__main__":
    main()
