# -*- coding: utf-8 -*-

import json
import os
import zipfile
from datetime import datetime
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.clickjacking import (
    xframe_options_exempt,
)

from upload.models import (
    DossierUpload,
    JonctionEtapeSuivi,
    RefControleQualite,
    RefEtapeEtude,
    RefEtatEtape,
    RefEtudes,
    SuiviUpload,
)

from .module_log import edition_log, information_log
from .module_views import (
    dict_upload,
    etude_tris,
    gestion_etape,
    gestion_etude_tris,
    info_etape,
    nom_etape_tris,
)


@login_required(login_url="/auth/auth_in/")
def upload_tris(request, id_tris):
    """Cette page est appelé lors du tris du tableau vers une autre étude, cet
    appel ce fait via ajax."""
    tab_list = []
    dict_nbr = {}
    etude_change = RefEtudes.objects.get(id=id_tris)
    dossier_all = SuiviUpload.objects.filter(
        etude__etude=id_tris
    ).distinct("dossier")
    if dossier_all.exists():
        nbr_etape = RefEtapeEtude.objects.filter(
            etude=etude_change.id
        ).count()
        nom_etape = nom_etape_tris(etude_change)
        for files in dossier_all:
            dict_upload = {}
            dict_upload = dict_upload(dict_upload, files)
            info_etape = info_etape(files)
            var_etape = gestion_etape(
                nom_etape, info_etape, nbr_etape
            )
            dict_upload["etape_etude"] = var_etape[1]
            dict_upload["error"] = var_etape[0]
            tab_list.append(dict_upload)
        dict_nbr["nbr_etape"] = nbr_etape
        dict_nbr["nom_etape"] = nom_etape
    list_centre = etude_tris(dossier_all)
    gestion_info = gestion_etude_tris(
        etude_change, dossier_all, list_centre
    )
    nbr_entrée = len(tab_list)
    # Enregistrement du log------------------------
    # ---------------------------------------------
    nom_documentaire = (
        " a créé un tris vers l'étude : " + etude_change.nom
    )
    information_log(request, nom_documentaire)
    # ---------------------------------------------
    # ---------------------------------------------
    return render(
        request,
        "admin_page_upload.html",
        {
            "resultat": tab_list,
            "dict_nbr": dict_nbr,
            "str_etude": gestion_info[1],
            "str_centre": gestion_info[0],
            "taille": nbr_entrée,
        },
    )


@xframe_options_exempt
@login_required(login_url="/auth/auth_in/")
def upload_mod(request):
    """Appel ajax lors du double clic sur une case du tableau.

    Ce module renvois la liste des états d'une étape et l'intégre dans
    la cellule ou l'utilisateur à cliqué
    """
    tab_list = {}
    val_etat = RefEtatEtape.objects.all()
    x = 0
    for etat in val_etat:
        var_str = "etat_" + str(x)
        tab_list[var_str] = {
            "id": etat.id,
            "nom": etat.nom,
            "var": var_str,
        }
        x += 1
    creation_json = json.dumps(tab_list)
    return HttpResponse(
        json.dumps(creation_json),
        content_type="application/json",
    )


@xframe_options_exempt
@login_required(login_url="/auth/auth_in/")
def upload_mod_qc(request):
    """Appel ajax lors du double clic sur une case du tableau.

    Ce module renvois la liste des états du controle qualité et
    l'intégre dans la cellule ou l'utilisateur à cliqué
    """
    tab_list = {}
    val_etat = RefControleQualite.objects.all()
    x = 0
    for etat in val_etat:
        var_str = "etat_" + str(x)
        tab_list[var_str] = {"id": etat.id, "nom": etat.nom}
        x += 1
    creation_json = json.dumps(tab_list)
    return HttpResponse(
        json.dumps(creation_json),
        content_type="application/json",
    )


@xframe_options_exempt
@login_required(login_url="/auth/auth_in/")
def upload_maj(request):
    """Appel ajax lors du changement d'état d'une étape.

    Ce module modifie l'état dans la base de donnée puis renvois vers la
    page pour afficher la modification
    """
    val_jonction = request.GET.get("jonction")
    val_etat = request.GET.get("etat_id")
    val_etude = request.GET.get("etude_id")
    id_log = JonctionEtapeSuivi.objects.get(
        id__exact=val_jonction
    )
    if val_etat == str(4):
        date_now = datetime.today()
        JonctionEtapeSuivi.objects.filter(
            id__exact=val_jonction
        ).update(etat=val_etat)
        JonctionEtapeSuivi.objects.filter(
            id__exact=val_jonction
        ).update(date=date_now)
    else:
        JonctionEtapeSuivi.objects.filter(
            id__exact=val_jonction
        ).update(etat=val_etat)
    var_url = "/admin_page/upfiles/tris/" + str(val_etude) + "/"
    # Enregistrement du log---------------------
    # ------------------------------------------
    nom_documentaire = (
        " a modifié l'état de l'étude : "
        + id_log.etape.etude.nom
        + " la nouvelle étape est : "
        + id_log.etat.nom
    )
    edition_log(request, nom_documentaire)
    # ------------------------------------------
    # ------------------------------------------
    return redirect(var_url)


@xframe_options_exempt
@login_required(login_url="/auth/auth_in/")
def upload_maj_qc(request):
    """Appel ajax lors du changement d'état d'un controle qualité.

    Ce module modifie l'état dans la base de donnée puis renvois vers la
    page pour afficher la modification
    """
    val_jonction = request.GET.get("jonction")
    val_etat = request.GET.get("etat_id")
    val_etude = request.GET.get("etude_id")
    id_log = SuiviUpload.objects.filter(
        dossier__id__exact=val_jonction
    )[:1]
    qc = RefControleQualite.objects.get(id__exact=val_etat)
    DossierUpload.objects.filter(id__exact=val_jonction).update(
        controle_qualite=qc
    )
    var_url = "/admin_page/upfiles/tris/" + str(val_etude) + "/"
    # Enregistrement du log-----------------
    # --------------------------------------
    nom_documentaire = (
        " a modifié l'état du controle qualité pour : "
        + id_log[0].id_patient
        + " la nouvelle étape est : "
        + qc.nom
    )
    edition_log(request, nom_documentaire)
    # --------------------------------------
    # --------------------------------------
    return redirect(var_url)


@xframe_options_exempt
@login_required(login_url="/auth/auth_in/")
def walk_up(request):
    """Permet de naviguer dans les dossier chargé dans l'application."""
    val_url = request.GET.get("url")
    path = os.path.dirname(val_url)
    list_tr = [{"url": path}]
    list_dir = os.listdir(val_url)
    for item in list_dir:
        lien_id = os.path.join(val_url, item)
        dict_list = {}
        if os.path.isdir(lien_id):
            for root, dirs, files in os.walk(
                lien_id, topdown=False
            ):
                x = 0
                y = 0
                for name in files:
                    x += 1
                for name in dirs:
                    y += 1
            dict_list = {
                "nom": item,
                "url": lien_id,
                "dir": True,
                "file": x,
                "direct": y,
            }
        else:
            dict_list = {
                "nom": item,
                "url": lien_id,
                "dir": False,
            }
        list_tr.append(dict_list)
    creation_json = json.dumps(list_tr)
    return HttpResponse(
        json.dumps(creation_json),
        content_type="application/json",
    )


@login_required(login_url="/auth/auth_in/")
def walk_down(request):
    """Permet de revenir à un dossier parent.

    L'utilisateur ne peux pas remonter plus loin que le dossier patient
    """
    list_tr = []
    val_url = request.GET.get("url")
    val_compare = request.GET.get("val_compare")
    if val_compare in val_url:
        path = os.path.dirname(val_url)
        if val_compare in path:
            list_tr = [{"url": path}]
            path_join = path
        else:
            list_tr = [{"url": val_url}]
            path_join = val_url
        list_dir = os.listdir(path_join)
        for item in list_dir:
            lien_id = os.path.join(path_join, item)
            dict_list = {}
            if os.path.isdir(lien_id):
                for root, dirs, files in os.walk(
                    lien_id, topdown=False
                ):
                    x = 0
                    y = 0
                    for name in files:
                        x += 1
                    for name in dirs:
                        y += 1
                dict_list = {
                    "nom": item,
                    "url": lien_id,
                    "dir": True,
                    "file": x,
                    "direct": y,
                }
            else:
                dict_list = {
                    "nom": item,
                    "url": lien_id,
                    "dir": False,
                }
            list_tr.append(dict_list)
        creation_json = json.dumps(list_tr)
        return HttpResponse(
            json.dumps(creation_json),
            content_type="application/json",
        )
    else:
        return HttpResponse()


@login_required(login_url="/auth/auth_in/")
def down_once(request, id):
    """Ce module est appelé lors du téléchargement d'un fichier chargé pour le
    patient donnée."""
    if os.path.exists(id):
        # Enregistrement du log-----------------------------
        # --------------------------------------------------
        nom_documentaire = " a téléchargé le document : " + id
        information_log(request, nom_documentaire)
        # --------------------------------------------------
        # --------------------------------------------------
        with open(id, "rb") as fh:
            response = HttpResponse(
                fh.read(),
                content_type="application/vnd.ms-excel",
            )
            response[
                "Content-Disposition"
            ] = "inline; filename=" + os.path.basename(id)
            return response


@login_required(login_url="/auth/auth_in/")
def down_all(request, id):
    """Ce module est appelé lorsque l'utilisateur souhaite téléchargé la
    totalité des fichiers chargé dans le dossier Ce téléchargement utilise
    zipfile en mémoir temporaire."""
    obj = SuiviUpload.objects.get(id=id)
    path = os.path.dirname(obj.fichiers.path)
    list_dir = os.listdir(path)
    in_memory = BytesIO()
    zip = zipfile.ZipFile(in_memory, "a")
    for item in list_dir:
        file_path = os.path.join(path, item)
        with open(file_path, "rb") as img:
            img_read = img.read()
        zip.writestr(item, img_read)
    zip.close()
    response = HttpResponse(content_type="application/zip")
    response[
        "Content-Disposition"
    ] = "attachement;filename=corelab.zip"
    in_memory.seek(0)
    response.write(in_memory.read())
    # Enregistrement du log------------------------------
    # ---------------------------------------------------
    nom_documentaire = (
        " a téléchargé tous les documents du patient : "
        + obj.id_patient
    )
    information_log(request, nom_documentaire)
    # ---------------------------------------------------
    # ---------------------------------------------------
    return response
