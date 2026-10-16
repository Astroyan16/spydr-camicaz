# Historique Spydr / Camicaz

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
