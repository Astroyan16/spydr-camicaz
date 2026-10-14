# Acces local a GitLab OBSPM avec glab

Le CLI officiel GitLab `glab` est installe sur le poste Windows.
Le depot local possede un remote `gitlab` pointant vers
`https://gitlab.obspm.fr/ybenazza/spydr-camicaz.git`.

Connexion verifiee depuis les outils Codex le 15 octobre 2026 : acces au projet,
aux issues, aux merge requests et aux pipelines. Le jeton de projet dedie
`codex-glab-spydr-2027` utilise le scope `api`, le role Maintainer et expire
le 14 octobre 2027. Ses actions sont attribuees au compte bot du projet.

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

## Connexion visible dans le terminal mais pas dans les outils Codex

Le jeton peut etre present dans le gestionnaire Windows alors que la
configuration du contexte d'execution n'active pas sa lecture. Verifier :

```powershell
glab config path
glab config get use_keyring --host gitlab.obspm.fr
glab config set use_keyring true --host gitlab.obspm.fr
glab auth status --hostname gitlab.obspm.fr
```

La correction validee consistait a activer `use_keyring` pour cet hote et a
configurer `api_host=gitlab.obspm.fr`, `api_protocol=https` et
`git_protocol=https`. Elle reutilise le jeton existant sans le lire en clair.
Ne pas recreer de jeton avant d'avoir verifie ces parametres.
