import os
import re
import glob
import mplcursors

import pandas as pd
import numpy as np

import config as config

from src.workers import ScriptWorker

from access_parser import AccessParser

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

import matplotlib
import matplotlib.cm as cm
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MadToolPage(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.df_all = {}  # { liquidClass: DataFrame }

        main_layout = QVBoxLayout(self)

        title = QLabel("MAD Tool")
        title.setObjectName("title")
        main_layout.addWidget(title)

        # ----- File Picker -----
        file_layout = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Select _mad.mdb file...")
        browse = QPushButton("Browse")
        browse.clicked.connect(self._browse_file)
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(browse)
        main_layout.addLayout(file_layout)

        main_layout.addSpacing(10)

        content_layout = QHBoxLayout()

        # ----- Linke Seite: Plot -----
        self.figure = Figure(figsize=(6, 6))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(400, 300)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.toolbar = NavigationToolbar(self.canvas, self)

        plot_widget = QWidget()
        plot_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        plot_widget_layout = QVBoxLayout(plot_widget)
        plot_widget_layout.setContentsMargins(0, 0, 0, 0)
        plot_widget_layout.addWidget(self.toolbar)
        plot_widget_layout.addWidget(self.canvas)
        plot_widget_layout.addStretch()

        content_layout.addWidget(plot_widget, 3)

        # ----- Rechte Seite: Filter Controls -----
        control_widget = QWidget()
        control_widget.setFixedWidth(250)
        control_layout = QVBoxLayout(control_widget)
        control_layout.setContentsMargins(10, 0, 0, 0)
        control_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Liquid Class
        control_layout.addWidget(QLabel("Liquid Class"))
        self.cb_liquid_class = QComboBox()
        self.cb_liquid_class.currentTextChanged.connect(self._update_filters)
        control_layout.addWidget(self.cb_liquid_class)

        control_layout.addSpacing(10)

        # Time
        control_layout.addWidget(QLabel("Time"))
        self.cb_time = QComboBox()
        self.cb_time.currentTextChanged.connect(self._update_channel_filter)
        control_layout.addWidget(self.cb_time)

        control_layout.addSpacing(10)

        # Channel
        control_layout.addWidget(QLabel("Channel"))
        self.cb_channel = QComboBox()
        control_layout.addWidget(self.cb_channel)

        control_layout.addStretch()

        self.btn_plot = QPushButton("Plot")
        self.btn_plot.clicked.connect(self._plot)
        control_layout.addWidget(self.btn_plot)

        content_layout.addWidget(control_widget, 1)

        main_layout.addLayout(content_layout)


    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select MDB File",
            config.get("input_folder"),
            "MAD MDB Files (*_mad.mdb)"
        )
        if path:
            self.file_input.setText(path)
            self._load_file()

    def _load_file(self):
        path = self.file_input.text().strip()
        if not path or not os.path.isfile(path):
            self.logger.warning("No valid MDB file selected")
            return

        try:
            db = AccessParser(path)
            self.df_all = {}
            for key in db.catalog.keys():
                if key != "MSysObjects":
                    table = db.parse_table(key)
                    self.df_all[key] = pd.DataFrame(table)

            self.cb_liquid_class.clear()
            self.cb_liquid_class.addItems(list(self.df_all.keys()))
            self.logger.info(f"Loaded {len(self.df_all)} liquid classes from {os.path.basename(path)}")
        except Exception as e:
            self.logger.error(f"Failed to load MDB: {e}")

    def _update_filters(self, liquid_class):
        self.cb_time.clear()
        self.cb_channel.clear()
        if liquid_class and liquid_class in self.df_all:
            df = self.df_all[liquid_class]
            self.cb_time.addItems([str(t) for t in df['Time'].unique()])

    def _update_channel_filter(self, time):
        self.cb_channel.clear()
        liquid_class = self.cb_liquid_class.currentText()
        if not liquid_class or liquid_class not in self.df_all:
            return
        df = self.df_all[liquid_class]
        try:
            sub = df[df['Time'].astype(str) == str(time)]
            self.cb_channel.addItem("All")
            self.cb_channel.addItems([str(c) for c in sub['Channel'].unique()])
            self.cb_channel.setCurrentIndex(0)
            self.logger.debug(f"Channels for Time {time}: {sub['Channel'].unique().tolist()}")
        except Exception as e:
            self.logger.error(f"Error updating channel filter: {e}")

    def _parse_border(self, border_str):
        values = []
        for x in border_str.split():
            x = x.lstrip('qh')
            try:
                values.append(int(x))
            except ValueError:
                values.append(0)
        return values

    def _plot(self):
        liquid_class = self.cb_liquid_class.currentText()
        time_val     = self.cb_time.currentText()
        channel_val  = self.cb_channel.currentText()

        if not all([liquid_class, time_val]):
            self.logger.warning("Please select Liquid Class and Time")
            return

        df  = self.df_all[liquid_class]
        sub = df[df['Time'].astype(str) == str(time_val)]

        if channel_val == "All":
            channels = sub['Channel'].unique()
        else:
            channels = [channel_val]

        self.figure.clear()
        ax1 = self.figure.add_subplot(111)
        ax1.format_coord = lambda x, y: ""
        ax2 = ax1.twinx()
        ax2.format_coord = lambda x, y: ""

        colors = [cm.tab20(i) for i in range(16)]

        border = None
        for i, channel in enumerate(channels):

            channelColor = int(re.sub("Ch", "", channel))

            if isinstance(channelColor, int):
                channelColor = channelColor
            else:
                channelColor = i

            color = colors[channelColor % len(colors)]

            extracted = sub[sub['Channel'].astype(str) == str(channel)]

            uniqueVolume = extracted['Volume'].unique()
            uniqueBorder = extracted['Border'].unique()

            if len(uniqueVolume) != 1 or len(uniqueBorder) != 1:
                self.logger.warning(f"Skipping Channel {channel} - no unique Volume/Border")
                continue

            volume    = int(uniqueVolume[0])
            border    = self._parse_border(uniqueBorder[0])

            valueList = " ".join([str(x) for x in extracted['Data'].tolist()]).replace('0000 ', '').split()
            values = []
            for i in valueList:
                try:
                    values.append(int(float(i)))
                except ValueError:
                    continue

            if not values:
                self.logger.warning(f"Skipping {channel} - no valid data")
                continue

            # X-Achse in 2ms Schritten
            x = [i * 2 for i in range(len(values))]

            # Differenz zwischen aufeinanderfolgenden Werten
            diff = [0] + [values[i] - values[i-1] for i in range(1, len(values))]

            # linke Y-Achse: Rohdaten
            ax1.plot(x, values, color=color, label=f"{channel} | {volume} µl")

            # rechte Y-Achse: Differenz
            ax2.plot(x, diff, color=color, linestyle='--', linewidth=0.8, label=f"{channel} diff")

        # Borders vom letzten Channel (sind gleich für alle)
        if border:
            start_value = values[0]

            if border[4] > 0:
                ax1.axhline(y=start_value + border[4], color='lightgreen', linestyle='-', label=f"_ Δp upper {start_value + border[4]}")
            if border[5] > 0:
                ax1.axhline(y=start_value - border[5], color='lightgreen', linestyle='-', label=f"_ Δp lower {start_value - border[5]}")

            if border[0] > 0:
                ax1.axhline(y=border[0], color='lightblue', linestyle='-', label="_ Clot Threshold")

        ax1.set_ylim(bottom=150)
        ax2.set_ylim(-20, 30)

        ax1.set_xlabel("t [2ms]")
        ax1.set_ylabel("A/D value")
        ax2.set_ylabel("A/D value different")
        ax1.set_title(f"{liquid_class}\nTime: {time_val}")

        # Legenden zusammenführen
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='center left', bbox_to_anchor=(1.2, 0.5))

        self.figure.tight_layout()

        # Hover
        cursor = mplcursors.cursor([ax1, ax2], hover=True)
        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.set_text(
                f"{sel.artist.get_label()}\nx: {sel.target[0]:.0f} ms\ny: {sel.target[1]:.0f} pa"
            )
            sel.annotation.get_bbox_patch().set(fc="white", alpha=0.8)

        def on_leave(event):
            for sel in cursor.selections:
                sel.annotation.set_visible(False)
            self.canvas.draw_idle()

        self.canvas.mpl_connect("figure_leave_event", on_leave)

        self.canvas.draw()
        channel_info = "All channels" if channel_val == "All" else f"{channel_val}"
        self.logger.info(f"Plotted {liquid_class} / Time {time_val} / {channel_info}")


