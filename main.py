import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                            QFileDialog, QRadioButton, QLabel, QProgressBar, QHBoxLayout, 
                            QButtonGroup, QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import gzip
import lzma
import bz2

class ProcessThread(QThread):
    progress_signal = pyqtSignal(int)
    completed_signal = pyqtSignal(bool, str)

    def __init__(self, file_path, mode, method, destination_folder):
        super().__init__()
        self.file_path = file_path
        self.mode = mode  # "compress" or "decompress"
        self.method = method  # "gzip", "lzma", or "bz2"
        self.destination_folder = destination_folder

    def run(self):
        try:
            if self.mode == "compress":
                self.compress()
            else:
                self.decompress()
        except Exception as e:
            self.completed_signal.emit(False, str(e))

    def compress(self):
        if self.method == "gzip":
            compressed_file_path = os.path.join(self.destination_folder, os.path.basename(self.file_path) + ".gz")
            with open(self.file_path, 'rb') as f_in, gzip.open(compressed_file_path, 'wb') as f_out:
                f_out.writelines(f_in)
        elif self.method == "lzma":
            compressed_file_path = os.path.join(self.destination_folder, os.path.basename(self.file_path) + ".xz")
            with open(self.file_path, 'rb') as f_in, lzma.open(compressed_file_path, 'wb') as f_out:
                f_out.writelines(f_in)
        elif self.method == "bz2":
            compressed_file_path = os.path.join(self.destination_folder, os.path.basename(self.file_path) + ".bz2")
            with open(self.file_path, 'rb') as f_in, bz2.open(compressed_file_path, 'wb') as f_out:
                f_out.writelines(f_in)
        self.completed_signal.emit(True, "Compression Complete!")

    def decompress(self):
        decompressed_file_path = os.path.join(self.destination_folder, os.path.basename(self.file_path).rsplit('.', 1)[0])
        if self.method == "gzip":
            with gzip.open(self.file_path, 'rb') as f_in, open(decompressed_file_path, 'wb') as f_out:
                f_out.writelines(f_in)
        elif self.method == "lzma":
            with lzma.open(self.file_path, 'rb') as f_in, open(decompressed_file_path, 'wb') as f_out:
                f_out.writelines(f_in)
        elif self.method == "bz2":
            with bz2.open(self.file_path, 'rb') as f_in, open(decompressed_file_path, 'wb') as f_out:
                f_out.writelines(f_in)
        self.completed_signal.emit(True, "Decompression Complete!")

class CmprssrApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Mode selection
        self.mode_group = QGroupBox("Mode:")
        mode_layout = QHBoxLayout()
        self.radio_compress = QRadioButton("Compress")
        self.radio_decompress = QRadioButton("Decompress")
        self.radio_compress.setChecked(True)
        mode_layout.addWidget(self.radio_compress)
        mode_layout.addWidget(self.radio_decompress)
        self.mode_group.setLayout(mode_layout)
        layout.addWidget(self.mode_group)

        # File selection
        self.label_file = QLabel("Select a file:")
        layout.addWidget(self.label_file)
        file_select_layout = QHBoxLayout()
        self.line_file_path = QLabel("No file selected.")
        self.line_file_path.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.btn_select_file = QPushButton("Select File")
        self.btn_select_file.clicked.connect(self.select_file)
        file_select_layout.addWidget(self.line_file_path, 1)
        file_select_layout.addWidget(self.btn_select_file)
        layout.addLayout(file_select_layout)

        # Method selection
        self.method_group = QGroupBox("Method:")
        method_layout = QHBoxLayout()
        self.radio_gzip = QRadioButton("gzip")
        self.radio_lzma = QRadioButton("lzma")
        self.radio_bz2 = QRadioButton("bz2")
        method_layout.addWidget(self.radio_gzip)
        method_layout.addWidget(self.radio_lzma)
        method_layout.addWidget(self.radio_bz2)
        self.method_group.setLayout(method_layout)
        layout.addWidget(self.method_group)

        # Destination folder selection
        self.label_destination = QLabel("Select destination folder:")
        layout.addWidget(self.label_destination)
        destination_layout = QHBoxLayout()
        self.line_destination = QLabel("No destination selected.")
        self.line_destination.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.btn_select_destination = QPushButton("Select Destination")
        self.btn_select_destination.clicked.connect(self.select_destination)
        destination_layout.addWidget(self.line_destination, 1)
        destination_layout.addWidget(self.btn_select_destination)
        layout.addLayout(destination_layout)

        # Process button
        self.btn_process = QPushButton("Start")
        self.btn_process.clicked.connect(self.start_process)
        layout.addWidget(self.btn_process)

        # Progress Bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.resize(500, 250)

    def select_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if self.file_path:
            self.line_file_path.setText(self.file_path)
            if self.radio_decompress.isChecked():
                # Automatically set method based on file extension
                if self.file_path.endswith(".gz"):
                    self.radio_gzip.setChecked(True)
                elif self.file_path.endswith(".xz"):
                    self.radio_lzma.setChecked(True)
                elif self.file_path.endswith(".bz2"):
                    self.radio_bz2.setChecked(True)

    def select_destination(self):
        self.destination_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if self.destination_folder:
            self.line_destination.setText(self.destination_folder)

    def start_process(self):
        mode = "compress" if self.radio_compress.isChecked() else "decompress"
        if not self.file_path:
            QMessageBox.warning(self, 'Warning', 'Please select a file.')
            return

        if not (self.radio_gzip.isChecked() or self.radio_lzma.isChecked() or self.radio_bz2.isChecked()):
            QMessageBox.warning(self, 'Warning', 'Please select a method.')
            return

        if not self.destination_folder:
            QMessageBox.warning(self, 'Warning', 'Please select a destination folder.')
            return

        method = ""
        if self.radio_gzip.isChecked():
            method = "gzip"
        elif self.radio_lzma.isChecked():
            method = "lzma"
        elif self.radio_bz2.isChecked():
            method = "bz2"

        # Disable buttons during processing
        self.disable_elements(True)

        self.thread = ProcessThread(self.file_path, mode, method, self.destination_folder)
        self.thread.completed_signal.connect(self.process_complete)
        self.thread.start()

    def process_complete(self, success, message):
        if success:
            QMessageBox.information(self, 'Success', message)
        else:
            QMessageBox.critical(self, 'Error', message)
        # Re-enable buttons after processing
        self.disable_elements(False)

    def disable_elements(self, disabled):
        self.btn_process.setDisabled(disabled)
        self.btn_select_destination.setDisabled(disabled)
        self.btn_select_file.setDisabled(disabled)
        self.radio_gzip.setDisabled(disabled)
        self.radio_lzma.setDisabled(disabled)
        self.radio_bz2.setDisabled(disabled)
        self.radio_compress.setDisabled(disabled)
        self.radio_decompress.setDisabled(disabled)

app = QApplication(sys.argv)
window = CmprssrApp()
window.setWindowTitle('Cmprssr')
window.show()
sys.exit(app.exec())
