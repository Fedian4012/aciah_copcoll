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
    Dépendances : pygobject, pyyaml, notify2, dbus (dépendance de notify2)

Description : Permet de copier/coller rapidement des morceaux de texte prédéfinis

"""

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import yaml
import notify2
import os

NAME = "copcoll"
CONFIG = os.path.expanduser("~/Repos Git/aciah_copcoll/config.yml")
W,H = 240, 300 # largeur et hauteur

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
                "E-mails": {
                    "Association ACIAH": "aciah@free.fr"
                }
            }

    def save_config_file(self, file, content):
        try:
            with open(file, "w"):
                yaml.dump_all(content, indent=2)
        except Exception as e:
            print(f"Erreur: {e}")

    def create_window(self):
        """Crée la fenêtre principale et affiche la config dans l'UI"""
        self.window = Gtk.Window()
        self.window.set_title("CopColl")
        self.window.set_default_size(W, H)

        # Crée une boîte verticale
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        # Affiche les informations de la config dans la fenêtre
        self.show_config_in_window(self.vbox)

        # Ajoute la boîte contenant les widgets à la fenêtre
        self.window.add(self.vbox)  # `add()` au lieu de `set_child()`

        # Gère l'événement de fermeture de la fenêtre
        self.window.connect('delete-event', Gtk.main_quit)

        # Affiche la fenêtre
        self.window.show_all()

    def create_window(self):
        """Crée la fenêtre principale et affiche la config dans l'interface"""
        self.window = Gtk.Window()
        self.window.set_title("CopColl")
        self.window.set_default_size(W, H)

        # Crée une boîte verticale
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        # Affiche les informations de la config dans la fenêtre
        self.show_config_in_window(self.vbox)

        # Ajoute la boîte contenant les widgets à la fenêtre
        self.window.add(self.vbox)

        # Gère l'événement de fermeture de la fenêtre
        self.window.connect('delete-event', Gtk.main_quit)

        # Affiche la fenêtre
        self.window.show_all()

    def create_window(self):
        """Crée la fenêtre principale et affiche la config dans l'interface"""
        self.window = Gtk.Window()
        self.window.set_title("CopColl")
        self.window.set_default_size(W, H)

        # Crée une boîte verticale principale
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Crée le notebook pour les catégories
        self.categories_notebook = Gtk.Notebook()
        self.categories_notebook.set_tab_pos(Gtk.PositionType.LEFT)
        main_vbox.pack_start(self.categories_notebook, True, True, 0)

        # Affiche les informations de la config dans le notebook
        self.show_config_in_notebook()

        # Bouton global pour créer une nouvelle catégorie
        create_category_button = Gtk.Button(label="Créer une nouvelle catégorie")
        create_category_button.connect("clicked", self.dummy_function)
        main_vbox.pack_start(create_category_button, False, False, 10)

        # Ajoute la boîte principale à la fenêtre
        self.window.add(main_vbox)

        # Connecte l'événement de fermeture de la fenêtre
        self.window.connect('delete-event', Gtk.main_quit)

        # Affiche la fenêtre
        self.window.show_all()

    def show_config_in_notebook(self):
        """Affiche la configuration dans le notebook"""
        for category in self.config.keys():
            # Crée une VBox pour la page de la catégorie
            category_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

            category_data = self.config[category]

            if not category_data:
                label = Gtk.Label(label="Cette catégorie est vide")
                category_vbox.pack_start(label, False, False, 0)
            else:
                for sub_key, sub_value in category_data.items():
                    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

                    button = Gtk.Button(label=sub_key)

                    # Ajoute des marges autour des boutons
                    # Il n'y a pas d'attribut margin comme en CSS
                    button.set_margin_start(10)  # Marge à gauche
                    button.set_margin_end(10)    # Marge à droite
                    button.set_margin_bottom(10) # Marge en bas
                    button.set_margin_top(10)    # Marge en haut

                    # Connecte l'événement de clic à la fonction set_clipboard avec la valeur à copier
                    button.connect("clicked", lambda widget, text=str(sub_value): self.set_clipboard(text))
                    
                    # Ajoute le bouton au début du container
                    hbox.pack_start(button, False, False, 0)

                    # Bouton éditer
                    edit_button = Gtk.Button()
                    edit_icon = Gtk.Image.new_from_icon_name("document-edit", Gtk.IconSize.BUTTON)
                    edit_button.set_image(edit_icon)
                    edit_button.connect("clicked", self.dummy_function)
                    hbox.pack_end(edit_button, False, False, 0)

                    # Bouton supprimer
                    delete_button = Gtk.Button()
                    delete_icon = Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.BUTTON)
                    delete_button.set_image(delete_icon)
                    delete_button.connect("clicked", self.dummy_function)
                    hbox.pack_end(delete_button, False, False, 0)

                    category_vbox.pack_start(hbox, False, False, 0)

            # Bouton pour ajouter un nouveau bouton dans cette catégorie
            create_button = Gtk.Button(label="Ajouter un nouveau bouton")
            create_button.connect("clicked", self.dummy_function)
            category_vbox.pack_end(create_button, False, False, 10)

            # Ajoute la page au notebook
            label = Gtk.Label(label=category)
            self.categories_notebook.append_page(category_vbox, label)

    def dummy_function(self, widget):
        """Fonction temporaire pour les boutons vides"""
        print(f"Bouton cliqué : {widget.get_label() or 'Icône'}")
    
    def notify(self, message, title="Texte copié"):
        """Affiche une notification avec notify2"""
        # Initialise la connexion avec le système de notification
        notify2.init("CopColl")

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

    def reload(self, vbox):
        for widget in vbox.get_children():
            vbox.remove(widget)
        self.show_config_in_window(vbox)

def main():
    """Lance l'application GTK 3"""
    app = CopColl(CONFIG)
    Gtk.main()

if __name__ == "__main__":
    main()
