# Spydr portable test bundle

Ce dossier est pense pour tester une version modifiee de Spydr sur la machine Linux d'origine sans toucher a l'installation consideree comme stable.

## Principe

- le bundle utilise ses propres copies de `yCamicaz`, `libcamicaz` et `yorick/relocate`
- le lancement passe par des variables d'environnement locales au bundle
- rien n'est ecrit dans `/usr/local/bin` et rien n'ecrase la version stable

## Important

Les correctifs recents DAQmx sont dans le code C++.
Comme ce bundle est prepare depuis un poste Windows, les binaires Linux ne sont pas reconstruits ici.

Avant le premier test sur la machine Linux d'origine, il faut donc lancer:

```sh
chmod +x ./*.sh
./rebuild_portable.sh
```

Ensuite, le lancement se fait avec:

```sh
./run_spydr_portable.sh
```

## Arborescence attendue

- `libcamicaz/`
- `yCamicaz/`
- `yorick/relocate/`
- `run_spydr_portable.sh`
- `rebuild_portable.sh`

## Ce que le lanceur fait

- fixe `CAMTOP` et `STYCTOP` vers la copie locale de `yCamicaz`
- fixe `Y_PYTHON` et `Y_GLADE` vers la copie locale de `spydr`
- ajoute `libcamicaz/` au `LD_LIBRARY_PATH`
- lance `yorick` depuis la copie portable

## Strategie de test recommandee

1. Copier tout le dossier sur la machine Linux de test.
2. Lancer `./rebuild_portable.sh`.
3. Demarrer `./run_spydr_portable.sh`.
4. Verifier que la version stable installee d'origine fonctionne toujours en parallele.
5. Comparer les comportements:
   - demarrage sans signal NI
   - freerun puis record
   - acquisition simple
   - monitoring
