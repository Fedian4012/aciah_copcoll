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

NAME = "copcoll"
CONFIG = os.path.expanduser("~/Repos Git/aciah_copcoll/config.yml")
W,H = 240, 300 # largeur et hauteur

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
                    data = {}  # Très important : fichier vide = dictionnaire vide
                return data
        except FileNotFoundError:
            return {
                "E-mails": {
                    "Association ACIAH": "aciah@free.fr"
                }
            }

    def save_config_file(self, file, content):
        """Sauvegarde le fichier de configuration"""
        try:
            with open(file, "w") as f:
                yaml.dump(
                        content,
                        f, 
                        indent=2, 
                        sort_keys=False, 
                        allow_unicode=True
                        )

                """Voici quelques infos sur les paramètres passés à yaml.dump :
                    - indent=2 permet de définir les niveaux d'indentation à deux espaces de différence
                    - sort_keys=False permet de ne pas trier les clés dans l'ordre alphabétique
                    - allow_unicode=True permet de supporter les caractères spéciaux
                """
        except Exception as e:
            print(f"Erreur: {e}")

    def create_window(self):
        """Crée la fenêtre principale et affiche la config dans l'interface"""
        self.window = Gtk.Window()
        self.window.set_title("CopColl")
        self.window.set_default_size(W, H)

        # Crée une boîte verticale principale
        self.main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Crée le notebook pour les catégories
        self.categories_notebook = Gtk.Notebook()
        self.categories_notebook.set_tab_pos(Gtk.PositionType.LEFT)
        self.categories_notebook.connect("switch-page", lambda notebook, page, page_number: self.get_notebook_page(notebook, page, page_number))

        self.main_vbox.pack_start(self.categories_notebook, True, True, 0)

        # Affiche les informations de la config dans le notebook
        self.show_config_in_notebook()

        # Bouton global pour créer une nouvelle catégorie
        create_category_button = Gtk.Button(label="Créer une nouvelle catégorie")
        create_category_button.connect("clicked", lambda widget: self.pop_up_to_create_category())
        self.main_vbox.pack_start(create_category_button, False, False, 10)

        # Ajoute la boîte principale à la fenêtre
        self.window.add(self.main_vbox)

        # Connecte l'événement de fermeture de la fenêtre
        self.window.connect('delete-event', Gtk.main_quit)

        # Affiche la fenêtre
        self.window.show_all()

    def show_config_in_notebook(self):
        """Affiche la configuration dans le notebook"""

        # Crée une liste de correspondances pour les catégories
        self.page_num_to_category = []
        
        for category in self.config.keys():
            # Crée une VBox pour la page de la catégorie
            category_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            self.page_num_to_category.append(category)
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
                    edit_button.connect("clicked", lambda widget, category=category: self.pop_up_to_edit_button(category))
                    hbox.pack_end(edit_button, False, False, 0)

                    # Bouton supprimer
                    delete_button = Gtk.Button()
                    delete_icon = Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.BUTTON)
                    delete_button.set_image(delete_icon)
                    delete_button.connect("clicked", lambda widget, category=category, sub_key=sub_key: self.confirm_for_delete_button(category, sub_key))
                    hbox.pack_end(delete_button, False, False, 0)

                    category_vbox.pack_start(hbox, False, False, 0)

            # Bouton pour ajouter un nouveau bouton dans cette catégorie
            create_button = Gtk.Button(label="Ajouter un nouveau bouton")
            create_button.connect(
                "clicked",
                lambda widget: self.pop_up_to_create_button(
                    self.page_num_to_category[self.categories_notebook.get_current_page()]
                )
            )

            category_vbox.pack_end(create_button, False, False, 10)

            # Ajoute la page au notebook
            label = Gtk.Label(label=category)
            self.categories_notebook.append_page(category_vbox, label)

    def get_notebook_page(self, notebook, page, page_number):
        category_name = self.page_num_to_category[page_number]
        return category_name

    def pop_up_to_create_button(self, category):
        """Affiche une boîte de dialogue pour ajouter un nouveau bouton dans la catégorie spécifiée"""
        dialog = Gtk.Dialog(title="Nouveau bouton", parent=self.window, flags=0)
        dialog.set_default_size(400, 200)

        # Conteneur principal de la boîte de dialogue
        content_area = dialog.get_content_area()

        # Première ligne : labels
        labels_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title_label = Gtk.Label(label="Titre")
        rac_label = Gtk.Label(label="Nouveau texte")
        rac_label.set_size_request(150, -1)
        labels_box.pack_start(title_label, True, True, 5)
        labels_box.pack_start(rac_label, True, True, 5)
        content_area.pack_start(labels_box, False, False, 5)

        # Deuxième ligne : champs de saisie
        entries_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title_entry = Gtk.Entry()
        rac_textview = Gtk.TextView()
        rac_textview.set_size_request(150, -1)
        entries_box.pack_start(title_entry, True, True, 5)
        entries_box.pack_start(rac_textview, True, True, 5)
        content_area.pack_start(entries_box, False, False, 5)

        # Bouton d'ajout
        add_button = Gtk.Button(label="Ajouter")
        add_button.connect(
        "clicked",
        self.add_to_config,
        title_entry,
        rac_textview,
        category,
        dialog
        )   
        content_area.pack_start(add_button, False, False, 10)

        dialog.show_all()

    def add_to_config(self, button, title_entry, rac_textview, category, dialog):
        """Crée le nouveau bouton grâce aux données de la pop-up"""
        title = title_entry.get_text()
        buffer = rac_textview.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        content = buffer.get_text(start_iter, end_iter, True)

        if not title.strip() or not content.strip():
            print("Titre ou contenu vide.")
            return

        if not isinstance(self.config.get(category), dict):
            self.config[category] = {}

        self.config[category][title] = content
        self.save_config_file(CONFIG, self.config)
        self.reload()
        dialog.destroy()

    def confirm_for_delete_button(self, category, button):
        dialog = Gtk.MessageDialog(
            parent=self.window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Confirmation requise",
        )
        dialog.format_secondary_text("Êtes-vous sûr de vouloir supprimer ce bouton ?")

        response = dialog.run()

        if response == Gtk.ResponseType.YES:
            self.delete_button(category, button)
        else:
            return

        dialog.destroy()
    
    def delete_button(self, category, button):
        try:
            del self.config[category][button]
            self.reload()
        except KeyError:
            print(f"La clé {button} dans la catégorie {category} n'existe pas, rien n'a été supprimé")
    
    def pop_up_to_create_category(self):
        """Affiche une boîte de dialogue pour ajouter une nouvelle catégorie"""
        dialog = Gtk.Dialog(title="Nouvelle catégorie", parent=self.window, flags=0)
        dialog.set_default_size(400, 200)

        # Conteneur principal de la boîte de dialogue
        content_area = dialog.get_content_area()

        # Première ligne : labels
        labels_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        category_label = Gtk.Label(label="Nom de la catégorie")
        category_label.set_size_request(150, -1)
        labels_box.pack_start(category_label, True, True, 5)
        content_area.pack_start(labels_box, False, False, 5)

        # Deuxième ligne : champ de saisie
        entries_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        category_entry = Gtk.Entry()
        category_entry.set_size_request(150, -1)
        entries_box.pack_start(category_entry, True, True, 5)
        content_area.pack_start(entries_box, False, False, 5)

        # Bouton d'ajout
        add_button = Gtk.Button(label="Ajouter")
        add_button.connect(
            "clicked",
            self.add_category_to_config,
            category_entry,
            dialog
        )   
        content_area.pack_start(add_button, False, False, 10)

        dialog.show_all()

    def add_category_to_config(self, button, category_entry, dialog):
        """Ajoute la nouvelle catégorie au dictionnaire de config"""
        category_name = category_entry.get_text()

        if not category_name.strip():
            print("Le nom de la catégorie ne peut pas être vide.")
            return

        if category_name not in self.config:
            # Ajoute la nouvelle catégorie avec un dictionnaire vide comme valeur
            self.config[category_name] = {}
            self.save_config_file(CONFIG, self.config)
            self.reload()
            dialog.destroy()  # Ferme la boîte de dialogue après l'ajout
        else:
            print(f"La catégorie '{category_name}' existe déjà.")

    def pop_up_to_edit_button(self, category):
        """Affiche une boîte de dialogue pour ajouter un nouveau bouton dans la catégorie spécifiée"""
        dialog = Gtk.Dialog(title="Éditer le bouton", parent=self.window, flags=0)
        dialog.set_default_size(400, 200)

        # Conteneur principal de la boîte de dialogue
        content_area = dialog.get_content_area()

        # Première ligne : labels
        labels_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title_label = Gtk.Label(label="Titre")
        rac_label = Gtk.Label(label="Nouveau texte")
        rac_label.set_size_request(150, -1)
        labels_box.pack_start(title_label, True, True, 5)
        labels_box.pack_start(rac_label, True, True, 5)
        content_area.pack_start(labels_box, False, False, 5)

        # Deuxième ligne : champs de saisie
        entries_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        title_entry = Gtk.Entry()
        rac_textview = Gtk.TextView()
        rac_textview.set_size_request(150, -1)
        entries_box.pack_start(title_entry, True, True, 5)
        entries_box.pack_start(rac_textview, True, True, 5)
        content_area.pack_start(entries_box, False, False, 5)

        # Bouton d'ajout
        add_button = Gtk.Button(label="Ajouter")
        add_button.connect(
        "clicked",
        self.edit_button_in_config,
        title_entry,
        rac_textview,
        category,
        dialog
        )   
        content_area.pack_start(add_button, False, False, 10)

        dialog.show_all()

    def edit_button_in_config(self, button, title_entry, rac_textview, category, dialog):
        """Crée le nouveau bouton grâce aux données de la pop-up"""
        title = title_entry.get_text()
        buffer = rac_textview.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        content = buffer.get_text(start_iter, end_iter, True)

        if not title.strip() or not content.strip():
            print("Titre ou contenu vide.")
            return

        if not isinstance(self.config.get(category), dict):
            self.config[category] = {}

        self.delete_button(category, title)
        self.config[category][title] = content
        self.save_config_file(CONFIG, self.config)
        self.reload()
        dialog.destroy()
        

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

    def reload(self):
        """Réinitialise le contenu du vbox et recharge les éléments du notebook."""
        current_page = self.categories_notebook.get_current_page()
        while len(self.categories_notebook.get_children()) > 0:
            self.categories_notebook.remove_page(0)
        self.show_config_in_notebook()
        self.window.show_all()

def main():
    """Lance l'application GTK 3"""
    app = CopColl(CONFIG)
    Gtk.main()

if __name__ == "__main__":
    main()
