# Spydr / Camicaz 0.9.2

Instantane retrospectif de `spydr_camicaz_0.9.2_test`, archive le 22 octobre 2026.

- La case Enable chopping transmet maintenant ses changements au freerun actif,
  sans devoir arreter puis relancer l'acquisition.
- Activation/desactivation prise en compte au prochain cycle, sans callback
  supplementaire. Une activation repetee ne reinitialise pas l'alternance.
- Desactiver arrete l'alternance sans imposer un retour a une position mecanique.
- Tests du callback Python et de la boucle Yorick avec camera simulee ;
  validation du mouvement reel sur l'instrument encore necessaire.

## Utilisation

Telecharger le ZIP de la [release v0.9.2](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.2), puis extraire son dossier dans un chemin Linux sans espaces :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

Les sources de ce tag correspondent aux fichiers utiles de la livraison conservee dans dist. Les metadonnees SVN, caches et binaires de compilation sont exclus. Le manifeste `docs/releases/v0.9.2/manifest.json` permet de verifier la correspondance des sources et de l'archive.

Cible : Scientific Linux 6.2, Yorick, Python 2/PyGTK et pilotes NI deja installes. Cette version 0.9.x est une version de test ; la validation avec la camera NICMOS reste necessaire. L'installation stable de l'instrument ne doit pas etre remplacee.

Credits : Francois Rigaut (Spydr), Arnaud Sevin et Damien Gratadour (plugin camera), Yannis Benazza (maintenance). Les licences et mentions historiques des composants sont conservees.
