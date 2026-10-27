# Spydr / Camicaz - lancement isole avec le Yorick existant

Release 0.9.8b : voir aussi RELEASE_0.9.8b.md et son perimetre de validation.

Cette livraison est destinee a une copie isolee sur la machine Linux d'origine sans modifier le Yorick deja present, ni l'installation stable de Spydr / Camicaz.

## Ce que cette variante garantit

- elle ne copie pas `yorick/relocate`
- elle n'installe rien dans le Yorick existant
- elle ne remplace aucun fichier de la version stable
- elle reconstruit `libcamicaz.so` et `yCamicaz.so` uniquement dans le dossier de test copie

## Contenu du bundle

- `libcamicaz/`
- `yCamicaz/`
- `run_spydr_test.sh`
- `rebuild_with_existing_yorick.sh`

## Utilisation sur la machine Linux d'origine

Copier le dossier complet sur le disque local, dans un nouveau dossier de test
dont le chemin ne contient pas d'espaces. Ouvrir un terminal dans ce dossier.
Une livraison neuve ne contient pas les deux bibliotheques compilees :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

Avec `sh`, aucun `chmod` n'est necessaire. Les dependances doivent deja etre
presentes : Yorick et ses fichiers de compilation (`Make.cfg`, en-tetes,
outils), `make`, `g++`, Python 2/PyGTK et les bibliotheques NI/Boost requises.
La copie de test reutilise ces dependances sans les installer.

## Affichage et focale

La fenetre est redimensionnable et maximisable. L'image reste ancree en haut
a gauche, avec des marges eventuelles a droite ou en bas pour conserver ses
proportions. Le zoom et la palette sont conserves au redimensionnement.
Verifier le bas de la fenetre des le premier lancement sur le PC cible.

Dans **View > Plugins pane** (`Ctrl+P`), panneau **PSF fit**, renseigner
**Effective focal length (mm)** au detecteur, optiques de reprise incluses.
L'interface reste en anglais. **Plate scale (arcsec/pixel)** affiche en lecture
seule l'echelle calculee pour des pixels NICMOS de 40 um :
`arcsec/pixel = 8250.592249883855 / focale_mm`.
Le reglage dure pour la session ; 0 conserve l'echelle existante.
Il concerne l'image courante et les prochaines acquisitions, et n'ajoute pas
de calibration WCS aux fichiers FITS enregistres.
Activer **View > Graph axis in arcsec** pour les coordonnees angulaires.

## Mise a jour d'une copie deja compilee

Pour la seule correction de taille initiale et de placement, si la copie du
test de focale precedent fonctionne deja, fermer Spydr puis remplacer :

- `yCamicaz/yorick/spydr/spydr.py`
- `yCamicaz/yorick/spydr/spydr.glade`

Relancer `sh run_spydr_test.sh` ; aucune recompilation n'est necessaire pour
ces deux fichiers. Pour une nouvelle livraison complete, effectuer les deux
commandes de reconstruction et de lancement ci-dessus.

## Metadonnees FITS (0.9.8 et 0.9.8b)

Au clic sur Record, si les reglages n'ont pas ete appliques ou ont change,
une alerte propose Apply and Record ou Cancel. Apres confirmation, Record attend
le retour reussi des commandes serie au rack. Homing invalide le dernier Apply.
Le detail et les consignes du correctif sont dans APPLY_AND_RECORD.md si fourni.

Les acquisitions Record enregistrent l'objet, l'observateur, les commentaires,
les reglages appliques, la version logicielle et la configuration camera.
Les dates sont en UTC (horloge du PC). L'extension FRAMELOG conserve l'ordre
des expositions, les temps des appels logiciels et les positions DTR imposees.
Les derniers releves de sondes disponibles incluent leur anciennete et leur
conversion historique. La focale est incluse si elle a ete renseignee.
Les textes complets sont conserves dans un bloc JSON encode sans perte.
Ces champs decrivent les reglages et mesures disponibles ; les sondes ne sont
pas relues automatiquement au demarrage du Record.
Le visualiseur conserve son export generique ; archiver les fichiers Record
pour disposer de ces metadonnees. Voir FITS_METADATA.md si fourni a la livraison.

La 0.9.8b ajoute un module natif utilisant clock_gettime pour UTC et MONOTONIC.
FRAMELOG contient 12 colonnes : les 3 colonnes de la 0.9.8 puis les secondes et
nanosecondes natives avant/apres lecture et la duree monotone de cet appel.
Le noyau indique sa resolution nominale dans UTCRES et MONORES.
Ces temps restent des temps logiciels, sans synchronisation avec le detecteur.
La reconstruction dans le dossier de test est obligatoire pour la 0.9.8b,
meme si une copie 0.9.8 est deja compilee. Ne pas melanger leurs fichiers.

## Detection de Yorick

Le script essaie dans cet ordre:

1. `SPYDR_TEST_YORICK_BIN`
2. `command -v yorick`
3. `/home/etudiants/yorick.git/relocate/bin/yorick`

Si besoin, tu peux imposer explicitement le binaire:

```sh
SPYDR_TEST_YORICK_BIN=/chemin/vers/yorick sh rebuild_with_existing_yorick.sh
SPYDR_TEST_YORICK_BIN=/chemin/vers/yorick sh run_spydr_test.sh
```

Tu peux aussi imposer la racine Yorick si l'autodetection du `relocate` n'est pas correcte:

```sh
SPYDR_TEST_YORICK_ROOT=/chemin/vers/yorick/relocate sh rebuild_with_existing_yorick.sh
```

## Isolation du test

Le lancement force:

- `CAMTOP` vers la copie de test de `yCamicaz`
- `STYCTOP` vers la copie de test de `yCamicaz`
- `Y_PYTHON` et `Y_GLADE` vers la copie de test de `spydr`
- `LD_LIBRARY_PATH` vers la copie de test de `libcamicaz`

L'environnement Yorick et les dependances systeme existants sont reutilises.
Les ressources Spydr / Camicaz chargees viennent du dossier de test copie.
Cette isolation suppose de travailler dans une copie complete, pas dans le
repertoire de l'installation stable. Les tests logiciels ne remplacent pas
la validation avec la camera NICMOS.
