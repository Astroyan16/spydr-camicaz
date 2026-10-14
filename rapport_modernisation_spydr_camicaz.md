# Rapport de modernisation Spydr / Camicaz

## Objet

Ce document synthétise l'architecture retrouvée dans `PC TP IR` et propose une trajectoire de modernisation vers un système plus stable, maintenable et compatible Windows.

## Résumé court

Le système actuel n'est pas un seul programme monolithique.

- plusieurs copies de `Spydr` sont présentes dans l'archive, mais elles ne sont pas équivalentes;
- la version réellement lancée par l'icône du vieux PC est une version caméra personnalisée, pas le `Spydr` générique;
- `Spydr` est surtout un visualiseur/analyseur d'images avec interface `Python 2 + PyGTK/Glade + Yorick`.
- `yCamicaz` est un plugin Yorick qui appelle une bibliothèque C++ locale nommée `libcamicaz`.
- `libcamicaz` parle directement au matériel:
  - un port série pour la caméra,
  - un second port série pour le chopping via la ligne DTR,
  - une carte National Instruments via NI-DAQmx.
- `darc` ajoute une couche "RTC" séparée, plus orientée contrôle temps réel, avec un wrapper C distinct.

La bonne nouvelle est que la logique utile est déjà assez bien séparée. La mauvaise est que l'ensemble dépend fortement d'une pile ancienne et Linux:

- `Python 2`
- `gtk` / `gtk.glade`
- `Yorick`
- `Boost`
- `pthread`, `open`, `ioctl`, `tcflush`
- `NIDAQmx` version Linux
- chemins `/dev/ttyS0`, `/dev/ttyS1`

## Arborescence utile

- `PC TP IR/TP_Master_version/yCamicaz`
  - plugin Yorick de pilotage direct de la caméra
- `PC TP IR/TP_Master_version/libcamicaz`
  - bibliothèque C++ qui communique avec la caméra, les ports série et la carte NI
- `PC TP IR/TP_Master_version/darc`
  - couche RTC additionnelle, distincte du widget caméra standard
- `PC TP IR/TP_Master_version/yCamicaz/yorick/spydr`
  - copie/extension locale de `Spydr`

## Versions de Spydr retrouvées

Plusieurs familles de fichiers `spydr` coexistent dans l'archive.

### 1. Version caméra personnalisée

Dossier principal:

- `PC TP IR/TP_Master_version/yCamicaz/yorick/spydr`

Caractéristiques:

- script de lancement personnalisé `spydr`
- `spydr.i` en version `0.8.3`
- intégration du plugin caméra `spydr_widgetcam.i`
- dépendance explicite à la variable d'environnement `CAMTOP`
- message de démarrage de type `SPYDR_CAM`

Cette version est celle qui inclut la pile `yCamicaz` et les commandes liées à la caméra.

### 2. Copie équivalente dans le Yorick relocatable

Dossier:

- `PC TP IR/yorick.git/relocate`

Caractéristiques:

- `relocate/bin/spydr` est strictement identique au script `TP_Master_version/yCamicaz/yorick/spydr/spydr`
- `relocate/i/spydr.i` est également la variante caméra `0.8.3`
- `relocate/python/spydr.py` est identique à la copie `TP_Master_version/yCamicaz/yorick/spydr/spydr.py`

Conclusion:

- ce n'est pas une autre branche fonctionnelle;
- c'est une seconde copie de déploiement de la même version caméra.

### 3. Version générique Spydr 0.8.2

Dossier:

- `PC TP IR/Yorick/packages/yorick-spydr-0.8.2`

Caractéristiques:

- `spydr.i` version `0.8.2`
- pas d'intégration `yCamicaz`
- pas de `spydr_widgetcam.i`
- script de lancement standard `yorick -i spydr.i`

Cette copie correspond au paquet `Spydr` générique.

### 4. Version générique de travail plus récente ou modifiée

Dossier:

- `PC TP IR/Yorick/packages/yorick-spydr`

Caractéristiques:

- contient `spydr.py`, `spydr.glade`, `spydr.conf`, etc.
- ne contient pas ici le même `spydr.i` complet que la version caméra
- le script `spydr` y reste standard

Cette copie ressemble davantage à un paquet générique ou à un répertoire de travail, mais pas au lanceur réellement utilisé pour la caméra.

## Version réellement lancée par l'icône

La photo du vieux PC permet d'identifier précisément la version active.

Ce qu'on lit à l'écran:

- `which spydr` retourne `/usr/local/bin/spydr`
- `file /usr/local/bin/spydr` indique un lien symbolique
- ce lien pointe vers:
  - `/home/etudiants/Packages/tp_master/tags/TP_Master_version/yCamicaz/yorick/spydr/spydr`

Le script correspondant retrouvé dans l'archive est:

- `PC TP IR/TP_Master_version/yCamicaz/yorick/spydr/spydr`

Son contenu montre:

- `CAMTOP=/home/etudiants/Packages/tp_master/tags/TP_Master_version/yCamicaz`
- `LD_LIBRARY_PATH=/home/etudiants/Packages/tp_master/tags/TP_Master_version/libcamicaz`
- lancement de:
  - `/home/etudiants/yorick.git/relocate/bin/yorick -i spydr.i`

Conclusion forte:

- l'icône ne lançait pas le `Spydr` standard;
- elle lançait la version `Spydr` spécifique `yCamicaz`, donc la version caméra personnalisée.

## Chaîne de lancement réelle

La chaîne de démarrage la plus probable du système historique est:

1. l'utilisateur clique l'icône `Spydr`
2. l'icône appelle `/usr/local/bin/spydr`
3. `/usr/local/bin/spydr` est un lien symbolique vers `TP_Master_version/yCamicaz/yorick/spydr/spydr`
4. ce script fixe `CAMTOP` et `LD_LIBRARY_PATH`
5. le script lance `yorick -i spydr.i` via la copie relocatable de Yorick
6. `spydr.i` charge les modules `spydr_*` spécifiques à `CAMTOP`
7. `spydr.i` charge `spydr_widgetcam.i`
8. `spydr_widgetcam.i` orchestre l'interface caméra
9. `widget_camicaz.py` fournit l'interface PyGTK
10. `yCamicaz` appelle `libcamicaz`
11. `libcamicaz` dialogue avec:
    - le port série caméra,
    - le port série chopping,
    - la carte NI

## Conséquence pour l'analyse

Pour comprendre le système réellement utilisé, il faut prendre comme référence principale:

- `TP_Master_version/yCamicaz`
- `TP_Master_version/libcamicaz`

et non:

- le paquet `yorick-spydr-0.8.2`
- ni le `Spydr` générique isolé

Autrement dit:

- la bonne base historique est `Spydr + yCamicaz + libcamicaz`;
- `Spydr` seul ne suffit pas à décrire le système observé sur le vieux PC.

## Architecture reconstituée

### 1. Interface utilisateur

Le widget caméra est en `Python 2 + PyGTK`:

- `yCamicaz/widgets/widget_camicaz.py`

Il envoie des commandes à Yorick, par exemple:

- `apply_param`
- `snap_image`
- `camicaz_start_freerun`
- `camicaz_send2spydr`
- `start_monitoring`
- `start_follow`

### 2. Orchestration Yorick

Le fichier principal du widget est:

- `yCamicaz/yorick/widget_camicaz.i`

Ce fichier:

- lance le widget Python,
- initialise `camicaz_handle`,
- appelle directement `yCamicaz_new(styctop+"/camicaz.ini")`,
- utilise `yCamicaz_get_image`, `yCamicaz_get_cube`, `yCamicaz_set_param`, etc.

Point important:

- l'ancien concept de "serveur caméra" existe encore dans le code,
- mais les appels distants `sesame_exec` sont commentés,
- le chemin réellement actif semble être local, via `camicaz.ini`.

### 3. Plugin Yorick natif

Le plugin Yorick est dans:

- `yCamicaz/yCamicaz.cpp`

Ce plugin ne contient presque pas de logique métier. Il sert surtout de pont:

- `new Camicaz(configFile)`
- récupération d'image,
- acquisition de cube,
- changement de paramètres,
- lecture monitoring,
- retour fréquence.

Conclusion:

- `yCamicaz` est un simple wrapper autour de `libcamicaz`.

### 4. Bibliothèque matérielle

Le coeur matériel est dans:

- `libcamicaz/src/camicaz.cpp`
- `libcamicaz/include/camicaz.h`
- `libcamicaz/src/TimeoutSerial.cpp`

Cette bibliothèque:

- ouvre le port série caméra,
- ouvre le port série de chopping,
- configure une tâche NI-DAQmx,
- déclenche une acquisition en envoyant `g0g1` sur le port série caméra,
- lit les données numériques via `DAQmxReadDigitalU32`,
- reconstruit l'image finale dans un tampon `256 x 256 x 2`.

### 5. Couche RTC séparée

Le dossier `darc` utilise un autre wrapper:

- `darc/src/camCamicaz.c`
- `darc/conf/configcamCamicaz.py`

Cette couche charge `libcamCamicaz.so`, qui elle-même dépend de `libcamicaz`.

Important:

- `darc/src/camCamicaz.c` a des chemins et paramètres codés en dur:
  - `/dev/ttyS0`
  - `/dev/ttyS1`
  - `"Dev1/port2,Dev1/port3"`
  - `"/Dev1/PFI3"`

Donc `darc` est encore plus couplé à l'ancien environnement Linux que le widget caméra direct.

## Configuration matérielle retrouvée

Le fichier:

- `yCamicaz/camicaz.ini`

décrit la configuration active du chemin direct:

- dimensions image:
  - `256 x 256 x 2`
- port série caméra:
  - `/dev/ttyS0`
  - `9600 bauds`
- port série chopping:
  - `/dev/ttyS1`
  - `9600 bauds`
- nombre de valeurs de housekeeping:
  - `4`
- ports NI:
  - `Dev1/port2,Dev1/port3`
- horloge externe:
  - `/Dev1/PFI3`

Précision importante:

- d'après votre information, la carte National Instruments d'origine est une `PCI-DIO-32HS`;
- cela est cohérent avec le code retrouvé, qui utilise des entrées numériques sur plusieurs ports et une horloge externe via `PFI3`, plutôt qu'une carte d'acquisition analogique classique.

## Protocole matériel déduit

Le protocole série caméra paraît simple et réimplémentable.

Commandes identifiées dans `libcamicaz/src/camicaz.cpp`:

- `g0g1`
  - déclenche une acquisition
- `t<valeur>`
  - règle le temps d'exposition
- `l<valeur>`
  - règle la latence
- `f<valeur>\n`
  - position du filtre
- `u\n`
  - lecture monitoring / housekeeping
- `h\n`
  - retour position home de la roue à filtres
- `n<valeur>\n`
  - déplacement moteur en nombre de pas
- `s<valeur>\n`
  - sauvegarde de position filtre

Réponse série:

- lecture jusqu'au caractère `>` comme terminateur.

Chopping:

- le second port série n'est pas utilisé pour un protocole texte;
- il sert à piloter la ligne `DTR` via `ioctl(TIOCMSET)`.

## Ce qui bloque un portage Windows direct

### Blocages forts

- UI en `Python 2 + PyGTK/Glade`, obsolète sous Windows moderne.
- dépendance Yorick pour l'orchestration et l'affichage.
- code C/C++ utilisant des appels Unix:
  - `pthread`
  - `open`
  - `close`
  - `ioctl`
  - `tcflush`
  - `usleep`
- build pensé pour Linux:
  - `.so`
  - `Makefile`
  - `-fPIC`
  - chemins `/usr/local/natinst/...`
- `darc` et `libcamicaz` liés à NI-DAQmx Linux.

### Blocages moyens

- la reconstruction d'image est codée dans C++ et devra être reproduite fidèlement.
- le widget historique applique des conventions spécifiques:
  - affichage des plans `Start`, `End`, `Diff`
  - inversion de signe côté Yorick sur certaines acquisitions
  - export FITS
- la présence d'une carte `PCI-DIO-32HS` implique aussi une contrainte matérielle:
  - si vous conservez cette carte, il faudra garder une machine hôte compatible PCI et une chaîne pilote adaptée;
  - si vous la remplacez, il faudra revalider toute la logique de lecture numérique et d'horloge externe.

### Blocages faibles

- le protocole série lui-même semble assez court et simple.
- le fichier `.ini` permet déjà de séparer configuration et code.

## Ce qu'il faut conserver

Je recommande de conserver seulement la connaissance métier utile:

- format des images `256 x 256 x 2`
- ordre de reconstruction du buffer NI
- commandes série et leurs paramètres
- logique `Start / End / Diff`
- sauvegarde FITS
- housekeeping
- gestion de la roue à filtres

Je recommande de ne pas conserver tel quel:

- `Spydr` comme base d'interface
- Yorick comme couche d'orchestration
- `PyGTK/Glade`
- le wrapper `darc` pour la première modernisation Windows

## Architecture cible recommandée sous Windows

### Recommandation principale

Faire une réécriture contrôlée en `Python 3` avec séparation nette en 3 couches:

1. `hardware`
   - `pyserial` pour les deux ports série
   - `nidaqmx` pour la carte NI
   - une classe `CamicazController`

2. `acquisition`
   - reconstruction image
   - acquisition simple
   - acquisition cube
   - housekeeping
   - roue à filtres
   - chopping
   - export FITS via `astropy`

3. `ui`
   - `PySide6` ou `PyQt6`
   - vue image en direct
   - réglages expo / latence / filtre
   - sauvegarde
   - monitoring

### Pourquoi Python 3 natif plutôt qu'un port C++ direct

- beaucoup plus simple pour Windows;
- accès NI officiel disponible;
- accès ports série standard;
- développement et maintenance plus faciles;
- meilleure testabilité;
- possibilité d'ajouter journalisation, configuration JSON/INI/YAML, mode simulation.

## Stratégie de migration recommandée

### Option A: recommandée

Réécriture directe du pilotage en Python 3 sous Windows.

Avantages:

- compatible Windows rapidement;
- peu de dette historique embarquée;
- plus simple à maintenir localement;
- possibilité de garder le vieux PC seulement comme référence de validation.

Inconvénients:

- il faut revalider la reconstruction image et le protocole.

### Option B: intermédiaire

Conserver temporairement l'ancien backend Linux et créer un client Windows moderne.

Avantages:

- moins de risque au tout début.

Inconvénients:

- vous gardez le vieux PC dans la boucle;
- vous ne supprimez pas la fragilité principale.

### Option C: portage C++ de `libcamicaz`

Porter `libcamicaz` vers Windows puis réécrire seulement l'UI.

Avantages:

- réutilise une partie du code existant.

Inconvénients:

- effort important pour un gain limité;
- beaucoup de code Unix à adapter;
- résultat final souvent plus fragile qu'une réécriture Python 3 claire.

## Ma recommandation pratique

Je recommande:

1. de prendre `libcamicaz` comme spécification fonctionnelle,
2. de réimplémenter le pilotage matériel en Python 3,
3. de construire une petite UI Windows moderne,
4. de laisser `Spydr` et `Yorick` de côté pour la première version.

Autrement dit:

- garder la connaissance,
- jeter la pile technique ancienne.

## Premier lot de travail concret

### Phase 1. Banc de validation sans interface

Créer un programme console Python 3 capable de:

- lire la configuration matérielle,
- ouvrir les deux ports série,
- ouvrir la tâche NI,
- envoyer `g0g1`,
- lire une image,
- reconstruire le tableau final,
- sauvegarder un FITS de test.

Livrable:

- un script `acquire_once.py`
- un fichier FITS de validation
- logs complets

### Phase 2. Fonctions de contrôle

Ajouter:

- réglage expo
- réglage latence
- position filtre
- home filtre
- déplacement moteur
- lecture housekeeping
- chopping on/off

### Phase 3. Interface Windows

Créer une UI simple:

- affichage image
- bouton acquisition
- mode freerun
- réglages
- monitoring
- sauvegarde FITS

### Phase 4. Validation croisée

Comparer ancien et nouveau système sur:

- dimensions image
- orientation image
- plan `Start`
- plan `End`
- image `Diff`
- temps d'acquisition
- cohérence housekeeping
- comportement roue à filtres

## Points d'attention

### 1. Reconstruction d'image

La routine `getLastImage()` ne copie pas simplement le buffer NI.
Elle remappe les données dans l'image finale par quadrants.

C'est un point critique de validation.

### 2. Chopping

Le chopping dépend de `DTR` sur le deuxième port série.
Sous Windows il faudra vérifier l'équivalent exact via la bibliothèque série choisie.

### 3. Monitoring

Le code C++ sait lire le monitoring, mais le widget Yorick autonome semble avoir une partie monitoring inachevée ou désactivée.
Il faudra donc valider sur le matériel réel les valeurs attendues et leur signification.

### 4. Temps réel

Si votre besoin principal est seulement le contrôle caméra et la récupération d'images, `darc` n'est probablement pas le bon point de départ.

Si vous avez encore un besoin RTC plus large, il faudra traiter `darc` comme un sous-projet distinct.

### 5. Licences

Le dépôt contient des composants sous GPL / AGPL et d'autres sous licence Boost.
Pour un usage interne ce n'est généralement pas le problème principal, mais si vous redistribuez un nouveau logiciel, il faudra refaire un point licence proprement.

### 6. Carte NI d'origine

Le modèle exact `PCI-DIO-32HS` est une information précieuse pour la suite.

Conséquences pratiques:

- le système historique lit donc vraisemblablement un flux numérique cadencé venant de la caméra, pas une image via une interface caméra moderne standard;
- la carte NI fait partie du chemin de reconstruction de l'image, elle n'est pas un simple accessoire;
- dans la modernisation Windows, il faudra décider assez tôt si l'objectif est:
  - de conserver cette carte NI et son mode de lecture,
  - ou de remplacer cette couche matérielle par une interface plus moderne.

## Conclusion

Le système n'est pas perdu ni opaque.
Au contraire, les éléments essentiels ont été retrouvés:

- configuration matérielle,
- protocole série,
- accès NI,
- format image,
- couches logicielles.

La meilleure trajectoire n'est pas de "porter Spydr".
La meilleure trajectoire est de reconstruire un contrôleur caméra moderne pour Windows, en réutilisant le comportement observé de `libcamicaz` comme référence.

## Suite proposée

La prochaine étape la plus utile est de créer un prototype Python 3 minimal de pilotage matériel, sans interface graphique, pour valider:

- ports série,
- NI-DAQmx,
- acquisition d'une image,
- reconstruction du buffer.

Si vous le souhaitez, la prochaine itération peut consister à démarrer directement ce prototype dans un nouveau dossier propre.

## Modifications récentes relevées dans le snapshot local

Important:

- le dépôt Git local n'a pas encore d'historique de commits;
- je ne peux donc pas attribuer formellement ces changements à un commit du week-end;
- de plus, les fichiers source modifiés portent surtout des dates du `9 avril 2026`, et les scripts d'outillage des dates du `9-10 avril 2026`;
- ce qui suit est donc une reconstitution des différences entre le code actif actuel et la base historique conservée dans les répertoires `.svn`.

### 1. Durcissement du backend caméra `libcamicaz`

Fichiers concernés:

- `PC TP IR/TP_Master_version/libcamicaz/include/camicaz.h`
- `PC TP IR/TP_Master_version/libcamicaz/src/camicaz.cpp`

Évolutions observées:

- ajout d'un champ de statut texte `lastErrorMessage`;
- ajout de `getStatusMessage()`;
- ajout de l'API C `camicaz_isOpen(void *hCam)`;
- `unsetupCam()` devient `unsetupCam(bool releaseDims=true)`;
- initialisation plus propre de plusieurs membres internes;
- en cas d'échec d'initialisation ou d'acquisition, le backend conserve un état cohérent au lieu de laisser des pointeurs ou drapeaux ambigus;
- `getLastImage()` renvoie maintenant une image nulle si la caméra n'est pas ouverte;
- `getMonitoring()` renvoie aussi un tableau nul si la caméra n'est pas ouverte ou si la trame de monitoring est invalide.

Interprétation:

- l'objectif semble être de rendre le système plus robuste quand la caméra ou le signal NI ne sont pas disponibles;
- ce point est important pour des essais sur banc ou des démarrages "à vide".

### 2. Remontée explicite de l'état "caméra ouverte" jusqu'à Yorick

Fichiers concernés:

- `PC TP IR/TP_Master_version/yCamicaz/yCamicaz.cpp`
- `PC TP IR/TP_Master_version/yCamicaz/yorick/yCamicaz.i`

Évolutions observées:

- ajout d'une fonction Yorick `yCamicaz_is_open`;
- export de cette fonction dans `yCamicaz.i`;
- `yCamicaz.i` ne cherche plus seulement le plugin dans des chemins relatifs, mais s'appuie explicitement sur `CAMTOP`.

Interprétation:

- le chargement devient plus fiable dans un contexte de bundle ou de copie de test;
- l'interface Yorick peut désormais tester proprement si le backend est réellement opérationnel.

### 3. Corrections et sécurisation du comportement de l'interface caméra

Fichiers concernés:

- `PC TP IR/TP_Master_version/yCamicaz/yorick/spydr/spydr.py`
- `PC TP IR/TP_Master_version/yCamicaz/yorick/spydr/spydr.i`
- `PC TP IR/TP_Master_version/yCamicaz/yorick/spydr/spydr_widgetcam.i`

Évolutions observées:

- `spydr_version` passe de `0.8.2` à `0.8.3`;
- au démarrage, l'acquisition automatique `snap_image, 1;` est désactivée;
- un avertissement utilisateur a été ajouté si aucun signal n'est détecté sur la carte National Instruments;
- le mode freerun reçoit maintenant aussi l'état du chopping;
- le freerun peut alterner le chopping à chaque image;
- un enregistrement coupe désormais d'abord le freerun si celui-ci est actif;
- ajout d'une action de homing du filtre depuis l'interface;
- après un abort ou une sauvegarde, les boutons principaux sont correctement réactivés;
- le message de progression d'acquisition a été corrigé;
- la génération du nom de fichier corrige une erreur sur les temps d'exposition `277ms`, `485ms` et `1110ms`.

Interprétation:

- ces changements ressemblent à un lot de stabilisation du flux opérateur;
- ils réduisent les cas où l'interface part dans un état incohérent ou masque une indisponibilité matérielle;
- ils apportent aussi un support plus propre des essais avec chopping et roue à filtres.

### 4. Mise en place d'un outillage de test isolé

Fichiers concernés:

- `README.md`
- `.gitignore`
- `.gitattributes`
- `tools/build-spydr-portable-bundle.ps1`
- `tools/build-spydr-system-yorick-bundle.ps1`
- `tools/spydr-portable/*`
- `tools/spydr-system-yorick/*`
- `dist/spydr_camicaz_portable_test/*`
- `dist/spydr_camicaz_test_existing_yorick/*`

Évolutions observées:

- initialisation d'un dépôt local centré sur le snapshot actif et le rapport d'analyse;
- exclusion volontaire du reste des archives historiques, des `.svn` et des bundles reconstruisibles;
- création d'un bundle de test "portable" qui embarque sa propre copie de `yorick/relocate`;
- création d'un bundle de test alternatif qui réutilise le binaire Yorick déjà présent sur la machine Linux d'origine.
- présence dans `dist/` des deux bundles déjà préparés, prêts à être copiés sur la machine Linux de test:
  - `dist/spydr_camicaz_portable_test`
  - `dist/spydr_camicaz_test_existing_yorick`

Précision:

- ces dossiers `dist/` ne sont pas le code source de référence;
- ce sont des livrables de test générés à partir du snapshot courant;
- ils comptent néanmoins bien comme un ajout récent important, car ils matérialisent la stratégie de validation sur la machine historique.

Interprétation:

- ce travail prépare une validation des correctifs sur la machine Linux historique sans écraser l'installation stable;
- c'est une bonne approche pour qualifier les changements avant toute réécriture Windows.

### 5. Lecture globale

Le snapshot actuel montre donc deux axes de travail récents:

- stabiliser l'existant historique pour qu'il supporte mieux l'absence de signal ou les séquences d'usage réelles;
- préparer un mode de test isolé sur la machine Linux d'origine.

Autrement dit, avant même la modernisation Windows, un travail de sécurisation de la pile historique a déjà commencé.

## Correction du freerun : affichage et mémoire (22 septembre 2026)

Le correctif concerne le snapshot actif `PC TP IR/TP_Master_version/yCamicaz/yorick/spydr/`
et ses deux copies de test dans `dist/`. Les archives historiques ne sont pas modifiées.

### Affichage

Le rendu 2D principal prépare désormais l'image et ses annotations hors écran,
puis les présente ensemble. Le tampon graphique temporaire est libéré après chaque
dessin, y compris en cas d'erreur. La description graphique de la dernière image
est reconstruite hors écran après sa présentation : Yorick marque sinon le dessin
pour effacement après `fma`, ce qui pouvait provoquer un écran blanc au changement
de fenêtre ou lors d'un redessin. Cette reconstruction ajoute du travail graphique,
mais ne conserve pas un historique d'images.

### Mémoire et acquisitions

- Chaque acquisition live remplace la précédente dans Spydr, même avec l'option
  d'ajout activée. Cette option reste disponible pour les images hors freerun.
- Le cube caméra courant contient les deux plans Start/End ; l'image affichée,
  les données de rendu et un éventuel fond de référence restent de taille bornée
  pour des dimensions d'image et de fenêtre fixes. Il ne s'agit donc pas d'une
  unique allocation, mais d'un nombre limité de buffers réutilisés ou remplacés.
- La boucle programme la prochaine acquisition seulement après le rendu et annule
  ses anciens rappels. Un démarrage répété ne crée pas une seconde boucle.
- L'arrêt, le passage en enregistrement et les erreurs interrompent la programmation
  des acquisitions. L'aller-retour Python de sélection à chaque image a été supprimé ;
  les changements Start/End/Diff et de soustraction du fond restent transmis.

### Validation et limites

`tools/tests/check_freerun.py` exécute les fonctions extraites des sources avec
Yorick 2.2.04 et Xvfb sous Linux, une caméra simulée et des communications GTK simulées.
Le test vérifie visuellement l'absence de publication partielle, la conservation du
dernier affichage, les sélections et le fond, les erreurs et les redémarrages.
Sur 3 000 rafraîchissements, la pile reste à une image et le cube caméra à deux plans.
La mémoire résidente de Yorick et du serveur graphique est également surveillée,
avec une tolérance de 16 Mio de croissance après les 500 premières images.
Lors de la dernière exécution réussie, Yorick passe de 10 996 Kio à 11 668 Kio
(maximum échantillonné : 11 860 Kio) et Xvfb reste à 124 544 Kio entre les images
500 et 3 000. Les quatre fichiers modifiés sont identiques dans les sources et les
deux bundles ; la syntaxe Python 2 et le fichier Glade ont aussi été vérifiés.

Ces vérifications n'établissent pas l'absence de toute fuite dans les pilotes NI,
la bibliothèque native ou GTK. La validation finale reste à effectuer sur la caméra :
freerun prolongé, changements de sélection, fond, arrêts/redémarrages, déplacement
et masquage de la fenêtre, puis contrôle de la mémoire des processus. Les fenêtres
auxiliaires et les modes contours/3D ne bénéficient pas de ce nouveau rendu tamponné.
Ce correctif ne constitue pas un portage natif Windows.
