import numpy as np
import pyqtgraph as pg

from model.Channel import Channel
from model.Signal import Signal
from model.Component import Component


class SamplingHandler:
    def __init__(self, dark_mode) -> None:
        self.signals = []
        self.channels = [
            Channel("Original Signal & Sampled Points", dark_mode),
            Channel("Reconstructed Signal", dark_mode),
            Channel("Reconstruction Error", dark_mode),
        ]

    def add_signal_component(
        self, sig: Signal, amplitude: float, frequency: float, shift: float
    ) -> None:
        """
        Adds a component to a signal at a given index
        """
        signal_component = Component(amplitude, frequency, shift)
        if sig in self.signals:
            index = self.signals.index(sig)
            self.signals[index].add_component(signal_component)

    def add_signal(self, sig) -> None:
        """
        Adds a signal to the mixer
        """
        self.signals.append(sig)

    def delete_signal(self, sig) -> None:
        self.signals.remove(sig)

    def get_signal_components(self, index: int) -> list:
        """
        Returns a list of components for a given signal
        """
        return self.signals[index].get_components()

    def get_signal(self, index: int) -> Signal:
        """
        Returns a signal at a given index
        """
        return self.signals[index]

    def get_signals(self) -> list:
        """
        Returns a list of signals
        """
        return self.signals

    def change_nq_rate(self, nq_rate, sig):
        """
        Changes the sampling frequency of a signal
        """
        sig.new_sampling_freq = nq_rate * sig.fmax + 1

    def change_sampling_freq(self, freq, sig):
        """
        Changes the sampling frequency of a signal
        """
        sig.new_sampling_freq = freq

    def draw_signal(self, sig: Signal):
        """
        Draws a signal on the graph
        """
        if sig in self.signals:
            for channel in self.channels:
                channel.clear()
                channel.setXRange(0, 3)
                channel.setLimits(xMin=-0.2, xMax=sig.x[-1] + 0.2)

            index = self.signals.index(sig)
            signal = self.signals[index]

            signal.sample_signal()
            sampled_points = signal.sampled_points
            x_values, y_values_sampled = zip(*sampled_points)
            interpolate = sig.whittaker_shannon_interpolation(
                sig.x, y_values_sampled, x_values, 1 / sig.new_sampling_freq
            )
            self.channels[0].plot(
                signal.x,
                signal.y,
                pen="r",
            )
            sample_markers = pg.ScatterPlotItem(
                x=x_values,
                y=y_values_sampled,
                pen=None,
                symbol="x",
                symbolPen="b",
                name="sample_markers",
            )
            self.channels[0].addItem(sample_markers)
            self.channels[1].plot(sig.x, interpolate)

            error = np.array(signal.y) - interpolate
            self.channels[2].plot(sig.x, error, pen="r")
            self.channels[2].setYRange(-2, 2)
