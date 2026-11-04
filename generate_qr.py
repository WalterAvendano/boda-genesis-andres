import sys
import os
import socket
import qrcode
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

COUPLE_NAMES = os.getenv("COUPLE_NAMES", "Nuestra Boda")
EVENT_DATE = os.getenv("EVENT_DATE", "¡Gracias por acompañarnos!")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def create_wedding_qr_card(url: str, output_path: str = None, couple_names: str = None, event_date: str = None):
    """
    Genera una tarjeta elegante lista para imprimir en las mesas de la boda con el código QR.
    """
    if output_path is None:
        output_path = Path(__file__).parent / "tarjeta_qr_boda.png"
    names = couple_names or COUPLE_NAMES
    date_text = event_date or EVENT_DATE

    # 1. Generar código QR con alta resolución
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta redundancia (30%)
        box_size=12,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Color elegante para el QR (azul oscuro / carbón elegante en lugar de negro plano)
    qr_img = qr.make_image(fill_color="#2b2d42", back_color="#ffffff").convert("RGBA")

    # 2. Crear lienzo de la tarjeta (ancho x alto: 1200 x 1600 px, proporción ideal para foto/tarjeta)
    card_w, card_h = 1200, 1600
    card = Image.new("RGBA", (card_w, card_h), "#fdfbf7")  # Fondo marfil / lino cálido
    draw = ImageDraw.Draw(card)

    # Marco dorado / floral geométrico elegante
    gold_color = "#c5a059"
    dark_text = "#2b2d42"
    sub_text = "#6c757d"

    # Doble borde exterior e interior
    draw.rectangle([40, 40, card_w - 40, card_h - 40], outline=gold_color, width=3)
    draw.rectangle([55, 55, card_w - 55, card_h - 55], outline=gold_color, width=1)

    # Adornos en las 4 esquinas
    for corner in [(70, 70), (card_w - 70, 70), (70, card_h - 70), (card_w - 70, card_h - 70)]:
        cx, cy = corner
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=gold_color)

    # Intentar cargar fuentes del sistema o usar la predeterminada
    def get_font(size):
        for font_name in ["georgia.ttf", "times.ttf", "arial.ttf"]:
            try:
                return ImageFont.truetype(font_name, size)
            except IOError:
                continue
        return ImageFont.load_default()

    font_title = get_font(84)
    font_subtitle = get_font(42)
    font_inst_head = get_font(36)
    font_inst = get_font(32)
    font_url = get_font(26)

    # Función auxiliar para texto centrado
    def draw_centered_text(y, text, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (card_w - text_w) // 2
        draw.text((x, y), text, font=font, fill=fill)
        return y + (bbox[3] - bbox[1])

    # Título (Nombres de los novios)
    y_pos = 130
    draw_centered_text(y_pos, "—  ✦  —", font_subtitle, gold_color)
    y_pos += 60
    draw_centered_text(y_pos, names, font_title, dark_text)
    y_pos += 105
    draw_centered_text(y_pos, "¿Tomaste fotos o videos hoy?", font_subtitle, gold_color)
    y_pos += 55
    draw_centered_text(y_pos, "¡Ayúdanos a guardar cada recuerdo!", font_inst, sub_text)

    # Pegar código QR en el centro
    qr_w, qr_h = qr_img.size
    qr_x = (card_w - qr_w) // 2
    qr_y = 470

    # Fondo blanco con sombra / borde sutil para el QR
    draw.rectangle([qr_x - 15, qr_y - 15, qr_x + qr_w + 15, qr_y + qr_h + 15], fill="#ffffff", outline=gold_color, width=2)
    card.paste(qr_img, (qr_x, qr_y), qr_img)

    # Instrucciones paso a paso
    y_inst = qr_y + qr_h + 45
    draw_centered_text(y_inst, "INSTRUCCIONES:", font_inst_head, gold_color)
    y_inst += 50
    draw_centered_text(y_inst, "1. Abre la cámara de tu celular", font_inst, dark_text)
    y_inst += 45
    draw_centered_text(y_inst, "2. Apunta y escanea este código QR", font_inst, dark_text)
    y_inst += 45
    draw_centered_text(y_inst, "3. Elige tus fotos y videos favoritos para subirlos", font_inst, dark_text)
    y_inst += 65
    draw_centered_text(y_inst, f"O entra directamente a: {url}", font_url, sub_text)
    y_inst += 70
    draw_centered_text(y_inst, date_text, font_subtitle, gold_color)

    # Guardar
    out_file = Path(output_path)
    card.convert("RGB").save(out_file, quality=95)
    print(f"[QR] Tarjeta de mesa generada exitosamente en: {out_file.resolve()}")
    return out_file

if __name__ == "__main__":
    default_url = os.getenv("APP_URL") or f"http://{get_local_ip()}:5000"
    target_url = sys.argv[1] if len(sys.argv) > 1 else default_url
    create_wedding_qr_card(target_url)
