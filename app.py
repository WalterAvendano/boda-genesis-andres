import os
import io
import socket
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
import qrcode
from PIL import Image

def get_local_ip():
    """Detecta la IP local de la computadora en la red Wi-Fi automáticamente."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# Importar servicio de Google Drive
from drive_service import upload_file_to_drive, check_drive_connection, UPLOAD_FOLDER
from generate_qr import create_wedding_qr_card

load_dotenv()

app = Flask(__name__)
# Permitir subidas de hasta 500 MB (para videos de alta resolución)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

COUPLE_NAMES = os.getenv("COUPLE_NAMES", "Ana & Carlos")
EVENT_DATE = os.getenv("EVENT_DATE", "¡Nuestra Boda!")
WELCOME_MESSAGE = os.getenv("WELCOME_MESSAGE", "Gracias por acompañarnos en este día tan especial. Sube aquí tus fotos y videos para que podamos revivir cada momento juntos.")

@app.route("/")
def index():
    """Página principal móvil para que los invitados suban sus fotos y videos."""
    return render_template(
        "index.html",
        couple_names=COUPLE_NAMES,
        event_date=EVENT_DATE,
        welcome_message=WELCOME_MESSAGE
    )

@app.route("/api/upload", methods=["POST"])
def upload():
    """Recibe las fotos/videos y las sube a Google Drive (o guarda en local si está en modo demo)."""
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No se envió ningún archivo"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Archivo sin nombre"}), 400

    guest_name = request.form.get("guest_name", "").strip()

    try:
        result = upload_file_to_drive(
            file_obj=file.stream,
            filename=file.filename,
            mimetype=file.mimetype,
            guest_name=guest_name
        )
        return jsonify(result)
    except Exception as e:
        print(f"Error procesando subida: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/qr")
def qr_page():
    """Página para previsualizar, personalizar e imprimir la tarjeta QR de las mesas."""
    # Sugerir la IP de la red Wi-Fi para que funcione en celulares
    port = int(os.getenv("PORT", 5000))
    lan_ip = get_local_ip()
    suggested_url = f"http://{lan_ip}:{port}" if lan_ip != "127.0.0.1" else request.host_url.rstrip("/")
    return render_template(
        "qr.html",
        couple_names=COUPLE_NAMES,
        event_date=EVENT_DATE,
        default_url=suggested_url
    )

@app.route("/api/generate-qr", methods=["GET"])
def get_qr_image():
    """Genera la imagen del código QR plano o con tarjeta para imprimir."""
    url = request.args.get("url", request.host_url).strip()
    with_card = request.args.get("card", "true").lower() == "true"
    couple = request.args.get("couple", COUPLE_NAMES)
    date_str = request.args.get("date", EVENT_DATE)

    if with_card:
        # Generar tarjeta completa
        temp_path = UPLOAD_FOLDER / "preview_qr_card.png"
        create_wedding_qr_card(url, str(temp_path), couple_names=couple, event_date=date_str)
        return send_file(temp_path, mimetype="image/png")
    else:
        # Solo código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#2b2d42", back_color="#ffffff")
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return send_file(buf, mimetype="image/png")

@app.route("/api/status")
def status():
    """Devuelve el estado de conexión con Google Drive y conteo de subidas."""
    drive_info = check_drive_connection()
    local_count = len(list(UPLOAD_FOLDER.glob("*.*"))) if UPLOAD_FOLDER.exists() else 0
    return jsonify({
        "drive": drive_info,
        "local_uploads_count": local_count,
        "couple_names": COUPLE_NAMES,
        "event_date": EVENT_DATE
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    lan_ip = get_local_ip()
    print(f"\n=======================================================")
    print(f"✨ APLICATIVO BODA QR & DRIVE ACTIVO ✨")
    print(f"-> En tu computadora: http://localhost:{port}")
    print(f"-> En tu celular (Wi-Fi): http://{lan_ip}:{port}")
    print(f"-> Generador de QR para imprimir: http://localhost:{port}/qr")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
