"""Main window"""

import datetime

from PyQt5 import QtCore, QtGui, QtWidgets, uic

from .birthday_list import BirthdayList
from .statusicon import StatusIcon
from .settings import Settings
from .paths import PICS_PATHS, UI_FILES_DIR


class MainWindow(QtWidgets.QMainWindow):
    """Main window"""

    def __init__(self):

        super().__init__()

        self.setWindowFlags(
            QtCore.Qt.Tool
            | QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
        )  # ??

        uic.loadUi(str(UI_FILES_DIR / "mainwindow.ui"), self)

        self.settings = Settings()
        self.bday_list = BirthdayList(self, self.settings)
        self.status_icon = StatusIcon(self, self.settings)

        # Initialise current day
        self.current_day = datetime.datetime.now().strftime("%d")

        # Check every 60 seconds for new day
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_new_day)
        self.timer.start(60 * 1000)

        self.reload()

        # TODO: Catch mouse focus out and close window

    def showEvent(self, event):
        """Callback for "show" event"""

        super().showEvent(event)

        # Window shall appear under system tray icon
        systray_icon_pos = self.status_icon.geometry().center()
        self.move(systray_icon_pos.x() - self.width() / 2, systray_icon_pos.y())

        # Ensure the window is not minimized on virtual desktop change
        self.showNormal()

    def reload(self):
        """Reload birthdays and update GUI accordingly"""

        # Reload birthdays
        self.bday_list.reload()

        # Reload status icon
        self.status_icon.reload_set_icon()

        # Set title
        if self.bday_list.bdays_in_period():
            self.titleLabel.setText(self.tr("Birthdays"))
        else:
            self.titleLabel.setText(self.tr("No birthdays in specified period"))

        # Empty birthday list
        # http://stackoverflow.com/questions/4528347/
        for i in reversed(range(self.birthdaysLayout.count())):
            widget = self.birthdaysLayout.itemAt(i).widget()
            self.birthdaysLayout.removeWidget(widget)
            widget.setParent(None)

        # Add birthdays
        firstday = self.settings.value("firstday", type=int)
        lastday = self.settings.value("lastday", type=int)
        for delta_day in range(firstday, lastday + 1):
            for birthdate, name in self.bday_list.check_day(delta_day):
                row = self.birthdaysLayout.rowCount()
                for col, label in enumerate(
                    self.make_birthday_line(delta_day, name, birthdate)
                ):
                    self.birthdaysLayout.addWidget(label, row, col)

    def check_new_day(self):
        """Check for new day

        Should be called e.g. every 60 seconds to check if day has changed.
        """
        new_day = datetime.datetime.now().strftime("%d")
        if self.current_day != new_day:
            self.current_day = new_day
            self.reload()

    def make_birthday_line(self, delta_day, name, birthdate):
        """Return a row as a list of widgets

        deltaday (int): day index in specified period
        name (str): person name
        birthdate (dt.date): date of birth
        """
        label_image = QtWidgets.QLabel()
        # TODO: use Qt to localize day + month
        label_day = QtWidgets.QLabel(str(birthdate.day))
        label_month = QtWidgets.QLabel(birthdate.strftime("%B"))
        label_name = QtWidgets.QLabel(name)
        label_when = QtWidgets.QLabel()
        label_age = QtWidgets.QLabel(
            self.tr("{} years old").format(datetime.date.today().year - birthdate.year)
        )

        label_day.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        label_when.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        label_age.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        labels = [
            label_image,
            label_day,
            label_month,
            label_name,
            label_when,
            label_age,
        ]

        # Birthday today
        if delta_day == 0:
            label_image.setPixmap(QtGui.QPixmap(PICS_PATHS["birthdaytoday"]))
            label_when.setText(self.tr("Today"))
            for label in labels:
                label.setStyleSheet("QLabel { font: bold; }")
        # Birthday in the past
        elif delta_day < 0:
            label_image.setPixmap(QtGui.QPixmap(PICS_PATHS["birthdaylost"]))
            if delta_day == -1:
                label_when.setText(self.tr("Yesterday"))
            else:
                label_when.setText(self.tr("{} days ago").format(-delta_day))
            for label in labels:
                label.setStyleSheet("QLabel { color : grey; }")
        # Birthday in the future
        else:
            label_image.setPixmap(QtGui.QPixmap(PICS_PATHS["birthdaynext"]))
            if delta_day == 1:
                label_when.setText(self.tr("Tomorrow"))
            else:
                label_when.setText(self.tr("{} days").format(delta_day))

        return labels

    def show_error_message(self, msg):
        """Display an error message in a dialog box"""
        QtWidgets.QMessageBox.warning(
            self,
            QtCore.QCoreApplication.applicationName(),
            msg,
            QtWidgets.QMessageBox.Close,
        )
