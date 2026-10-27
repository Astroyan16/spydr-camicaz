# Lecture automatique des sondes

L'interface demande le Status trois secondes apres son initialisation, puis
toutes les 60 secondes, y compris pendant le freerun. Le bouton Status reste utilisable et remet
le compteur de 60 secondes a zero apres une lecture.

Pendant Record (y compris une sauvegarde en attente), aucune
demande de monitoring n'est envoyee. Une seule demande differee est conservee,
avec verification de disponibilite toutes les cinq secondes. Apres l'arret,
la lecture reprend donc normalement sous cinq secondes. Il n'y a ni historique
croissant en RAM, ni file de demandes accumulees.

En freerun, le Status manuel et le rappel automatique peuvent lire les sondes.
Les rappels Yorick s'executent successivement, entre deux mises a jour de
l'image. Le freerun n'est ni arrete ni relance ; une pause d'affichage pendant
la reponse serie reste possible. Aucun nouveau tampon d'images n'est ajoute.

Les commandes synchrones Apply, Homing et les acquisitions unitaires utilisent
le meme interpreteur que le rappel automatique : le rappel ne s'execute pas au
milieu de ces commandes. Il peut s'executer apres leur retour.

La fermeture annule le rappel. Le demarrage ne declenche pas de Homing ni de
changement de parametres camera.

## Reponse absente ou invalide

Les quatre sondes passent a N/A sur fond gris si la camera est indisponible,
si la lecture echoue, ou si les quatre valeurs strictement positives attendues
ne sont pas presentes. Une nouvelle tentative reste programmee a 60 secondes.
Une erreur ne produit donc plus de faux affichage vert a zero kelvin.

Le dernier echantillon valide reste disponible pour les metadonnees FITS,
avec sa date originale et son anciennete HKAGE. Une lecture en echec ne
rajeunit pas artificiellement cet echantillon. Les informations d'un Record
restent figees au debut de ce Record ; une longue sequence peut donc contenir
des temperatures anciennes. La conversion historique par le facteur 1.5
reste inchangee et ne constitue pas une nouvelle calibration des PT100.

## Limites et validation instrumentale

Status utilise la commande serie historique u et attend le prompt du rack.
Le delai maximal existant du port serie peut rendre l'interface momentanement
indisponible en cas de rack non repondant. Ce correctif ne rend pas le protocole
serie asynchrone et ne modifie pas le pilote natif.

Le pilote acquiert deja des images dans un thread en arriere-plan, meme hors
freerun. La protection logicielle evite les demandes automatiques pendant les
sequences Record ; elle ne prouve pas l'absence de tout
chevauchement materiel. La cohabitation avec ce thread conserve les mecanismes
du Status manuel existant et doit etre validee avec le rack et la NICMOS.

Sur une copie isolee, verifier : lecture au lancement puis apres une minute,
Status manuel repete, rafraichissement des sondes pendant freerun sans perte
de l'etat de zoom ni changement de contraste, absence de Status pendant Record,
reprise apres Stop, fermeture puis relance, et comportement si le rack ne
repond plus. Les tests simules ne remplacent pas cette validation.

## Installation du correctif interprete

Les dossiers de test 0.9.8 et 0.9.8b dans dist sont mis a jour. Le correctif
cumulatif spydr_auto_status_freerun_20261021.zip fournit, pour chaque version,
spydr.i, spydr.py, spydr_widgetcam.i et spydr_metadata.i. Il inclut les
corrections Record et Apply and Record precedentes.

Fermer Spydr et conserver une copie des quatre fichiers existants. Remplacer
ces quatre fichiers dans yCamicaz/yorick/spydr de la copie de test, avec les
fichiers du sous-dossier de meme version. Relancer normalement. Aucune
recompilation supplementaire n'est necessaire sur une copie deja compilee
pour cette version. Ne pas remplacer l'installation stable ni melanger
les fichiers 0.9.8 et 0.9.8b.
