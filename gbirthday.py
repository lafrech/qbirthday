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
import subprocess
import gobject


addressBookLocation = os.path.join(os.environ['HOME'], '.evolution/addressbook/local/system/')
imageslocation = "/usr/share/gbirthday/"
cumpleshoy = False

class AddressBook:
    def __init__(self, book=None):

	cumplelista=[]
        location = addressBookLocation
        for name in book or []:
            location = os.path.join(location, 'subfolders', name)
        location = os.path.join(location, 'addressbook.db')
	addressbook=location
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

        global firstday
        global lastday
        
        for d in range(firstday,lastday+1):
            sDate = now + datetime.timedelta(d)

            for k in range(len(self.bdays)):
                sDateDay = str(sDate.day)

                if len(sDateDay) != 2: sDateDay = '0' + sDateDay
                sDateMonth = str(sDate.month)
                if len(sDateMonth) != 2: sDateMonth = '0' + sDateMonth

                if bdayKeys[k].find('-'+sDateMonth+'-'+sDateDay) != -1:
                    if d == 0:
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
		mostRecentName = mostRecentName.replace("\,",",")
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
    blink_img.set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_MENU,)
    blink_menu.set_image(blink_img)
    blink_menu.show()
    blink_menu.connect_object("activate", stop_blinking, "stop blinking")
    menu.append(blink_menu)

    preferences_menu = gtk.ImageMenuItem('Preferences')
    preferences_img = gtk.Image()
    preferences_img.set_from_stock(gtk.STOCK_PREFERENCES, gtk.ICON_SIZE_MENU,)
    preferences_menu.set_image(preferences_img)
    preferences_menu.show()
    preferences_menu.connect_object("activate", preferences_window, "about")
    menu.append(preferences_menu)

    about_menu = gtk.ImageMenuItem('About')
    about_img = gtk.Image()
    about_img.set_from_stock(gtk.STOCK_ABOUT, gtk.ICON_SIZE_MENU,)
    about_menu.set_image(about_img)
    about_menu.show()
    about_menu.connect_object("activate", create_dialog, None)
    menu.append(about_menu)

    salir = gtk.ImageMenuItem('Quit')
    salir.set_image(cerrar)
    salir.show()
    salir.connect_object("activate", cerrar_gbirthday, "file.quit")
    menu.append(salir)
    menu.popup(None, None,
        gtk.status_icon_position_menu, event_button,
        event_time, icon)

def on_right_click(icon, event_button, event_time):
    make_menu(event_button, event_time, icon)
    
def on_left_click(icon, event_button, event_time):
	global showbdcheck
	if showbdcheck == 0:
		showbdcheck = 1
		openwindow()
	else:
		closebdwindow('focus_out_event', closebdwindow, "")

def openwindow():
        # Create a new window
	global showbd 
	global showbdcheck
	showbd = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # Set the window title
        showbd.set_decorated(False)
	showbd.set_position(gtk.WIN_POS_MOUSE)
	showbd.set_icon_from_file(imageslocation + 'birthday.png')

        # Set a handler for delete_event that immediately
        # exits GTK.
        #showbd.connect("delete_event", self.delete_event)

        # Sets the border width of the window.
        showbd.set_border_width(0)

    	lista=AddressBook.manageBdays(AB)
    	listaiconos = []

	box = gtk.HBox()
	box.set_border_width(5)
	box.show()
	frame = gtk.Frame(None)
	showbd.add(frame)
	table = gtk.Table(7, 6, False)
	box.pack_start(table, False , False, 0)
	frame.add(box)
	table.set_col_spacings(10)
	monthtext = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	fila = 0
	event_box = gtk.EventBox()
	table.attach(event_box, 0, 6, 0, 1)
	event_box.show()
	label = gtk.Label("GBirthday")
	if len(lista) > 0:
		label.set_markup('<b>Birthdays</b>')
	else:
		label.set_markup('<b>\n    No birthdays within selected range    \n</b>')
	label.set_justify(gtk.JUSTIFY_RIGHT)
	event_box.add(label)
	label.show()
	style = label.get_style()
	#event_box.modify_bg(gtk.STATE_NORMAL, event_box.get_colormap().alloc_color("grey"))
	event_box.modify_bg(gtk.STATE_NORMAL, style.bg[gtk.STATE_NORMAL])
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
			label = gtk.Label(str(cumple[4] * -1) + " Days ago")
			label.set_markup("<span foreground='grey'>" + str(cumple[4] * -1) + " Days ago</span>")
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
	frame.show()
        showbd.show()
	showbd.connect('focus_out_event', closebdwindow,"texto")

def closebdwindow(uno, dos, textocw):
    global showbdcheck
    showbdcheck = 0
    showbd.destroy()


def on_url(d, link, data):
        subprocess.Popen(["firefox", "http://dernalis.googlepages.com/gbirthday.html"])

gtk.about_dialog_set_url_hook(on_url, None)

def create_dialog(uno):
	global dlg
	dlg = gtk.AboutDialog()
	dlg.set_version("0.3.4")
	dlg.set_comments("Birthday reminder for Evolution Contacts")
	dlg.set_name("GBirthday")
	image = gtk.gdk.pixbuf_new_from_file(imageslocation + 'gbirthday.png')
	dlg.set_logo(image)
	dlg.set_icon_from_file(imageslocation + 'birthday.png')
	dlg.set_copyright(u"Copyright \u00A9 2007 Alex Mallo")
	dlg.set_license(" Licensed under the GNU General Public License Version 2\n\n Power Manager is free software; you can redistribute it and\/or\nmodify it under the terms of the GNU General Public License\nas published by the Free Software Foundation; either version 2\nof the License, or (at your option) any later version.\n\n Power Manager is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU General Public License for more details.\n\n You should have received a copy of the GNU General Public License\nalong with this program; if not, write to the Free Software\nFoundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA\n02110-1301, USA.")
	dlg.set_authors(["Alex Mallo <dernalis@gmail.com>","Internatinalization:", "Robert Widburger <robert@wildburguer.com>"])
	dlg.set_artists(["Alex Mallo <dernalis@gmail.com>"])
	dlg.set_translator_credits("English: Robert Widburger <robert@wildburguer.com>\nGerman: Robert Widburger <robert@wildburguer.com>")
	dlg.set_website("http://dernalis.googlepages.com/gbirthday.html")
	def close(w, res):
		if res == gtk.RESPONSE_CANCEL:
			w.hide()
	dlg.connect("response", close)
	dlg.run()
	
def preferences_window(textocw):
	global imageslocation
	global preferences
	preferences = gtk.Window(gtk.WINDOW_TOPLEVEL)
        # Set the window title
        preferences.set_decorated(True)
	preferences.set_position(gtk.WIN_POS_CENTER)
	preferences.set_title("Preferences")
	preferences.set_icon_from_file(imageslocation + 'birthday.png')

	box = gtk.VBox(False, 0)
	preferences.add(box)
	
	table = gtk.Table(2, 2, True)
	table.set_col_spacings(10)
	table.set_row_spacings(10)

	label= gtk.Label("Past birthdays")
	table.attach(label, 0, 1, 0, 1)
	label.show()

	label= gtk.Label("Next birthdays")
	table.attach(label, 0, 1, 1, 2)
	label.show()
	
	past = gtk.Adjustment(firstday, lower=-30, upper=0, step_incr=-1, page_incr=0, page_size=0)
	spin = gtk.SpinButton(past, climb_rate=0.0, digits=0)
	spin.connect("value-changed", cambiar_preferencias,"firstday", spin)
	table.attach(spin,1, 2, 0, 1)
	spin.show()

	next = gtk.Adjustment(lastday, lower=0, upper=90, step_incr=1, page_incr=0, page_size=0)
	spin = gtk.SpinButton(next, climb_rate=0.0, digits=0)
	spin.connect("value-changed", cambiar_preferencias,"lastday", spin)
	table.attach(spin,1, 2, 1, 2)
	spin.show()

	box.pack_start(table, False , False, 8)
	table.show()

	button = gtk.Button("Save & Close")
	box.pack_start(button, False , False, 2)
	button.connect("clicked", cerrar_preferences, None)
	button.show()
	box.show()
        # Sets the border width of the window.
	preferences.set_border_width(5)
	preferences.show()

def cambiar_preferencias(uno, opcion, spin):
	global firstday
	global lastday
	spin.update()
	if opcion == "firstday": firstday = spin.get_value_as_int()
	elif opcion == "lastday": lastday = spin.get_value_as_int()
	else: print "Valor no indicado"

def cerrar_gbirthday(texto):
	if dlg != None:
		dlg.destroy()
	gtk.main_quit()

def cerrar_about(uno,texto):
    about.destroy()

def cerrar_preferences(uno,texto):
	global firstday
	global lastday
	f = open(os.environ['HOME']+"/.gbirthday.conf",'w')
	f.write("firstday="+str(firstday) + "\n")
	f.write("lastday="+str(lastday) + "\n")
	f.close()
	preferences.destroy()

def recargar_gbirthday(texto):
    global AB
    AB = AddressBook(0)
    icon.set_blinking(AddressBook.checktoday(AB))

def stop_blinking(texto):
	global icon
	icon.set_blinking(False)
    
def StatusIcon(parent=None):
    global icon
    icon = gtk.status_icon_new_from_file(imageslocation + 'birthday.png')
    icon.set_blinking(AddressBook.checktoday(AB))
    icon.connect('popup-menu', on_right_click)
    icon.connect('activate', on_left_click, 20, 20)
def check_new_day():
	global dia
	fecha = time.asctime(time.localtime(time.time()))
	sem, mes, nada, diahoy, hora = fecha.split(" ",5)
	if dia != diahoy:
		icon.set_blinking(AddressBook.checktoday(AB))
		dia = diahoy
	return True

if __name__ == '__main__':
    global firstday
    global lastday
    global AB
    global icon
    global icono
    global showbdcheck
    global dlg
    global dia
    dlg= None
    showbdcheck = 0
    try:
    	f = open(os.environ['HOME']+"/.gbirthday.conf",'r')
    except IOError:
		f = open(os.environ['HOME']+"/.gbirthday.conf",'w')
		firstday = -2
		lastday = 30
		f.write("firstday="+str(firstday) + "\n")
		f.write("lastday="+str(lastday) + "\n")
		f.close()
		print "Created configuration file."
    else:
    	for line in f:
			line = line.replace("\n","")
			label, value = line.split('=', 1)
			if label == "firstday": firstday = int(value)
			elif label == "lastday": lastday = int(value)
			else: print "Unhandled vale in gbirthday.conf: " + line
    	f.close()
#    print time.asctime(time.localtime(time.time()))
    AB = AddressBook(0)
    icono = StatusIcon()
    fecha = time.asctime(time.localtime(time.time()))
    sem, mes, nada, dia, hora = fecha.split(" ",5)
#    h, dia, seg = hora.split(":",2)
    gobject.timeout_add(60000, check_new_day)
    gtk.main()
