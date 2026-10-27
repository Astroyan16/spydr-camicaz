# Spydr / Camicaz

Version courante : **0.9.8b**, release publiee le 27 octobre 2026.

[Telecharger la release](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.8b)
- [Historique des versions](docs/VERSIONS.md)
- [Validation et installation 0.9.8b](docs/RELEASE_0.9.8b.md).
Le [Status automatique des sondes](docs/AUTO_STATUS.md) est demande au demarrage
puis toutes les minutes, y compris en freerun, avec report pendant Record.
La version d'execution est definie dans
`PC TP IR/TP_Master_version/yCamicaz/yorick/spydr/VERSION`.

Sources historiques et travail de maintenance du logiciel de pilotage et
d'acquisition d'une camera NICMOS, utilisant Yorick, Spydr et NI-DAQmx.

La chaine instrumentale relie l'interface Python 2 / PyGTK et Yorick au wrapper
`yCamicaz`, puis a `libcamicaz` en C++. Le detecteur comporte quatre quadrants.
Une exposition fournit deux plans, `Start` et `End`; l'image differentielle
est calculee par `End - Start`.

## Organisation

La [synchronisation vers GitLab OBSPM](docs/GITLAB_MIRROR.md) est active via
GitHub Actions, apres chaque push et avec un controle horaire.
Le [CLI glab](docs/GLAB.md) permet aussi l'acces local aux outils de suivi GitLab.

- `PC TP IR/TP_Master_version/` : sources de la chaine historique et correctifs.
- `tools/spydr-system-yorick/` : scripts de compilation et de lancement isoles.
- `tools/build-spydr-system-yorick-bundle.ps1` : generation du dossier de test
  depuis Windows.
- `tools/tests/` : tests de regression et consignes de validation.
- [Rapport de modernisation](rapport_modernisation_spydr_camicaz.md) : analyse
  de l'architecture et pistes de migration.

Les anciens environnements installes, depots imbriques, metadonnees SVN,
binaires compiles et dossiers generes `dist/` sont exclus du suivi Git.
Les fichiers LabVIEW `.vi` sont egalement exclus du perimetre actuel.

## Reconstruire une archive de release

Depuis un tag local existant, sans modifier la copie de travail :

```sh
python tools/build-spydr-release.py --ref v0.9.8b --docs-ref HEAD --launchers-ref HEAD --revision r3 --output dist/rebuild_0.9.8b_r3
```

Le dossier de sortie doit etre nouveau. Le script prend les sources exactes
avec `git archive`, produit un ZIP et un tar.gz avec manifeste et SHA-256,
et verifie que leur contenu correspond aux blobs Git du commit indique. Les sources
d'acquisition proviennent exclusivement de `--ref`. Les deux scripts de lancement
et de reconstruction peuvent etre pris dans `--launchers-ref` (par defaut `--ref`). La documentation vient de
`--docs-ref` (HEAD par defaut) ; les commits d'acquisition, des lanceurs et de documentation sont inscrits au manifeste.
L'archive contient seulement un guide `README.md`, le schema dans `docs/`,
et les informations de verification dans `docs/verification/`. Les notes de
correctifs et l'historique detaille restent dans le depot.

## Preparer une version de test

Depuis PowerShell, a la racine du depot :

```powershell
./tools/build-spydr-system-yorick-bundle.ps1
```

La generation remplace le dossier de sortie s'il existe deja. Les dossiers
generes auparavant ne sont pas automatiquement mis a jour lorsque les sources
changent. Pour produire une autre copie, utiliser le parametre `-OutputDir`
avec un nouveau chemin de dossier.

Copier le dossier genere `dist/spydr_camicaz_test_existing_yorick` sur le disque
de la machine Linux de l'instrument, dans un nouveau dossier de test dont le
chemin ne contient pas d'espaces, puis executer dans ce dossier :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

Cette variante reutilise le Yorick existant et compile les bibliotheques dans
le dossier de test. Voir les [instructions detaillees](tools/spydr-system-yorick/README_SYSTEM_YORICK.md).
Avec ces commandes, aucun `chmod` ni privilege administrateur n'est necessaire.
La compilation exige que les dependances soient deja presentes sur la cible.
La variante avec Yorick embarque exige aussi une copie locale de l'ancien
environnement `PC TP IR/yorick.git/relocate`, absent de ce depot.

## Affichage et focale

La fenetre est redimensionnable et maximisable. Sa taille minimale est calculee
apres la configuration des panneaux au demarrage. L'image est ancree en haut
a gauche, conserve ses proportions et s'adapte a l'espace disponible ; les
marges eventuelles restent a droite ou en bas. Le redimensionnement conserve
le zoom et la palette. La correction du premier affichage reste a valider
visuellement sur le PC de l'instrument.

Dans **View > Plugins pane** (`Ctrl+P`), le panneau **PSF fit** propose
**Effective focal length (mm)** et **Plate scale (arcsec/pixel)** en lecture
seule pour l'echelle calculee. L'interface reste en anglais. Le calcul
suppose des pixels NICMOS de 40 micrometres et la focale effective au detecteur,
optiques de reprise incluses. Le reglage dure pour la session et s'applique
a l'image courante ainsi qu'aux prochaines acquisitions. Activer
**View > Graph axis in arcsec** pour les coordonnees angulaires.
Voir les [details et limites du reglage](docs/FOCALE_NICMOS.md).

Pour la seule correction de taille initiale et de placement, une copie de test
compilee issue du test de focale precedent peut etre mise a jour, Spydr ferme,
en remplacant `spydr.py` et `spydr.glade` dans `yCamicaz/yorick/spydr`.
Ces deux fichiers ne demandent aucune recompilation. Une nouvelle livraison
complete exige en revanche la reconstruction de ses bibliotheques ; les
changements C/C++ ou du wrapper Yorick peuvent aussi l'exiger.

## Environnement et validation

Le [correctif Record du 21 octobre 2026](docs/CORRECTIF_RECORD_20261021.md)
corrige un blocage avant la premiere pose dans les livraisons initiales
0.9.8/0.9.8b. Les dossiers complets dans dist sont corriges ; une copie deja
compilee peut recevoir le seul spydr_metadata.i correspondant a sa version.

Depuis la 0.9.8, les fichiers produits par **Record** contiennent les
metadonnees d'observation dans leur en-tete et un journal par exposition
dans l'extension `FRAMELOG`. Les textes complets, accents compris, sont
conserves dans un bloc JSON encode. Voir le [schema FITS](docs/FITS_METADATA.md)
pour les champs, leur interpretation et les limites des mesures.
La **0.9.8b** ajoute les horloges UTC et monotone natives avec conservation des
secondes/nanosecondes dans FRAMELOG (schema METAVER=2, 12 colonnes).
Elle doit etre reconstruite dans son propre dossier de test ; le dossier
0.9.8 deja livre reste disponible pour comparaison.

La cible historique est Scientific Linux 6.2 avec Yorick, Python 2, PyGTK,
NI-DAQmx, les outils de compilation C/C++ et leurs dependances. Le depot
n'embarque pas les pilotes NI ni un environnement Linux complet.

Les correctifs doivent etre valides sur l'instrument avant d'etre consideres
comme une version stable. Les tests logiciels disponibles et leurs limites
sont decrits dans [tools/tests/README.md](tools/tests/README.md).

Depuis la 0.9.6, les parametres affiches doivent correspondre au dernier Apply
reussi avant Record. Le [correctif Apply and Record](docs/APPLY_AND_RECORD.md)
ajoute une alerte proposant Apply and Record ou Cancel si necessaire, y compris
apres Homing. L'acquisition attend le retour reussi des commandes au rack.
Les fichiers incluent les secondes et un suffixe numerote en cas de collision ;
l'ecrasement est desactive. Les acquisitions interrompues portent `-partial`.
En cas d'echec de sauvegarde, ne pas quitter le logiciel : le cube reste en
memoire et les acquisitions restent verrouillees. Corriger le probleme disque
ou les permissions du dossier de destination, puis appuyer sur Stop pour
retenter la sauvegarde. Ce stockage en memoire ne protege pas d'un arret du PC.

Le premier commit capture l'etat actuel, qui comprend deja des modifications.
Il ne constitue pas une archive certifiee de la version stable d'origine.

## Credits

Spydr : Francois Rigaut. Plugin camera : Arnaud Sevin et Damien Gratadour.

Reprise du projet, maintenance et ameliorations :
**Yannis Benazza** - [yannis.benazza@obspm.fr](mailto:yannis.benazza@obspm.fr).

## Licences

Les mentions et licences historiques sont conservees dans les sources.
Spydr contient une [copie de la GNU GPL version 3](PC%20TP%20IR/TP_Master_version/yCamicaz/yorick/spydr/LICENSE).
La presence de ce fichier ne determine pas a elle seule la licence des autres
composants de cette chaine.
