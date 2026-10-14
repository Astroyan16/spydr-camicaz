# Acces local a GitLab OBSPM avec glab

Le CLI officiel GitLab `glab` est installe sur le poste Windows.
Le depot local possede un remote `gitlab` pointant vers
`https://gitlab.obspm.fr/ybenazza/spydr-camicaz.git`.

GitHub reste le depot principal pour les commits et branches. Publier le code
avec `git push origin ...` ; GitHub Actions alimente ensuite le miroir GitLab.
Utiliser glab pour le suivi GitLab (issues, merge requests et pipelines).

## Commandes

```powershell
glab auth status --hostname gitlab.obspm.fr
glab repo view https://gitlab.obspm.fr/ybenazza/spydr-camicaz
glab issue list -R https://gitlab.obspm.fr/ybenazza/spydr-camicaz
glab mr list -R https://gitlab.obspm.fr/ybenazza/spydr-camicaz
glab ci list -R https://gitlab.obspm.fr/ybenazza/spydr-camicaz
```

Si un terminal deja ouvert ne trouve pas `glab`, ouvrir un nouveau terminal.
Le binaire Windows est installe dans `%LOCALAPPDATA%/Programs/glab/glab.exe`.

L'authentification locale est independante du secret GitHub de synchronisation.
Stocker les identifiants dans le gestionnaire Windows ; ne pas utiliser
`--insecure-storage` ni enregistrer un jeton dans les sources.
