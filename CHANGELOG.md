# Historique Spydr / Camicaz

Les [versions archivees sur GitHub](docs/VERSIONS.md) comprennent la reference
historique 0.8.3, les livraisons 0.9.0 a 0.9.7 et la release 0.9.8b.
Leur publication retrospective date du 22 octobre 2026.

## 0.9.8b - 2026-10-27 (release)

- Metadonnees FITS figees au debut du Record : objet, observateur, commentaires,
  configuration, reglages camera, focale et dernieres sondes connues.
- Horloges natives UTC et monotone, avec secondes/nanosecondes conservees dans
  FRAMELOG (METAVER=2, douze colonnes). Les dates texte UTC ont six decimales.
- Correction du protocole Record pour le mini-parseur du Yorick 2.2.02x :
  arguments positionnels et protection des champs texte vides.
- Correction de lecture de camicaz.ini et conversion UTC sans processus date.
- Confirmation Apply and Record, Status automatique avec report pendant Record,
  reglage de focale et redimensionnement de la fenetre.
- Etat final explicite de la sauvegarde : vert pour succes complet, orange pour
  interruption sauvegardee, rouge si echec avec conservation des donnees.
- Nouvelles icones et mention de Yannis Benazza sur la page principale About.
- Acquisition et sauvegarde testees sur NICMOS / Scientific Linux avec Yorick
  2.2.02x ; cubes fournis de deux puis cinq poses sans chopping. Les autres
  modes n'ont pas tous fait l'objet de nouveaux essais instrumentaux.
- La 0.9.7 reste la reference de secours ; la 0.9.8 demeure un essai local.

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
