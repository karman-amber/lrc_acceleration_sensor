# This is a sample Python script.
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from gui.mcps_mainForm import MainWindow


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
