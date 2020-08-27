# Adapted from some original code by bennuttall and waveform80
# -------------------------------------------------------------

from PIL import Image, ImageOps, ImageEnhance, ImageFilter
from itertools import cycle

# EDIT THESE VALUES ------------------------
#overlays_dir = "/home/pi/photobooth/overlays"
overlays_dir = "/home/pi/photobooth/photobooth_assets"

assets_dir = "/home/pi/photobooth/assets"
overlays = ['1','2','3','4','5','6','7','8','9','10']
# ------------------------------------------


overlay = overlays[0] # Starting value

def _get_overlay_image(overlay):

    # Open the overlay as an Image object
    return Image.open(overlays_dir + "/" + overlay + ".png")

def _get_overlay_watermark_image():

    # Open the overlay as an Image object
    return Image.open(assets_dir + "/watermark.png")

def _pad(resolution, width=32, height=16):
    # Pads the specified resolution
    # up to the nearest multiple of *width* and *height*; this is
    # needed because overlays require padding to the camera's
    # block size (32x16)
    return (
        ((resolution[0] + (width - 1)) // width) * width,
        ((resolution[1] + (height - 1)) // height) * height,
    )

def remove_overlays(camera):

    # Remove all overlays from the camera preview
    for o in camera.overlays:
        camera.remove_overlay(o)


def preview_overlay(camera=None, overlay=None):

    # Remove all overlays
    remove_overlays(camera)

    # Get an Image object of the chosen overlay
    overlay_img = _get_overlay_image(overlay)
    overlay_watermark_img = _get_overlay_watermark_image() #watermark

    # Pad it to the right resolution
    pad = Image.new('RGBA', _pad(camera.resolution))
    pad.paste(overlay_img, (0, 0))

    # Pad it to the right resolution (watermark)
    pad2 = Image.new('RGBA', _pad(camera.resolution))
    pad2.paste(overlay_watermark_img, (0, 0))

    # Add the overlay
    camera.add_overlay(pad.tobytes(), alpha=128, layer=3)
    #camera.add_overlay(pad2.tobytes(), alpha=128, layer=4)


def output_overlay(output=None, overlay=None):

    # Take an overlay Image
    overlay_img = _get_overlay_image(overlay)
    overlay_watermark_img = _get_overlay_watermark_image() #watermark

    # ...and a captured photo
    imagen = Image.open(output).convert('RGB')

    # añadimos los filtros de mirror + iluminar
    img2 = imagen.filter(ImageFilter.EDGE_ENHANCE)
    #espejo = ImageOps.mirror(img2)
    autocontraste = ImageOps.autocontrast(img2, cutoff=0)
    ecualizada = ImageOps.equalize(img2)
    blendimg = Image.blend(autocontraste, ecualizada, alpha=0.1)
    output_img = ImageEnhance.Brightness(blendimg).enhance(1.0)

    output_img_RGBA = output_img.convert('RGBA')
    #output_img_RGBA2 = output_img_RGBA.transpose(Image.FLIP_LEFT_RIGHT)    
    # Combine the two and save the image as output
    print("----overlay")
    print(overlay_img)
    print(output_img)
    new_output = Image.alpha_composite(output_img_RGBA, overlay_img)
    new_output = Image.alpha_composite(new_output, overlay_watermark_img)
    new_output.save(output)

all_overlays = cycle(overlays)
