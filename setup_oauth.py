import os
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

def run_oauth_setup():
    project_dir = Path(__file__).parent
    client_secrets_file = project_dir / "client_secrets.json"
    token_file = project_dir / "token.json"

    if not client_secrets_file.exists():
        print("\n❌ Error: No se encontró el archivo 'client_secrets.json'.")
        print("Sigue estos pasos rápidos en Google Cloud Console:")
        print("1. Ve a: https://console.cloud.google.com/apis/credentials")
        print("2. Clic en '+ Crear credenciales' > 'ID de cliente de OAuth'.")
        print("3. Tipo de aplicación: 'App de escritorio' (Desktop app).")
        print("4. Clic en 'Crear' y descarga el archivo JSON.")
        print(f"5. Guárdalo como '{client_secrets_file.resolve()}' y vuelve a ejecutar este script.\n")
        return False

    print("\nIniciando autorización con tu cuenta de Google...")
    print("Se abrirá una pestaña en tu navegador para que autorices a la aplicación a subir fotos a tu Drive.")
    
    flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_file), SCOPES)
    creds = flow.run_local_server(port=0)

    # Guardar credenciales con refresh token
    with open(token_file, "w") as token:
        token.write(creds.to_json())

    print(f"\n✅ ¡Autorización exitosa! Credenciales guardadas en: {token_file.name}")
    print("A partir de ahora, todas las fotos y videos se subirán directamente a tu cuenta con tus 15 GB de Drive.")
    return True

if __name__ == "__main__":
    run_oauth_setup()
