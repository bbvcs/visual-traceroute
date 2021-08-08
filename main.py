import sys
from enum import Enum, auto

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit, \
    QLabel, QGridLayout, QWidget, QAbstractItemView, QListWidgetItem, QCheckBox, QComboBox
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import random

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

from node_utils import val_known
from ip_utils import get_traceroute_node_list


class TracerouteMethods(Enum):
    DEFAULT = 0
    ICMP = 1
    UDP = 2
    TCP = 3
    DCCP = 4


class FlowNodeInfoBox(QListWidgetItem):

    def __init__(self, node, pos):
        super().__init__()
        self.layout = QVBoxLayout()

        # Should be Impossible to get no coords, IP, rtt
        # self.private    = "Private" if node.private else "Public"
        self.ip = node.ip if val_known(node.ip) else "(IP Not Provided)"
        self.org = node.org if val_known(node.org) else "(Org Not Provided)"
        self.hostname = node.hostname if val_known(node.hostname) else "Hostname Not Provided"
        self.location = "{} {}".format(
            node.city + "," if val_known(node.city) else "(City Not Provided)",
            node.region + "" if val_known(node.region) else "(Region Not Provided)")
        self.coords = "{},  {}".format(node.get_latitude(), node.get_longitude()) if val_known(
            node.coords) else "(Coordinates Not Provided)"
        self.rtt = node.rtt + " round trip time from last node" if val_known(
            node.rtt) else "(Round Trip Time Not Provided)"  # add like "from last node"

        # self.setMaximumHeight(150)
        # self.setLayout(self.layout)

        text = "({}) : {}    {}    {}\n   {}     ({})\n   {}\n".format(
            pos, self.org, self.location, self.coords, self.ip, self.hostname, self.rtt)
        if node.private:
            text = "({}) : Unreachable; Device chose not to respond, or timed out.\n".format(pos)

        text = """    ------------------------------------------------------------------------------------------------------
        {}""".format(text)

        self.setText(text)


class Window(QWidget):
    class CustomNavigationToolbar(NavigationToolbar2QT):
        """Subclass of standard toolbar, with some buttons removed."""
        toolitems = [t for t in NavigationToolbar.toolitems if
                     t[0] in ('Home', 'Pan', 'Zoom', 'Save')]

    def __init__(self, parent=None):
        # super(Window, self).__init__(parent)
        super().__init__()
        self.setWindowTitle("Visual Traceroute")

        # self.showFullScreen()

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = self.CustomNavigationToolbar(self.canvas, self)

        # draw map
        self.ax = self.generate_map_axes()
        self.canvas.draw()

        # coords enter
        # self.addr_text = QLabel("Enter a web address ...")
        self.addr_entry = QLineEdit("www.google.com")
        self.addr_entry.setAlignment(Qt.AlignCenter)
        self.addr_entry.setMaximumWidth(200)
        # self.addr_text.setBuddy(self.addr_entry)
        self.button = QPushButton('Perform Traceroute')
        self.button.setMaximumWidth(200)
        self.button.clicked.connect(self.plot)

        main_layout = QGridLayout()

        # set the layout
        map_layout = QVBoxLayout()
        map_layout.addWidget(self.toolbar)
        map_layout.addWidget(self.canvas)
        main_layout.addLayout(map_layout, 0, 0)

        self.flow_list = QListWidget()  # QHBoxLayout()
        self.flow_list.setMaximumHeight(170)
        self.flow_list.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        main_layout.addWidget(self.flow_list, 1, 0)

        entry_layout = QGridLayout()
        # entry_layout.addWidget(self.addr_text)
        entry_layout.addWidget(self.addr_entry, 0, 1, alignment=Qt.AlignHCenter)
        entry_layout.addWidget(self.button, 1, 1, alignment=Qt.AlignHCenter)

        self.traceroute_options = QComboBox()
        self.traceroute_options.addItems(["Default/'Traditional' (Not Reccomended)",
                                          "ICMP (Reccomended)",
                                          "UDP",
                                          "TCP (Reccomended, requires superuser privileges)",
                                          "DCCP (Requires superuser privileges)"])
        self.traceroute_options.setCurrentIndex(1)
        self.traceroute_method = TracerouteMethods(1)
        self.traceroute_options.currentIndexChanged.connect(self.traceroute_options_change)
        entry_layout.addWidget(self.traceroute_options, 0, 0)
        entry_layout.addWidget(QLabel("Use the Zoom Tool (Magnifying Glass, top left) to zoom in on nodes.\n"
                                      + "Try some different Traceroute Methods to see what works best - firewalls on some nodes block packets of "
                                      + "certain types."), 0, 2)

        main_layout.addLayout(entry_layout, 2, 0)

        self.setLayout(main_layout)

    def traceroute_options_change(self, i):
        self.traceroute_method = TracerouteMethods(i)

    def generate_map_axes(self):
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()
        ax.stock_img()
        ax.add_feature(cfeature.BORDERS.with_scale('50m'))
        ax.add_feature(cfeature.STATES.with_scale('50m'))

        return ax

    def plot(self):

        self.flow_list.clear()
        self.figure.clear()
        self.ax.cla()
        self.ax = self.generate_map_axes()
        self.canvas.draw()

        node_list = get_traceroute_node_list(self.addr_entry.text(), self.traceroute_method)

        self.flow_list.addItem("START")

        visited_coords = []
        marker_color = 'red'
        i = city_dup = last_valid = 0
        for node in node_list:
            print(repr(node))

            if node.coords_provided():

                longitude = round(float(node.get_longitude()), 2)  # round to 2dp required by plt plot/text methods
                latitude = round(float(node.get_latitude()), 2)

                if i > 0:
                    marker_color = 'blue'
                if i == len(node_list) - 1:
                    marker_color = 'green'  # electric green

                plt.plot(longitude, latitude, marker_color, marker='o', markersize=12, transform=ccrs.PlateCarree())

                if i > 1 and node_list[
                    last_valid].coords_provided():  # error where last valid node is 0 and coords not disclosed, think fixed now

                    last_valid_node = node_list[last_valid]
                    # print("i={}, last_valid={}, last_valid_node={}".format(i, last_valid, last_valid_node.ip))
                    prev_latitude = round(float(last_valid_node.get_latitude()), 2)
                    prev_longitude = round(float(last_valid_node.get_longitude()), 2)
                    plt.plot([longitude, prev_longitude], [latitude, prev_latitude], color='blue', linewidth=0.8,
                             transform=ccrs.Geodetic())

                coords_used = "{},{}".format(longitude, latitude)
                tmp = ""
                if coords_used in visited_coords:
                    tmp = ""
                    # build amount of spaces to prepend
                    for x in range(visited_coords.count(coords_used)):
                        tmp += "\n\n"
                    tmp += "and "

                visited_coords.append(coords_used)

                plt.text(longitude, latitude, tmp + str(i), color='white', horizontalalignment='center',
                         verticalalignment='center', transform=ccrs.PlateCarree())

                self.canvas.draw()

                last_valid = i

            # add node into flow
            self.flow_list.addItem(FlowNodeInfoBox(node, i))

            i = i + 1
        self.flow_list.addItem("END")


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
