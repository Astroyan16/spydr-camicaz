# Spydr / Camicaz 0.9.8b

Acquisition et visualisation de la camera NICMOS. Cette livraison utilise le
Yorick et les pilotes NI deja installes sur le PC instrument.

## Installer et lancer

Extraire le dossier complet dans un emplacement definitif sans espaces.
Ouvrir un terminal dans ce dossier, puis executer une premiere fois :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

La compilation reste dans le dossier extrait. Elle demande Yorick et ses
en-tetes, NI-DAQmx, Boost, make, g++ et Python 2/PyGTK. Aucun pilote ou binaire
camera compile n'est fourni. La version historique et son Yorick sont conserves.
Pour les lancements suivants, seule la deuxieme commande est necessaire.

## Commande spydr-new

Depuis ce meme dossier :

```sh
SPYDR_DIR=$(pwd -P)
mkdir -p "$HOME/bin"
cat > "$HOME/bin/spydr-new" <<EOF
#!/bin/sh
exec /bin/sh "$SPYDR_DIR/run_spydr_test.sh" "\$@"
EOF
chmod +x "$HOME/bin/spydr-new"
```

Si `$HOME/bin` n'est pas dans PATH, ajouter cette ligne a `~/.bash_profile`,
puis ouvrir un nouveau terminal :

```sh
export PATH="$PATH:$HOME/bin"
```

La commande `spydr-new` lance cette livraison. La commande `spydr` garde son
role historique. Le dossier de la nouvelle version doit conserver son emplacement.

## Icone du bureau

Creer un lanceur de type **Application dans un terminal** :

- Nom : **Spydr 0.9.8b**.
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

La release inclut les corrections Record du Yorick historique, les metadonnees,
les horloges UTC/monotone, les dates UTC, l'etat final de sauvegarde, les icones
et le credit de maintenance dans About.

Des series de deux puis cinq poses sans chopping ont ete verifiees sur NICMOS
avec Yorick 2.2.02x ; les 21 scripts de regression passent. Tous les modes
materiels n'ont pas fait l'objet de nouveaux essais. La 0.9.7 reste disponible
comme reference de secours.

Le manifeste et le bilan des tests sont dans `docs/verification/`.
Les SHA-256 des archives sont fournis sur la page de release.
L'historique des versions et les anciennes notes de correctifs restent dans
le [depot GitHub](https://github.com/Astroyan16/spydr-camicaz).
