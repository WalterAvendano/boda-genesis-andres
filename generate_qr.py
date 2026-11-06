import sys
import os
import socket
import qrcode
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

COUPLE_NAMES = os.getenv("COUPLE_NAMES", "Génesis & Andrés")
EVENT_DATE = os.getenv("EVENT_DATE", "14 de Noviembre, 2026")

# Paleta de colores extraída de la invitación
COLOR_TEAL = "#186b62"        # Verde esmeralda elegante (color de los nombres)
COLOR_MAUVE = "#b87b87"       # Rosa palo / malva (sello de la invitación)
COLOR_MAUVE_LIGHT = "#f7eded" # Rosa pastel suave
COLOR_BORDER = "#dfc7c7"      # Borde suave del sobre
COLOR_BG = "#fcf9f9"          # Fondo blanco marfil rosado
COLOR_TEXT_MUTED = "#7a6669"  # Texto secundario malva oscuro

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def generate_qr_with_logo(url: str, box_size: int = 12) -> Image.Image:
    """Genera un código QR con el color verde esmeralda y el monograma de los novios en el centro."""
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% redundancia para permitir logo central
        box_size=box_size,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Color verde esmeralda idéntico a la invitación
    qr_img = qr.make_image(fill_color=COLOR_TEAL, back_color="#ffffff").convert("RGBA")

    # Ruta del logo
    logo_path = Path(__file__).parent / "static" / "monograma.png"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        qr_w, qr_h = qr_img.size

        # El logo toma aprox 24% del ancho del QR
        logo_size = int(qr_w * 0.25)
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

        # Fondo circular blanco con borde rosa suave
        bg_size = logo_size + 16
        logo_bg = Image.new("RGBA", (bg_size, bg_size), (0, 0, 0, 0))
        bg_draw = ImageDraw.Draw(logo_bg)
        bg_draw.ellipse((0, 0, bg_size - 1, bg_size - 1), fill="#ffffff", outline=COLOR_BORDER, width=3)

        # Pegar logo centrado
        offset = (bg_size - logo_size) // 2
        logo_bg.paste(logo, (offset, offset), mask=logo)

        # Pegar en el centro del código QR
        pos = ((qr_w - bg_size) // 2, (qr_h - bg_size) // 2)
        qr_img.paste(logo_bg, pos, mask=logo_bg)

    return qr_img

def create_wedding_qr_card(url: str, output_path: str = None, couple_names: str = None, event_date: str = None):
    """
    Genera una tarjeta elegante lista para imprimir en las mesas de la boda con la paleta y diseño oficial.
    """
    if output_path is None:
        output_path = Path(__file__).parent / "tarjeta_qr_boda.png"
    names = couple_names or COUPLE_NAMES
    date_text = event_date or EVENT_DATE

    # 1. QR con logo
    qr_img = generate_qr_with_logo(url, box_size=12)

    # 2. Lienzo de la tarjeta (1200 x 1600 px)
    card_w, card_h = 1200, 1600
    card = Image.new("RGBA", (card_w, card_h), COLOR_BG)
    draw = ImageDraw.Draw(card)

    # Marco con los colores de la invitación
    draw.rectangle([40, 40, card_w - 40, card_h - 40], outline=COLOR_MAUVE, width=3)
    draw.rectangle([55, 55, card_w - 55, card_h - 55], outline=COLOR_BORDER, width=1)

    # Detalle en las 4 esquinas
    for corner in [(70, 70), (card_w - 70, 70), (70, card_h - 70), (card_w - 70, card_h - 70)]:
        cx, cy = corner
        draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=COLOR_MAUVE)

    # Intentar cargar fuentes bonitas del sistema
    def get_font(size, is_script=False):
        if is_script:
            for font_name in ["GreatVibes-Regular.ttf", "AlexBrush-Regular.ttf", "BrushScript.ttf", "segoeprb.ttf", "georgia.ttf"]:
                try:
                    return ImageFont.truetype(font_name, size)
                except IOError:
                    continue
        for font_name in ["georgia.ttf", "times.ttf", "arial.ttf"]:
            try:
                return ImageFont.truetype(font_name, size)
            except IOError:
                continue
        return ImageFont.load_default()

    font_title = get_font(96, is_script=True)
    font_subtitle = get_font(34)
    font_inst_head = get_font(34)
    font_inst = get_font(30)
    font_url = get_font(24)

    def draw_centered_text(y, text, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (card_w - text_w) // 2
        draw.text((x, y), text, font=font, fill=fill)
        return y + (bbox[3] - bbox[1])

    # Monograma superior en el encabezado
    logo_path = Path(__file__).parent / "static" / "monograma.png"
    y_pos = 90
    if logo_path.exists():
        top_logo = Image.open(logo_path).convert("RGBA")
        top_logo = top_logo.resize((130, 130), Image.Resampling.LANCZOS)
        logo_x = (card_w - 130) // 2
        card.paste(top_logo, (logo_x, y_pos), mask=top_logo)
        y_pos += 150
    else:
        y_pos += 50

    # Nombres en verde esmeralda
    draw_centered_text(y_pos, names, font_title, COLOR_TEAL)
    y_pos += 115
    draw_centered_text(y_pos, "TE INVITAMOS A COMPARTIR TUS RECUERDOS", font_subtitle, COLOR_MAUVE)
    y_pos += 50
    draw_centered_text(y_pos, "¡Ayúdanos a guardar cada foto y video de este día!", font_inst, COLOR_TEXT_MUTED)

    # Pegar código QR en el centro
    qr_w, qr_h = qr_img.size
    qr_x = (card_w - qr_w) // 2
    qr_y = 520

    # Marco circular / rectangular para el QR
    draw.rectangle([qr_x - 14, qr_y - 14, qr_x + qr_w + 14, qr_y + qr_h + 14], fill="#ffffff", outline=COLOR_BORDER, width=2)
    card.paste(qr_img, (qr_x, qr_y), qr_img)

    # Instrucciones estilo invitación
    y_inst = qr_y + qr_h + 45
    draw_centered_text(y_inst, "— o   INSTRUCCIONES   o —", font_inst_head, COLOR_TEAL)
    y_inst += 52
    draw_centered_text(y_inst, "1. Abre la cámara de tu celular", font_inst, "#2c2a29")
    y_inst += 44
    draw_centered_text(y_inst, "2. Apunta y escanea este código QR", font_inst, "#2c2a29")
    y_inst += 44
    draw_centered_text(y_inst, "3. Elige tus fotos y videos favoritos para subirlos", font_inst, "#2c2a29")
    y_inst += 60
    draw_centered_text(y_inst, f"O entra directamente a: {url}", font_url, COLOR_TEXT_MUTED)
    y_inst += 60
    draw_centered_text(y_inst, f"✦ {date_text} ✦", font_subtitle, COLOR_MAUVE)

    # Guardar
    out_file = Path(output_path)
    card.convert("RGB").save(out_file, quality=95)
    print(f"[QR] Tarjeta generada exitosamente en: {out_file.resolve()}")
    return out_file

if __name__ == "__main__":
    default_url = os.getenv("APP_URL") or "https://boda-genesis-andres.onrender.com"
    target_url = sys.argv[1] if len(sys.argv) > 1 else default_url
    create_wedding_qr_card(target_url)
