# Spydr / Camicaz 0.9.4

Instantane retrospectif de `spydr_camicaz_0.9.4_test`, archive le 22 octobre 2026.

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

## Utilisation

Telecharger le ZIP de la [release v0.9.4](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.4), puis extraire son dossier dans un chemin Linux sans espaces :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

Les sources de ce tag correspondent aux fichiers utiles de la livraison conservee dans dist. Les metadonnees SVN, caches et binaires de compilation sont exclus. Le manifeste `docs/releases/v0.9.4/manifest.json` permet de verifier la correspondance des sources et de l'archive.

Cible : Scientific Linux 6.2, Yorick, Python 2/PyGTK et pilotes NI deja installes. Cette version 0.9.x est une version de test ; la validation avec la camera NICMOS reste necessaire. L'installation stable de l'instrument ne doit pas etre remplacee.

Credits : Francois Rigaut (Spydr), Arnaud Sevin et Damien Gratadour (plugin camera), Yannis Benazza (maintenance). Les licences et mentions historiques des composants sont conservees.
