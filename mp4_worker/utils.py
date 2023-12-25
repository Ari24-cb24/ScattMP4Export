from PIL import Image


def resize_image(img: Image, w: int, h: int) -> Image:
    return img.resize((w, h), Image.ANTIALIAS)
