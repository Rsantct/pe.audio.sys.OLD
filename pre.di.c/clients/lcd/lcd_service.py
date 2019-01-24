#!/usr/bin/env python3

# Copyright (c) 2018 Rafael Sánchez
# This file is part of pre.di.c
# pre.di.c, a preamp and digital crossover
# Copyright (C) 2018 Roberto Ripio
#
# pre.di.c is based on FIRtro https://github.com/AudioHumLab/FIRtro
# Copyright (c) 2006-2011 Roberto Ripio
# Copyright (c) 2011-2016 Alberto Miguélez
# Copyright (c) 2016-2018 Rafael Sánchez
#
# pre.di.c is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pre.di.c is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pre.di.c.  If not, see <https://www.gnu.org/licenses/>.

#!/usr/bin/env python3
"""

    WORK IN PROGRESSSSSSS


    pre.di.c info displayed on LCD

    Para hacer pruebas en línea de comandos:

        server_lcdproc.py   --test          Inicia un modo interactivo para
                                            escribir mensajes en la pantalla LCD.

                            --level xx.xx   Se muestra el valor en números grandes.

                            --msg cadena    Se muestra la cadena en scroll con caracteres grandes.

                            --layouts       Se muestran las layouts predefinidas para
                                            presentar la pantalla resumen del estado de FIRtro.

    (Los mensajes de estas pruebas expiran en 10 seg)
"""

# Some features:

#   Configurable layouts

#   'lcd_info_timeout: 0' was intended to avoid displaying the short-lived info screen 
#   about he last command, but currently pre.di.c does not manage it.    

#   It is posible to adjust the priority for the main status screen 'scr_1'

#   Display level with big digits

#   Big chars messages scrolling

#   Big mute optional can be displayed

#   It is available a full screen scroll that shows a string by using the routines
#   from lcdbig.py, which scalates the chars through by a custom method based in
#   4 text lines of basic ascii, because lcdproc protocol does not alows extended ascii.


import os
HOME = os.path.expanduser("~")
import sys
from time import sleep
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import basepaths as bp
import client_lcd
import lcdbig
import players

# Will watch for files changed on this folder and subfolders:
WATCHED_DIR = f'{HOME}/pre.di.c/'

# Read LCD settings
f = open( f'{bp.config_folder}/lcd.yml', 'r')
tmp = f.read()
f.close()
try:
    lcdConfig = yaml.load(tmp)
except:
    print ( 'YAML error into ' + lcdConfig_fname )


def split_by_n( seq, n ):
    # A generator to divide a sequence into chunks of n units
    while seq:
        yield seq[:n]
        seq = seq[n:]

def posi(coord):
    # auxiliar para colocar los widgets, usada por show_widgets
    # notese que se devuelve "columna  fila"
    return " ".join(str(x) for x in coord[::-1])

def printa_layouts():
    # ABAJO se deben  configurar estos  esquemas de presentacion
    print()
    print( " ----- ESQUEMA 1 (por defecto) ----")
    print( "    12345678901234567890"           )
    print( " 1  Vol: -12.5 HR: 22.0 "           )
    print( " 2  Bass: -2 Treble: -3 "           )
    print( " 3  input: analog       "           )
    print( " 4  Loud: 12 (6.47 dB)  "           )
    print(                                      )
    print( " ----- ESQUEMA 2 ------------------")
    print( "    12345678901234567890"           )
    print( " 1  V -32.0 H 34.0  B -2"           )
    print( " 2  B -2 T -3 sEQ DRC PQ"           )
    print( " 3  input_name    Lns ST"           )
    print( " 4  preset_name       mp"           )
    print()

def show_widget(type, value):

    # Usamos nombres de tres letras para identificar los widgets aquí
    # al objeto de ayudar en las lineas de lanzamiento de widgets de más abajo
    #
    # Hay dos propiedades que definir:
    #   1 - Las coordenadas del widget, ejemplo       Cvol=1,1
    #       Nota: para que NO SE MUESTRE pondremos    Cvol=0,0
    #       OjO:  cuidado de no solapar widgets en la misma linea
    #
    #   2 - La etiqueta antes de mostrar el value del widget
    #       Ejemplo   Lvol = "Vol: "
    #
    # Puede ser necesario transformar values como se hace en el esquema 2

    # Inicializamos coordenadas y etiquetas a cero:
    Cvol=0,0; Chea=0,0; Cbal=0,0; Cbas=0,0; Ctre=0,0; Cseq=0,0; Cdrc=0,0;
    Cpeq=0,0; Cinp=0,0; Clns=0,0; Cmon=0,0; Cpre=0,0; Cfty=0,0; Clni=0,0;
    Lvol="";  Lhea="";  Lbal="";  Lbas="";  Ltre="";  Lseq="";  Ldrc="";
    Lpeq="";  Linp="";  Llns="";  Lmon="";  Lpre="";  Lfty="";  Llni="";

    # ---------- ESQUEMA 2 ------------
    if lcdConfig['layout'] == 2:

        # coordenadas
        Cvol=1,1;       Chea=1,9;                     Cbal=1,17;
        Cbas=2,1;  Ctre=2,6;  Cseq=2,11;  Cdrc=2,15;  Cpeq=2,19;
        Cinp=3,1;                         Clns=3,15;  Cmon=3,19;
        Cpre=4,1;                                     Cfty=4,19;

        # etiquetas para algunos values:
        Lvol="V ";     Lhea="H ";                 Lbal="B "
        Lbas="B ";   Ltre="T ";

        # Transformaciones de algunos values ya que en este esquema
        # los mostraremos solo si están activos
        if type == 'loud':
            if value == "True": value = "LNS"
            else:               value = " - "
        if type == 'syseq':
            if value == "True": value = "sEQ"
            else:               value = " - "
        if type == 'drc':
            if value!="0":      value = "DRC"
            else:               value = " - "
        if type == 'peq':
            if value=="off":    value = "- "
            else:               value = "PQ"
        if type == 'mono':
            if value=="off":    value = "ST"
            else:               value = "MO"

    # ------- ESQUEMA 1 (POR DEFECTO) ------------
    else:

        # coordenadas
        Cvol=1,1;            Chea=1,12;
        Cbas=2,1;         Ctre=2,10;
        Cinp=3,1;
        Clni=4,1; # loudness_level_info de server_process

        # etiquetas para el value:
        Lvol="Vol: ";     Lhea="HR: "
        Lbas="Bass: ";   Ltre="Treb: ";
        Linp="Input: ";
        Llni="Loud: "

        # nota: este esquema no requiere transformaciones

    # Lanzamiento de los comandos para mostrar los widgets.
    # Recordatorio: los widgets DEBEN ESTAR DECLARADOS en _configure_main_screen()
    if type == 'level':
        LCD.send('widget_set scr_1 level       ' + posi(Cvol) + ' "' + Lvol + value + '"')
    elif type == 'headroom':
        LCD.send('widget_set scr_1 headroom    ' + posi(Chea) + ' "' + Lhea + value + '"')
    elif type == 'balance':
        LCD.send('widget_set scr_1 balance     ' + posi(Cbal) + ' "' + Lbal + value + '"')

    elif type == 'bass':
        LCD.send('widget_set scr_1 bass        ' + posi(Cbas) + ' "' + Lbas + value + '"')
    elif type == 'treble':
        LCD.send('widget_set scr_1 treble      ' + posi(Ctre) + ' "' + Ltre + value + '"')
    elif type == 'syseq':
        LCD.send('widget_set scr_1 syseq       ' + posi(Cseq) + ' "' + Lseq + value + '"')
    elif type == 'drc':
        LCD.send('widget_set scr_1 drc         ' + posi(Cdrc) + ' "' + Ldrc + value + '"')
    elif type == 'peq':
        LCD.send('widget_set scr_1 peq         ' + posi(Cpeq) + ' "' + Lpeq + value + '"')

    elif type == 'input':
        LCD.send('widget_set scr_1 input       ' + posi(Cinp) + ' "' + Linp + value + '"')
    elif type == 'loud':
        LCD.send('widget_set scr_1 loud        ' + posi(Clns) + ' "' + Llns + value + '"')
    elif type == 'mono':
        LCD.send('widget_set scr_1 mono        ' + posi(Cmon) + ' "' + Lmon + value + '"')

    elif type == 'loudinfo':
        LCD.send('widget_set scr_1 loudinfo    ' + posi(Clni) + ' "' + Llni + value + '"')

    elif type == 'preset':
        LCD.send('widget_set scr_1 preset      ' + posi(Cpre) + ' "' + Lpre + value + '"')
    elif type == 'ftype':
        LCD.send('widget_set scr_1 ftype       ' + posi(Cfty) + ' "' + Lfty + value + '"')

    elif type == 'info' and lcdConfig['lcd_info_timeout'] > 0:
        show_screen_Info(value)

    elif type == 'test':
        LCD.send('widget_set scr_1 volume 1 1 "   Test LCD FIRtro"')

def show_screen_Info( value, to=lcdConfig['info_timeout'] ):
    # Creamos una SCREEN ADICIONAL con informacion efímera (timeout)
    string = LCD.send('screen_add scr_info')
    to = 8 * to # se debe indicar en 1/8sec al server
    LCD.send('screen_set scr_info -cursor no -priority foreground -timeout ' + str(to))
    if string[:4] != 'huh?': # huh? en el lenguaje lcdproc significa ¿comooooor?
        # La pantalla no existe, creamos los widgets
        LCD.send('widget_add scr_info info_tit title')
        LCD.send('widget_add scr_info info_txt2 string')
        LCD.send('widget_add scr_info info_txt3 string')
        LCD.send('widget_add scr_info info_txt4 string')
    LCD.send('widget_set scr_info info_tit "FIRtro info"')
    line = 2
    for data in split_by_n(value,20):
        LCD.send('widget_set scr_info info_txt' + str(line) + ' 1 ' + str(line) + ' "' + data + '"')
        line = line + 1
        if line == 5:
            break

def show_status(data, priority="info"):

    # permite redefinir la prioridad 'info' con la que se creó 
    # la pantalla principal de este módulo - ESTO NO LO ENTIENDO :-/
    _configure_main_screen()

    # Visualizamos de los datos recibidos los que deseemos presentar en el LCD
    # NOTA: Los widgets a visualizar DEBEN ESTAR DECLARADOS 'widget_add'
    #       en _configure_main_screen(), de tipo 'string'.
    #show_widget('preset',      data['preset'])
    #show_widget('ftype',       data['filter_type'])
    show_widget('input',       data['input'])
    show_widget('level',       str(data['level']))
    show_widget('bass',        str(int(data['bass'])))
    show_widget('treble',      str(int(data['treble'])))
    show_widget('balance',     str(int(data['balance'])).rjust(2))
    #show_widget('headroom',    str(data['headroom']))
    show_widget('drc',         data['DRC_set'])
    #show_widget('loud',        str(data['loudness_track']))
    show_widget('mono',        data['mono'])
    #show_widget('syseq',       str(data['system_eq']))

    # caso especial tener en cuenta si peq está defeated
    #if not data['peqdefeat']:
    #    show_widget('peq',         data['peq'])
    #else:
    #    show_widget('peq',         "off")

    # caso especial loudness_level_info manipulado si loudness_track=False
    if data['loudness_track']:
        show_widget('loudinfo',    str(data['loudness_ref']))
    else:
        show_widget('loudinfo',    "off")

    ## Mostramos warnings o el comando recibido excepto si es 'status'
    #if len(data['warnings']) > 0:
    #    show_widget('info', data['warnings'][0])
    #elif data['order'] != 'status':
    #    show_widget('info', data['order'])

def _configure_main_screen():
    # definimos la SCREEN principal de este módulo
    LCD.send('screen_add scr_1')
    # WIDGETS utilizables en la screen principal de este modulo
    LCD.send('widget_add scr_1 level       string')
    #LCD.send('widget_add scr_1 headroom    string')
    LCD.send('widget_add scr_1 balance     string')
    LCD.send('widget_add scr_1 bass        string')
    LCD.send('widget_add scr_1 treble      string')
    LCD.send('widget_add scr_1 loud        string')
    #LCD.send('widget_add scr_1 loudinfo    string')
    LCD.send('widget_add scr_1 input       string')
    LCD.send('widget_add scr_1 preset      string')
    LCD.send('widget_add scr_1 mono        string')
    LCD.send('widget_add scr_1 ftype       string')
    LCD.send('widget_add scr_1 syseq       string')
    LCD.send('widget_add scr_1 drc         string')
    LCD.send('widget_add scr_1 peq         string')

def interactive_test_lcd():
    lcd_size = open('FIRtro')
    print ('llll', lcd_size)
    if lcd_size == -1:
        return -1
    print( '=> LCD ' + str(lcd_size[0])+' x ' +str(lcd_size[1]) )
    show_widget ('test', '')
    while True:
        string = raw_input('Mensaje emergente (quit para salir): ')
        if string == 'quit':
            break
        show_widget('info', string)
    cLCD.close()

def ver_tipos_json(data): # solo para debug
    for cosa in data:
        print ( ">"*5, cosa.ljust(12), type(data[cosa]), data[cosa] )

class changed_files_handler(FileSystemEventHandler):
    """
        This is a handler that will do something when some file has changed
    """

    def on_modified(self, event):

        path = event.src_path
        
        if 'state.yml' in path:
            with open(path, 'r') as f:
                dicci = f.read()
                dicci = yaml.load(dicci)
                show_status( dicci )
        
        if '.librespot_events' in path:
            sleep(.1)
            meta = players.get_librespot_meta()

if __name__ == "__main__":

    # Registers a client under the system's LCDd server
    LCD = client_lcd.Client('pre.di.c', host='localhost', port=13666)
    if LCD.connect():
        LCD.register()
        print ( LCD.query('hello') )
        print ( LCD.get_size() )
    else:
        print( 'Error registering pre.di.c on LCDd' )
        sys.exit()

    #######################################################
    # Starts a WATCHDOG to see pre.di.c files changes,
    # and handle these changes to update the LCD display
    #   https://stackoverflow.com/questions/18599339/
    #   python-watchdog-monitoring-file-for-changes
    observer = Observer()
    observer.schedule(event_handler=changed_files_handler(), path=WATCHED_DIR, recursive=True)
    observer.start()
    observer.join()
    #######################################################
