# Spydr / Camicaz 0.9.8b

Release du 27 octobre 2026, issue des correctifs testes sur l'instrument.
Le tag `v0.9.8b` et les archives de cette release correspondent aux memes sources.
La 0.9.7 reste la reference de secours ; les archives et tags anterieurs sont conserves.

## Contenu

- Acquisition Record compatible avec le mini-parseur du Yorick historique
  2.2.02x : arguments positionnels, prise en charge des champs texte vides.
- Correction de la lecture de configuration avant la premiere pose.
- Metadonnees FITS d'observation : objet, observateur, commentaires UTF-8,
  reglages camera, configuration, focale et dernieres sondes disponibles.
- METAVER=2 et FRAMELOG de douze colonnes : secondes/nanosecondes UTC et
  monotones conservees, avec durees de lecture et etat du chopping.
- Dates texte UTC a six decimales, terminees par Z, converties directement
  dans Yorick uniquement a la sauvegarde, sans commande date externe.
- Confirmation Apply and Record et Status automatique avec report pendant Record.
- Fenetre redimensionnable et reglage de focale effective.
- Etat de sauvegarde explicite : Saving FITS..., succes complet en vert,
  interruption sauvegardee en orange, echec disque en rouge avec donnees retenues.
- Nouvelles icones et mention de Yannis Benazza sur la page principale About.

## Installation isolee sur Scientific Linux 6.2

Telecharger le ZIP ou le tar.gz joint a la release et extraire le dossier
complet sur le disque Linux, dans un NOUVEAU chemin sans espaces.
Depuis la racine du dossier extrait :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

Le nom historique du lanceur est conserve. L'interface et le message de
lancement indiquent desormais `Spydr / Camicaz v0.9.8b`, sans mention test.
La reconstruction utilise le Yorick, les en-tetes, NI-DAQmx, Boost, make,
g++ et Python 2/PyGTK deja presents. Les bibliotheques sont compilees dans
le dossier extrait ; le Yorick installe et l'installation stable restent intacts.
Aucun pilote NI ni binaire camera compile n'est fourni.

La reconstruction initiale est obligatoire : la 0.9.8b ajoute des fonctions
natives d'horloge. Ne pas utiliser le yCamicaz.so d'une autre version.
Pour une copie 0.9.8b deja compilee et corrigee, les modifications purement
interpretees se mettent a jour logiciel ferme ; ne pas melanger les versions.

## Validation disponible

Essais instrumentaux fournis le 22 octobre 2026 sur NICMOS avec Yorick 2.2.02x :

- Une serie de deux poses pour chacune des variantes corrigees 0.9.8 et 0.9.8b.
- Un cube 0.9.8b de cinq poses, filtre H, exposition nominale 75 ms, sans
  chopping : 5/5 poses, deux lectures Start/End de 256 x 256 pixels par pose,
  fin normale et FITS lisible avec Astropy sans avertissement structurel.
- Les dates UTC et les metadonnees sont presentes. Les durees monotones
  correspondent aux colonnes secondes/nanosecondes du journal de poses.
- L'utilisateur a ensuite confirme le fonctionnement de l'etat final de Record
  et de la mention About. Le retrait des zeros de remplissage ne change pas
  les horloges ni les donnees, et a ete verifie par les tests locaux.

Le 27 octobre, 21 scripts de regression passent : protocole historique reel,
configuration, FITS relus independamment, UTC, horloges natives C++98,
sequences et erreurs simulees, sauvegarde/reprise, Status, GTK simule,
redimensionnement, affichage, reconstruction des quadrants et liaison wrapper.
Le rendu des couleurs a aussi ete controle avec GTK2 sous WSL.
Les donnees scientifiques fournies pour les essais ne sont pas publiees dans les archives.

Ces essais ne couvrent pas a nouveau tous les modes materiels de chopping,
la mecanique de la roue a filtres, les arrets prolonges ou tous les scenarios
simules d'erreur disque. Les temperatures gardent le facteur historique 1.5 ;
aucune nouvelle calibration n'est revendiquee. Les horloges datent les appels
logiciels de lecture, pas un declenchement materiel du detecteur.

## Verification des archives

Chaque livraison contient un manifeste des fichiers et leurs SHA-256.
Le fichier SHA256SUMS joint a la release permet de verifier le ZIP et le tar.gz.
Le manifeste indique aussi le commit source exact du tag.

Documentation : [schema FITS](FITS_METADATA.md), [confirmation Record](APPLY_AND_RECORD.md),
[Status automatique](AUTO_STATUS.md), [etat final Record](RECORD_PROGRESS.md).
