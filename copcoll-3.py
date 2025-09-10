"""
Version basée sur Python 2 :
    Auteur :      thuban (thuban@yeuxdelibad.net)
    Licence :     GNU General Public Licence v3
    Dépendances : python-gtk2

Version basée sur Python 3 :
    Auteur :      Fedian4012 (francois.fedian.4012@free.fr)
    Licence :     GNU General Public Licence v3
    Dépendances : python3-gi, python3-yaml, python3-notify2

Description : Permet de copier/coller rapidement des morceaux de texte prédéfinis
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

import os
from functools import partial

import notify2
import yaml

config_file = os.path.expanduser("~/Repos Git/aciah_copcoll/config.yml")
CSS_FILE = os.path.expanduser("~/Repos Git/aciah_copcoll/style.css")

# ce texte à propos de CopColl est provisoire
TEXTE_A_PROPOS = """
Version basée sur Python 2 :
    Auteur :      thuban (thuban@yeuxdelibad.net)
    Licence :     GNU General Public Licence v3
    Dépendances : python-gtk2

Version basée sur Python 3 :
    Auteur :      Fedian4012 (francois.fedian.4012@free.fr)
    Licence :     GNU General Public Licence v3
    Dépendances : python3-gi, python3-yaml, python3-notify2

Description : Permet de copier/coller rapidement des morceaux de texte prédéfinis
"""

class CopColl(Gtk.Window):
    def __init__(self, config_file):
        super().__init__(title="CopColl")
        self.set_default_size(240, 300)

        css_applier = Gtk.CssProvider()
        css_applier.load_from_path(CSS_FILE)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_applier,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Création de la barre de menu
        menubar = Gtk.MenuBar()
        menubar.get_style_context().add_class("barre-menus")
        menu_aide = Gtk.Menu()
        item_aide = Gtk.MenuItem(label="Aide")
        item_aide.get_style_context().add_class("menu")
        item_aide.set_submenu(menu_aide)

        # Item "À propos de CopColl"
        item_apropos = Gtk.MenuItem(label="À propos de CopColl")
        item_apropos.connect("activate", self.afficher_a_propos)
        menu_aide.append(item_apropos)

        menubar.append(item_aide)
        self.main_vbox.pack_start(menubar, False, False, 0)

        self.categories_notebook = Gtk.Notebook()
        self.categories_notebook.set_tab_pos(Gtk.PositionType.LEFT)
        self.categories_notebook.set_scrollable(True)
        self.main_vbox.pack_start(self.categories_notebook, True, True, 0)

        self.config = self.load_config_file(config_file)
        self.show_config_in_notebook()

        create_category_button = Gtk.Button(label="Créer une nouvelle catégorie")
        create_category_button.get_style_context().add_class("bouton")
        create_category_button.connect("clicked", partial(self.pop_up_to_create_category))
        self.main_vbox.pack_end(create_category_button, True, True, 0)

        self.add(self.main_vbox)

        notify2.init("CopColl") # connexion une fois pour toutes au système de notifications

    def load_config_file(self, file):
        default_value = [
                {
                    "title": "ACIAH",
                    "values": [
                        {
                            "label": "E-mail",
                            "text": "aciah@free.fr",
                            "alt": "L'e-mail officiel de l'association ACIAH"
                        }
                    ]
                }
            ]

        try:
            with open(file, "r") as config_file:
                data = yaml.safe_load(config_file)
                if data is None:
                    data = default_value
                    
        except (FileNotFoundError, yaml.YAMLError) as e:
            print(f"Erreur rencontrée de type '{e}'. Valeur par défaut utilisée.")
            data = default_value
        return data

    def save_config_file(self, file, content):
        with open(file, "w") as config_file:
            yaml.dump(content, config_file, indent=2, sort_keys=False, allow_unicode=True)

    def show_config_in_notebook(self):
        categories_list = []

        for i, categ in enumerate(self.config):
            categories_list.append(categ["title"])
            category_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

            for j, item in enumerate(categ["values"]):
                label = item["label"]
                text = item["text"]
                alt = item["alt"]

                hbox_button = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                button = Gtk.Button(label=label)
                button.connect("clicked", partial(self.set_clipboard, text=text))
                button.set_tooltip_text(str(alt))
                button.get_style_context().add_class("bouton")

                icone_stylo = Gtk.Image.new_from_icon_name("document-edit", Gtk.IconSize.BUTTON)
                # Pour charger depuis un fichier : icone_stylo = Gtk.Image.new_from_file(mon-chemin)
                icone_stylo.get_style_context().add_class("copcoll-icon")
                bouton_edit = Gtk.Button()
                bouton_edit.set_image(icone_stylo)
                bouton_edit.set_tooltip_text("Éditer cet élément")
                bouton_edit.get_style_context().add_class("bouton")
                bouton_edit.connect("clicked", partial(self.pop_up_to_edit_button, button_number=j))

                icone_poubelle = Gtk.Image.new_from_icon_name("user-trash", Gtk.IconSize.BUTTON)
                bouton_delete = Gtk.Button()
                bouton_delete.set_image(icone_poubelle)
                bouton_delete.set_tooltip_text("Supprimer cet élément")
                bouton_delete.get_style_context().add_class("bouton")
                bouton_delete.get_style_context().add_class("rouge")
                bouton_delete.connect("clicked", partial(self.remove_button, category_number=i, button_number=j))

                hbox_button.pack_start(button, False, False, 0)
                hbox_button.pack_end(bouton_delete, False, False, 0)
                hbox_button.pack_end(bouton_edit, False, False, 0)
                hbox_button.get_style_context().add_class("hbox-bouton")
                category_vbox.pack_start(hbox_button, False, False, 0)

            create_button = Gtk.Button(label="Ajouter un nouveau bouton")
            create_button.get_style_context().add_class("bouton")
            create_button.connect("clicked", partial(self.pop_up_to_create_button))
            category_vbox.pack_end(create_button, False, False, 0)

            notebook_current_tab_name = categories_list[i]
            notebook_tab_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            notebook_tab_label = Gtk.Label(label=notebook_current_tab_name)
            notebook_tab_hbox.get_style_context().add_class("onglet-notebook")
            notebook_tab_hbox.pack_start(notebook_tab_label, False, False, 0)

            icone_stylo = Gtk.Image.new_from_icon_name("document-edit", Gtk.IconSize.BUTTON)
            bouton_edit = Gtk.Button()
            bouton_edit.set_image(icone_stylo)
            bouton_edit.get_style_context().add_class("bouton")
            bouton_edit.set_tooltip_text("Éditer cette catégorie")
            bouton_edit.connect(
                "clicked", 
                partial(
                    self.pop_up_to_edit_category,
                    category_number=i
                )
            )
            bouton_edit.get_style_context().add_class("bouton")

            icone_poubelle = Gtk.Image.new_from_icon_name("user-trash", Gtk.IconSize.BUTTON)
            bouton_delete = Gtk.Button()
            bouton_delete.set_image(icone_poubelle)
            bouton_delete.get_style_context().add_class("bouton")
            bouton_delete.get_style_context().add_class("rouge")
            bouton_delete.set_tooltip_text("Supprimer cette catégorie")
            bouton_delete.connect(
                "clicked",
                partial(
                    self.remove_category,
                    category_number=i
                )
            )
            bouton_delete.get_style_context().add_class("bouton")

            notebook_tab_hbox.pack_start(bouton_edit, False, False, 0)
            notebook_tab_hbox.pack_start(bouton_delete, False, False, 0)

            notebook_tab_hbox.show_all() # comme c'est une hbox, elle a besoin de ça pour s'afficher
            self.categories_notebook.append_page(category_vbox, notebook_tab_hbox)

    def pop_up_to_create_button(self, widget):
        current_category = self.categories_notebook.get_current_page()
        dialog = Gtk.Dialog(title="Ajouter un raccourci", transient_for=self, flags=0)
        dialog.set_default_size(400, 300)

        content_area = dialog.get_content_area()

        vbox_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_form.set_margin_top(10)
        vbox_form.set_margin_bottom(10)
        vbox_form.set_margin_start(10)
        vbox_form.set_margin_end(10)

        title_label = Gtk.Label(label="Titre")
        title_label.set_xalign(0)
        title_entry = Gtk.Entry()
        title_entry.set_tooltip_text("Titre du nouveau bouton")
        vbox_form.pack_start(title_label, False, False, 0)
        vbox_form.pack_start(title_entry, False, False, 0)

        associated_text_label = Gtk.Label(label="Nouveau texte")
        associated_text_label.set_xalign(0)
        associated_text_entry = Gtk.TextView()
        associated_text_entry.set_size_request(-1, 100)
        associated_text_entry.set_tooltip_text("Texte associé au nouveau bouton")
        associated_text_entry.set_accepts_tab(False) # pour qu'un appui sur Tab alors qu'on est dans cette boite de texte fasse basculer sur la boite suivante au lieu de faire une tab dans le texte de la zone
        vbox_form.pack_start(associated_text_label, False, False, 0)
        vbox_form.pack_start(associated_text_entry, False, False, 0)

        tooltip_text_label = Gtk.Label(label="Nouvelle infobulle")
        tooltip_text_label.set_xalign(0)
        tooltip_text_entry = Gtk.Entry()
        tooltip_text_entry.set_tooltip_text("Texte qui s'affichera au survol")
        vbox_form.pack_start(tooltip_text_label, False, False, 0)
        vbox_form.pack_start(tooltip_text_entry, False, False, 0)

        content_area.add(vbox_form)

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

    def add_button_into_config(self, widget, title_entry, associated_text_entry, tooltip_entry, category, dialog):
        title = title_entry.get_text()

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

        self.config[category]["values"].append(new_button)
        self.save_config_file(config_file, self.config)
        self.reload()
        dialog.destroy()

    def remove_button(self, widget, category_number, button_number):
        category = self.config[category_number]
        button = self.config[category_number]["values"][button_number]

        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Voulez-vous vraiment supprimer ce bouton ?"
        )
        dialog.format_secondary_text(f"Le bouton {button['label']} sera supprimé définitivement.\nVoulez-vous continuer ?")

        reponse = dialog.run()

        if reponse == Gtk.ResponseType.YES:
            del self.config[category_number]["values"][button_number]
            self.save_config_file(config_file, self.config)
            self.reload()
        elif reponse == Gtk.ResponseType.NO:
            self.notify(f"Le bouton '{button['label']}' n'a pas été supprimé", title="Rien n'a été supprimé")

        dialog.destroy()

    def pop_up_to_edit_button(self, widget, button_number):
        current_category = self.categories_notebook.get_current_page()
        dialog = Gtk.Dialog(title="Modifier le raccourci", transient_for=self, flags=0)
        dialog.set_default_size(400, 300)

        content_area = dialog.get_content_area()

        vbox_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_form.set_margin_top(10)
        vbox_form.set_margin_bottom(10)
        vbox_form.set_margin_start(10)
        vbox_form.set_margin_end(10)

        title_label = Gtk.Label(label="Titre")
        title_label.set_xalign(0)
        title_entry = Gtk.Entry()
        title_entry.set_text(self.config[current_category]["values"][button_number]["label"])
        title_entry.set_tooltip_text("Nouveau titre")
        vbox_form.pack_start(title_label, False, False, 0)
        vbox_form.pack_start(title_entry, False, False, 0)

        associated_text_label = Gtk.Label(label="Nouveau texte")
        associated_text_label.set_xalign(0)
        associated_text_entry = Gtk.TextView()
        associated_text_entry.set_size_request(-1, 100)
        associated_text_entry.set_accepts_tab(False)
        buffer = associated_text_entry.get_buffer()
        buffer.set_text(self.config[current_category]["values"][button_number]["text"])
        vbox_form.pack_start(associated_text_label, False, False, 0)
        vbox_form.pack_start(associated_text_entry, False, False, 0)

        tooltip_text_label = Gtk.Label(label="Nouvelle infobulle")
        tooltip_text_label.set_xalign(0)
        tooltip_text_entry = Gtk.Entry()
        tooltip_text_entry.set_text(self.config[current_category]["values"][button_number]["alt"])
        tooltip_text_entry.set_tooltip_text("Texte qui s'affichera au survol")
        vbox_form.pack_start(tooltip_text_label, False, False, 0)
        vbox_form.pack_start(tooltip_text_entry, False, False, 0)

        content_area.add(vbox_form)

        modify_button = Gtk.Button(label="Enregistrer")
        modify_button.connect(
            "clicked",
            lambda widget: self.modify_button_into_config(
                title_entry,
                associated_text_entry,
                tooltip_text_entry,
                current_category,
                button_number,
                dialog
            )
        )

        content_area.pack_start(modify_button, False, False, 10)

        dialog.show_all()

    def modify_button_into_config(self, title_entry, associated_text_entry, tooltip_entry, current_category, button_number, dialog):
        title = title_entry.get_text()

        buffer = associated_text_entry.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        text = buffer.get_text(start_iter, end_iter, True)

        tooltip = tooltip_entry.get_text()

        content_to_put = {
            "label": title,
            "text": text,
            "alt": tooltip
        }
        self.config[current_category]["values"][button_number] = content_to_put
        self.save_config_file(config_file, self.config)
        self.reload()
        dialog.destroy()

    def pop_up_to_create_category(self, widget):
        dialog = Gtk.Dialog(title="Ajouter une nouvelle catégorie", transient_for=self, flags=0)

        vbox_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_form.set_margin_top(10)
        vbox_form.set_margin_bottom(10)
        vbox_form.set_margin_start(10)
        vbox_form.set_margin_end(10)

        title_label = Gtk.Label(label="Nom")
        title_label.set_xalign(0)
        title_entry = Gtk.Entry()
        title_entry.set_tooltip_text("Nom de la nouvelle catégorie")
        vbox_form.pack_start(title_label, False, False, 0)
        vbox_form.pack_start(title_entry, False, False, 0)

        def on_submit(widget):
            name = title_entry.get_text().strip()
            if name:
                self.add_category(title_entry)
                dialog.destroy()
            else:
                title_entry.set_placeholder_text("Ce champ ne peut pas être vide")

        submit_button = Gtk.Button(label="Créer la nouvelle catégorie")
        submit_button.connect("clicked", on_submit)
        vbox_form.pack_end(submit_button, False, False, 10)

        dialog.get_content_area().add(vbox_form)
        dialog.show_all()

    def add_category(self, title_entry):
        title = title_entry.get_text()

        object_of_new_category = {
            "title": title,
            "values": []
        }

        self.config.append(object_of_new_category)
        self.save_config_file(config_file, self.config)
        self.reload()
    
    def remove_category(self, widget, category_number):
        category_title = self.config[category_number]["title"]

        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Voulez-vous vraiment supprimer cette catégorie ?"
        )
        dialog.format_secondary_text(f"La catégorie {category_title} sera supprimée définitivement.\nVoulez-vous continuer ?")

        reponse = dialog.run()

        if reponse == Gtk.ResponseType.YES:
            del self.config[category_number]
            self.save_config_file(config_file, self.config)
            self.reload()
        elif reponse == Gtk.ResponseType.NO:
            self.notify(f"La catégorie '{category_title}' n'a pas été supprimée", title="Rien n'a été supprimé")

        dialog.destroy()
    
    def pop_up_to_edit_category(self, widget, category_number):
        dialog = Gtk.Dialog(title="Modifier le raccourci", transient_for=self, flags=0)
        dialog.set_default_size(400, 300)

        content_area = dialog.get_content_area()

        vbox_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_form.set_margin_top(10)
        vbox_form.set_margin_bottom(10)
        vbox_form.set_margin_start(10)
        vbox_form.set_margin_end(10)

        title_label = Gtk.Label(label="Titre")
        title_label.set_xalign(0)
        title_entry = Gtk.Entry()
        title_entry.set_text(self.config[category_number]["title"])
        title_entry.set_tooltip_text("Nouveau titre")
        vbox_form.pack_start(title_label, False, False, 0)
        vbox_form.pack_start(title_entry, False, False, 0)

        content_area.add(vbox_form)

        modify_button = Gtk.Button(label="Enregistrer")
        modify_button.connect(
            "clicked",
            partial(
                self.modify_category_into_config, 
                category_number=category_number,
                title_entry=title_entry,
                dialog=dialog
            )
        )
        
        content_area.add(modify_button)
        dialog.show_all()
    
    def modify_category_into_config(self, widget, category_number, title_entry: Gtk.Entry, dialog: Gtk.Dialog):
        new_title = title_entry.get_text()
        self.config[category_number]["title"] = new_title
        self.save_config_file(config_file, self.config)
        self.reload()
        dialog.destroy()

    def notify(self, message, title="Texte copié"):
        notification = notify2.Notification(title, message)
        notification.show()

    def set_clipboard(self, widget, text: str):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)
        clipboard.store()
        self.notify(f"Le texte '{text}' a été copié dans le presse-papiers.")

    def reload(self):
        while len(self.categories_notebook.get_children()) > 0:
            self.categories_notebook.remove_page(0)
        self.show_config_in_notebook()
        self.show_all()

    def afficher_a_propos(self, widget):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="À propos de CopColl",
        )

        dialog.format_secondary_text(TEXTE_A_PROPOS)

        dialog.run()
        dialog.destroy()

    def dummy_func(self):
        print("Vous avez cliqué sur un bouton")

def main():
    app = CopColl(config_file) # On crée une instance de l'appli
    app.connect('delete-event', Gtk.main_quit) # on fait en sorte que ça quitte proprement (en libérant la mémoire par exemple)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
