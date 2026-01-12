import io
from flask import session
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError


def get_drive_service():
    if "credentials" not in session:
        raise RuntimeError("Sessão expirada ou usuário não autenticado")

    creds = Credentials(**session["credentials"])
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def criar_pasta(nome):
    service = get_drive_service()
    try:
        pasta = service.files().create(
            body={
                "name": nome,
                "mimeType": "application/vnd.google-apps.folder"
            },
            fields="id"
        ).execute()
        return pasta["id"]
    except HttpError as e:
        raise RuntimeError(f"Erro ao criar pasta: {e}")


def listar_processos():
    service = get_drive_service()
    try:
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.folder' and trashed=false",
            fields="files(id,name)",
            orderBy="createdTime desc"
        ).execute()
        return results.get("files", [])
    except HttpError as e:
        raise RuntimeError(f"Erro ao listar processos: {e}")


def listar_arquivos(pasta_id):
    service = get_drive_service()
    try:
        results = service.files().list(
            q=f"'{pasta_id}' in parents and trashed=false",
            fields="files(id,name)"
        ).execute()
        return results.get("files", [])
    except HttpError as e:
        raise RuntimeError(f"Erro ao listar arquivos: {e}")


def upload_arquivo(pasta_id, file):
    service = get_drive_service()
    media = MediaIoBaseUpload(
        io.BytesIO(file.read()),
        mimetype=file.content_type,
        resumable=True
    )
    try:
        service.files().create(
            body={
                "name": file.filename,
                "parents": [pasta_id]
            },
            media_body=media
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"Erro ao enviar arquivo '{file.filename}': {e}")


def excluir_arquivo(file_id):
    service = get_drive_service()
    try:
        service.files().delete(fileId=file_id).execute()
    except HttpError as e:
        raise RuntimeError(f"Erro ao excluir arquivo: {e}")


def obter_nome_pasta(pasta_id):
    service = get_drive_service()
    try:
        file = service.files().get(
            fileId=pasta_id,
            fields="name"
        ).execute()
        return file["name"]
    except HttpError as e:
        raise RuntimeError(f"Erro ao obter nome da pasta: {e}")


def renomear_pasta(pasta_id, novo_nome):
    service = get_drive_service()
    try:
        service.files().update(
            fileId=pasta_id,
            body={"name": novo_nome}
        ).execute()
    except HttpError as e:
        raise RuntimeError(f"Erro ao renomear pasta: {e}")
