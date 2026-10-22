# Spydr / Camicaz 0.9.0

Instantane retrospectif de `spydr_camicaz_0.9.0_test`, archive le 22 octobre 2026.

- Identification commune dans le titre de la fenetre, le dialogue A propos,
  le message de demarrage et les lanceurs des bundles.
- Fichier VERSION commun a Python, Yorick et aux scripts de lancement.
- Premiere version identifiee du travail de maintenance : gestion freerun /
  Record, erreurs DAQmx et ameliorations d'affichage presentes dans les sources.

Cette version reste a valider sur la camera et la machine Linux d'origine.
Les versions historiques des composants tiers et leurs licences sont conservees.

## Utilisation

Telecharger le ZIP de la [release v0.9.0](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.0), puis extraire son dossier dans un chemin Linux sans espaces :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

Les sources de ce tag correspondent aux fichiers utiles de la livraison conservee dans dist. Les metadonnees SVN, caches et binaires de compilation sont exclus. Le manifeste `docs/releases/v0.9.0/manifest.json` permet de verifier la correspondance des sources et de l'archive.

Cible : Scientific Linux 6.2, Yorick, Python 2/PyGTK et pilotes NI deja installes. Cette version 0.9.x est une version de test ; la validation avec la camera NICMOS reste necessaire. L'installation stable de l'instrument ne doit pas etre remplacee.

Credits : Francois Rigaut (Spydr), Arnaud Sevin et Damien Gratadour (plugin camera), Yannis Benazza (maintenance). Les licences et mentions historiques des composants sont conservees.
