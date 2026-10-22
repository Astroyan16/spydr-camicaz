# Spydr test bundle using the existing Yorick installation

Ce bundle est destine au test sur la machine Linux d'origine sans modifier le Yorick deja present, ni l'installation stable de Spydr / Camicaz.

## Ce que cette variante garantit

- elle ne copie pas `yorick/relocate`
- elle n'installe rien dans le Yorick existant
- elle ne remplace aucun fichier de la version stable
- elle reconstruit `libcamicaz.so` et `yCamicaz.so` uniquement dans le dossier de test copie

## Contenu du bundle

- `libcamicaz/`
- `yCamicaz/`
- `run_spydr_test.sh`
- `rebuild_with_existing_yorick.sh`

## Utilisation sur la machine Linux d'origine

```sh
chmod +x ./*.sh
./rebuild_with_existing_yorick.sh
./run_spydr_test.sh
```

## Detection de Yorick

Le script essaie dans cet ordre:

1. `SPYDR_TEST_YORICK_BIN`
2. `which yorick`
3. `/home/etudiants/yorick.git/relocate/bin/yorick`

Si besoin, tu peux imposer explicitement le binaire:

```sh
SPYDR_TEST_YORICK_BIN=/chemin/vers/yorick ./rebuild_with_existing_yorick.sh
SPYDR_TEST_YORICK_BIN=/chemin/vers/yorick ./run_spydr_test.sh
```

Tu peux aussi imposer la racine Yorick si l'autodetection du `relocate` n'est pas correcte:

```sh
SPYDR_TEST_YORICK_ROOT=/chemin/vers/yorick/relocate ./rebuild_with_existing_yorick.sh
```

## Isolation du test

Le lancement force:

- `CAMTOP` vers la copie de test de `yCamicaz`
- `STYCTOP` vers la copie de test de `yCamicaz`
- `Y_PYTHON` et `Y_GLADE` vers la copie de test de `spydr`
- `LD_LIBRARY_PATH` vers la copie de test de `libcamicaz`

Autrement dit, on reutilise uniquement le binaire `yorick` existant. Les ressources Spydr / Camicaz chargees viennent du dossier de test copie.
