# Versions archivees sur GitHub

Les livraisons principales conservees dans `dist/` ont ete archivees sur GitHub
le **22 octobre 2026**. La release 0.9.8b a ete ajoutee le **27 octobre 2026**.
Chaque version dispose d'un tag, d'une release, d'une
archive ZIP et d'une empreinte SHA-256.

[Voir toutes les releases](https://github.com/Astroyan16/spydr-camicaz/releases).

| Version | Sources | Livraison | Contenu principal |
| --- | --- | --- | --- |
| 0.8.3 | [Tag v0.8.3](https://github.com/Astroyan16/spydr-camicaz/tree/v0.8.3) | [Release](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.8.3) | Etat historique de TP_Master_version au premier import Git. |
| 0.9.0 | [Tag v0.9.0](https://github.com/Astroyan16/spydr-camicaz/tree/v0.9.0) | [Release](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.0) | Premiere identification commune de la version de maintenance. |
| 0.9.1 | [Tag v0.9.1](https://github.com/Astroyan16/spydr-camicaz/tree/v0.9.1) | [Release](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.1) | Correction du cadrage au retour du Record vers le freerun. |
| 0.9.2 | [Tag v0.9.2](https://github.com/Astroyan16/spydr-camicaz/tree/v0.9.2) | [Release](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.2) | Activation du chopping pendant le freerun. |
| 0.9.3 | [Tag v0.9.3](https://github.com/Astroyan16/spydr-camicaz/tree/v0.9.3) | [Release](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.3) | Correction du dossier de destination du Record. |
| 0.9.4 | [Tag v0.9.4](https://github.com/Astroyan16/spydr-camicaz/tree/v0.9.4) | [Release](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.4) | Motifs Record ABAB, ABBA, 2A2B, 5A5B et 10A10B. |
| 0.9.5 | [Tag v0.9.5](https://github.com/Astroyan16/spydr-camicaz/tree/v0.9.5) | [Release](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.5) | Ajout du motif ABBABAABBAABABBA. |
| 0.9.6 | [Tag v0.9.6](https://github.com/Astroyan16/spydr-camicaz/tree/v0.9.6) | [Release](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.6) | Sauvegardes sans ecrasement, erreurs et acquisitions partielles. |
| 0.9.7 | [Tag v0.9.7](https://github.com/Astroyan16/spydr-camicaz/tree/v0.9.7) | [Release](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.7) | Correction de reconstruction des quadrants. |
| 0.9.8b | [Tag v0.9.8b](https://github.com/Astroyan16/spydr-camicaz/tree/v0.9.8b) | [Release](https://github.com/Astroyan16/spydr-camicaz/releases/tag/v0.9.8b) | Release du 27 octobre 2026 : FITS METAVER=2, horloges natives, Record corrige, UTC et confirmation de sauvegarde. |

## Provenance

La version historique 0.8.3 correspond a `PC TP IR/TP_Master_version` dans le
premier commit Git `2d2c0ad`. `spydr.i` declare 0.8.3 ; certains fichiers
historiques d'empaquetage indiquent encore 0.8.2. Les sources sont conservees
sans changer ces declarations. Ce premier import comprend deja des modifications
locales : il ne certifie pas l'identite avec l'installation instrumentale d'origine.

Les tags 0.9.x sont des instantanes retrospectifs des livraisons conservees,
pas une reconstitution des dates de developpement. Leurs commits sont regroupes
sur la branche [codex/version-history](https://github.com/Astroyan16/spydr-camicaz/tree/codex/version-history).
Le code actif de `main` conserve son historique existant.

Pour chaque tag 0.9.x, `docs/releases/vVERSION/manifest.json` indique le dossier
d'origine, les chemins dans la livraison et dans Git, et les empreintes SHA-256
des fichiers. Les sources de `libcamicaz` et `yCamicaz` sont situees sous
`PC TP IR/TP_Master_version/` ; les scripts de lancement et de reconstruction
sont sous `tools/spydr-system-yorick/`.

Les essais initiaux 0.9.8 et 0.9.8b ont ete retires le 22 octobre 2026 apres
signalement d'un blocage Record. Le protocole du Yorick historique a depuis
ete corrige et l'acquisition a ete retestee sur l'instrument. La **0.9.8b corrigee**
est publiee comme release le **27 octobre 2026**, depuis `main` ; le tag
`v0.9.8b` pointe exclusivement sur cet etat corrige. La 0.9.8 reste locale.
Voir [validation et installation](RELEASE_0.9.8b.md).

Les essais intermediaires non numerotes (focale, disposition, redimensionnement)
et les correctifs seuls n'ont pas de release distincte. Les versions publiees
representent les jalons principaux ; les corrections presentes dans chaque
instantane sont conservees, sans pretendre reconstituer un etat anterieur perdu.

## Utilisation

Telecharger le ZIP joint a la release, plutot que les archives automatiques
"Source code" de GitHub, pour obtenir le dossier de livraison avec ses lanceurs.
Les ZIP 0.9.x ne contiennent ni metadonnees SVN ni binaires compiles.
L'archive 0.8.3 est une archive historique des sources, pas un bundle moderne.

Pour une version 0.9.x, extraire dans un nouveau dossier Linux sans espaces :

```sh
sh rebuild_with_existing_yorick.sh
sh run_spydr_test.sh
```

Les archives 0.9.0 a 0.9.7 sont des preversions historiques. La 0.9.8b
est une release avec les essais instrumentaux decrits dans ses notes. Les dependances instrumentales
doivent deja etre disponibles ; l'installation stable et le Yorick existant
ne doivent pas etre remplaces.
