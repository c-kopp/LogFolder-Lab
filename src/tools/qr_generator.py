import os
import qrcode
import datetime

import config as config

from PIL import Image

OUTPUT_FOLDER = config.get_output_folder("QRCode")


def create_qr_code(path, logger):

    if not path.strip():
        logger.warning("No input provided")
        return

    pathLogo = os.path.join(config.get("image_folder"), "CS_quadratic.png")
    logo = Image.open(pathLogo)

    baseWidth= 100

    wpercent = (baseWidth / float(logo.size[0]))
    hsize = int((float(logo.size[1])*float(wpercent)))
    logo = logo.resize((baseWidth, hsize))

    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )

    QRcode.add_data(path)
    QRcode.make()
    QRcolor = (28, 45, 87)

    QRimg = QRcode.make_image(
        fill_color=QRcolor,
        back_color="white"
    ).convert("RGB")

    pos = (
        (QRimg.size[0] - logo.size[0]) // 2,
        (QRimg.size[1] - logo.size[1]) // 2
    )

    QRimg.paste(logo, pos)

    outputFile = os.path.join(OUTPUT_FOLDER, f"ISD_QR_{datetime.datetime.now().strftime('%Y%m%d-%H%M')}.png")

    QRimg.save(outputFile)

    logger.info(f"QR Code saved as {outputFile}")
