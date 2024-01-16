from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
)
from view.Icon import Icon


class ComponentItem(QFrame):
    def __init__(self, amplitude: str, frequency: str, shift: str):
        super().__init__()
        self.horizontalLayout = QHBoxLayout(self)
        self.ampLabel = QLabel()
        self.ampLabel.setObjectName("ampLabel")
        self.horizontalLayout.addWidget(self.ampLabel)
        self.ampValue = QLabel()
        self.ampValue.setObjectName("ampValue")
        self.horizontalLayout.addWidget(self.ampValue)
        self.freqLabel = QLabel()
        self.freqLabel.setObjectName("freqLabel")
        self.horizontalLayout.addWidget(self.freqLabel)
        self.freqValue = QLabel()
        self.freqValue.setObjectName("freqValue")
        self.horizontalLayout.addWidget(self.freqValue)
        self.shiftLabel = QLabel()
        self.shiftLabel.setObjectName("shiftLabel")
        self.horizontalLayout.addWidget(self.shiftLabel)
        self.shiftValue = QLabel()
        self.shiftValue.setObjectName("shiftValue")
        self.horizontalLayout.addWidget(self.shiftValue)
        self.editButton = QPushButton()
        self.editButton.setObjectName("editButton")

        self.editButton.setFixedSize(25, 25)
        editIcon = Icon("icons/edit.svg")
        self.editButton.setIcon(editIcon)
        self.editButton.setIconSize(QtCore.QSize(15, 15))
        self.horizontalLayout.addWidget(self.editButton)

        self.deleteButton = QPushButton()
        self.deleteButton.setObjectName("deleteButton")
        self.deleteButton.setFixedSize(25, 25)
        deleteIcon = Icon("icons/delete.svg")
        self.deleteButton.setIcon(deleteIcon)
        self.deleteButton.setIconSize(QtCore.QSize(15, 15))
        self.horizontalLayout.addWidget(self.deleteButton)

        self.amplitude = amplitude
        self.frequency = frequency
        self.shift = shift

        self.ampValue.setText(amplitude)
        self.freqValue.setText(frequency)
        self.shiftValue.setText(shift)
        self.ampLabel.setText("Amp:")
        self.freqLabel.setText("Freq:")
        self.shiftLabel.setText("Shift:")

    def getAmplitude(self):
        return float(self.amplitude)

    def getFrequency(self):
        return float(self.frequency)

    def getShift(self):
        return float(self.shift)

    def setAmplitude(self, amplitude):
        self.amplitude = amplitude
        self.ampValue.setText(amplitude)

    def setFrequency(self, frequency):
        self.frequency = frequency
        self.freqValue.setText(frequency)

    def setShift(self, shift):
        self.shift = shift
        self.shiftValue.setText(shift)
