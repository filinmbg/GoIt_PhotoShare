import qrcode
from io import BytesIO


def generate_qr_code(text: str) -> bytes:
    """
    The generate_qr_code function takes a string as input and returns a QR code image of that string.

    :param text: str: Specify the text that will be encoded in the qr code
    :return: A bytes object
    :doc-author: Trelent
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_byte_array = BytesIO()
    img.save(img_byte_array)
    return img_byte_array.getvalue()
