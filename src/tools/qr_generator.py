import os
import qrcode
import datetime

import config as config

from PIL import Image

from pylibdmtx.pylibdmtx import encode

OUTPUT_FOLDER = config.get_output_folder("QRCode")
QR_COLOR = (28, 45, 87)
QR_SIZE = 100
QR_BACK_COLOR = "white"


def generate_qrcode(path, barcode_type, logger):
    logger.info("Generate QR Code started")
    if not path.strip():
        logger.warning("No valid link is provided for QR Generator")
        return

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(OUTPUT_FOLDER, f"QRCode_{barcode_type}_{timestamp}.png")

    img = generate_preview_image(path, barcode_type)

    try:
        img.save(output_path)
        logger.info(f"QR Code saved: {output_path}")
    except Exception as e:
        logger.error(f"QR Code not saved: {e}")


def generate_preview_image(data, barcode_type, color=QR_COLOR):
    if barcode_type == "QR Code":
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(data)
        qr.make()
        qr_img = qr.make_image(fill_color=QR_COLOR, back_color=QR_BACK_COLOR).convert("RGB")

        logo = Image.open(os.path.join(config.get("image_folder"), "CS_quadratic.png"))
        ratio = QR_SIZE / float(logo.size[0])
        h_size = int(logo.size[1] * ratio)
        logo = logo.resize((QR_SIZE, h_size))

        pos = (
            (qr_img.size[0] - logo.size[0]) // 2,
            (qr_img.size[1] - logo.size[1]) // 2
        )
        qr_img.paste(logo, pos)

        return qr_img

    elif barcode_type == "Data Matrix":
        encoded = encode(data.encode("utf-8"))
        img = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)

        img = img.convert("RGBA")
        pixels = img.load()
        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = pixels[x, y]
                if r < 128:
                    pixels[x, y] = (*color, 255)
        img = img.convert("RGB")

        scale = 10
        img = img.resize((encoded.width * scale, encoded.height * scale), Image.NEAREST)

        return img
