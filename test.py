from gi.repository import Gtk
import yaml

def load_config_file(file):
    try:
        with open(file, "r") as config_file:
            config = yaml.safe_load(config_file)
    except FileNotFoundError:
        config = {
            "E-mail association Aciah": "aciah@free.fr"
        }
    return config

def create_window(config):
    # Convertir la configuration en chaîne de caractères
    config_str = str(config)  # Cela transforme la configuration en une chaîne lisible

    # Créer la fenêtre avec un label affichant la configuration
    window = Gtk.Window()
    window.set_title("CopColl")
    window.set_default_size(400, 300)

    # Utiliser la configuration convertie en chaîne
    label = Gtk.Label(label='Bienvenue sur CopColl\nConfiguration :\n' + config_str)
    window.add(label)
    window.show_all()

    # Connecter l'événement de fermeture de la fenêtre
    window.connect('delete-event', Gtk.main_quit)

    # Démarrer la boucle principale GTK
    Gtk.main()

def main():
    # Charger la configuration dès le démarrage
    config = load_config_file("config.yml")
    print("Configuration chargée : ", config)  # Vérification dans le terminal

    # Créer la fenêtre avec la configuration chargée
    create_window(config)

if __name__ == "__main__":
    main()
