# Spydr / Camicaz 0.9.9

Acquisition et visualisation de la camera NICMOS. Cette livraison utilise le
Yorick et les pilotes NI deja installes sur le PC instrument.

## Installer et lancer

Extraire le dossier complet dans un emplacement definitif sans espaces.
Ouvrir un terminal dans ce dossier, fermer Spydr, puis executer :

```sh
sh install_spydr.sh
```

Cette commande compile les bibliotheques dans le dossier extrait, puis cree ou
actualise `$HOME/bin/spydr-new`. A chaque mise a jour, extraire la nouvelle
archive dans un nouveau dossier definitif et executer la meme commande.
En cas d'echec de compilation, `spydr-new` conserve sa version precedente.
La commande historique `spydr` et son Yorick ne sont pas modifies.
Garder l'ancien dossier permet de revenir en arriere avec son lanceur.

La compilation demande Yorick et ses en-tetes, NI-DAQmx, Boost, make, g++ et
Python 2/PyGTK deja installes sur le PC instrument. Aucun pilote ou binaire
camera compile n'est fourni. En cas d'erreur, conserver la sortie de compilation.

Pour lancer ensuite :

```sh
spydr-new
```

Si la commande n'est pas trouvee, utiliser `$HOME/bin/spydr-new` ; ajouter
`export PATH="$PATH:$HOME/bin"` dans `~/.bash_profile` pour les prochains terminaux.
Le lancement direct depuis le dossier reste possible avec `sh run_spydr.sh`.
Pour compiler sans actualiser la commande, utiliser
`sh rebuild_with_existing_yorick.sh`.

## Icone du bureau

Creer un lanceur de type **Application dans un terminal** :

- Nom : **Spydr 0.9.9**.
- Commande : le chemin complet de `bin/spydr-new` dans le dossier personnel.
- Icone : `yCamicaz/yorick/spydr/spydr-doux-48.png` dans cette livraison.

## Utilisation

1. Choisir le filtre, l'exposition et la latence, puis faire **Apply**.
2. Renseigner le type d'observation, l'observateur, l'objet, les commentaires
   et le dossier d'enregistrement.
3. Choisir le nombre de poses ou le motif de chopping, puis cliquer **Record**.
   Si necessaire, **Apply and Record** applique d'abord les reglages ; **Cancel** annule.
4. Attendre la confirmation de sauvegarde :
   - **Saving FITS...** : sauvegarde en cours.
   - **Record successful** en vert : toutes les poses sont sauvegardees.
   - Orange : serie interrompue, avec le nombre de poses sauvegardees.
   - **Save failed - data retained** en rouge : corriger le chemin ou le disque,
     puis utiliser **Stop** pour retenter. Ne pas quitter avant d'avoir sauve le cube.

Les sondes sont relues automatiquement toutes les minutes, avec report pendant
Record. La focale effective peut etre renseignee dans le panneau des plugins.
Les temperatures utilisent la conversion historique, sans nouvelle calibration.

## Donnees FITS

Les lectures Start et End sont conservees. Les dates sont en UTC, suffixe Z,
avec six decimales ; FRAMELOG conserve separement secondes et nanosecondes
natives. Ces horodatages entourent les appels logiciels de lecture.

Voir le [schema FITS](docs/FITS_METADATA.md) pour les mots-cles, les colonnes,
les conventions d'image et les limites de precision.

## Version et validation

La 0.9.9 convertit les lectures par `ADU = 65535 - lecture_camera`, pour
obtenir Start et End entre 0 et 65535. `End - Start` est strictement inchange.
Les nouveaux FITS portent ADUOFF=65535. Les anciens cubes ne sont pas modifies.
Les darks, flats et images scientifiques doivent utiliser la meme convention.

Les tests logiciels couvrent les valeurs limites, les captures, le freerun,
les sequences Record et les metadonnees FITS. La nouvelle conversion reste
a valider sur NICMOS dans ce dossier isole. Les essais instrumentaux de
la 0.9.8b ne constituent pas une validation materielle de la 0.9.9.

Le manifeste et le bilan des tests sont dans `docs/verification/`.
Les SHA-256 des archives sont fournis sur la page de release.
L'historique des versions et les anciennes notes de correctifs restent dans
le [depot GitHub](https://github.com/Astroyan16/spydr-camicaz).
