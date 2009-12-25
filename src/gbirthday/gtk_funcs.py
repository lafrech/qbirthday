'''Collection of gtk functions'''
import gtk

def show_error_msg(message, title=None, parent=None):
    '''show an error error message as MessageDialog'''
    if (not title):
        title = 'Error'
    errmsg = gtk.MessageDialog(parent, type=gtk.MESSAGE_ERROR,
        buttons=gtk.BUTTONS_OK, flags=gtk.DIALOG_MODAL,
        message_format=message)
    errmsg.set_title(title)
    errmsg.run()
    errmsg.destroy()
