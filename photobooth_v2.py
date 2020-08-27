import time
from picamera import PiCamera
from gpiozero import Button, LED
from overlay_functions import *
from time import sleep, strftime, localtime
from guizero import App, PushButton, Text, Picture, Window, Box
import threading
import pygame
import flickrapi
import os.path

# Dome Buttons
disable_buttons = True
led_izq = LED(21)
led_der = LED(13)

#Initialise pygame and the mixer (Sonido)
pygame.init()
pygame.mixer.init()

# Cuenta atras
photo_countdown_time = 4    # countdown time before photo is taken


def print_overlay(string_to_print):
    """
    Writes a string to both [i] the console, and [ii] camera.annotate_text
    """
    #log_print(string_to_print)
    camera.annotate_text = string_to_print


def countdown():
    for counter in range(photo_countdown_time,0,-1):
        print_overlay("                                           ..." + str(counter))
        led_izq.off()
        led_der.off()
        sleep(.5)
        led_izq.on()
        led_der.on()
        sleep(.5)

    camera.annotate_text = ''


# Fickr
#https://stuvel.eu/flickrapi-doc/index.html
api_key = u'API_KEY'
api_secret = u'API_SECRET'

flickr = flickrapi.FlickrAPI(api_key, api_secret)
flickr.authenticate_via_browser(perms='write')

class FileWithCallback(object):
    def __init__(self, filename, callback):
        self.file = open(filename, 'rb')
        self.callback = callback
        # the following attributes and methods are required
        self.len = os.path.getsize(filename)
        self.fileno = self.file.fileno
        self.tell = self.file.tell

    def read(self, size):
        if self.callback:
            self.callback(self.tell() * 100 // self.len)
        return self.file.read(size)

def callback(progress):
    print(progress)


# Tell the next overlay button what to do
def next_overlay():
    if disable_buttons == False:
        global overlay
        overlay = next(all_overlays)
        preview_overlay(camera, overlay)


# Tell the take picture button what to do
def take_picture():
    if disable_buttons == False:
        countdown()
        global filename
        global output
        filename = strftime("%Hh%M%S%d%m%Y.png", localtime())
        output = "/home/pi/photobooth/photos/" + filename

        #load the sound file
        mysound = pygame.mixer.Sound("/home/pi/photobooth/wav/Shutter-01.wav")
        #play the sound file
        mysound.play()

        camera.capture(output)
        camera.stop_preview()
        remove_overlays(camera)
        output_overlay(output, overlay)

        view_last_picture(output)


def new_picture():
    global disable_buttons
    disable_buttons = False
    led_izq.on()
    led_der.on()
    camera.start_preview(alpha=255, fullscreen=True, window=(0, 0, 800, 480))
    preview_overlay(camera, overlay)


def send_picture():
    params = {}
    params['filename'] = output
    params['title'] = filename
    params['description'] = ''

    params['fileobj'] = FileWithCallback(params['filename'], callback)

    # quitamos botones mientras enviamos

    flickr_enviando.text_color = "#ffffff"
    flickr_enviando.tk.configure(font="Verdana 20 bold")
    flickr_enviando.width = 12

    cancel_pic_button.hide()
    new_pic_button.hide()
    send_pic_button.hide()
    grupo_botones.hide()
    flickr_enviando.show()
    app.update()

    rsp = flickr.upload(params['filename'], params['fileobj'], None, title=params['title'], description=params['description'])
    print(rsp)
    flickr_enviando.hide()
    app.update()

    flickr_ok()


# Volver a la pantalla principal
def cancel_picture():
    #camera_window.hide()
    #enviado_window.hide()
    pantalla_inicial()


# Set up buttons
next_overlay_btn = Button(23)
next_overlay_btn.when_pressed = next_overlay
take_pic_btn = Button(25)
take_pic_btn.when_pressed = take_picture

# Set up camera (with resolution of the touchscreen)
camera = PiCamera()
camera.resolution = (800, 480)
camera.hflip = False

# Set up filename
output = ""
filename = ""

latest_photo = '/home/pi/photobooth/photos/' + filename


# Start camera preview
def open_camera():
    global disable_buttons
    disable_buttons = False
    led_izq.on()
    led_der.on()
    global overlay

    app_picture.hide()
    open_camera_button.hide()
    app.update()

    overlay = next(all_overlays)
    preview_overlay(camera, overlay)
    camera.start_preview(alpha=255, fullscreen=True, window=(0, 0, 800, 480))


# Ver foto, hacer nueva o enviar

def preparar_botones():
    cancel_pic_button.bg = "#EE2B31"
    cancel_pic_button.text_color = "#ffffff"
    cancel_pic_button.tk.configure(font="Verdana 20 bold")
    cancel_pic_button.width = 12

    new_pic_button.bg = "#00adef"
    new_pic_button.text_color = "#ffffff"
    new_pic_button.tk.configure(font="Verdana 20 bold")
    new_pic_button.width = 12

    send_pic_button.bg = "#1DBC60"
    send_pic_button.text_color = "#ffffff"
    send_pic_button.tk.configure(font="Verdana 20 bold")
    send_pic_button.width = 12

def view_last_picture(output):
    global disable_buttons
    disable_buttons = True
    led_izq.off()
    led_der.off()

    your_pic.image=output
    your_pic.width = 800
    your_pic.height = 480

    preparar_botones()

    your_pic.show()
    cancel_pic_button.show()
    new_pic_button.show()
    send_pic_button.show()
    grupo_botones.show()

    app.update()


# Foto enviada correctamente
def flickr_ok():
    global disable_buttons
    disable_buttons = True
    led_izq.off()
    led_der.off()


    # flickr_ok_text = Text(enviado_window, text="Foto enviada correctament!", color="#ffffff")
    # flickr_ok_text.tk.configure(font="Verdana 24 bold")

    flickr_ok_button.bg = "#00adef"
    flickr_ok_button.text_color = "#ffffff"
    flickr_ok_button.tk.configure(font="Verdana 20 bold")
    flickr_ok_button.width = 12

    your_pic.hide()
    cancel_pic_button.hide()
    new_pic_button.hide()
    send_pic_button.hide()
    grupo_botones.hide()

    flickr_ok_picture.show()
    flickr_ok_button.show()


    app.update()
    time.sleep(5)

    pantalla_inicial()
#    camera_window.hide()
#    enviado_window.show()
#    enviado_window.focus()



def pantalla_inicial():
  app_picture.image="/home/pi/photobooth/assets/splash_bg.jpg"
  open_camera_button.text="FES-TE UNA FOTO!"
  open_camera_button.bg = "#F75314"
  open_camera_button.text_color = "#ffffff"
  open_camera_button.tk.configure(font="Verdana 20 bold")

  your_pic.hide()
  cancel_pic_button.hide()
  new_pic_button.hide()
  send_pic_button.hide()
  grupo_botones.hide()
  flickr_ok_button.hide()
  flickr_ok_picture.hide()
  flickr_enviando.hide()

  app.update()

  app_picture.show()
  open_camera_button.show()

  app.update()


#elementos comunes
app = App(title="Any del Llibre - Ripolab", width=800, height=480, layout="grid", bg="#231f20")
app.tk.attributes("-fullscreen", True)

# elementos Pantalla inicial
app_picture = Picture(app, grid=[0,0])
open_camera_button = PushButton(app, command=open_camera, grid=[0,0])

# elementos pantalla de enviar foto
#your_pic = Picture(app, grid=[0,0,3,1])
your_pic = Picture(app, grid=[0,0])
grupo_botones = Box(app, layout="grid", grid=[0,0], align="top")
cancel_pic_button = PushButton(grupo_botones, cancel_picture, text="Cancel·la", grid=[0,0])
new_pic_button = PushButton(grupo_botones, new_picture, text="Nova foto", grid=[1,0])
send_pic_button = PushButton(grupo_botones, send_picture, text="Enviar foto", grid=[2,0])

flickr_ok_button = PushButton(app, command=cancel_picture, text="Tornar a l'inici", grid=[0,0])
flickr_ok_picture = Picture(app, image="/home/pi/photobooth/assets/flickr_ok.jpg", grid=[0,0])
flickr_enviando = PushButton(app, text="Enviant...", grid=[0,0])

pantalla_inicial()


# Hacer foto
#camera_window = Window(app, title="Fes-te una foto!", width=800, height=480, layout="grid", bg="#231f20")
#camera_window.hide()

# Foto enviada
#enviado_window = Window(app, title="Foto enviada correctament!", width=800, height=480, layout="grid", bg="#231f20")
#enviado_window.hide()


app.display()
