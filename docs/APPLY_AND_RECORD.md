# Confirmation Apply and Record

## Comportement

Au clic sur Record, Yorick compare le filtre, l'exposition et la latence affiches
aux derniers parametres appliques avec succes. Si ces trois valeurs correspondent,
l'acquisition demarre normalement.

Si Apply n'a jamais reussi, si les reglages ont change, ou apres Homing,
une fenetre modale en anglais propose :

- **Cancel** : ne modifie aucun reglage et ne demarre pas Record. Un freerun en cours reste actif.
- **Apply and Record** : arrete le freerun, applique les trois parametres puis demarre le Record demande, seulement apres le retour reussi de la commande camera.

Cancel est la reponse par defaut. La fermeture de la fenetre equivaut a Cancel.
Les metadonnees, destination, nombre de poses et sequence correspondent a la
demande initiale ; changer le filtre, l'exposition ou la latence pendant la
preparation annule la demande et invite a recliquer sur Record.

Un seul Record peut etre prepare a la fois. Les reponses anciennes ou dupliquees
ne demarrent pas une seconde acquisition. Si une acquisition attend encore sa
sauvegarde, elle reste prioritaire et aucune nouvelle demande n'est lancee.

## Attente du rack et Homing

Le code C++ existant envoie successivement les reglages d'exposition, de latence
et de filtre et attend, pour chaque commande serie, le retour du prompt `>` du
rack. La nouvelle fonction s'appuie sur cette attente existante. Aucun delai
arbitraire supplementaire ni commande Homing automatique n'est ajoute.

Homing envoie la commande `h`; la selection de filtre utilise `f` puis le numero
de filtre. Le role mecanique exact de `h` et le fait que `>` signifie bien la fin
du mouvement restent a confirmer sur le rack. Aucun capteur logiciel independant
ne valide la position physique. Apres Homing, le cache des parametres appliques
est invalide afin de refaire Apply avant le prochain Record.

Si l'application des parametres echoue ou si la camera est indisponible au retour,
les parametres restent non confirmes, l'acquisition ne demarre pas et une fenetre
d'erreur signale l'echec. La barre d'etat conserve le detail de l'erreur.

## Installation du correctif

Les dossiers complets 0.9.8 et 0.9.8b dans dist sont mis a jour. Pour une copie
deja compilee, fermer Spydr puis prendre les trois fichiers dans le sous-dossier
du correctif correspondant exactement a sa version :

- spydr.py
- spydr_widgetcam.i
- spydr_metadata.i (inclut le correctif du blocage Record du 21 octobre)

Les copier dans `yCamicaz/yorick/spydr/` de cette copie de test, puis relancer :

```sh
sh run_spydr_test.sh
```

Ces modifications ne demandent pas de recompilation. Ne pas intervertir les
variantes 0.9.8 et 0.9.8b. Une nouvelle copie complete doit toujours etre compilee
avant son premier lancement.

## Validation

Les callbacks Python sont testes avec des doubles GTK : ouverture differee de
l'alerte hors lecture du pipe, Cancel, confirmation, reponse par defaut, doublons,
demande obsolete et changement des selections. Les tests Yorick des deux versions
verifient le controle initial, le mapping des filtres, l'invalidation apres
Homing, Apply avant la premiere lecture et l'absence d'acquisition si Apply echoue.

Sur la manip, tester d'abord Cancel puis Apply and Record avec une sequence courte,
et verifier le comportement de la roue a filtres au retour du rack. Les simulations
ne valident pas la synchronisation mecanique ni la boite de dialogue PyGTK2 reelle.
