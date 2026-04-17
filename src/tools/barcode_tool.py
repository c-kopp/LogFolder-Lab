import os
import segno
import barcode
import datetime

import config as config

from pylibdmtx.pylibdmtx import encode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image

OUTPUT_FOLDER = config.get_output_folder("Barcode")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def generate_barcodes(prefix, suffix, start_number, count, barcode_type, label_w_mm, label_h_mm, min_digits, crop_marks, logger):
    logger.info("Generate Barcodes started")
    logger.debug("Barcode: {prefix}{start_number}{suffix}")
    logger.debug("NumberOfBarcodes: {count}")
    logger.debug("Dimensions: {label_w_mm}x{label_h_mm}")
    logger.debug("Type: {barcode_type}")

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(OUTPUT_FOLDER, f"Barcodes_{barcode_type}_{timestamp}.pdf")

    pageWidth, pageHeight = 210, 297

    cropLen = 1.5 * mm
    cropOffset = 3 * mm

    minGap = (cropLen + cropOffset) * 2
    maxGap = max(minGap, label_w_mm * 0.15 * mm) / mm

    cols = max(1, int((pageWidth - 2 * maxGap) / (label_w_mm + maxGap)))
    rows = max(1, int((pageHeight - 2 * maxGap) / (label_h_mm + maxGap)))

    totalWidth = cols * label_w_mm + (cols - 1) * maxGap
    totalHeight = rows * label_h_mm + (rows - 1) * maxGap

    marginX = (pageWidth - totalWidth) / 2
    marginY = (pageHeight - totalHeight) / 2

    pageWidth = pageWidth * mm
    pageHeight = pageHeight * mm

    c = canvas.Canvas(output_path, pagesize=(pageWidth, pageHeight))
    col, row = 0, 0

    for i in range(count):
        min_number_len = max(0, min_digits - len(prefix) - len(suffix))
        number = str(start_number + i).zfill(min_number_len)
        content = f"{prefix}{number}{suffix}"

        x = (marginX + col * (label_w_mm + maxGap)) * mm
        y = pageHeight - (marginY + (row + 1) * label_h_mm + row * maxGap) * mm

        # ----- create barcode -----
        img = generate_barcode_image(barcode_type, content, label_w_mm, label_h_mm)

        img_buffer = BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        fontSize = max(2, min(10, label_w_mm * 0.15))
        padding = 0.5 * mm
        textH = fontSize * 0.325 * mm

        textY = y + padding
        barcodeWidth = textY + textH + padding
        barcodeHeight = (y + label_h_mm * mm) - barcodeWidth - padding

        is_2d = barcode_type in ["QR Code", "Data Matrix"]

        c.drawImage(
            ImageReader(img_buffer),
            x, barcodeWidth,
            width=label_w_mm * mm,
            height=barcodeHeight,
            preserveAspectRatio=is_2d,
            anchor="c"
        )

        c.setFont("Helvetica", fontSize)
        c.drawCentredString(
            x + label_w_mm * mm / 2,
            textY,
            content
        )

        # ----- Crop Marks -----
        if crop_marks:
            c.setStrokeColorRGB(0.5, 0.5, 0.5)
            c.setLineWidth(0.25)
            _draw_crop_marks(c, x, y, label_w_mm * mm, label_h_mm * mm, cropLen, cropOffset)

        # ----- next position -----
        col += 1
        if col >= cols:
            col = 0
            row += 1
            if row >= rows:
                row = 0
                c.showPage()

    try:
        c.save()
        logger.info(f"Barcode PDF saved: {output_path}")
    except Exception as e:
        logger.error(f"Barcode PDF not saved: {e}")


def generate_barcode_image(barcode_type, content, w_mm, h_mm):
    dpi = 300
    w_px = int(w_mm / 25.4 * dpi)
    h_px = int(h_mm / 25.4 * dpi)

    if barcode_type == "QR Code":
        qr = segno.make_qr(content)
        buffer = BytesIO()
        qr.save(buffer, kind="png", scale=10)
        buffer.seek(0)
        img = Image.open(buffer).convert("RGB")

    elif barcode_type == "Data Matrix":
        encoded = encode(content.encode("utf-8"))
        img = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)

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
    marks = [
        # top left
        (x - offset, y + h, x - offset - length, y + h),
        (x, y + h + offset, x, y + h + offset + length),
        # top right
        (x + w + offset, y + h, x + w + offset + length, y + h),
        (x + w, y + h + offset, x + w, y + h + offset + length),
        # bottom left
        (x - offset, y, x - offset - length, y),
        (x, y - offset, x, y - offset - length),
        # bottom right
        (x + w + offset, y, x + w + offset + length, y),
        (x + w, y - offset, x + w, y - offset - length),
    ]
    for x1, y1, x2, y2 in marks:
        c.line(x1, y1, x2, y2)
