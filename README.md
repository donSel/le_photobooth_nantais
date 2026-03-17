# le_photobooth_nantais
Ressources et plugin qui m'ont permis de modifier légèrement le logiciel [pibooth](https://github.com/pibooth/pibooth) afin de créer le logiciel pour Le Photobooth Nantais.

Ce plugin parmet d'ajouter deux nouveaux format de photo au logiciel [pibooth](https://github.com/pibooth/pibooth) :
- Format marque page 5x15cm(3 photos verticales)
- Format paysage 10x15cm (1 photos au format paysage)

Les images `layout2.png` et `layout3.png` sont les images des boutons du menu de ces deux nouveaux formats.

Le fichier `pibooth_dnp_switcher.py` est le code du plugin permettant de changer de configuration d'imprimante lorsque le formet marque page est sélectionné. En effet le format marque page nécessite d'avoir une configuration CUPS de plus pour l'imprimante afin de pouvoir gérer l'impression en 5x15cm.   
