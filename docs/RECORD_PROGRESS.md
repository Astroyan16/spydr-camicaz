# Etat final de Record

Fin d'enregistrement explicite - Spydr 0.9.8 et 0.9.8b - 22 octobre 2026

Affichage de la barre de progression :
- Preparing record... : debut du Record ; remise a zero de la couleur.
- Progression habituelle pendant les poses.
- Saving FITS... : images acquises, sauvegarde en cours.
- Vert : Record successful - N/N saved, apres sauvegarde d'une serie complete.
- Orange : Record interrupted - N/M saved, apres sauvegarde d'une serie interrompue.
- Rouge : Save failed - data retained. Le cube reste en memoire et Stop
  permet de retenter apres correction du disque ou du chemin.
- Erreur sans image : Record failed - no images saved.
La fin reste visible jusqu'au prochain Record. Les Status ne l'effacent pas.

INSTALLATION
Fermer la copie de test de Spydr. Choisir le sous-dossier de SA version,
0.9.8 ou 0.9.8b, et copier les TROIS fichiers dans :
  yCamicaz/yorick/spydr/
Fichiers : spydr.py, spydr_widgetcam.i, spydr_metadata.i.
Conserver les anciens fichiers a part. Ne pas melanger les variantes.
Ce correctif cumulatif conserve le protocole Record compatible avec le
Yorick historique et inclut la conversion legere des dates UTC.
Les deux schemas FITS et les horloges propres a chaque version sont conserves.
Aucune recompilation pour une copie de la meme version deja compilee.
La version 0.9.7 et le Yorick installe ne sont pas modifies.

Relancer :
  sh run_spydr_test.sh
Faire un Record de 2 poses sans chopping : la barre doit afficher
Saving FITS..., puis rester verte avec Record successful - 2/2 saved.
Le texte de sauvegarde peut etre tres bref si le disque repond vite.
Verifier aussi le FITS et le retour des boutons, puis un autre Record
pour verifier le retour a la couleur normale.

VALIDATION LOCALE
Rendu reel GTK2 verifie sous WSL ; apercu joint au ZIP.
Tests du callback GTK, reinitialisation, serie complete, arret partiel,
echec disque et nouvelle tentative de sauvegarde. Les tests de sequence
passent pour les deux variantes (30 series et injections d'erreur).
La validation de cet affichage sur Scientific Linux 6.2 reste a effectuer.
