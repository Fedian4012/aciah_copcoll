import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

import os
from functools import partial
from plyer import notification
import yaml

# --- Configuration des chemins ---
APP_FOLDER = os.path.expanduser("~/Projets/aciah_copcoll/") # dossier principal de l'application
GLADE_FILE = os.path.expanduser(f"{APP_FOLDER}/interface.glade") # fichier XML décrivant l'interface
DATA_FILE = os.path.expanduser(f"{APP_FOLDER}/data.yml") # fichier des données de l'application (catégories + boutons)
SETTINGS_FILE = os.path.expanduser(f"{APP_FOLDER}/settings.yml") # fichier des paramètres (inutilisés pour l'instant)
CSS_FILE = os.path.expanduser(f"{APP_FOLDER}/style.css") # le fichier CSS pour le style

# --- Autres constantes ---
BUTTON_CHARS_LIMIT = 40 # limite de longueur pour les noms de boutons
CATEGORIES_CHARS_LIMIT = 20 # limite de longueur pour les noms de boutons
MARGIN = 4 # marge entre les différents éléments

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

class CopColl:
    def __init__(self, config_file, settings_file):
        # 1. Chargement du fichier XML Glade
        self.builder = Gtk.Builder()
        self.builder.add_from_file(GLADE_FILE)
        
        # 2. Récupération des composants principaux définis dans le XML
        self.window = self.builder.get_object("main_window")
        self.categories_notebook = self.builder.get_object("categories_notebook")
        
        # Application du style CSS global
        self.css_applier = Gtk.CssProvider()
        self.css_applier.load_from_path(CSS_FILE)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.css_applier,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # 3. Connexion des signaux Glade et fermeture propre
        self.builder.connect_signals(self)
        self.window.connect("destroy", Gtk.main_quit)

        # 4. Chargement des données YAML
        self.data = self.load_data_file(config_file)
        self.settings = self.load_settings_file(settings_file)
        
        # 5. Construction de la partie dynamique et affichage
        self.build_window_content()
        self.window.show_all()

    # --- ÉVÉNEMENTS LIÉS AUX SIGNAUX DE INTERFACE.GLADE ---
    
    def on_about_item_activate(self, widget):
        """Ouvre la boîte de dialogue 'À propos'."""
        dialog = Gtk.MessageDialog(
            transient_for=self.window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="À propos de CopColl",
        )
        dialog.format_secondary_text(TEXTE_A_PROPOS)
        dialog.run()
        dialog.destroy()

    def on_create_category_button_clicked(self, widget):
        """Déclenché par le bouton du bas du Notebook."""
        self.pop_up_to_create_category(widget)

    # --- LOGIQUE DYNAMIQUE DE L'INTERFACE ---

    def build_window_content(self):
        """Génère dynamiquement les onglets et les boutons avec des marges et tailles strictes."""
        # Définition de la taille fixe pour 40 caractères (approx. 320 pixels selon la police standard)
        TAILLE_BOUTON_40_CHAR = 320
        TAILLE_ONGLET_20_CHAR = 160

        for i, categ in enumerate(self.data):
            # Le conteneur global de l'onglet
            category_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=MARGIN)
            # Marge de 4 pixels entre le contenu et les bords extérieurs de la fenêtre
            category_vbox.set_margin_top(MARGIN)
            category_vbox.set_margin_bottom(MARGIN)
            category_vbox.set_margin_start(MARGIN)
            category_vbox.set_margin_end(MARGIN)

            # Remplissage de la catégorie avec ses boutons de copie
            for j, item in enumerate(categ["values"]):
                # Ligne contenant le bouton principal + les boutons d'action
                # spacing=6 gère l'espace entre le gros bouton, le stylo et la poubelle
                hbox_button = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
                hbox_button.set_margin_start(MARGIN)   # Gauche
                hbox_button.set_margin_end(MARGIN)     # Droite
                hbox_button.set_margin_top(MARGIN)     # Haut
                hbox_button.set_margin_bottom(MARGIN)  # Bas
                
                # 1. Bouton principal de copie (Taille fixe)
                bouton_principal = Gtk.Button(label=item["label"])
                bouton_principal.connect("clicked", partial(self.set_clipboard, text=str(item["text"])))
                bouton_principal.set_tooltip_text(str(item["alt"]))
                bouton_principal.get_style_context().add_class("bouton")
                bouton_principal.set_margin_top(MARGIN)
                # button.set_margin_bottom(MARGIN / 2) 
                # bouton_principal.set_margin_start(MARGIN)
                # button.set_margin_end(MARGIN / 2)
                
                # On force la largeur fixe calculée, la hauteur (-1) s'adapte automatiquement
                bouton_principal.set_size_request(TAILLE_BOUTON_40_CHAR, -1)
                # On empêche le bouton de s'étirer si la fenêtre s'agrandit
                bouton_principal.set_hexpand(False) 

                # 2. Bouton d'édition (Taille carrée naturelle pour l'icône)
                bouton_edit = Gtk.Button()
                bouton_edit.set_image(Gtk.Image.new_from_icon_name("document-edit", Gtk.IconSize.BUTTON))
                bouton_edit.set_tooltip_text("Éditer cet élément")
                bouton_edit.get_style_context().add_class("bouton")
                # bouton_edit.set_margin_top(MARGIN / 2) # si deux boutons côte à côte ont une marge de 4, ça fait 8 pixels entre les deux
                # bouton_edit.set_margin_bottom(MARGIN / 2)
                # bouton_edit.set_margin_start(MARGIN / 2)
                # bouton_edit.set_margin_end(4)
                bouton_edit.connect("clicked", partial(self.pop_up_to_edit_button, button_number=j))

                # 3. Bouton de suppression
                bouton_delete = Gtk.Button()
                bouton_delete.set_image(Gtk.Image.new_from_icon_name("user-trash", Gtk.IconSize.BUTTON))
                bouton_delete.set_tooltip_text("Supprimer cet élément")
                bouton_delete.get_style_context().add_class("bouton")
                bouton_delete.get_style_context().add_class("rouge")
                # bouton_delete.set_margin_top(MARGIN / 2)
                # bouton_delete.set_margin_bottom(MARGIN / 2)
                # bouton_delete.set_margin_start(MARGIN / 2)
                # bouton_delete.set_margin_end(MARGIN)
                bouton_delete.connect("clicked", partial(self.remove_button, category_number=i, button_number=j))

                # On empile de gauche à droite proprement
                hbox_button.pack_start(bouton_principal, False, False, 0)
                hbox_button.pack_start(bouton_edit, False, False, 0)
                hbox_button.pack_start(bouton_delete, False, False, 0)
                
                category_vbox.pack_start(hbox_button, False, False, 0)

            # Bouton d'ajout d'élément en bas de la liste (Marge supérieure pour l'isoler)
            create_button = Gtk.Button(label="Ajouter un nouveau bouton")
            create_button.get_style_context().add_class("bouton")
            create_button.set_margin_top(MARGIN)
            create_button.set_margin_bottom(MARGIN)
            create_button.connect("clicked", partial(self.pop_up_to_create_button))
            category_vbox.pack_end(create_button, False, False, 0)

            # --- Création de l'en-tête de l'onglet personnalisé ---
            notebook_tab_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=MARGIN)
            
            notebook_tab_hbox.set_size_request(300, 32)

            notebook_tab_hbox.set_margin_top(MARGIN)
            notebook_tab_hbox.set_margin_bottom(MARGIN)
            notebook_tab_hbox.set_margin_start(MARGIN)
            notebook_tab_hbox.set_margin_end(MARGIN)

            # 1. Label de la catégorie (Titre)
            notebook_tab_label = Gtk.Label(label=categ["title"])
            notebook_tab_label.set_xalign(0)  # Aligne le texte à gauche dans sa zone           
            
            # On impose une largeur fixe de 100 pixels pour aligner verticalement les boutons.
            # 20 caractères standards rentrent parfaitement dans ce gabarit.
            notebook_tab_label.set_size_request(TAILLE_ONGLET_20_CHAR, -1)

            # 2. Bouton Éditer la catégorie
            bouton_edit_cat = Gtk.Button()
            bouton_edit_cat.set_image(Gtk.Image.new_from_icon_name("document-edit", Gtk.IconSize.BUTTON))
            bouton_edit_cat.connect("clicked", partial(self.pop_up_to_edit_category, category_number=i))
            bouton_edit_cat.get_style_context().add_class("bouton")
            bouton_edit_cat.set_margin_top(MARGIN)
            bouton_edit_cat.set_margin_bottom(MARGIN)
            bouton_edit_cat.set_valign(Gtk.Align.CENTER)

            # 3. Bouton Supprimer la catégorie
            bouton_delete_cat = Gtk.Button()
            bouton_delete_cat.set_image(Gtk.Image.new_from_icon_name("user-trash", Gtk.IconSize.BUTTON))
            bouton_delete_cat.connect("clicked", partial(self.remove_category, category_number=i))
            bouton_delete_cat.get_style_context().add_class("bouton")
            bouton_delete_cat.get_style_context().add_class("rouge")
            bouton_delete_cat.set_margin_top(MARGIN)
            bouton_delete_cat.set_margin_bottom(MARGIN)
            bouton_delete_cat.set_valign(Gtk.Align.CENTER)

            # On empile les éléments les uns après les autres
            notebook_tab_hbox.pack_start(notebook_tab_label, False, False, 0)
            notebook_tab_hbox.pack_end(bouton_edit_cat, False, False, 0)
            notebook_tab_hbox.pack_end(bouton_delete_cat, False, False, 0)
            notebook_tab_hbox.show_all()

            # Injection de la page complète dans le Notebook
            self.categories_notebook.append_page(category_vbox, notebook_tab_hbox)

    # --- BOITES DE DIALOGUE (FORMULAIRES ET POPUPS) ---

    def pop_up_to_create_button(self, widget):
        current_category = self.categories_notebook.get_current_page()
        dialog = Gtk.Dialog(title="Ajouter un raccourci", transient_for=self.window, flags=0)
        dialog.set_default_size(400, 300)

        content_area = dialog.get_content_area()
        vbox_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_form.set_margin_top(10); vbox_form.set_margin_bottom(10)
        vbox_form.set_margin_start(10); vbox_form.set_margin_end(10)

        title_label = Gtk.Label(label="Titre")
        title_label.set_xalign(0)
        title_entry = Gtk.Entry()
        title_entry.set_max_length(BUTTON_CHARS_LIMIT)
        vbox_form.pack_start(title_label, False, False, 0)
        vbox_form.pack_start(title_entry, False, False, 0)

        associated_text_label = Gtk.Label(label="Nouveau texte")
        associated_text_label.set_xalign(0)
        associated_text_entry = Gtk.TextView()
        associated_text_entry.set_size_request(-1, 100)
        associated_text_entry.set_accepts_tab(False)
        vbox_form.pack_start(associated_text_label, False, False, 0)
        vbox_form.pack_start(associated_text_entry, False, False, 0)

        tooltip_text_label = Gtk.Label(label="Nouvelle infobulle")
        tooltip_text_label.set_xalign(0)
        tooltip_text_entry = Gtk.Entry()
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
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        tooltip = tooltip_entry.get_text()

        new_button = {"label": title, "text": text, "alt": tooltip}
        self.data[category]["values"].append(new_button)
        self.save_data_file(DATA_FILE, self.data)
        self.reload()
        dialog.destroy()

    def pop_up_to_edit_button(self, widget, button_number):
        current_category = self.categories_notebook.get_current_page()
        dialog = Gtk.Dialog(title="Modifier le raccourci", transient_for=self.window, flags=0)
        dialog.set_default_size(400, 300)

        content_area = dialog.get_content_area()
        vbox_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_form.set_margin_top(10); vbox_form.set_margin_bottom(10)
        vbox_form.set_margin_start(10); vbox_form.set_margin_end(10)

        title_entry = Gtk.Entry()
        title_entry.set_text(self.data[current_category]["values"][button_number]["label"])
        title_entry.set_max_length(BUTTON_CHARS_LIMIT)
        vbox_form.pack_start(Gtk.Label(label="Titre", xalign=0), False, False, 0)
        vbox_form.pack_start(title_entry, False, False, 0)

        associated_text_entry = Gtk.TextView()
        associated_text_entry.set_size_request(-1, 100)
        associated_text_entry.set_accepts_tab(False)
        associated_text_entry.get_buffer().set_text(self.data[current_category]["values"][button_number]["text"])
        vbox_form.pack_start(Gtk.Label(label="Texte", xalign=0), False, False, 0)
        vbox_form.pack_start(associated_text_entry, False, False, 0)

        tooltip_text_entry = Gtk.Entry()
        tooltip_text_entry.set_text(self.data[current_category]["values"][button_number]["alt"])
        vbox_form.pack_start(Gtk.Label(label="Infobulle", xalign=0), False, False, 0)
        vbox_form.pack_start(tooltip_text_entry, False, False, 0)

        content_area.add(vbox_form)

        modify_button = Gtk.Button(label="Enregistrer")
        modify_button.connect(
            "clicked",
            lambda w: self.modify_button_into_config(
                title_entry, associated_text_entry, tooltip_text_entry, current_category, button_number, dialog
            )
        )
        content_area.pack_start(modify_button, False, False, 10)
        dialog.show_all()

    def modify_button_into_config(self, title_entry, associated_text_entry, tooltip_entry, current_category, button_number, dialog):
        title = title_entry.get_text()
        buffer = associated_text_entry.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        tooltip = tooltip_entry.get_text()

        self.data[current_category]["values"][button_number] = {"label": title, "text": text, "alt": tooltip}
        self.save_data_file(DATA_FILE, self.data)
        self.reload()
        dialog.destroy()

    def remove_button(self, widget, category_number, button_number):
        button = self.data[category_number]["values"][button_number]
        dialog = Gtk.MessageDialog(
            transient_for=self.window, flags=0, message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO, text="Voulez-vous vraiment supprimer ce bouton ?"
        )
        dialog.format_secondary_text(f"Le bouton {button['label']} sera supprimé définitivement.")
        if dialog.run() == Gtk.ResponseType.YES:
            del self.data[category_number]["values"][button_number]
            self.save_data_file(DATA_FILE, self.data)
            self.reload()
        dialog.destroy()

    def pop_up_to_create_category(self, widget):
        dialog = Gtk.Dialog(title="Ajouter une nouvelle catégorie", transient_for=self.window, flags=0)
        vbox_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_form.set_margin_top(10); vbox_form.set_margin_bottom(10)
        vbox_form.set_margin_start(10); vbox_form.set_margin_end(10)

        title_entry = Gtk.Entry()
        title_entry.set_max_length(CATEGORIES_CHARS_LIMIT)
        vbox_form.pack_start(Gtk.Label(label="Nom de la catégorie", xalign=0), False, False, 0)
        vbox_form.pack_start(title_entry, False, False, 0)

        def on_submit(w):
            name = title_entry.get_text().strip()
            if name:
                self.data.append({"title": name, "values": []})
                self.save_data_file(DATA_FILE, self.data)
                self.reload()
                dialog.destroy()
            else:
                title_entry.set_placeholder_text("Ce champ ne peut pas être vide")

        submit_button = Gtk.Button(label="Créer la nouvelle catégorie")
        submit_button.connect("clicked", on_submit)
        vbox_form.pack_end(submit_button, False, False, 10)

        dialog.get_content_area().add(vbox_form)
        dialog.show_all()

    def pop_up_to_edit_category(self, widget, category_number):
        dialog = Gtk.Dialog(title="Modifier la catégorie", transient_for=self.window, flags=0)
        vbox_form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_form.set_margin_top(10); vbox_form.set_margin_bottom(10)
        vbox_form.set_margin_start(10); vbox_form.set_margin_end(10)

        title_entry = Gtk.Entry()
        title_entry.set_text(self.data[category_number]["title"])
        title_entry.set_max_length(CATEGORIES_CHARS_LIMIT)
        vbox_form.pack_start(Gtk.Label(label="Titre", xalign=0), False, False, 0)
        vbox_form.pack_start(title_entry, False, False, 0)

        modify_button = Gtk.Button(label="Enregistrer")
        modify_button.connect(
            "clicked",
            lambda w: self.modify_category_into_config(category_number, title_entry, dialog)
        )
        vbox_form.pack_end(modify_button, False, False, 10)
        dialog.get_content_area().add(vbox_form)
        dialog.show_all()

    def modify_category_into_config(self, category_number, title_entry, dialog):
        self.data[category_number]["title"] = title_entry.get_text()
        self.save_data_file(DATA_FILE, self.data)
        self.reload()
        dialog.destroy()

    def remove_category(self, widget, category_number):
        category_title = self.data[category_number]["title"]
        dialog = Gtk.MessageDialog(
            transient_for=self.window, flags=0, message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO, text="Voulez-vous vraiment supprimer cette catégorie ?"
        )
        dialog.format_secondary_text(f"La catégorie {category_title} ainsi que tous les boutons qu'elles contient seront supprimés.")
        if dialog.run() == Gtk.ResponseType.YES:
            del self.data[category_number]
            self.save_data_file(DATA_FILE, self.data)
            self.reload()
        dialog.destroy()

    # --- SERVICES ET UTILITAIRES (YAML, Presse-papier, Notifications...) ---

    def load_data_file(self, file):
        default = [{"title": "ACIAH", "values": [{"label": "E-mail", "text": "aciah@free.fr", "alt": "L'e-mail officiel"}]}]
        try:
            with open(file, "r") as f:
                data = yaml.safe_load(f)
                return data if data is not None else default
        except:
            return default

    def save_data_file(self, file, content):
        with open(file, "w") as f:
            yaml.dump(content, f, indent=2, sort_keys=False, allow_unicode=True)

    def load_settings_file(self, file):
        try:
            with open(file, "r") as f:
                return yaml.safe_load(f)
        except:
            return {"notification_timeout": {"value": 3}}

    def set_clipboard(self, widget, text: str):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(text, -1)
        clipboard.store()
        self.notify(f"Le texte '{text}' a été copié dans le presse-papiers.")

    def notify(self, message, title="Texte copié"):
        notification.notify(title, message, "Copcoll")

    def reload(self):
        """Vide le notebook et force une reconstruction complète pour rafraîchir l'interface."""
        while len(self.categories_notebook.get_children()) > 0:
            self.categories_notebook.remove_page(0)
        self.build_window_content()
        self.window.show_all()


def main():
    app = CopColl(DATA_FILE, SETTINGS_FILE)
    Gtk.main()

if __name__ == "__main__":
    main()
