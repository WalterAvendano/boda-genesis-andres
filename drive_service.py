import os
import json
import io
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

UPLOAD_FOLDER = Path(__file__).parent / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "").strip()
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
SERVICE_ACCOUNT_JSON_ENV = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()

TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
TOKEN_JSON_ENV = os.getenv("GOOGLE_TOKEN_JSON", "").strip()

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

_drive_service = None

def get_drive_service():
    """Inicializa y retorna el cliente de Google Drive API."""
    global _drive_service
    if _drive_service is not None:
        return _drive_service

    try:
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        credentials = None

        # ---------------------------------------------------------
        # PRIORIDAD 1: OAuth2 (Tu cuenta personal de Google con 15GB de cuota)
        # ---------------------------------------------------------
        if TOKEN_JSON_ENV:
            try:
                from google.oauth2.credentials import Credentials
                info = json.loads(TOKEN_JSON_ENV)
                credentials = Credentials.from_authorized_user_info(info, SCOPES)
            except Exception as e:
                print(f"[Drive] Error parseando GOOGLE_TOKEN_JSON: {e}")

        if not credentials:
            token_path = Path(TOKEN_FILE)
            if not token_path.is_absolute():
                token_path = Path(__file__).parent / token_path

            if token_path.exists():
                from google.oauth2.credentials import Credentials
                credentials = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        if credentials:
            if credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except Exception as e:
                    print(f"[Drive] Error refrescando token OAuth: {e}")

            if credentials.valid:
                _drive_service = build("drive", "v3", credentials=credentials, cache_discovery=False)
                print("[Drive] Conexión establecida con éxito vía OAuth2 (Tu cuenta de Google).")
                return _drive_service

        # ---------------------------------------------------------
        # PRIORIDAD 2: Service Account
        # ---------------------------------------------------------
        from google.oauth2 import service_account

        if SERVICE_ACCOUNT_JSON_ENV:
            try:
                info = json.loads(SERVICE_ACCOUNT_JSON_ENV)
                credentials = service_account.Credentials.from_service_account_info(
                    info, scopes=SCOPES
                )
            except Exception as e:
                print(f"[Drive] Error parseando GOOGLE_SERVICE_ACCOUNT_JSON: {e}")

        if not credentials:
            file_path = Path(SERVICE_ACCOUNT_FILE)
            if not file_path.is_absolute():
                file_path = Path(__file__).parent / file_path
            
            if file_path.exists():
                credentials = service_account.Credentials.from_service_account_file(
                    str(file_path), scopes=SCOPES
                )

        if credentials:
            _drive_service = build("drive", "v3", credentials=credentials, cache_discovery=False)
            print("[Drive] Conexión establecida vía Service Account.")
            return _drive_service

    except Exception as e:
        print(f"[Drive] No se pudo inicializar Google Drive API: {e}")

    return None

def check_drive_connection():
    """Verifica si Google Drive está configurado y accesible."""
    service = get_drive_service()
    if not service:
        return {
            "connected": False,
            "mode": "demo_local",
            "message": "Sin credenciales de Google Drive. Modo demo local activo (los archivos se guardan en uploads/)."
        }

    if not DRIVE_FOLDER_ID:
        return {
            "connected": False,
            "mode": "missing_folder_id",
            "message": "Credenciales válidas, pero falta configurar DRIVE_FOLDER_ID en el archivo .env."
        }

    try:
        folder = service.files().get(
            fileId=DRIVE_FOLDER_ID,
            fields="id, name",
            supportsAllDrives=True
        ).execute()
        return {
            "connected": True,
            "mode": "google_drive",
            "folder_name": folder.get("name", "Carpeta de la boda"),
            "folder_id": folder.get("id"),
            "message": f"Conectado a Google Drive: '{folder.get('name')}'"
        }
    except Exception as e:
        return {
            "connected": False,
            "mode": "permission_error",
            "message": f"Error accediendo a la carpeta de Drive: {str(e)}."
        }

def upload_file_to_drive(file_obj, filename, mimetype, guest_name=""):
    """
    Sube un archivo a Google Drive. Si falla o no está configurado,
    lo guarda en la carpeta local uploads/ como respaldo.
    """
    service = get_drive_service()
    prefix = f"[{guest_name.strip()}] " if guest_name and guest_name.strip() else ""
    final_filename = f"{prefix}{filename}"

    # Modo Google Drive
    if service and DRIVE_FOLDER_ID:
        try:
            from googleapiclient.http import MediaIoBaseUpload

            file_obj.seek(0)
            media = MediaIoBaseUpload(
                file_obj,
                mimetype=mimetype or "application/octet-stream",
                resumable=True
            )

            file_metadata = {
                "name": final_filename,
                "parents": [DRIVE_FOLDER_ID]
            }

            request = service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id, name, webViewLink",
                supportsAllDrives=True
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"[Drive] Subiendo {final_filename}: {int(status.progress() * 100)}%")

            print(f"[Drive] Archivo subido con éxito: {response.get('name')} (ID: {response.get('id')})")
            return {
                "success": True,
                "destination": "google_drive",
                "file_id": response.get("id"),
                "file_name": response.get("name"),
                "view_link": response.get("webViewLink")
            }
        except Exception as e:
            print(f"[Drive] Error subiendo a Drive: {e}. Guardando copia local de respaldo...")

    # Fallback local (Demo o respaldo ante fallos)
    file_obj.seek(0)
    safe_name = "".join(c for c in final_filename if c.isalnum() or c in "._- []")
    local_path = UPLOAD_FOLDER / safe_name
    
    counter = 1
    base_name = local_path.stem
    ext = local_path.suffix
    while local_path.exists():
        local_path = UPLOAD_FOLDER / f"{base_name}_{counter}{ext}"
        counter += 1

    with open(local_path, "wb") as f:
        f.write(file_obj.read())

    return {
        "success": True,
        "destination": "local_demo",
        "file_name": local_path.name,
        "local_path": str(local_path),
        "message": "Guardado en carpeta local"
    }
