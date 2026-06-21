from typing import Any, Dict, Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from pslipstream.config import SETTINGS_DEFAULTS, config


class SettingsDialog(QDialog):
    """Edit the read/backup settings and persist them to the user config."""

    CRACK_MODES = [
        ("key (libdvdcss default)", "key"),
        ("disc", "disc"),
        ("title", "title"),
        ("unset (let libdvdcss decide)", "unset"),
    ]
    VERBOSITY = [
        ("0 - Silent", 0),
        ("1 - Errors", 1),
        ("2 - Errors + Debug", 2),
    ]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(460)

        form = QFormLayout()

        self.css_crack_mode = QComboBox()
        for text, mode in self.CRACK_MODES:
            self.css_crack_mode.addItem(text, mode)
        self.css_crack_mode.setToolTip("libdvdcss CSS title-key method (DVDCSS_METHOD).")
        form.addRow("CSS crack mode", self.css_crack_mode)

        self.css_verbosity = QComboBox()
        for text, level in self.VERBOSITY:
            self.css_verbosity.addItem(text, level)
        self.css_verbosity.setToolTip("libdvdcss log verbosity (DVDCSS_VERBOSE).")
        form.addRow("libdvdcss verbosity", self.css_verbosity)

        self.pycdlib_open_attempts = QSpinBox()
        self.pycdlib_open_attempts.setRange(1, 50)
        self.pycdlib_open_attempts.setToolTip(
            "Times to retry opening the disc in pycdlib (drives can be flaky on spin-up)."
        )
        form.addRow("Disc open attempts", self.pycdlib_open_attempts)

        self.pycdlib_open_retry_delay = QDoubleSpinBox()
        self.pycdlib_open_retry_delay.setRange(0.0, 30.0)
        self.pycdlib_open_retry_delay.setSingleStep(0.5)
        self.pycdlib_open_retry_delay.setDecimals(1)
        self.pycdlib_open_retry_delay.setSuffix(" s")
        self.pycdlib_open_retry_delay.setToolTip("Delay between disc open attempts.")
        form.addRow("Disc open retry delay", self.pycdlib_open_retry_delay)

        self.read_buffer_sectors = QSpinBox()
        self.read_buffer_sectors.setRange(1, 1024)
        self.read_buffer_sectors.setToolTip("Sectors read per step during a backup (1 sector = 2 KiB).")
        form.addRow("Read buffer (sectors)", self.read_buffer_sectors)

        self.scsi_read_attempts = QSpinBox()
        self.scsi_read_attempts.setRange(1, 20)
        self.scsi_read_attempts.setToolTip("Retries for a raw SCSI read of a sector libdvdcss could not read.")
        form.addRow("SCSI read attempts", self.scsi_read_attempts)

        self.scsi_max_transfer_sectors = QSpinBox()
        self.scsi_max_transfer_sectors.setRange(1, 256)
        self.scsi_max_transfer_sectors.setToolTip(
            "Max sectors per raw SCSI read command (drives cap single transfers)."
        )
        form.addRow("SCSI max transfer (sectors)", self.scsi_max_transfer_sectors)

        note = QLabel("Changes apply the next time a disc is loaded.")
        note.setEnabled(False)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        restore = buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults)
        if restore is not None:
            restore.clicked.connect(self.restore_defaults)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(note)
        layout.addWidget(buttons)

        self._apply_values(
            {
                "css_crack_mode": config.css_crack_mode,
                "css_verbosity": config.css_verbosity,
                "pycdlib_open_attempts": config.pycdlib_open_attempts,
                "pycdlib_open_retry_delay": config.pycdlib_open_retry_delay,
                "read_buffer_sectors": config.read_buffer_sectors,
                "scsi_read_attempts": config.scsi_read_attempts,
                "scsi_max_transfer_sectors": config.scsi_max_transfer_sectors,
            }
        )

    @staticmethod
    def _set_combo(combo: QComboBox, value: Any) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _apply_values(self, values: Dict[str, Any]) -> None:
        self._set_combo(self.css_crack_mode, values["css_crack_mode"])
        self._set_combo(self.css_verbosity, values["css_verbosity"])
        self.pycdlib_open_attempts.setValue(int(values["pycdlib_open_attempts"]))
        self.pycdlib_open_retry_delay.setValue(float(values["pycdlib_open_retry_delay"]))
        self.read_buffer_sectors.setValue(int(values["read_buffer_sectors"]))
        self.scsi_read_attempts.setValue(int(values["scsi_read_attempts"]))
        self.scsi_max_transfer_sectors.setValue(int(values["scsi_max_transfer_sectors"]))

    def restore_defaults(self) -> None:
        """Reset the form to default values (not saved until Save is pressed)."""
        self._apply_values(SETTINGS_DEFAULTS)

    def save(self) -> None:
        config.css_crack_mode = self.css_crack_mode.currentData()
        config.css_verbosity = self.css_verbosity.currentData()
        config.pycdlib_open_attempts = self.pycdlib_open_attempts.value()
        config.pycdlib_open_retry_delay = self.pycdlib_open_retry_delay.value()
        config.read_buffer_sectors = self.read_buffer_sectors.value()
        config.scsi_read_attempts = self.scsi_read_attempts.value()
        config.scsi_max_transfer_sectors = self.scsi_max_transfer_sectors.value()
        config.save()
        self.accept()
