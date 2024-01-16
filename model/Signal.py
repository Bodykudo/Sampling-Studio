import numpy as np
import pandas as pd
from diffpy.utils.parsers.resample import wsinterp
from model.Component import Component


class Signal:
    """
    A class representing a signal for digital signal processing.

    Attributes:
        x (numpy.ndarray): The time values of the signal.
        N (int): The number of data points in the signal.
        y (numpy.ndarray): The amplitude values of the signal.
        fmax (int): The maximum frequency in the signal.
        SNR (float): The Signal-to-Noise Ratio.
        sampling_freq (int): The sampling frequency of the signal.
        sampling_factor (int): The sampling factor affecting the sampling frequency.
        sampled_points (list): A list of (x, y) tuples for sampled points.
        recovered_points (list): A list of (x, y) tuples for recovered points.
        noise_samples (list): A list of noise samples applied to the signal.
    """

    def __init__(self):
        """
        Initializes a Signal object with default values for its attributes.
        """
        self.x = None
        self.N = 1000
        self.y = 0
        self.fmax = 0
        self.SNR = 0
        self.sampling_freq_given = 125
        self.sampling_factor = None
        self.noise_samples = []
        self.new_sampling_freq = 0
        self.sampled_points = []
        self.recovered_points = []
        self.components = []
        self.uploaded = False
        self.original_y = 0
        self.fmin = float("inf")
        self.noise = []
        self.original_y = None

    def read_data_from_csv(self, file_path="data/bidmc_01_Signals.csv"):
        """
        Read data from a CSV file and initialize signal attributes.

        Args:
            file_path (str): The path to the CSV file containing signal data.

        Returns:
            None

        This method reads the first 1000 rows of data from the specified CSV file
        and initializes the signal attributes including time values (x), amplitude
        values (y), the number of data points (N), sampling frequency (sampling_freq),
        the maximum frequency (fmax), and the sampling factor (sampling_factor).
        """
        data = pd.read_csv(file_path).iloc[: self.N, :]
        self.x = data["Time [s]"].to_numpy()
        self.y = data[" II"].to_numpy()
        self.N = 1000
        self.sampling_freq_given = 125
        self.fmax = 62
        self.sampling_factor = 1
        self.new_sampling_freq = 125
        self.uploaded = True
        self.original_y = self.y.copy()

    def change_snr(self, new_snr):
        """
        Change the Signal-to-Noise Ratio (SNR) of the signal.

        Parameters
        ----------
        new_snr : float
            The new SNR value to set.

        Returns
        -------
        None

        This method updates the SNR attribute of the signal to the specified
        new SNR value and creates noise samples accordingly.
        """
        self.SNR = new_snr
        self.y = self.apply_noise(self.original_y)

    def change_sampling_factor(self, new_sampling_factor):
        """
        Change the sampling factor of the signal.

        Parameters
        ----------
        new_sampling_factor : float
            The new sampling factor to set.

        Returns
        -------
        None

        This method updates the sampling factor attribute of the signal to
        the specified new sampling factor and also updates the sampling frequency
        based on the product of the new sampling factor and the signal's maximum frequency (fmax).
        """
        self.sampling_factor = new_sampling_factor
        self.change_sampling_freq(self.fmax * self.sampling_factor)

    def change_sampling_freq(self, new_sampling_freq):
        """
        Change the sampling frequency of the signal.

        Parameters
        ----------
        new_sampling_freq : float
            The new sampling frequency to set.

        Returns
        -------
        None

        This method updates the sampling frequency attribute of the signal to the specified new sampling frequency.
        It may also include functionality to update the signal plot to reflect the new sampling frequency.
        """
        self.new_sampling_freq = new_sampling_freq
        # Update the plot (if necessary) to reflect the new sampling frequency.

    def create_noise(self, y):
        """
        Create noise samples based on the current SNR.

        Returns
        -------
        None

        This method generates noise samples based on the current SNR and appends them to the noise_samples list.
        """
        self.noise_samples.clear()
        self.noise.clear()
        temp_signal = self.y.copy()
        signal_power = temp_signal**2
        signal_average_power = np.mean(signal_power)
        noise_power = signal_average_power / self.SNR
        noise = np.random.normal(0, np.sqrt(noise_power), len(temp_signal))
        self.noise_samples.append(noise)
        noise = self.noise_samples.copy()
        self.noise = noise.copy()
        return noise

    def apply_noise(self, y):
        """
        Apply noise samples to the signal.

        Returns
        -------
        numpy.ndarray
            The noisy signal after applying noise.

        This method applies the accumulated noise samples to the signal and returns the noisy signal.
        """
        noisy = self.create_noise(y)
        noisy_signal = y.copy()
        for noise in noisy:
            noisy_signal += noise
        return noisy_signal

    def get_impulse_train(self):
        if self.uploaded:
            impulse_train = np.arange(0, self.x[-1], (1 / self.new_sampling_freq))
        else:
            impulse_train = np.arange(0, self.x[-1], 1 / (self.new_sampling_freq))
        impulse_train = np.around(impulse_train, 3)
        return impulse_train

    def sample_signal(self):
        impulse_train = self.get_impulse_train()
        y_values_sampled = np.zeros(len(impulse_train))
        y_values_sampled = wsinterp(impulse_train, self.x, self.y)
        self.sampled_points = list(zip(impulse_train, y_values_sampled))

    def whittaker_shannon_interpolation(self, x, y, x_new, T=1):
        """
        Perform Whittaker-Shannon interpolation on the given data.

        Parameters:
        x : array_like
            The x-coordinates of the data points.
        y : array_like
            The y-coordinates of the data points.
        x_new : array_like
            The x-coordinates at which to evaluate the interpolated values.
        T : float, optional
            The sampling period. Default is 1.

        Returns:
        y_new : ndarray
            The interpolated values at `x_new`.
        """

        # Ensure inputs are arrays
        x = np.asarray(x)
        y = np.asarray(y)
        x_new = np.asarray(x_new)

        # Calculate the sinc matrix
        sinc_matrix = np.sinc((x - x_new[:, None]) / T)

        # Perform the interpolation
        y_new = np.dot(y, sinc_matrix)

        return y_new

    def add_component(self, component: Component) -> None:
        """
        Adds a component to the signal (adds a sinusoidal component to the signal)
        """
        if self.fmax < component.frequency:
            self.fmax = component.frequency
        if self.fmin > component.frequency:
            self.fmin = component.frequency
        self.new_sampling_freq = 2 * self.fmax
        self.x = np.arange(0, 20, 0.02)
        self.y += component.amplitude * np.sin(
            2 * np.pi * component.frequency * self.x + component.shift * np.pi
        )
        self.original_y = self.y.copy()
        self.components.append(component)

    def get_signal_components(self) -> list:
        """
        Returns the components of the signal
        """
        return self.components

    def get_components(self) -> list:
        """
        Returns the components of the signal
        """
        return self.components

    def update_component_frequency(self, index: int, new_frequency: float) -> None:
        """
        Updates the frequency of a component
        """
        self.components[index].change_frequency(new_frequency)

    def update_component_amplitude(self, index: int, new_amplitude: float) -> None:
        """
        Updates the amplitude of a component
        """
        self.components[index].change_amplitude(new_amplitude)

    def update_component_shift(self, index: int, new_shift: float) -> None:
        """
        Updates the shift of a component
        """
        self.components[index].change_shift(new_shift)