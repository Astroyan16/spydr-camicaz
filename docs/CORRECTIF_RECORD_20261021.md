# Correctif Record du 21 octobre 2026

## Probleme reproduit

Les livraisons initiales 0.9.8 et 0.9.8b contiennent une boucle de lecture de
camicaz.ini dont le test de fin de fichier est incorrect. rdline renvoie une
chaine nulle en fin de fichier, pas la valeur vide [] de Yorick. La boucle ne
se termine pas et accumule des entrees apres la fin du fichier. Elle intervient
avant la premiere acquisition : Record reste grise, la progression ne commence
pas et les commandes de l'interface ne sont plus traitees normalement.

Le correctif utilise rdfile, la fonction standard de lecture complete qui gere
correctement la fin de fichier. Les tests precedents ne couvraient pas cette
branche avec un fichier de configuration reel.

Le blocage est reproduit et corrige localement. Le signal SIGSEGV observe sur
le PC instrument apres fermeture reste a recontroler lors du prochain essai ;
la photo seule ne fournit pas de trace permettant de localiser ce crash.

## Mise a jour sans recompilation

Fermer la copie de test. Utiliser le fichier correspondant exactement a sa version :

| Copie de test | Fichier fourni dans le correctif |
| --- | --- |
| 0.9.8 | 0.9.8/spydr_metadata.i |
| 0.9.8b | 0.9.8b/spydr_metadata.i |

Remplacer uniquement `yCamicaz/yorick/spydr/spydr_metadata.i` dans le dossier
de test correspondant, puis relancer depuis ce dossier :

```sh
sh run_spydr_test.sh
```

Aucun chmod ni recompilation n'est necessaire pour ce correctif interprete.
Ne pas intervertir les deux variantes : leurs fonctions d'horodatage et schemas
FRAMELOG different. L'installation stable de l'instrument reste inchangee.

Les dossiers complets spydr_camicaz_0.9.8_fits_test et
spydr_camicaz_0.9.8b_fits_test disponibles dans dist ont aussi ete corriges.
Une copie neuve complete doit toujours etre reconstruite avant son premier
lancement ; cette obligation est distincte de la mise a jour d'une copie
deja compilee par remplacement du seul fichier interprete.

## Controle sur l'instrument

Apres Apply, lancer Record sans chopping avec deux ou trois expositions.
Verifier la progression, le retour des boutons a leur etat disponible et la
creation du FITS. Tester ensuite une interruption avec Stop et la fermeture
du logiciel. Conserver le terminal ouvert pour noter toute erreur restante.

## Regression logicielle

Le test check_config_snapshot.py reproduisait le blocage par expiration de
son delai avant correction. Il passe apres correction sur les sources et les
deux livraisons, avec un fichier reel, des lignes vides, une fin sans saut de
ligne, un fichier vide, un fichier absent et plusieurs demarrages successifs.
Les tests de sequence utilisent desormais la configuration camera sur disque.
Le test FITS independant lit aussi une configuration reelle avant sauvegarde.
Ces tests ne simulent pas les pilotes NI ni l'acquisition NICMOS physique.
