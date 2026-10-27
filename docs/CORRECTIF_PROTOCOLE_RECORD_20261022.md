# Blocage Record : protocole du Yorick historique

Correctif Record Python/Yorick historique - 22 octobre 2026

Cause reproduite : le mini-parseur funcdef du Yorick 2.2.02x n'accepte
pas les virgules ni les arguments nommes observer=..., metadata=..., etc.
Il renvoie [] sans appeler record_image. Les versions 0.9.8 et 0.9.8b
avaient ajoute cette syntaxe au message envoye par Python.
Le controle des parametres reussissait, puis Record restait grise.

Le correctif utilise cam_record_request et des arguments positionnels.
L'adaptateur Yorick transmet ensuite les parametres nommes a record_image
par le parseur normal. Les champs texte sont prefixes sur le fil puis
restaures pour eviter aussi le defaut des chaines vides du vieux funcdef.
Les metadonnees FITS et les deux fonctions d'horodatage sont conservees.
Les traces de diagnostic sont conservees pour le prochain essai.

INSTALLATION : fermer Spydr. Dans une COPIE DE TEST de la meme version,
prendre les TROIS fichiers du sous-dossier 0.9.8 ou 0.9.8b de ce ZIP :
  spydr.py
  spydr_widgetcam.i
  spydr_metadata.i
Les copier dans yCamicaz/yorick/spydr/. Conserver les originaux a part.
Utiliser de preference la copie de diagnostic deja compilee et testee.
Ne pas intervertir les variantes. Ne pas modifier la 0.9.7 fonctionnelle.
Aucune recompilation pour cette mise a jour interpretee ; une nouvelle
copie complete 0.9.8b exige toujours son module natif compile auparavant.

Relancer depuis la racine de cette copie :
  sh run_spydr_test.sh 2>&1 | tee diagnostic_record.log
Faire Apply, puis un Record de 2 poses sans chopping.
Le journal frontend doit maintenant montrer TX cam_record_request,
et le terminal doit afficher R01 Record entered puis les etapes suivantes.
Verifier la progression, la creation du FITS et la reactivation des boutons.
Conserver diagnostic_record.log et
  yCamicaz/yorick/spydr/record_frontend_diagnostic.log

Validation locale : echec original reproduit avec le vrai code C historique
funcdef.c compile dans un plugin isole. Le callback de communication reel
execute 32 commandes corrigees, y compris fragmentees et regroupees, avec
metadonnees longues, champs vides et guillemets/antislashs. Les parametres,
les metadonnees et le drapeau Apply sont verifies. Les tests des callbacks
Python passent egalement. L'acquisition NICMOS reste a valider sur place.
Ces essais 0.9.8/0.9.8b ne sont pas republies comme releases GitHub.
