import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QVBoxLayout, QWidget
from PyQt6.QtGui import QDoubleValidator

from view.ComponentItem import ComponentItem
from view.SignalItem import SignalItem
from view.Icon import Icon

from model.Component import Component
from model.SamplingHandler import SamplingHandler
from model.Signal import Signal

from view.mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.currentSignal = None
        self.currentComponents = []
        self.currentSignals = []

        # connect the upload button to the handleUploadFile function
        self.uploadSignalButton.clicked.connect(self.handleUploadFile)

        # connect the add component button to the handleAddComponent function
        self.addComponentButton.clicked.connect(
            lambda: self.handleAddComponent(False, None)
        )

        # connect the add signal button to the handleAddSignal function
        self.addSignalButton.clicked.connect(self.handleAddSignal)

        # set the step of the slider with 1 and the maximum value with 5
        self.signalToNoiseRatioSlider.setMinimum(1)
        self.signalToNoiseRatioSlider.setMaximum(50)

        # connect the noise checkbox to the activateNoise function
        self.deactivateNoise()
        self.noiseCheckBox.setEnabled(False)
        self.noiseCheckBox.stateChanged.connect(
            lambda: self.activateNoise()
            if self.noiseCheckBox.isChecked()
            else self.deactivateNoise()
        )

        # set the step of the slider with 1 and the maximum value with 5
        self.nyquistRateSlider.setMinimum(0)
        self.nyquistRateSlider.setMaximum(4)
        self.nyquistRateSlider.setSingleStep(1)
        self.nyquistRateSlider.setEnabled(False)
        self.samplingFrequencySlider.setSingleStep(1)
        self.samplingFrequencySlider.setEnabled(False)

        # create a sampling handler
        self.handler = SamplingHandler(dark_mode=self.isDarkMode())

        # add the graph widgets to the layout
        self.originalSignalGraphFrame.setLayout(QVBoxLayout())
        self.reconstructedSignalGraphFrame.setLayout(QVBoxLayout())
        self.reconstructionErrorGraphFrame.setLayout(QVBoxLayout())
        self.originalSignalGraphFrame.layout().addWidget(self.handler.channels[0])
        self.reconstructedSignalGraphFrame.layout().addWidget(self.handler.channels[1])
        self.reconstructionErrorGraphFrame.layout().addWidget(self.handler.channels[2])

        # connect the nyquist rate slider to the handleChangeRate function
        self.nyquistRateSlider.valueChanged.connect(self.handleChangeNyquistRate)
        self.samplingFrequencySlider.valueChanged.connect(
            self.handleChangeSamplingFrequency
        )

        # connect the snr slider to the handleChangeNoise function
        self.signalToNoiseRatioSlider.valueChanged.connect(
            self.handleChangeSignalToNoiseRatio
        )

        self.componentInputType()

    def handleAddComponent(self, isEditing, componentItem):
        """
        Adds a component to the tree view
        """
        self.componentInputType()
        amplitude = self.amplitudeValue.text()
        frequency = self.frequencyValue.text()
        shift = self.shiftValue.text()

        if amplitude == "" or frequency == "" or shift == "":
            return

        if isEditing == True:
            componentItem.setAmplitude(amplitude)
            componentItem.setFrequency(frequency)
            componentItem.setShift(shift)
            self.addComponentButton.setText("Add Component")
            self.addComponentButton.clicked.disconnect()
            self.addComponentButton.clicked.connect(
                lambda: self.handleAddComponent(False, None)
            )
        else:
            compItem = ComponentItem(amplitude, frequency, shift)
            # insert the component item to the layout at the top
            self.componentsScrollAreaContents.layout().insertWidget(0, compItem)
            compItem.editButton.clicked.connect(
                lambda: self.handleEditComponent(
                    str(amplitude), str(frequency), str(shift), compItem
                )
            )
            compItem.deleteButton.clicked.connect(
                lambda: self.handleDeleteComponent(compItem)
            )

            self.currentComponents.append(compItem)

        self.amplitudeValue.setText("")
        self.frequencyValue.setText("")
        self.shiftValue.setText("")

    def handleEditComponent(self, amplitude, frequency, shift, componentItem):
        """
        Edits a component from the tree view
        """
        self.amplitudeValue.setText(amplitude)
        self.frequencyValue.setText(frequency)
        self.shiftValue.setText(shift)
        self.addComponentButton.setText("Edit Component")
        self.addComponentButton.clicked.disconnect()
        self.addComponentButton.clicked.connect(
            lambda: self.handleAddComponent(isEditing=True, componentItem=componentItem)
        )

    def handleDeleteComponent(self, componentItem):
        """
        Deletes a component from the tree view
        """
        componentItem.hide()
        self.currentComponents.remove(componentItem)

    def handleAddSignal(self):
        """
        Adds a signal to the graph
        """
        if len(self.currentComponents) == 0:
            return

        newSignal = Signal()
        for compItem in self.currentComponents:
            currComponent = Component(
                float(compItem.getAmplitude()),
                float(compItem.getFrequency()),
                float(compItem.getShift()),
            )
            newSignal.add_component(currComponent)
            compItem.hide()
            self.currentComponents = []

        newSignalItem = SignalItem(f"Signal {len(self.currentSignals) + 1}")
        newSignalItem.showButton.clicked.connect(
            lambda: self.handleShowSignal(newSignalItem, newSignal)
        )
        newSignalItem.deleteButton.clicked.connect(
            lambda: self.handleDeleteSignal(newSignalItem, newSignal)
        )
        self.signalsScrollAreaContents.layout().insertWidget(0, newSignalItem)
        self.currentSignals.append(newSignalItem)
        self.handler.add_signal(newSignal)
        self.handler.change_sampling_freq(2 * newSignal.fmax, newSignal)
        if len(self.currentSignals) == 1:
            self.handleShowSignal(newSignalItem, newSignal)

    def handleShowSignal(self, signalItem, signal):
        """
        Shows a signal on the graph
        """
        hideIcon = Icon("icons/hide.svg")
        showIcon = Icon("icons/show.svg")
        for item in self.currentSignals:
            if not item == signalItem:
                item.showButton.setIcon(showIcon)
                signalItem.showButton.setEnabled(False)

        signalItem.showButton.setIcon(hideIcon)
        signalItem.showButton.setEnabled(True)
        self.currentSignal = signal
        self.handler.draw_signal(signal)
        self.minimumFsValue.setText("0")
        self.maximumFsValue.setText(str(int(4 * signal.fmax)))
        self.noiseCheckBox.setEnabled(True)
        self.nyquistRateSlider.setEnabled(True)
        self.samplingFrequencySlider.setEnabled(True)
        self.samplingFrequencySlider.setMinimum(1)
        self.samplingFrequencySlider.setMaximum(int(4 * signal.fmax))
        self.samplingFrequencySlider.setValue(int(signal.new_sampling_freq))
        self.signalToNoiseRatioSlider.setValue(50)

    def handleDeleteSignal(self, signalItem, signal):
        """
        Deletes a signal from the graph
        """
        signalItem.hide()
        self.currentSignals.remove(signalItem)
        self.handler.delete_signal(signal)
        if signal == self.currentSignal:
            for channel in self.handler.channels:
                channel.clear()

    def handleUploadFile(self):
        """
        Allows the user to browse for a file to upload
        """
        file = QFileDialog.getOpenFileName(
            self, "Open file", ".\\", "CSV files (*.csv)"
        )
        if file:
            newSignal = Signal()
            newSignal.read_data_from_csv(file[0])
            self.handler.add_signal(newSignal)
            signalName = os.path.splitext(os.path.basename(file[0]))[0]
            newSignalItem = SignalItem(signalName)
            newSignalItem.showButton.clicked.connect(
                lambda: self.handleShowSignal(newSignalItem, newSignal)
            )
            newSignalItem.deleteButton.clicked.connect(
                lambda: self.handleDeleteSignal(newSignalItem, newSignal)
            )
            self.signalsScrollAreaContents.layout().insertWidget(0, newSignalItem)
            self.currentSignals.append(newSignalItem)
            self.handler.add_signal(newSignal)
            self.handler.change_sampling_freq(2 * newSignal.fmax, newSignal)
            if len(self.currentSignals) == 1:
                self.handleShowSignal(newSignalItem, newSignal)

    def handleChangeNyquistRate(self):
        """
        Changes the nyquist rate of the signal
        """
        signal = self.currentSignal
        newValue = self.nyquistRateSlider.value()
        self.nyquistRateValue.setNum(newValue)
        self.samplingFrequencySlider.setValue(int(newValue * signal.fmax))
        self.handler.change_nq_rate(newValue, signal)
        self.handler.draw_signal(signal)

    def handleChangeSamplingFrequency(self):
        """
        Changes the sampling frequency of the signal
        """
        signal = self.currentSignal
        newValue = self.samplingFrequencySlider.value()
        self.samplingFreqencyValue.setNum(newValue)
        self.nyquistRateSlider.setValue(int(newValue / signal.fmax))
        self.nyquistRateValue.setNum(round(newValue / signal.fmax))
        self.handler.change_sampling_freq(newValue, signal)
        self.handler.draw_signal(signal)

    def handleChangeSignalToNoiseRatio(self):
        """
        Changes the signal to noise ratio of the signal
        """
        newValue = self.signalToNoiseRatioSlider.value()
        self.currentSignal.change_snr(float(newValue))
        self.handler.draw_signal(self.currentSignal)
        self.signalToNoiseRatioValue.setText(f"{newValue}")

    def activateNoise(self):
        """
        Activates the noise section
        """
        self.signalToNoiseRatioValue.setEnabled(True)
        self.signalToNoiseRatioSlider.setEnabled(True)
        if self.currentSignal:
            self.currentSignal.change_snr(10000)

    def deactivateNoise(self):
        """
        Deactivates the noise section
        """
        self.signalToNoiseRatioValue.setEnabled(False)
        self.signalToNoiseRatioValue.setText("0")
        self.signalToNoiseRatioSlider.setValue(50)
        self.signalToNoiseRatioSlider.setEnabled(False)
        if self.currentSignal:
            self.currentSignal.change_snr(10000)

    def componentInputType(self):
        """
        Limit the input of the amplitude, frequency and shift to only numbers
        """
        self.amplitudeValue.setValidator(QDoubleValidator())
        self.frequencyValue.setValidator(QDoubleValidator())
        self.shiftValue.setValidator(QDoubleValidator())

    def isDarkMode(self):
        """
        Checks if the application is in dark mode
        """
        widget = QWidget()
        color = widget.palette().color(QWidget().backgroundRole())
        brightness = color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114
        return brightness < 128


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
