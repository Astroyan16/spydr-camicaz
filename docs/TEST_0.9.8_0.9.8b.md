# Comparaison 0.9.8 / 0.9.8b sur le PC instrument

Deux livraisons distinctes sont disponibles :

- `dist/spydr_camicaz_0.9.8_fits_test` : horodatage logiciel a la seconde, FRAMELOG de 3 colonnes (METAVER=1).
- `dist/spydr_camicaz_0.9.8b_fits_test` : horloges natives UTC et monotone, FRAMELOG de 12 colonnes (METAVER=2).

Le dossier 0.9.8 n'est pas mis a jour par la preparation de la 0.9.8b.
L'installation stable de l'instrument reste la reference de secours.

## Preparation

Copier les deux dossiers complets sur le disque local Linux, dans deux nouveaux
dossiers de test dont les chemins ne contiennent pas d'espaces. Dans chacun :

```sh
sh rebuild_with_existing_yorick.sh
```

La 0.9.8b ajoute des fonctions natives et un fichier C++ : cette reconstruction
est obligatoire, meme si la 0.9.8 fonctionne deja. Le compilateur et les pilotes
NI deja presents sont reutilises. Les bibliotheques restent dans chaque copie.
Avec `sh`, aucun chmod n'est necessaire.

## Test avec la camera

1. Lancer une seule version a la fois avec `sh run_spydr_test.sh` et verifier la version dans le titre.
2. Renseigner Object, Observer et Comments. Renseigner la focale si elle est connue ; mettre a jour le monitoring des sondes si souhaite.
3. Cliquer sur Apply, puis enregistrer une sequence courte sans chopping dans un dossier de donnees dedie a cette version.
4. Refaire une sequence ABBA, puis une sequence interrompue avec Stop.
5. Verifier l'ouverture des FITS avec le DS9 disponible sur la cible ; selectionner le bloc primaire `[0]` si necessaire.
6. Fermer completement cette version et refaire les memes acquisitions avec l'autre version.

Conserver les memes filtre, exposition, latence, nombre d'images et options
d'affichage pour comparer la duree totale des acquisitions. La 0.9.8b doit
conserver le meme contenu Start/End et le meme ordre de chopping.
Verifier aussi le freerun : aucun journal d'images supplementaire n'y est cree.

## Controles des fichiers

SOFTVER identifie la version. Le cube primaire conserve ses dimensions et son
type numerique. Dans la 0.9.8b, verifier METAVER=2, TIMESRC=clock_gettime,
UTCRES/MONORES positifs et FRAMELOG de dimensions FITS `[12,NSAVED]`.
Ses trois premieres colonnes gardent le sens de celles de la 0.9.8.
READ_DT (colonne 12) mesure la duree monotone de l'appel de lecture camera ;
elle n'inclut pas le rendu ni les pauses entre appels.

Les resolutions UTCRES/MONORES sont celles annoncees par le noyau ; elles ne
certifient ni la synchronisation de l'heure ni l'instant physique des poses.
Les mesures locales de performance ne sont pas celles de ce PC instrument.
Le schema detaille et les exemples de lecture sont dans FITS_METADATA.md.

Le nouveau journal occupe 96 octets par exposition, soit 19.2 ko pour 200
expositions, contre environ 100 Mio pour les pixels du cube correspondant.
Les donnees TP existantes ne sont pas modifiees par cette comparaison.
