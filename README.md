# Spydr / Camicaz

Version courante : **0.9.0**, version de test a valider sur l'instrument.
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

## Preparer une version de test

Depuis PowerShell, a la racine du depot :

```powershell
./tools/build-spydr-system-yorick-bundle.ps1
```

Copier le dossier `dist/spydr_camicaz_test_existing_yorick` sur la machine Linux
de l'instrument, puis executer dans ce dossier :

```sh
chmod +x ./*.sh
./rebuild_with_existing_yorick.sh
./run_spydr_test.sh
```

Cette variante reutilise le Yorick existant et compile les bibliotheques dans
le dossier de test. Voir les [instructions detaillees](tools/spydr-system-yorick/README_SYSTEM_YORICK.md).
La variante avec Yorick embarque exige aussi une copie locale de l'ancien
environnement `PC TP IR/yorick.git/relocate`, absent de ce depot.

## Environnement et validation

La cible historique est Scientific Linux 6.2 avec Yorick, Python 2, PyGTK,
NI-DAQmx, les outils de compilation C/C++ et leurs dependances. Le depot
n'embarque pas les pilotes NI ni un environnement Linux complet.

Les correctifs doivent etre valides sur l'instrument avant d'etre consideres
comme une version stable. Les tests logiciels disponibles et leurs limites
sont decrits dans [tools/tests/README.md](tools/tests/README.md).

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
