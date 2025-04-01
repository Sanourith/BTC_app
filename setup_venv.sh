#!/bin/bash

set -e

venv_dir="./venv_btc"

# Vérification si le venv existe déjà
if [ ! -d "$venv_dir" ]; then
    echo "Création de l'environnement virtuel dans $venv_dir..."
    python3 -m venv "$venv_dir"
    echo "Environnement virtuel créé avec succès."
else
    echo "L'environnement virtuel existe déjà à $venv_dir."
fi

# Activation de l'environnement virtuel
echo "Activation de l'environnement virtuel..."
source "$venv_dir/bin/activate"

# Vérification si requirements.txt existe
if [ -f "requirements.txt" ]; then
    echo "Installation des dépendances depuis requirements.txt..."
    pip install --upgrade pip  # Met à jour pip avant d'installer
    pip install -r requirements.txt
else
    echo "Aucun fichier requirements.txt trouvé dans le répertoire actuel."
fi

# Affichage de l'état de l'environnement virtuel
echo "Environnement virtuel activé : $(which python)"





