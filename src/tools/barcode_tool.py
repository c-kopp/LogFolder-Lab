import os
import qrcode
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image


def generate_barcodes(
    output_folder,
    prefix,
    suffix,
    start_number,
    count,
    barcode_type,       # "code128" oder "qr"
    label_w_mm,         # Etikettenbreite in mm
    label_h_mm,         # Etikettenhöhe in mm
    min_digits,
    crop_marks,         # bool
    logger
):
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "barcodes.pdf")

    gap_mm = max(label_w_mm, label_h_mm) * 0.15
    margin_mm = gap_mm
    crop_len = 1.5 * mm
    crop_offset = 0.5 * mm

    a4_w_mm = 210
    a4_h_mm = 297

    cols = int((a4_w_mm - 2 * margin_mm) / (label_w_mm + gap_mm))
    rows = int((a4_h_mm - 2 * margin_mm) / (label_h_mm + gap_mm))
    cols = max(1, cols)
    rows = max(1, rows)

    total_w = cols * label_w_mm + (cols - 1) * gap_mm
    total_h = rows * label_h_mm + (rows - 1) * gap_mm
    margin_x = (a4_w_mm - total_w) / 2
    margin_y = (a4_h_mm - total_h) / 2

    page_w = a4_w_mm * mm
    page_h = a4_h_mm * mm

    c = canvas.Canvas(output_path, pagesize=(page_w, page_h))
    col, row = 0, 0

    for i in range(count):
        min_number_len = max(0, min_digits - len(prefix) - len(suffix))
        number = str(start_number + i).zfill(min_number_len)
        content = f"{prefix}{number}{suffix}"

        x = (margin_x + col * (label_w_mm + gap_mm)) * mm
        y = page_h - (margin_y + (row + 1) * label_h_mm + row * gap_mm) * mm

        # --- Barcode als Bild generieren ---
        img = _generate_barcode_image(barcode_type, content, label_w_mm, label_h_mm)

        # Bild ins PDF zeichnen
        img_buffer = BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)


        font_size = 6
        padding = 0.5 * mm
        text_h = font_size * 0.325 * mm

        text_y = y + padding
        barcode_y = text_y + text_h + padding
        barcode_h = (y + label_h_mm * mm) - barcode_y - padding

        c.drawImage(
            ImageReader(img_buffer),
            x, barcode_y,
            width=label_w_mm * mm,
            height=barcode_h,
            preserveAspectRatio=False,
            anchor="c"
        )

        c.setFont("Helvetica", font_size)
        c.drawCentredString(
            x + label_w_mm * mm / 2,
            text_y,
            content
        )

        # --- Schneidzeichen ---
        if crop_marks:
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.setLineWidth(0.25)
            _draw_crop_marks(c, x, y, label_w_mm * mm, label_h_mm * mm, crop_len, crop_offset)

        # Nächste Position
        col += 1
        if col >= cols:
            col = 0
            row += 1
            if row >= rows:
                row = 0
                c.showPage()

    c.save()
    logger.info(f"PDF gespeichert: {output_path}")
    return output_path


def _generate_barcode_image(barcode_type, content, w_mm, h_mm):
    dpi = 300
    w_px = int(w_mm / 25.4 * dpi)
    h_px = int(h_mm / 25.4 * dpi)

    if barcode_type == "QR Code":
        qr = qrcode.QRCode(box_size=10, border=1)
        qr.add_data(content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    else:
        type_map = {
            "Code 128": "code128",
            "Code 39":  "code39",
        }
        bc_type = type_map[barcode_type]
        bc = barcode.get(bc_type, content, writer=ImageWriter())
        buffer = BytesIO()
        bc.write(buffer, options={
            "module_width": 0.2,
            "module_height": h_mm * 0.6,
            "font_size": 0,
            "text_distance": 1,
            "quiet_zone": 2,
            "dpi": dpi,
            "write_text": False,
        })
        buffer.seek(0)
        img = Image.open(buffer).convert("RGB")

    img = img.resize((w_px, h_px), Image.LANCZOS)
    return img


def _draw_crop_marks(c, x, y, w, h, length, offset):
    # Ecken: oben-links, oben-rechts, unten-links, unten-rechts
    marks = [
        # oben-links
        (x - offset, y + h, x - offset - length, y + h),
        (x, y + h + offset, x, y + h + offset + length),
        # oben-rechts
        (x + w + offset, y + h, x + w + offset + length, y + h),
        (x + w, y + h + offset, x + w, y + h + offset + length),
        # unten-links
        (x - offset, y, x - offset - length, y),
        (x, y - offset, x, y - offset - length),
        # unten-rechts
        (x + w + offset, y, x + w + offset + length, y),
        (x + w, y - offset, x + w, y - offset - length),
    ]
    for x1, y1, x2, y2 in marks:
        c.line(x1, y1, x2, y2)
