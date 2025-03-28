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
                return yaml.safe_load(config_file)  # Retourne directement la config chargée
        except FileNotFoundError:
            return {
                "E-mail association Aciah": "aciah@free.fr"
            }

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
        categories_list = [list(item.keys())[0] for item in self.config["raccourcis"]]
        
        categories_notebook = Gtk.Notebook()
        categories_notebook.set_tab_pos(Gtk.PositionType.LEFT)
        vbox.pack_start(categories_notebook, True, True, 0)
        
        for category in categories_list:
            page = Gtk.Box()
            
            # Récupération des données sous chaque catégorie
            category_data = next(item[category] for item in self.config["raccourcis"] if category in item)
            
            # Création d'un Gtk.Box pour contenir les sous-clés et leurs valeurs
            category_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            
            for sub_key, sub_value in category_data[0].items():
                # Ajoute un label pour chaque sous-clé et sa valeur
                sub_label = Gtk.Label(label=f"{sub_key}: {sub_value}")
                category_content.pack_start(sub_label, False, False, 0)
            
            # Ajoute le contenu de la catégorie à la page
            page.add(category_content)
            
            label = Gtk.Label(label=f"{category}")  # Titre de l'onglet
            categories_notebook.append_page(page, label)  # Ajout de la page au notebook

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
