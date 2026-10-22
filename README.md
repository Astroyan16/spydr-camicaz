# Spydr / Camicaz 0.9.3

Instantane retrospectif de `spydr_camicaz_0.9.3_test`, archive le 22 octobre 2026.

- Record utilise le dossier selectionne, et non le dossier affiche dans le
  selecteur GTK, qui peut etre son parent lors de la premiere sequence.
- Une selection absente ou un dossier inexistant bloque le lancement avec un
  message, sans arreter le freerun ni desactiver les commandes.
- Echappement des antislashs et guillemets du chemin transmis a Yorick.
- Regression du callback Record avec dossiers temporaires et GTK simule.

## Utilisation

Telecharger le ZIP de la [release v0.9.3](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.3), puis extraire son dossier dans un chemin Linux sans espaces :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

Les sources de ce tag correspondent aux fichiers utiles de la livraison conservee dans dist. Les metadonnees SVN, caches et binaires de compilation sont exclus. Le manifeste `docs/releases/v0.9.3/manifest.json` permet de verifier la correspondance des sources et de l'archive.

Cible : Scientific Linux 6.2, Yorick, Python 2/PyGTK et pilotes NI deja installes. Cette version 0.9.x est une version de test ; la validation avec la camera NICMOS reste necessaire. L'installation stable de l'instrument ne doit pas etre remplacee.

Credits : Francois Rigaut (Spydr), Arnaud Sevin et Damien Gratadour (plugin camera), Yannis Benazza (maintenance). Les licences et mentions historiques des composants sont conservees.
