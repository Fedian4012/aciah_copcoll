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


    def show_config_in_window(self, vbox):
        """Affiche la configuration dans la fenêtre"""
        categories_list = list(self.config.keys())

        categories_notebook = Gtk.Notebook()
        categories_notebook.set_tab_pos(Gtk.PositionType.LEFT)
        vbox.pack_start(categories_notebook, True, True, 0)

        for category in categories_list:
            page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

            # Récupération des données sous chaque catégorie
            category_data = self.config[category]

            # Cas de la catégorie vide
            if not category_data:
                label = Gtk.Label(label="Cette catégorie est vide")
                page.pack_start(label, False, False, 0)

            else:
                for sub_key, sub_value in category_data.items():
                    
                    # Crée une hbox pour les fonctions de suppression et édition
                    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

                    # Crée un bouton avec la clé comme libellé
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

                    # Crée un bouton pour l'édition
                    edit_button = Gtk.Button()
                    edit_icon = Gtk.Image.new_from_icon_name("edit", Gtk.IconSize.BUTTON)  # "edit" est l'icône du stylo
                    edit_button.set_image(edit_icon)

                    edit_button.set_margin_start(10) 
                    edit_button.set_margin_end(10)   
                    edit_button.set_margin_bottom(10)                   
                    edit_button.set_margin_top(10) 

                    hbox.pack_end(edit_button, False, False, 0)

                    # Créer un bouton avec une icône de poubelle (pour supprimer)
                    delete_button = Gtk.Button()
                    delete_icon = Gtk.Image.new_from_icon_name("trash", Gtk.IconSize.BUTTON)  # "trash" est l'icône de la poubelle
                    delete_button.set_image(delete_icon)
                    hbox.pack_end(delete_button, False, False, 0)

                    delete_button.set_margin_start(10) 
                    delete_button.set_margin_end(10)   
                    delete_button.set_margin_bottom(10)                   
                    delete_button.set_margin_top(10)
                    
                    # Ajoute les boutons au conteneur
                    page.pack_start(hbox, False, False, 0)

            # Crée un label pour le titre de l'onglet
            hbox_for_notebook = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            category_name_label = Gtk.Label(label=category)
            hbox_for_notebook.pack_start(category_name_label, False, False, 0)
            
            # Crée un bouton pour l'édition
            edit_button = Gtk.Button()
            edit_icon = Gtk.Image.new_from_icon_name("edit", Gtk.IconSize.BUTTON)  # "edit" est l'icône du stylo
            edit_button.set_image(edit_icon)
            edit_button.set_margin_start(10) 
            edit_button.set_margin_end(10)   
            edit_button.set_margin_bottom(10)                   
            edit_button.set_margin_top(10) 
            hbox_for_notebook.pack_end(edit_button, False, False, 0)
            
            # Créer un bouton avec une icône de poubelle (pour supprimer)
            delete_button = Gtk.Button()
            delete_icon = Gtk.Image.new_from_icon_name("trash", Gtk.IconSize.BUTTON)  # "trash" est l'icône de la poubelle
            delete_button.set_image(delete_icon)
            delete_button.set_margin_start(10) 
            delete_button.set_margin_end(10)   
            delete_button.set_margin_bottom(10)                   
            delete_button.set_margin_top(10)
            hbox_for_notebook.pack_end(delete_button, False, False, 0)
            
            hbox_for_notebook.show_all()
            categories_notebook.append_page(page, hbox_for_notebook)

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
