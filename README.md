# Spydr / Camicaz 0.9.1

Instantane retrospectif de `spydr_camicaz_0.9.1_test`, archive le 22 octobre 2026.

- Retour au cadrage automatique de l'image principale au passage d'un cube
  enregistre au freerun, pour eviter de conserver un zoom vertical residuel.
- Le zoom utilisateur reste conserve lors d'un redemarrage ordinaire du freerun.
- Regression Yorick/Gist avec un cube de 800 expositions (200 cycles ABBA) et
  un cadrage vertical residuel simule. Validation materielle encore necessaire.

## Utilisation

Telecharger le ZIP de la [release v0.9.1](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.1), puis extraire son dossier dans un chemin Linux sans espaces :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

Les sources de ce tag correspondent aux fichiers utiles de la livraison conservee dans dist. Les metadonnees SVN, caches et binaires de compilation sont exclus. Le manifeste `docs/releases/v0.9.1/manifest.json` permet de verifier la correspondance des sources et de l'archive.

Cible : Scientific Linux 6.2, Yorick, Python 2/PyGTK et pilotes NI deja installes. Cette version 0.9.x est une version de test ; la validation avec la camera NICMOS reste necessaire. L'installation stable de l'instrument ne doit pas etre remplacee.

Credits : Francois Rigaut (Spydr), Arnaud Sevin et Damien Gratadour (plugin camera), Yannis Benazza (maintenance). Les licences et mentions historiques des composants sont conservees.
