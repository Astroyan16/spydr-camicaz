# Spydr / Camicaz

- Sources actives : `PC TP IR/TP_Master_version` ; scripts de livraison : `tools`.
- GitHub `origin` est la source de reference. GitLab OBSPM est un miroir
  automatique des branches et tags. Publier les commits vers `origin`.
- Pour consulter les issues, merge requests et pipelines GitLab, utiliser
  `glab` avec `-R https://gitlab.obspm.fr/ybenazza/spydr-camicaz`.
  Voir `docs/GLAB.md` pour les commandes locales.
- Ne pas utiliser le secret du miroir pour les operations API ; glab utilise
  son propre acces local. Ne jamais afficher ni versionner les jetons.
- Preserver l'installation stable sur la machine de l'instrument. Compiler et
  tester dans un dossier isole ; ne pas modifier le Yorick existant.
- Les tests logiciels ne remplacent pas une validation avec la camera NICMOS.
