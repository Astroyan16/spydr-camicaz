# Spydr / Camicaz 0.9.6

Instantane retrospectif de `spydr_camicaz_0.9.6_test`, archive le 22 octobre 2026.

- Noms de fichiers a la seconde, suffixes numerotes en cas de collision et
  sauvegardes Record sans ecrasement des fichiers existants.
- Etat d'enregistrement explicite ; Stop annule le callback et termine la
  sauvegarde avant de reactiver les commandes. Les callbacks tardifs sont ignores.
- Erreurs d'acquisition et de chopping remontees par le wrapper C++ ; seules les
  images valides sont conservees, avec suffixe -partial si le cube est incomplet.
- En cas d'erreur disque, conservation du cube et du verrou d'acquisition ;
  Stop permet de retenter apres correction, sans retirer deux fois l'image initiale.
- Record exige un Apply reussi correspondant aux parametres affiches. Les
  erreurs serie invalident la confirmation ; appliquer de nouveau les trois
  parametres apres un echec. Le motif choisi survit a la reactivation du chopping.
- Tests avec vrais fichiers FITS et tests C++98 sur doubles materiels ; pas de
  compilation complete NI-DAQmx ni de validation de la mecanique sur ce PC.

## Utilisation

Telecharger le ZIP de la [release v0.9.6](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.6), puis extraire son dossier dans un chemin Linux sans espaces :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

Les sources de ce tag correspondent aux fichiers utiles de la livraison conservee dans dist. Les metadonnees SVN, caches et binaires de compilation sont exclus. Le manifeste `docs/releases/v0.9.6/manifest.json` permet de verifier la correspondance des sources et de l'archive.

Cible : Scientific Linux 6.2, Yorick, Python 2/PyGTK et pilotes NI deja installes. Cette version 0.9.x est une version de test ; la validation avec la camera NICMOS reste necessaire. L'installation stable de l'instrument ne doit pas etre remplacee.

Credits : Francois Rigaut (Spydr), Arnaud Sevin et Damien Gratadour (plugin camera), Yannis Benazza (maintenance). Les licences et mentions historiques des composants sont conservees.
