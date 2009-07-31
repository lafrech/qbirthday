#!/usr/bin/env python
'''GBirthday

Just a KBirthday clone for Gnome environment and working with evolution data server.
'''
### Original source from:
## pygtk-demo Status Icon: Nikos Kouremenos
## EvoBdayReminder.py: Axel Heim. http://www.axelheim.de/

import gtk
import bsddb, os, re
import datetime
from datetime import date
import time

addressBookLocation = os.path.join(os.environ['HOME'], '.evolution/addressbook/local/system/')
imageslocation = "/usr/local/gbirthday/"
cumpleshoy = False

class AddressBook:
    def __init__(self, book=None):

	cumplelista=[]
        location = addressBookLocation
        for name in book or []:
            location = os.path.join(location, 'subfolders', name)
        location = os.path.join(location, 'addressbook.db')
	addressbook=location
	print 'Recargando.....'
        self.contacts = []
        self.bdays = {}
        file = bsddb.hashopen(addressbook)
        for key in file.keys():
            data = file[key]
            if not data.startswith('BEGIN:VCARD'):
                continue
            self.contacts.append(Contact(data,self.bdays))

    def manageBdays(self):

        now = date.today()
        bdayKeys = self.bdays.keys()
        cumplelista = []
	temporal = []

        global D
        global T
        
        for d in range(-2,D+1):
            sDate = now + datetime.timedelta(d)

            for k in range(len(self.bdays)):
                sDateDay = str(sDate.day)

                if len(sDateDay) != 2: sDateDay = '0' + sDateDay
                sDateMonth = str(sDate.month)
                if len(sDateMonth) != 2: sDateMonth = '0' + sDateMonth

                if bdayKeys[k].find('-'+sDateMonth+'-'+sDateDay) != -1:
                    if d == 0:
                        print 'Ohoh! Birthday today!!!'
                        print ' '
			cumpleshoy = True
			icono = 'birthdaytoday.png'
   		    elif d < 0:
			icono = 'birthdaylost.png'
		    else:
			icono = 'birthdaynext.png'

                    bday = bdayKeys[k]
                    name = self.bdays[bdayKeys[k]]
		    ano, mes, dia = bday.split('-', 2)
		    ano = sDate.year - int(ano)

		    temporal = [icono, bday, name, str(d), d, sDate.month, sDate.day, ano]
		    #cumplelista.append(bday + ': ' + name + ' -->  ' + str(d) + ' days')
		    cumplelista.append(temporal)
        return cumplelista

    def checktoday(self):

        now = date.today()
        bdayKeys = self.bdays.keys()
	cumpleshoy = False

        global D
        global T
        
        for d in range(0,1):
            sDate = now + datetime.timedelta(d)

            for k in range(len(self.bdays)):
                sDateDay = str(sDate.day)
                if len(sDateDay) != 2: 
			sDateDay = '0' + sDateDay
                sDateMonth = str(sDate.month)
                if len(sDateMonth) != 2: 
			sDateMonth = '0' + sDateMonth

                if bdayKeys[k].find('-'+sDateMonth+'-'+sDateDay) != -1:
                    if d == 0:
                        print 'Checktoday'
			cumpleshoy = True
	return cumpleshoy
 
class Contact:

    _splitRE = re.compile(r'\r?\n')

    _ignoreFields = ['BEGIN', 'VERSION', 'END', 'UID']

    def __init__(self, data, bdays):
        lines = self._splitRE.split(data)
        mostRecentName = ''
	mostRecentDate = ''
        for line in lines:
 
            if not line.strip() or line == '\x00':
                continue
            if startswithany(line, self._ignoreFields):
                continue
            if line.find(':') == -1: continue
            label, value = line.split(':', 1)
            if label == 'X-EVOLUTION-FILE-AS': 
		mostRecentName = value
            if label == 'BDAY':
                mostRecentDate = value
	    if (mostRecentName != '') & (mostRecentDate != ''):
                bdays[mostRecentDate] = mostRecentName		
		mostRecentName = ''
                mostRecentDate = ''

def startswithany(s, patList):
    for pat in patList:
        if s.startswith(pat):
            return True
    return False

def make_menu(event_button, event_time, icon):
    menu = gtk.Menu()
    cerrar = gtk.Image()
    cerrar.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU,)
    recargar = gtk.ImageMenuItem('Reload')
    recarga_img = gtk.Image()
    recarga_img.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_MENU,)
    recargar.set_image(recarga_img)
    recargar.show()
    recargar.connect_object("activate", recargar_gbirthday, "reload")
    menu.append(recargar)
    blink_menu = gtk.ImageMenuItem('Stop blinking')
    blink_img = gtk.Image()
    blink_img.set_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_MENU,)
    blink_menu.set_image(blink_img)
    blink_menu.show()
    blink_menu.connect_object("activate", stop_blinking, "reload")
    menu.append(blink_menu)
    salir = gtk.ImageMenuItem('Quit')
    salir.set_image(cerrar)
    salir.show()
    salir.connect_object("activate", cerrar_gbirthday, "file.quit")
    menu.append(salir)
    menu.popup(None, None,
        gtk.status_icon_position_menu, event_button,
        event_time, icon)

def on_right_click(icon, event_button, event_time):
    print "Boton Derecho"
    make_menu(event_button, event_time, icon)
    
def on_left_click(icon, event_button, event_time):
        # Create a new window
	global showbd 
	showbd = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # Set the window title
        showbd.set_decorated(False)
	showbd.set_position(gtk.WIN_POS_MOUSE)

        # Set a handler for delete_event that immediately
        # exits GTK.
        #showbd.connect("delete_event", self.delete_event)

        # Sets the border width of the window.
        showbd.set_border_width(5)

    	lista=AddressBook.manageBdays(AB)
    	listaiconos = []

        # Create a 2x2 table
	event_box = gtk.EventBox()
	showbd.add(event_box)
	event_box.show()
        table = gtk.Table(7, 6, False)
        event_box.add(table)
	table.set_col_spacings(10)
	monthtext = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	fila = 0
	if len(lista) > 0:
		event_box = gtk.EventBox()
		table.attach(event_box, 0, 6, 0, 1)
		event_box.show()
		label = gtk.Label("GBirthday")
		label.set_markup('<b>Birthdays</b>')
		label.set_justify(gtk.JUSTIFY_RIGHT)
        	event_box.add(label)
        	label.show()
		event_box.modify_bg(gtk.STATE_NORMAL, event_box.get_colormap().alloc_color("grey"))
		fila = fila +1
        # Create second button
	for cumple in lista:
		image = gtk.Image()
		image.set_from_file(imageslocation + cumple[0])
        	table.attach(image, 0, 1, fila, fila+1)
        	image.show()

		if cumple[4] == 0:
			label = gtk.Label("<b>" + monthtext[cumple[5] - 1] + "</b>")
			label.set_markup("<b>" + monthtext[cumple[5] - 1] + "</b>")
		elif cumple[4] < 0:
			label = gtk.Label(monthtext[cumple[5] - 1])
			label.set_markup("<span foreground='grey'>" + monthtext[cumple[5] - 1] + "</span>")
		else:
			label = gtk.Label(monthtext[cumple[5] - 1])
		align = gtk.Alignment(0.0, 0.5, 0, 0)
		align.add(label)
		align.show()
        	table.attach(align, 1, 2, fila, fila+1)
        	label.show()

		if cumple[4] == 0:
			label = gtk.Label("<b>" + str(cumple[6]) + "</b>")
			label.set_markup("<b>" + str(cumple[6]) + "</b>")
		elif cumple[4] < 0:
			label = gtk.Label(str(cumple[6]))
			label.set_markup("<span foreground='grey'>" + str(cumple[6]) + "</span>")
		else:
			label = gtk.Label(str(cumple[6]))
		align = gtk.Alignment(1.0, 0.5, 0, 0)
		align.add(label)
		align.show()
        	table.attach(align, 2, 3, fila, fila+1)
        	label.show()

		if cumple[4] == 0:
			label = gtk.Label("<b>" + cumple[2] + "</b>")
			label.set_markup("<b>" + cumple[2] + "</b>")
		elif cumple[4] < 0:
			label = gtk.Label(cumple[2])
			label.set_markup("<span foreground='grey'>" + cumple[2] + "</span>")
		else:
			label = gtk.Label(cumple[2])
		align = gtk.Alignment(0.0, 0.5, 0, 0)
		align.add(label)
        	table.attach(align, 3, 4, fila, fila+1)
		align.show()
        	label.show()

		if cumple[4] == 0:
			label = gtk.Label("Today")
			label.set_markup("<b>Today</b>")
		elif cumple[4] == -1:
			label = gtk.Label("Yesterday")
			label.set_markup("<span foreground='grey'>Yesterday</span>")
		elif cumple[4] < -1:
			label = gtk.Label(cumple[3] + " Days ago")
			label.set_markup("<span foreground='grey'>" + cumple[3] + " Days ago</span>")
		elif cumple[4] == 1:
			label = gtk.Label("Tomorrow")
		else:
			label = gtk.Label(cumple[3] + " Days")
		align = gtk.Alignment(0.0, 0.5, 0, 0)
		align.add(label)
		align.show()
     	  	table.attach(align, 4, 5, fila, fila+1)
        	label.show()

		if cumple[4] == 0:
			label = gtk.Label("<b>" + str(cumple[7]) + " Years</b>")
			label.set_markup("<b>" + str(cumple[7]) + " Years</b>")
		elif cumple[4] < 0:
			label = gtk.Label(str(cumple[7]) + " Years")
			label.set_markup("<span foreground='grey'>" + str(cumple[7]) + " Years</span>")
		else:
			label = gtk.Label(str(cumple[7]) + " Years")
		align = gtk.Alignment(1.0, 0.5, 0, 0)
		align.add(label)
		align.show()
        	table.attach(align, 5, 6, fila, fila+1)
        	label.show()
		fila = fila +1

        table.show()
        showbd.show()
	showbd.connect('focus_out_event', closebdwindow,"texto")

def closebdwindow(uno, dos, textocw):
    print "pierde foco"
    showbd.destroy()

def cerrar_gbirthday(texto):
    print "Cierre de la aplicacion"
    gtk.main_quit()

def recargar_gbirthday(texto):
    global AB
    print 'pulsado reload'
    AB = AddressBook(0)
    icon.set_blinking(AddressBook.checktoday(AB))

def stop_blinking(texto):
    global icon
    print 'pulsado stop blinking'
    icon.set_blinking(False)
    
def StatusIcon(parent=None):
    global icon
    icon = gtk.status_icon_new_from_file(imageslocation + 'birthday.png')
    icon.set_blinking(AddressBook.checktoday(AB))
    icon.connect('popup-menu', on_right_click)
    icon.connect('activate', on_left_click, 20, 20)

if __name__ == '__main__':
    global D
    global T
    global AB
    global icon
    global icono
    
    # enter the number of days for which Bday warnings shall be given
    D = 30
    # enter the number of seconds for which the script shall sleep after execution
    T = 5
    AB = AddressBook(0)
    icono = StatusIcon()
    gtk.main()
