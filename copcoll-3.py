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
config_file = os.path.expanduser("~/Repos Git/aciah_copcoll/config.yml")
window_width, window_height = 240, 300

class CopColl(Gtk.Window):
    # categories_notebook: Gtk.Notebook = None

    def __init__(self, config_file):
        super().__init__()
        self.set_title("CopColl")
        self.set_default_size(window_width, window_height)

        self.main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.categories_notebook = Gtk.Notebook()
        self.categories_notebook.set_tab_pos(Gtk.PositionType.LEFT)

        self.main_vbox.pack_start(self.categories_notebook, True, True, 0)

        self.config = self.load_config_file(config_file)
        self.show_config_in_notebook()

        create_category_button = Gtk.Button(label="Créer une nouvelle catégorie")
        create_category_button.connect("clicked", lambda widget: self.dummy_func())
        self.main_vbox.pack_end(create_category_button, True, True, 0)

        self.add(self.main_vbox)

        self.connect('delete-event', Gtk.main_quit)

        self.show_all()

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
        with open(file, "w") as f:
            yaml.dump(
                content,
                f,
                indent=2,
                sort_keys=False,
                allow_unicode=True
            )  

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
            
            create_button = Gtk.Button(label="Ajouter un nouveau bouton")
            create_button.connect("clicked", lambda widget: self.pop_up_to_create_button(widget))
            category_vbox.pack_end(create_button, False, False, 0)
            notebook_tab = categories_list[i]
            notebook_tab_label = Gtk.Label(label=notebook_tab)
            self.categories_notebook.append_page(category_vbox, notebook_tab_label)
    
    def pop_up_to_create_button(self, widget):
        current_category = self.categories_notebook.get_current_page()
        dialog = Gtk.Dialog(title="Ajouter un raccourci", transient_for=self, flags=0)
        dialog.set_default_size(400, 300)

        content_area = dialog.get_content_area()
        
        # Conteneur vertical pour le formulaire
        vbox_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_form.set_margin_top(10)
        vbox_form.set_margin_bottom(10)
        vbox_form.set_margin_start(10)
        vbox_form.set_margin_end(10)

        # === Champ Titre ===
        title_label = Gtk.Label(label="Titre")
        title_label.set_xalign(0)
        title_entry = Gtk.Entry()
        title_entry.set_tooltip_text("Nouveau titre")
        vbox_form.pack_start(title_label, False, False, 0)
        vbox_form.pack_start(title_entry, False, False, 0)

        # === Champ Nouveau texte ===
        associated_text_label = Gtk.Label(label="Nouveau texte")
        associated_text_label.set_xalign(0)
        associated_text_entry = Gtk.TextView()
        associated_text_entry.set_size_request(-1, 100)  # Largeur auto, hauteur fixe
        vbox_form.pack_start(associated_text_label, False, False, 0)
        vbox_form.pack_start(associated_text_entry, False, False, 0)

        # === Champ Infobulle ===
        tooltip_text_label = Gtk.Label(label="Nouvelle infobulle")
        tooltip_text_label.set_xalign(0)
        tooltip_text_entry = Gtk.Entry()
        tooltip_text_entry.set_tooltip_text("Texte qui s'affichera au survol")
        vbox_form.pack_start(tooltip_text_label, False, False, 0)
        vbox_form.pack_start(tooltip_text_entry, False, False, 0)

        # Ajout du formulaire au contenu
        content_area.add(vbox_form)

        # === Bouton Ajouter ===
        add_button = Gtk.Button(label="Ajouter")
        add_button.connect(
            "clicked",
            self.add_button_into_config,
            title_entry,
            associated_text_entry,
            tooltip_text_entry,
            current_category,
            dialog
        )
        content_area.pack_start(add_button, False, False, 10)

        dialog.show_all()

    def add_button_into_config(self, button, title_entry, associated_text_entry, tooltip_entry, category, dialog):
        title = title_entry.get_text()

        # Pour TextView, on récupère le buffer
        buffer = associated_text_entry.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        text = buffer.get_text(start_iter, end_iter, True)

        tooltip = tooltip_entry.get_text()

        new_button = {
            "label": title,
            "text": text,
            "alt": tooltip
        }
        
        # print(category)
        self.config[category]["values"].append(new_button)
        
        self.save_config_file(config_file, self.config)
        self.reload()

        dialog.destroy()

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
        # current_page = self.categories_notebook.get_current_page()
        while len(self.categories_notebook.get_children()) > 0:
            self.categories_notebook.remove_page(0)
        self.show_config_in_notebook()
        self.window.show_all()

    def dummy_func(self):
        print("Vous avez cliqué sur un bouton")

def main():
    app = CopColl(config_file) # On crée une instance de l'appli
    Gtk.main()

if __name__ == "__main__":
    main()
