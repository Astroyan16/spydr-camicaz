# Dates UTC FITS

Correctif leger des dates UTC FITS - 22 octobre 2026

Ce correctif remplace uniquement la conversion des dates en texte.
Le calcul UTC est effectue dans Yorick, sans lancer la commande Linux date,
sans tube de lecture et sans nouvelle bibliotheque. Il s'execute seulement
a la sauvegarde des trois champs DATE-OBS, DATE-END et DATE.
Aucun travail supplementaire n'est ajoute entre les poses.
Les horloges, MJD-OBS, MJD-END et FRAMELOG sont conserves.

0.9.8 : YYYY-MM-DDTHH:MM:SSZ (resolution une seconde).
0.9.8b : YYYY-MM-DDTHH:MM:SS.ffffffZ (conversion a la microseconde).
Les secondes/nanosecondes natives restent conservees dans FRAMELOG en 0.9.8b.
Les trois zeros de remplissage de l'essai initial sont supprimes ; les six
decimales utiles des dates texte sont conservees.
Z signifie UTC. Ce correctif ne change pas l'heure systeme du PC.

INSTALLATION
A appliquer a la copie de test 0.9.8 ou 0.9.8b ou le correctif de protocole
Record a deja permis les acquisitions. Fermer Spydr.
Prendre spydr_metadata.i dans le sous-dossier correspondant a sa version,
puis remplacer uniquement :
  yCamicaz/yorick/spydr/spydr_metadata.i
Garder l'ancien fichier a part. Ne pas melanger les variantes.
Aucune recompilation. La 0.9.7 fonctionnelle reste intacte.
Relancer avec :
  sh run_spydr_test.sh
Faire un Record de deux poses sans chopping et verifier les trois champs
dans le NOUVEAU FITS. Les anciens FITS ne sont pas modifies.

VERIFICATIONS LOCALES
472 dates verifiees par version : annees bissextiles, minuit, arrondis,
epoques anterieures a 1970 et limite 2038. Calcul independant du fuseau.
FITS reels relus avec Astropy : les champs dates sont renseignes.
Le test FITS complet 0.9.8b passe aussi avec la bibliotheque fits.i historique.
Mesure indicative sur WSL : environ 5 microsecondes par conversion,
soit 15 microsecondes pour trois dates. Le PC instrument peut etre plus lent.
La validation finale de ce correctif sur le PC instrument reste a faire.
