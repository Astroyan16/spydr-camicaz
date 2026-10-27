# Metadonnees FITS des acquisitions Record (0.9.8b)

Les nouvelles acquisitions Record conservent leur tableau primaire historique :
`[256,256,2,N]` dans l'ordre FITS, ou `[256,256,2]` pour une seule exposition.
Les deux lectures sont Start puis End. Diff correspond a End - Start et n'est
pas stocke comme une troisieme lecture. Les valeurs signees sont reconstruites
par quadrants et inversees en signe par la chaine Camicaz/Spydr.
La soustraction du fond d'affichage ne modifie pas les donnees enregistrees.

Les informations sont figees au lancement de Record. Un changement ulterieur
dans l'interface n'altere pas la description de l'acquisition en cours.
Les donnees TP anterieures ne sont pas modifiees et leurs informations absentes
ne peuvent pas etre reconstituees automatiquement.

## En-tete primaire

| Mots-cles | Signification |
| --- | --- |
| SIMPLE, BITPIX, NAXIS, NAXISn | Structure et type numerique |
| ORIGIN, INSTRUME, SOFTVER, METAVER | Logiciel, instrument, version et schema |
| BUNIT | Comptages numeriques, sans calibration photometrique |
| READ1, READ2, CTYPEn | Interpretation des lectures et des axes |
| OBSTYPE, OBJECT, OBSERVER | Type d'observation, objet et observateur |
| COMMENT | Resume des notes et copie de la configuration camera |
| FILTER, EXPTIME, LATENCY | Filtre et durees nominales selectionnees en secondes |
| EXPIDX, LATIDX | Indices des reglages appliques |
| NSAVED, NREQUEST, NCYCLE | Expositions sauvegardees, expositions demandees, cycles demandes |
| PARTIAL, STOPWHY | Acquisition partielle et motif de fin |
| TIMESYS, DATE-OBS, MJD-OBS | UTC de lancement du Record avant l'image d'amorcage |
| DATE-END, MJD-END | UTC de fin de l'acquisition, avant la sauvegarde et ses tentatives |
| DATE | UTC de creation du fichier |
| TIMEPREC | Resolution de representation des dates UTC textuelles en secondes |
| TIMESRC, UTCRES, MONORES | Source et resolutions nominales des horloges natives |
| CHOPPING, CHOPPAT, CHOPWAIT, CHOPMAP | Activation, motif repete, attente et correspondance DTR |
| XPIXSZ, YPIXSZ | Pas natif suppose : 40 micrometres |
| FOCVALID, FOCALLEN, PIXSCALE | Focale effective saisie en mm et echelle native en arcsec/pixel |
| BGSUB | Faux : le fond d'affichage n'a pas ete soustrait au cube |
| HKVALID, HKMJD, HKAGE | Disponibilite, date et anciennete des dernieres sondes disponibles |
| HKRAW1..4, HKFACTOR, TEMP1..4 | Valeurs brutes, facteur historique 1.5 et valeurs affichees en K |
| METAFMT, METACNT, META0001.. | Textes utilisateur complets encodes sans perte |

La date et l'heure proviennent de l'horloge du PC. Elles ne prouvent ni sa
synchronisation ni l'instant exact du declenchement du detecteur. Depuis la
0.9.8b, `clock_gettime(CLOCK_REALTIME)` et `clock_gettime(CLOCK_MONOTONIC)` sont
appeles depuis un module C++98. Les secondes et nanosecondes sont conservees
separement pour chaque pose. UTCRES et MONORES donnent la resolution nominale
annoncee par le systeme, pas l'exactitude des instants physiques de pose.
La commande GNU `date` convertit les dates uniquement lors de la sauvegarde ;
aucun processus, conversion textuelle ou acces disque n'est ajoute entre poses.
Les durees EXPTIME et LATENCY decrivent les reglages, pas une mesure
independante du temps d'integration effectif.

CHOPPAT est le motif logique : A = DTR desactive (0), B = DTR active (1).
La correspondance physique avec une position sur le ciel reste a verifier.
NCYCLE indique la demande ; NSAVED indique ce qui a effectivement ete conserve.
PARTIAL permet de distinguer une acquisition interrompue.

Le journal et les metadonnees sont limites a l'acquisition courante : ils sont
reinitialises au Record suivant. Le freerun n'accumule pas de journal.

## Sondes et focale

Aucune lecture serie supplementaire n'est ajoutee au Record. Le fichier conserve
les quatre dernieres valeurs positives recues lors d'une demande de monitoring,
avec leur date et leur anciennete au debut du Record. Une valeur nulle ou une
lecture incomplete ne remplace pas ce cache et ne change pas sa date. HKAGE
doit donc etre consulte : HKVALID signifie qu'une lecture exploitable
est disponible, pas que la calibration ou la position des sondes est certifiee.
Le facteur 1.5 est celui de l'affichage historique ; les valeurs brutes permettent
de revoir la conversion ulterieurement. Sans mesure disponible, les temperatures
sont omises et HKVALID est faux : aucune temperature fictive n'est ecrite.

Le [Status automatique](AUTO_STATUS.md) demande ces valeurs au demarrage puis
toutes les minutes, y compris en freerun, sans lecture pendant Record.

Sans focale saisie, FOCVALID est faux et FOCALLEN/PIXSCALE sont omis.
La focale effective comprend les optiques de reprise. PIXSCALE decrit les pixels
natifs du cube enregistre, independamment du zoom/rebinning de l'affichage.
Il ne s'agit pas d'un WCS celeste : aucune coordonnee RA/Dec, orientation,
distorsion, gain, bruit de lecture ou calibration photometrique n'est inventee.

## Extension FRAMELOG

En 0.9.8b (METAVER=2), FRAMELOG est une extension IMAGE double precision de
dimensions FITS `[12,N]`. Dans NumPy/Astropy, sa forme est `(N,12)`.
La ligne i correspond a l'exposition i du tableau primaire.

| Colonne FITS (NumPy = colonne - 1) | Nom | Valeur / unite |
| --- | --- | --- |
| 1 | MJD-REQUEST | UTC avant la lecture, en jours MJD |
| 2 | MJD-RETURN | UTC au retour, en jours MJD |
| 3 | DTR | 0=A, 1=B, -1=chopping desactive |
| 4 | UTCREQ_S | Secondes UTC entieres depuis 1970 avant lecture |
| 5 | UTCREQ_N | Nanosecondes UTC dans la seconde, avant lecture |
| 6 | UTCRET_S | Secondes UTC entieres au retour |
| 7 | UTCRET_N | Nanosecondes UTC dans la seconde, au retour |
| 8 | MONOREQ_S | Secondes monotones entieres avant lecture |
| 9 | MONOREQ_N | Nanosecondes monotones dans la seconde, avant lecture |
| 10 | MONORET_S | Secondes monotones entieres au retour |
| 11 | MONORET_N | Nanosecondes monotones dans la seconde, au retour |
| 12 | READ_DT | Duree de l'appel de lecture selon l'horloge monotone, en secondes |

Les colonnes secondes/nanosecondes gardent exactement les valeurs natives.
Les deux horloges sont lues successivement et ne sont pas simultanees. La
representation MJD en double precision arrondit les dates ; les colonnes
separees evitent cette perte. Les dates textuelles sont representees a la
microseconde. L'horloge monotone est relative au demarrage du PC : elle permet
de calculer les durees meme si l'heure UTC est corrigee pendant l'acquisition.
Ne pas soustraire une date monotone a une date UTC.

La 0.9.8 (METAVER=1), conservee pour comparaison, utilise `[3,N]` avec des temps
a la seconde. Les trois premieres colonnes gardent le meme sens dans la 0.9.8b.

Ces temps encadrent l'appel logiciel de lecture ; ils ne sont pas des mesures
des instants physiques de debut/fin de pose.
Seules les lectures valides ajoutees au cube apparaissent dans ce journal.
L'image d'amorcage exclue du cube n'y figure pas.
Le journal utilise 96 octets par exposition (24 octets en 0.9.8), contre environ
512 Kio pour ses deux plans camera. Il est reinitialise a chaque Record et
n'est pas alimente en freerun.

## Textes complets et accents

Les mots-cles OBJECT/OBSERVER et les notes lisibles sont des resumes ASCII.
Pour eviter les limites de longueur du redacteur FITS historique et conserver
les accents, guillemets et sauts de ligne, le texte original complet est conserve
en JSON UTF-8 encode en Base64, reparti en cartes META0001, META0002, etc.
Ce bloc contient object, observer, comments, focal_length_mm et software_version.

Exemple de lecture avec Python et Astropy :

```python
import base64
import json
from astropy.io import fits

with fits.open("acquisition.fits") as hdus:
    header = hdus[0].header
    encoded = "".join(header[f"META{i:04d}"]
                      for i in range(1, header["METACNT"] + 1))
    metadata = json.loads(base64.b64decode(encoded))
    cube = hdus[0].data
    frame_log = hdus["FRAMELOG"].data
    print(metadata)
```

Cette evolution concerne les fichiers produits par Record. Les commandes
generiques d'export d'une image depuis le visualiseur ne recopient pas encore
cet ensemble de metadonnees ; conserver les fichiers Record pour l'archivage.

## Validation et livraison

`python tools/tests/check_fits_metadata.py` utilise Astropy et le vrai redacteur
Yorick (WSL Ubuntu sous Windows). Il verifie le format FITS independamment, les
valeurs du cube, les textes longs/Unicode, le journal, les sondes, les informations
figees, les donnees absentes et les acquisitions partielles.
Le meme test a aussi ete execute avec le `fits.i` historique copie depuis
`PC TP IR/yorick.git/relocate/i/fits.i`, via l'option `--fits-library`.
`python3 tools/tests/check_native_clock.py` sous Linux/WSL compile le module
C++98 avec les en-tetes historiques et teste les vraies horloges via Yorick.
Il affiche aussi un temps moyen indicatif par lecture sur la machine de test.
Ce chiffre ne remplace pas une mesure sur le vieux PC.
Les tests de sequence simulent aussi un saut de l'heure UTC, une erreur
d'horodatage et une reprise apres erreur disque ; les donnees et les temps
deja conserves restent coherents.
Les tests des sequences, collisions, sauvegarde et reprise apres erreur disque
restent applicables. La validation avec NI et NICMOS reste necessaire.

Pour une nouvelle copie de test complete :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

La 0.9.8b exige une reconstruction des bibliotheques dans sa propre copie de test :
elle ajoute `yCamicaz_clock.cpp`, deux fonctions natives et l'edition de liens
avec `librt` pour l'ancien Linux. Copier seulement les fichiers Python/Yorick
dans une ancienne copie compilee ne suffit pas. La 0.9.8 deja livree est conservee
dans son dossier distinct pour comparaison.


## Format des dates de la release 0.9.8b

`DATE-OBS`, `DATE-END` et `DATE` sont en UTC, par exemple
`2026-10-22T17:23:57.009504Z`, avec six decimales. La conversion utilise
uniquement quelques operations dans Yorick, au moment de la sauvegarde.
Elle ne lance aucun processus `date` et ne change pas l'heure du PC.

Ces champs texte sont arrondis a la microseconde ; les secondes et nanosecondes
natives restent separees dans FRAMELOG. Les valeurs MJD de l'en-tete peuvent
etre davantage arrondies par la bibliotheque FITS historique : pour les
comparaisons temporelles fines, utiliser les colonnes separees de FRAMELOG.
La resolution declaree des horloges ne garantit pas leur exactitude ni une
datation materielle du declenchement du detecteur.
