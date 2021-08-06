import sys
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QLineEdit, QLabel

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import random

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

from node_utils import MissingInfoTypes
from ip_utils import get_traceroute_node_list


def coords_provided(latitude, longitude):
    return (longitude != MissingInfoTypes.NOT_DISCLOSED and longitude != MissingInfoTypes.NOT_PROVIDED) \
                and (latitude != MissingInfoTypes.NOT_DISCLOSED and latitude != MissingInfoTypes.NOT_PROVIDED)

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
        self.ax = plt.axes(projection=ccrs.PlateCarree())
        self.ax.coastlines()
        self.ax.stock_img()
        self.canvas.draw()


        # coords enter
        self.addr_text = QLabel("Enter a web address ...")
        self.addr_entry = QLineEdit()
        self.button = QPushButton('Perform Traceroute')
        self.button.clicked.connect(self.plot)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        layout.addWidget(self.addr_text)
        layout.addWidget(self.addr_entry)

        layout.addWidget(self.button)
        self.setLayout(layout)


    def plot(self):

        plt.cla()
        self.ax = plt.axes(projection=ccrs.PlateCarree())
        self.ax.coastlines()
        self.ax.stock_img()

        """
        try:
            plt.plot(int(self.longitude.text()), int(self.latitude.text()), color='red', marker = 'o', transform = ccrs.PlateCarree())
        except:
            print("invalid coords")"""

        node_list = get_traceroute_node_list(self.addr_entry.text())

        i = last_valid = 0
        for node in node_list:
            print(repr(node))

            if coords_provided(node.get_latitude(), node.get_longitude()):

                longitude  = round(float(node.get_longitude()), 2) # round to 2dp required by plt plot/text methods
                latitude = round(float(node.get_latitude()),  2)
                tag = "({}): {}".format(i, node.city)

                plt.plot(longitude, latitude, color='red', marker='o', transform=ccrs.PlateCarree())

                if i > 1: # error lies in here i reckon

                    last_valid_node = node_list[last_valid]
                    print("i={}, last_valid={}, last_valid_node={}".format(i, last_valid, last_valid_node.ip))
                    prev_latitude  = round(float(last_valid_node.get_latitude()),  2)
                    prev_longitude = round(float(last_valid_node.get_longitude()), 2)
                    plt.plot([longitude, prev_longitude], [latitude, prev_latitude], color='blue', linewidth=2, transform=ccrs.PlateCarree())

                plt.text(longitude, latitude, tag, horizontalalignment = 'right', transform = ccrs.Geodetic())
                self.canvas.draw()
                last_valid = i

            i = i + 1



        #for node in node_list:


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
