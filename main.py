import sys
import os
from enum import Enum, auto

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit, \
    QLabel, QGridLayout, QWidget, QAbstractItemView, QListWidgetItem, QCheckBox, QComboBox, QMessageBox
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

import ip_utils
from node_utils import val_known
from ip_utils import get_traceroute_node_list, functions_correctly


class TracerouteMethods(Enum):
    DEFAULT = 0
    ICMP = 1
    UDP = 2
    TCP = 3
    DCCP = 4


class NodeListItem(QListWidgetItem):
    """ Textual representation of a hop node, to be displayed in a QListWidget"""

    def __init__(self, node, pos):
        super().__init__()
        self.layout = QVBoxLayout()

        # Should be Impossible to get no coords, IP, rtt
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

        text = "({}) : {}    {}    {}\n   {}     ({})\n   {}\n".format(
            pos, self.org, self.location, self.coords, self.ip, self.hostname, self.rtt)
        if node.private:
            text = "({}) : Unreachable; Device chose not to respond, or timed out.\n".format(pos)

        text = """    ------------------------------------------------------------------------------------------------------
        {}""".format(text)

        self.setText(text)


def show_message_box(title, message, extra=""):
    msg = QMessageBox()

    #msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setInformativeText(extra)
    #msg.setDetailedText("The details are as follows:")

    msg.show()

    retval = msg.exec_()
    #sys.exit(app.exec_())


class Window(QWidget):
    class CustomNavigationToolbar(NavigationToolbar2QT):
        """Subclass of standard toolbar, with some buttons removed."""
        toolitems = [t for t in NavigationToolbar.toolitems if
                     t[0] in ('Home', 'Pan', 'Zoom', 'Save')]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visual Traceroute")

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = self.CustomNavigationToolbar(self.canvas, self)

        # draw map
        self.ax = self.reset_map()
        self.canvas.draw()

        main_layout = QGridLayout()

        # LAYOUT: Map
        map_layout = QVBoxLayout()
        map_layout.addWidget(self.toolbar)
        map_layout.addWidget(self.canvas)
        main_layout.addLayout(map_layout, 0, 0)

        # LAYOUT: Node List Widget (Textual Representation)
        self.node_list_widget = QListWidget()
        self.node_list_widget.setMaximumHeight(int(round(self.height() * 0.4)))
        self.node_list_widget.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        main_layout.addWidget(self.node_list_widget, 1, 0)

        # LAYOUT: User Entry (IP, traceroute method selection)
        entry_layout = QGridLayout()

        self.addr_entry = QLineEdit("www.google.com")
        self.addr_entry.setAlignment(Qt.AlignCenter)
        self.addr_entry.setMaximumWidth(200)

        self.button = QPushButton('Perform Traceroute')
        self.button.setMaximumWidth(200)
        self.button.clicked.connect(self.perform_traceroute)

        self.traceroute_options = QComboBox()

        self.traceroute_options.addItems(["Default/'Traditional'",
                                          "ICMP (Reccomended)",
                                          "UDP",
                                          "TCP (Reccomended, requires superuser privileges)",
                                          "DCCP (Requires superuser privileges)"])
        self.traceroute_options.setCurrentIndex(1)

        self.traceroute_options.currentIndexChanged.connect(self.traceroute_options_change)

        entry_layout.addWidget(self.addr_entry, 0, 1, alignment=Qt.AlignHCenter)
        entry_layout.addWidget(self.button, 1, 1, alignment=Qt.AlignHCenter)
        entry_layout.addWidget(self.traceroute_options, 0, 0)
        entry_layout.addWidget(QLabel("Use the Zoom Tool (Magnifying Glass, top left) to zoom in on nodes.\n"
                                      + "Try some different Traceroute Methods to see what works best - firewalls on some nodes block packets of "
                                      + "certain types."), 0, 2)
        main_layout.addLayout(entry_layout, 2, 0)

        self.setLayout(main_layout)

        self.traceroute_method = TracerouteMethods(1)

    def traceroute_options_change(self, i):
        self.traceroute_method = TracerouteMethods(i)

    def reset_map(self):
        self.figure.clear()

        new_ax = plt.axes(projection=ccrs.PlateCarree())
        new_ax.coastlines()
        new_ax.stock_img()
        new_ax.add_feature(cfeature.BORDERS.with_scale('50m'))
        new_ax.add_feature(cfeature.STATES.with_scale('50m'))
        self.ax = new_ax

        self.canvas.draw()

    def perform_traceroute(self):

        # clear data from last run
        self.node_list_widget.clear()
        self.reset_map()

        # Actually perform traceroute and store resulting nodes in list
        node_list = get_traceroute_node_list(self.addr_entry.text(), self.traceroute_method)
        if node_list is not None:

            self.node_list_widget.addItem("START")

            visited_coords = []
            marker_color = 'red'
            i = last_valid = 0
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
                self.node_list_widget.addItem(NodeListItem(node, i))

                i = i + 1

            self.node_list_widget.addItem("END")


if __name__ == '__main__':
    app = QApplication(sys.argv)


    # is traceroute installed?
    result = os.popen("traceroute -n -q1 localhost")
    if not ip_utils.functions_correctly(result):
        show_message_box("Traceroute doesn't seem to be available on this system.",
                         "We tried using the traceroute command-line utility on your system, but it didn't work.\n"
                         "Traceroute is needed for this application.\n",
                         "If you're on a Debian/Ubuntu-based system, you can get traceroute using "
                         "'sudo apt install traceroute'.\n\nFor other distributions, please seek help online.")
    else:

        # does traceroute have sudo privileges?
        result = os.popen("sudo traceroute -M TCP -q1 localhost")
        if not ip_utils.functions_correctly(result):
            show_message_box("Traceroute does not have superuser privileges.",
                             "Traceroute is working on your computer, but you aren't running it with administrator/superuser privileges.\n\n"
                             "This is fine, but 2 of the 5 Traceroute methods (TCP/DCCP), which may provide better results, will not be available.\n\n"
                             "To fix this, please check the README file provided with this application.")

        main = Window()
        main.show()

    sys.exit(app.exec_())
