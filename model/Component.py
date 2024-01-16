class Component(object):
    def __init__(
        self, amplitude: float = 1, frequency: float = 1, shift: float = 0
    ) -> None:
        self.amplitude = amplitude
        self.frequency = frequency
        self.shift = shift

    def change_amplitude(self, new_amplitude: float) -> None:
        self.amplitude = new_amplitude

    def change_frequency(self, new_frequency: float) -> None:
        self.frequency = new_frequency

    def change_shift(self, new_shift: float) -> None:
        self.shift = new_shift

    def __str__(self) -> str:
        return f"amplitude: {self.amplitude}, frequency: {self.frequency}, shift: {self.shift}"
