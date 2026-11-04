import io
from app import app

def test_routes():
    client = app.test_client()

    print("1. Probando ruta principal / (Invitados)...")
    res = client.get("/")
    assert res.status_code == 200
    assert b"Comparte tus Fotos y Videos" in res.data
    print("   -> OK (200)")

    print("2. Probando ruta /qr (Generador de tarjetas)...")
    res = client.get("/qr")
    assert res.status_code == 200
    assert b"Configurar e Imprimir Tarjeta" in res.data
    print("   -> OK (200)")

    print("3. Probando /api/status...")
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.get_json()
    assert "drive" in data
    print(f"   -> OK (200): Modo={data['drive']['mode']}")

    print("4. Probando /api/generate-qr (QR plano)...")
    res = client.get("/api/generate-qr?card=false&url=https://test.com")
    assert res.status_code == 200
    assert res.mimetype == "image/png"
    print("   -> OK (200 PNG)")

    print("5. Probando /api/upload (Subida en modo demo)...")
    test_file = (io.BytesIO(b"dummy photo content"), "recuerdo_prueba.jpg")
    res = client.post("/api/upload", data={"file": test_file, "guest_name": "Pedro"}, content_type="multipart/form-data")
    assert res.status_code == 200
    upload_res = res.get_json()
    assert upload_res["success"] is True
    print(f"   -> OK (200): Destino={upload_res['destination']}, Archivo={upload_res['file_name']}")

    print("\nTODAS LAS PRUEBAS PASARON EXITOSAMENTE.")

if __name__ == "__main__":
    test_routes()
