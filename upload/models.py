# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

def user_directory_path(instance, filename):
	'''Module permettant l'enregistrement des fichiers dans suiviupload '''
	# faire en sorte de ramener l'enregistrement MEDIA_ROOT/<centre>/
	id_centre = RefInfocentre.objects.get(user__exact=instance.user.id)
	return '{0}/{1}/{2}/{3}'.format(instance.etude.etude.nom, id_centre, instance.id_patient, filename)

def doc_directory_path(instance, filename):
	'''Modèle gérant l'enregistrement des documents '''
	# faire en sorte de ramener l'enregistrement MEDIA_ROOT/<centre>/
	return '{0}/{1}'.format('document',filename)


class SuiviUpload(models.Model):
	'''Modèle gérant le chargement de fichier'''
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	etude = models.ForeignKey("JonctionUtilisateurEtude", on_delete=models.CASCADE)
	id_patient = models.CharField(max_length=5000)
	date_upload = models.DateTimeField("Date d'envois")
	date_examen = models.DateTimeField("Date examen")
	dossier = models.ForeignKey("DossierUpload", on_delete=models.CASCADE, blank=True, null=True)
	fichiers = models.FileField(upload_to=user_directory_path, null=True)


class JonctionUtilisateurEtude(models.Model):
	'''Modèle gérant le lien entre utilisateurs et études'''
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	etude = models.ForeignKey('RefEtudes', on_delete=models.CASCADE)
	date_autorisation = models.DateTimeField("Date d'autorisation")

class RefControleQualite(models.Model):
	'''modèle de reference pour le controle qualité'''
	nom = models.CharField(max_length=5000)

	def __str__(self):
		return self.nom

class RefEtudes(models.Model):
	'''Modèle gérant les études'''
	nom = models.CharField(max_length=5000)
	date_ouverture = models.DateTimeField("Date d'ouverture")

	def __str__(self):
		return self.nom

class RefInfocentre(models.Model):
	'''Modèle gérant les centres'''
	nom = models.CharField(max_length=5000)
	numero = models.IntegerField(blank=True)
	date_ajout = models.DateTimeField("Date d'ajout")
	user = models.ManyToManyField(User)

	def __str__(self):
		return self.nom

class RefEtapeEtude(models.Model):
	'''Modèle liant les étapes et les études'''
	nom = models.CharField(max_length=5000)
	etude = models.ForeignKey("RefEtudes", on_delete=models.CASCADE)

	def __str__(self):
		return self.nom

class RefEtatEtape(models.Model):
	'''Modèle gérant les différents états'''
	nom = models.CharField(max_length=5000)

	def __str__(self):
		return self.nom

class JonctionEtapeSuivi(models.Model):
	'''Modèle gérant les liens entre les étapes et le suivi'''
	upload = models.ForeignKey("DossierUpload", on_delete=models.CASCADE, blank=True)
	etape = models.ForeignKey("RefEtapeEtude", on_delete=models.CASCADE)
	etat = models.ForeignKey("RefEtatEtape", on_delete=models.CASCADE, blank=True, null=True)
	date = models.DateTimeField("Date de l'étape", blank=True, null=True)

class DossierUpload(models.Model):
	'''Modèle gérant les dossiers en lien avec le suiviupload'''
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	controle_qualite = models.ForeignKey("RefControleQualite", on_delete=models.CASCADE, null=True)
	date = models.DateTimeField("Date de création")

class SuiviDocument(models.Model):
	'''Modèle gerant le suivi de document'''
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	etude = models.ForeignKey('RefEtudes', on_delete=models.CASCADE)
	titre = models.CharField(max_length=5000)
	description = models.CharField(max_length=5000)
	date = models.DateTimeField("Date")
	fichiers = models.FileField(upload_to=doc_directory_path, null=True)
	background = models.CharField(max_length=5000, null=True, blank=True)

class log(models.Model):
	'''Modèle gérant le log'''
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	action = models.ForeignKey('RefTypeAction', on_delete=models.CASCADE)
	date = models.DateTimeField("Date")
	info = models.CharField(max_length=5000, null=True, blank=True)

class RefTypeAction(models.Model):
	'''Modèle gérant les actions du log'''
	nom = models.CharField(max_length=5000)

class Contact(models.Model):
	'''Modèle gérant les contacts'''
	nom = models.CharField(max_length=3000)
	prenom = models.CharField(max_length=3000)
	courriel = models.CharField(max_length=3000)
	telephone = models.CharField(blank=True, null=True, max_length=12)
	poste = models.CharField(max_length=3000)
