import sys
import subprocess
import socket
import os
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


class Controller(QWidget):
    def __init__(self):
        super().__init__()

        self.process = None

        self.setWindowTitle("Flower Clock Controller")

        layout = QVBoxLayout()

        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")

        self.start_btn.clicked.connect(self.start_app)
        self.stop_btn.clicked.connect(self.stop_app)

        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)

        self.setLayout(layout)

        self.update_buttons()

    def start_app(self):
        if self.process is None or self.process.poll() is not None:
            base_path = os.path.dirname(sys.executable)
            exe_path = os.path.join(base_path, "wallpaperGPT.exe")
            self.process = subprocess.Popen([exe_path], shell=True)
        self.update_buttons()

    
    def stop_app(self):
        # Try graceful shutdown via socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("localhost", 65432))
            s.sendall(b"exit")
            s.close()
        except:
            pass

        # Fallback: force kill if still running
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=2)
        self.process = None
        self.update_buttons()

    def update_buttons(self):
        running = self.process is not None and self.process.poll() is None

        self.start_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)


app = QApplication(sys.argv)
window = Controller()
window.show()
sys.exit(app.exec())
