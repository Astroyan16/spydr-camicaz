# Focale effective NICMOS

Dans le menu d'affichage, activer **Plugins pane** (raccourci **Ctrl+P**).
Dans le panneau PSF fit, l'ancien champ pixsize est remplace par :

- **Effective focal length (mm)** : focale au detecteur, optiques de reprise incluses.
- **Plate scale (arcsec/pixel)** : echelle de l'image courante, non modifiable ici.

L'interface reste en anglais, comme le reste du logiciel.

Les pixels natifs sont supposes mesurer 40 micrometres.
La formule des petits angles est :

`echelle = (180 * 3600 / pi) * 0.040 / focale_mm`

Ainsi, 10000 mm donne 0.825059225 arcsec/pixel natif.
Un rebinning 2x2 donne 1.65011845 arcsec/pixel de l'image rebinnnee.
Le zoom d'affichage ne change pas l'echelle.

Une focale positive modifie l'image courante et l'echelle par defaut des
prochaines acquisitions. Les autres images deja chargees ne sont pas
recalibrees. Les fichiers importes peuvent utiliser leur propre calibration.
Le champ focal ne constitue donc pas une mesure de la focale d'un fichier
importe ; l'echelle affichee reste celle de l'image courante.

Le reglage dure pour la session seulement. Au demarrage, 0 signifie qu'aucune
focale n'a ete saisie : l'echelle existante reste utilisee. Saisir 0 ensuite
ne remet pas la calibration a zero. Renseigner la focale avant les mesures
angulaires ; aucune focale nominale n'est presumee.

Activer **Graph axis in arcsec** pour afficher les coordonnees angulaires.
Changer la focale lorsque les axes sont en arcsec reinitialise leurs limites
pour ne pas conserver un cadrage calibre avec l'ancienne focale.

Cette modification concerne l'affichage et les mesures de Spydr.
Elle n'ajoute pas de calibration WCS aux fichiers FITS enregistres.

## Validation

`python3 tools/tests/check_focal_length.py` sous Linux/WSL avec Yorick verifie
la conversion, la saisie apres initialisation, l'absence d'image au demarrage,
le rebinning, les valeurs invalides et le defaut pour les nouvelles images.
Les tests locaux ne remplacent pas une validation PyGTK2 et NICMOS sur le PC cible.
