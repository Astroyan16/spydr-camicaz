# Synchronisation GitHub vers GitLab OBSPM

- Source : https://github.com/Astroyan16/spydr-camicaz
- Destination : https://gitlab.obspm.fr/ybenazza/spydr-camicaz
- Workflow : `.github/workflows/sync-gitlab.yml`

Synchronisation active et verifiee le 15 octobre 2026.
Le jeton de projet `github-mirror` dispose uniquement du scope
`write_repository` et expire le 14 novembre 2026. Renouveler ce jeton et
mettre a jour le secret GitHub `GITLAB_MIRROR_TOKEN` avant cette date.

Le workflow copie les branches et les tags apres un push GitHub, lors d'une
suppression de reference, sur demande et toutes les heures (minute 17 UTC).
Les executions planifiees dependent de la disponibilite de GitHub Actions.
Il recupere l'etat courant de GitHub pour eviter de republier un ancien commit.

GitHub est la source de reference : les modifications faites directement dans
GitLab peuvent etre ecrasees. Les branches et tags supprimes sur GitHub sont
supprimes dans le miroir. Issues, merge requests et parametres ne sont pas copies.

## Activation

1. Dans le projet GitLab, ouvrir Settings > Access tokens et creer un jeton de
   projet nomme `github-mirror`, avec le role Maintainer et uniquement le scope
   `write_repository`. Ce role permet le push initial sur la branche principale.
   Choisir une date d'expiration et prevoir son renouvellement.
2. Dans GitHub, ouvrir Settings > Secrets and variables > Actions et ajouter
   le secret de depot `GITLAB_MIRROR_TOKEN` avec ce jeton.
3. Dans GitHub, ouvrir Actions > Sync GitLab OBSPM > Run workflow.
4. Verifier que l'execution est verte et que les commits et references de GitLab
   correspondent a GitHub. Ensuite, les pushes declenchent la synchronisation.

Ne jamais ajouter le jeton dans les sources ou dans une URL Git.
Le workflow utilise HTTPS avec verification des certificats.
Si des protections de branches ou de tags refusent les mises a jour, le workflow
echoue sans contourner ces protections ; ajuster les droits du miroir dans GitLab.

## Desactivation

Desactiver le workflow dans GitHub Actions, puis revoquer le jeton GitLab.
Le secret GitHub doit etre remplace avant l'expiration du jeton.
