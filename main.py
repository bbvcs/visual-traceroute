import sys
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QLineEdit, QLabel

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import random

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

import ip_helper

class Window(QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        #self.showFullScreen()

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)



        # draw map
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()
        ax.stock_img()
        self.canvas.draw()

        # coords enter
        self.lat_text = QLabel("Latitude")
        self.lon_text = QLabel("Longitude")
        self.longitude = QLineEdit()
        self.latitude = QLineEdit()
        self.button = QPushButton('plot coords')
        self.button.clicked.connect(self.plot)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        layout.addWidget(self.lon_text)
        layout.addWidget(self.longitude)

        layout.addWidget(self.lat_text)
        layout.addWidget(self.latitude)

        layout.addWidget(self.button)
        self.setLayout(layout)

    def plot(self):

        try:
            plt.plot(int(self.longitude.text()), int(self.latitude.text()), color='red', marker = 'o', transform = ccrs.PlateCarree())
        except:
            print("invalid coords")
        self.canvas.draw()



if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())

"""import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
import cartopy.crs as ccrs
import matplotlib.pyplot as plt


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["a", "b", "c", "d"]

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("hello wold")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()
        ax.stock_img()

        plt.plot(-27, 4, color='red', marker = 'o')

        
        # Save the plot by calling plt.savefig() BEFORE plt.show()
        #plt.savefig('coastlines.pdf')
        #plt.savefig('coastlines.png')#

        plt.show()

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec()) """

