# Spydr / Camicaz 0.9.9

Release du 19 novembre 2026.

## Conversion ADU

Les lectures Start et End utilisent desormais `ADU = 65535 - lecture_camera`
au lieu de `-lecture_camera`. Elles sont comprises entre 0 et 65535, dans le
sens croissant du signal. Le changement concerne Record, les captures simples,
les cubes et le freerun, dans Spydr et dans l'interface Camicaz historique.

L'ajout de la meme constante aux deux lectures conserve exactement
`Diff = End - Start`. Il ne supprime pas les differences negatives de bruit.
Les anciens cubes restent inchanges. Pour comparer leurs lectures Start/End
avec cette version, leur ajouter 65535 une seule fois. Darks, flats et images
scientifiques doivent utiliser la meme convention.

Le nouveau mot-cle descriptif non standard `ADUOFF=65535` et les cartes HISTORY
documentent la conversion. ADUOFF n'est pas un offset electronique mesure.
Le schema temporel METAVER=2 et FRAMELOG restent inchanges.

## Installation isolee

Telecharger le ZIP ou le tar.gz joint a la release. Extraire dans un NOUVEAU
dossier Linux sans espaces, puis executer depuis sa racine :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

La reconstruction utilise le Yorick et les dependances instrumentales deja
installes ; les bibliotheques sont compilees dans le nouveau dossier.
Ne pas remplacer l'installation stable ni son Yorick. Les archives ne
contiennent pas de pilotes NI ou de bibliotheques camera compilees.

## Validation

Les tests logiciels exercent les fonctions de production Yorick avec une camera
simulee : codes limites, Start/End distincts, conservation de Diff, captures,
freerun et sequences Record. Les FITS produits par Yorick sont relus avec Astropy
pour verifier les donnees et les metadonnees, dont ADUOFF et HISTORY.
Le bilan exact des tests livres figure dans `docs/verification/VALIDATION.json`.
Les 24 scripts passent sous WSL Ubuntu ; la verification Astropy des FITS utilise
Python Windows avec le redacteur Yorick sous WSL. Le freerun est exerce sur
3000 images. Le test UTC est adapte aux numeros de version sans suffixe,
en conservant les microsecondes introduites en 0.9.8b.

La conversion 0.9.9 reste a valider avec la camera NICMOS. Les essais instrumentaux
anterieurs de la 0.9.8b ne sont pas une validation materielle de cette version.
Controler Start, End et Diff, ainsi que les darks/flats, dans la copie isolee.

Les archives ZIP et tar.gz contiennent un manifeste avec le commit source exact
et les empreintes des fichiers. SHA256SUMS.txt permet de verifier les archives.
