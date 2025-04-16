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

Description : Permet de copier/coller rapidement des morceaux de texte prédéfinis
"""

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import yaml
import notify2
import os

name = "copcoll"
config_file = os.path.expanduser("~/Repos Git/aciah_copcoll/new-config.yml")
window_width, window_height = 240, 300

class CopColl:
    categories_notebook: Gtk.Notebook = None

    def __init__(self, config_file):
        self.config = self.load_config_file(config_file)
        self.create_window()

    def load_config_file(self, file):
        try:
            with open(file, "r") as config_file:
                data = yaml.safe_load(config_file)
                if data is None:
                    data = {}
                return data
        except FileNotFoundError:
            data = [
                {
                    "title": "E-mails",
                    "values": [
                        {
                            "label": "E-mail asso ACIAH",
                            "text": "aciah@free.fr",
                            "alt": "L'e-mail officiel de l'association ACIAH"
                        }
                    ]
                }
            ]
            return data

    def save_config_file(self, file, content):
        try:
            with open(file, "w") as f:
                yaml.dump(
                    content,
                    f,
                    indent=2,
                    sort_keys=False,
                    allow_unicode=True
                )
        except Exception as e:
            print(f"Erreur: {e}")

    def create_window(self):
        self.window = Gtk.Window()
        self.window.set_title("CopColl")
        self.window.set_default_size(window_width, window_height)

        self.main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.categories_notebook = Gtk.Notebook()
        self.categories_notebook.set_tab_pos(Gtk.PositionType.LEFT)
        # self.categories_notebook.connect("switch-page", lambda notebook, page, page_number: self.get_notebook_page(notebook, page, page_number))

        self.main_vbox.pack_start(self.categories_notebook, True, True, 0)

        self.show_config_in_notebook()

        create_category_button = Gtk.Button(label="Créer une nouvelle catégorie")
        create_category_button.connect("clicked", lambda widget: self.dummy_func())
        self.main_vbox.pack_start(create_category_button, False, False, 10)

        self.window.add(self.main_vbox)

        self.window.connect('delete-event', Gtk.main_quit)

        self.window.show_all()

    def show_config_in_notebook(self):
        categories_list = []
        
        for i in range(len(self.config)):
            categ = self.config[i]
            categories_list.append(categ["title"])
            category_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

            for j in range(len(categ["values"])):
                item = categ["values"][j]
                label = item["label"]
                text = item["text"]
                alt = item["alt"]
                button = Gtk.Button(label=label)
                button.connect("clicked", lambda widget, text=str(text): self.set_clipboard(text))
                button.set_tooltip_text(str(alt))
                category_vbox.pack_start(button, False, False, 0)
            notebook_tab = categories_list[i]
            notebook_tab_label = Gtk.Label(label=notebook_tab)
            self.categories_notebook.append_page(category_vbox, notebook_tab_label)

    def notify(self, message, title="Texte copié"):
        notify2.init("CopColl")
        notification = notify2.Notification(title, message)
        notification.show()

    def set_clipboard(self, text):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)
        clipboard.store()
        self.notify(f'Le texte "{text}" a été copié dans le presse-papiers.')

    def reload(self):
        current_page = self.categories_notebook.get_current_page()
        while len(self.categories_notebook.get_children()) > 0:
            self.categories_notebook.remove_page(0)
        self.show_config_in_notebook()
        self.window.show_all()

    def dummy_func(self):
        print("Vous avez cliqué sur un bouton")

def main():
    app = CopColl(config_file)
    Gtk.main()

if __name__ == "__main__":
    main()
