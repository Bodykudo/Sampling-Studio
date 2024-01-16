from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from view.Icon import Icon


class SignalItem(QFrame):
    def __init__(self, title) -> None:
        super().__init__()
        self.horizontalLayout = QHBoxLayout(self)
        self.title = title
        self.signalName = QLabel()
        self.signalName.setObjectName("signalName")
        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.horizontalLayout.addWidget(self.signalName)
        self.signalName.setText(title)
        self.horizontalLayout.addItem(self.horizontalSpacer)
        self.showButton = QPushButton()
        self.showButton.setObjectName("showButton")
        showIcon = Icon("icons/show.svg")
        self.showButton.setIcon(showIcon)
        self.showButton.setIconSize(QtCore.QSize(15, 15))
        self.showButton.setFixedSize(25, 25)
        self.horizontalLayout.addWidget(self.showButton)
        self.deleteButton = QPushButton()
        self.deleteButton.setObjectName("deleteButton")
        deleteIcon = Icon("icons/delete.svg")
        self.deleteButton.setIcon(deleteIcon)
        self.deleteButton.setIconSize(QtCore.QSize(15, 15))
        self.deleteButton.setFixedSize(25, 25)
        self.horizontalLayout.addWidget(self.deleteButton)
