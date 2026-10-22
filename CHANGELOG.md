# Historique Spydr / Camicaz

Les [versions archivees sur GitHub](docs/VERSIONS.md) comprennent la reference
historique 0.8.3 et les livraisons 0.9.0 a 0.9.8b, avec tags et archives.
Leur publication retrospective date du 22 octobre 2026.

## 0.9.8b - 2026-10-21 (test)

- Horloges natives UTC et monotone, FRAMELOG de douze colonnes (METAVER=2).
- Conservation des metadonnees, corrections Record, Apply and Record et
  AutoStatus pendant le freerun, avec report pendant Record.
- Nouvelle icone des fenetres et logo dans A propos.
- Reconstruction du module natif obligatoire pour cette version.

## 0.9.8 - 2026-10-21 (test)

- Metadonnees FITS : objet, observateur, commentaires, focale et sondes.
- Horodatage logiciel a la seconde et FRAMELOG de trois colonnes (METAVER=1).
- Fenetre redimensionnable, corrections de cadrage et reglage de focale.
- Corrections cumulatives du blocage Record et confirmation Apply and Record.
- AutoStatus au lancement puis toutes les minutes, y compris en freerun,
  avec report pendant Record ; nouvelles icones de fenetre et A propos.

## 0.9.7 - 2026-10-16 (test)

- Correction d'un decalage d'un pixel dans l'origine du premier amplificateur
  lors de la reconstruction des quadrants. Le defaut decalait un quadrant,
  creait un chevauchement et laissait 128 pixels non renseignes par lecture.
- Ordre des amplificateurs et separation Start/End conserves. Aucun changement
  de signe, de gain ou d'offset des valeurs recues.
- Regression C++98 de la fonction reelle sur chaque pixel des deux lectures,
  les jonctions des quadrants, l'unicite des echantillons et les bornes memoire.
  L'orientation physique et les extrema restent a verifier sur l'instrument.

## 0.9.6 - 2026-10-16 (test)

- Noms de fichiers a la seconde, suffixes numerotes en cas de collision et
  sauvegardes Record sans ecrasement des fichiers existants.
- Etat d'enregistrement explicite ; Stop annule le callback et termine la
  sauvegarde avant de reactiver les commandes. Les callbacks tardifs sont ignores.
- Erreurs d'acquisition et de chopping remontees par le wrapper C++ ; seules les
  images valides sont conservees, avec suffixe -partial si le cube est incomplet.
- En cas d'erreur disque, conservation du cube et du verrou d'acquisition ;
  Stop permet de retenter apres correction, sans retirer deux fois l'image initiale.
- Record exige un Apply reussi correspondant aux parametres affiches. Les
  erreurs serie invalident la confirmation ; appliquer de nouveau les trois
  parametres apres un echec. Le motif choisi survit a la reactivation du chopping.
- Tests avec vrais fichiers FITS et tests C++98 sur doubles materiels ; pas de
  compilation complete NI-DAQmx ni de validation de la mecanique sur ce PC.

## 0.9.5 - 2026-10-16 (test)

- Ajout du motif Record ABBABAABBAABABBA en fin de menu, sans changer les indices
  des modes existants : 16 expositions par cycle, 8 en A et 8 en B.
- Tests du motif depuis les deux positions initiales et sur plusieurs cycles,
  dont 200 cycles (3200 expositions simulees). Freerun inchange.

## 0.9.4 - 2026-10-16 (test)

- Motifs d'enregistrement explicites pour ABAB, ABBA, 2A2B, 5A5B et 10A10B.
  Totaux de 2, 4, 4, 10 et 20 expositions par iteration respectivement.
- Premiere position imposee a chaque Record, independamment du freerun precedent.
  Convention logique identique a l'ancien ABAB : A=DTR desactivee, B=DTR activee.
- Commandes DTR aux transitions uniquement, apres initialisation ; delai
  d'attente historique conserve. Mode fige pendant l'enregistrement.
- Tests Yorick de 25 enregistrements simules, dont 200 cycles ABBA, sauvegarde
  simulee, arret anticipe et entrees invalides. Validation mecanique necessaire.
- Le freerun conserve son alternance simple ; le menu des motifs reste reserve
  a Record.

## 0.9.3 - 2026-10-16 (test)

- Record utilise le dossier selectionne, et non le dossier affiche dans le
  selecteur GTK, qui peut etre son parent lors de la premiere sequence.
- Une selection absente ou un dossier inexistant bloque le lancement avec un
  message, sans arreter le freerun ni desactiver les commandes.
- Echappement des antislashs et guillemets du chemin transmis a Yorick.
- Regression du callback Record avec dossiers temporaires et GTK simule.

## 0.9.2 - 2026-10-16 (test)

- La case Enable chopping transmet maintenant ses changements au freerun actif,
  sans devoir arreter puis relancer l'acquisition.
- Activation/desactivation prise en compte au prochain cycle, sans callback
  supplementaire. Une activation repetee ne reinitialise pas l'alternance.
- Desactiver arrete l'alternance sans imposer un retour a une position mecanique.
- Tests du callback Python et de la boucle Yorick avec camera simulee ;
  validation du mouvement reel sur l'instrument encore necessaire.

## 0.9.1 - 2026-10-16 (test)

- Retour au cadrage automatique de l'image principale au passage d'un cube
  enregistre au freerun, pour eviter de conserver un zoom vertical residuel.
- Le zoom utilisateur reste conserve lors d'un redemarrage ordinaire du freerun.
- Regression Yorick/Gist avec un cube de 800 expositions (200 cycles ABBA) et
  un cadrage vertical residuel simule. Validation materielle encore necessaire.

## 0.9.0 - 2026-10-14 (test)

- Identification commune dans le titre de la fenetre, le dialogue A propos,
  le message de demarrage et les lanceurs des bundles.
- Fichier VERSION commun a Python, Yorick et aux scripts de lancement.
- Premiere version identifiee du travail de maintenance : gestion freerun /
  Record, erreurs DAQmx et ameliorations d'affichage presentes dans les sources.

Cette version reste a valider sur la camera et la machine Linux d'origine.
Les versions historiques des composants tiers et leurs licences sont conservees.
