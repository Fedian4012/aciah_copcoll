#!/usr/bin/env bash

# Fait sur Linux Mint 22 "Xia"

# Constantes
DEPENDENCIES=( "pygobject" "pyyaml" "notify2" )
LOGFILE="/var/log/copcoll-$(date "+%Y-%m-%d-%H-%M-%S").log"

# Codes couleur
RED="\e[31m"
GREEN="\e[32m"
RESET="\e[0m"

# Fonctions
check_package() {
  package=$1

  if pip show "$package" > /dev/null 2>&1; then
    echo -e "$package -- ${GREEN}Présent${RESET}"
    return 0
  else
    echo -e "$package -- ${RED}Absent${RESET}"
    return 1
  fi
}

check_cmd()
{
# Merci à Adrien Linuxtricks (https://linuxtricks.fr) pour cette fonction

if [[ $? -eq 0 ]]
then
  echo -e "${GREEN}OK${RESET}"
else
  echo -e "${RED}ERREUR${RESET}"
fi
}

# Confirmation utilisateur
echo -e "Bienvenue dans le script d'installation de CopColl.\nCe script installera CopColl sur votre ordinateur." # Toute ressemblance à InstallShield Wizard est purement fortuite
read -p "Voulez-vous continuer (O/n) " continue
continue=$(echo "$continue" | tr '[:upper:]' '[:lower:]') # Met la réponse en minuscules
if [[ $continue = "n" ]]; then
  exit 0
fi

# On vérifie si on est en root
if [[ "$EUID" != "0" ]]
then
   echo "Ce script doit être lancé en tant que root" 
   exit 1
fi

touch "$LOGFILE"
echo "Les logs sont à retrouver dans $LOGFILE"
echo ""

# Vérification des dépendances
printf '%40s\n' | tr ' ' '-'
echo "1. INSTALLATION DES DEPENDANCES"
printf '%40s\n' | tr ' ' '-'

to_install=()
for package in "${DEPENDENCIES[@]}"; do
  if ! check_package "$package"; then
    to_install+=("$package")
  fi
done

if [[ ${#to_install[@]} -gt 0 ]]; then 
  echo "Installation des dépendances : ${to_install[@]}" | tee -a "$LOGFILE"
  pip install --break-system-packages "${to_install[@]}" >> "$LOGFILE" 2>&1 # Le --break-system-packages permet de forcer pip à installer les paquets qui ne viennent pas de la distro
else
  echo "Aucune dépendance à installer."
fi

printf '%40s\n' | tr ' ' '-'
echo "2. INSTALLATION DU SCRIPT"
printf '%40s\n' | tr ' ' '-'
