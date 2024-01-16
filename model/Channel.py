import pyqtgraph as pg


class Channel(pg.PlotWidget):
    def __init__(self, name, dark_mode, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not dark_mode:
            self.setBackground("w")
        self.setLabel("left", "Amplitude", fontsize=60)
        self.setLabel("bottom", "Time", fontsize=60)
        self.setTitle(name, fontsize=200)
        self.showGrid(x=True, y=True)
        self.setAutoVisible(x=True, y=True)
