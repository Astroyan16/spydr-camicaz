# Spydr / Camicaz 0.9.7

Instantane retrospectif de `spydr_camicaz_0.9.7_test`, archive le 22 octobre 2026.

- Correction d'un decalage d'un pixel dans l'origine du premier amplificateur
  lors de la reconstruction des quadrants. Le defaut decalait un quadrant,
  creait un chevauchement et laissait 128 pixels non renseignes par lecture.
- Ordre des amplificateurs et separation Start/End conserves. Aucun changement
  de signe, de gain ou d'offset des valeurs recues.
- Regression C++98 de la fonction reelle sur chaque pixel des deux lectures,
  les jonctions des quadrants, l'unicite des echantillons et les bornes memoire.
  L'orientation physique et les extrema restent a verifier sur l'instrument.

## Utilisation

Telecharger le ZIP de la [release v0.9.7](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.7), puis extraire son dossier dans un chemin Linux sans espaces :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

Les sources de ce tag correspondent aux fichiers utiles de la livraison conservee dans dist. Les metadonnees SVN, caches et binaires de compilation sont exclus. Le manifeste `docs/releases/v0.9.7/manifest.json` permet de verifier la correspondance des sources et de l'archive.

Cible : Scientific Linux 6.2, Yorick, Python 2/PyGTK et pilotes NI deja installes. Cette version 0.9.x est une version de test ; la validation avec la camera NICMOS reste necessaire. L'installation stable de l'instrument ne doit pas etre remplacee.

Credits : Francois Rigaut (Spydr), Arnaud Sevin et Damien Gratadour (plugin camera), Yannis Benazza (maintenance). Les licences et mentions historiques des composants sont conservees.
