from PyQt5.QtWidgets import QApplication
import qdarktheme
import sys
import gui.main_window, gui.splash

if __name__ == "__main__":
    qapp = QApplication.instance()
    if not qapp:
        qapp = QApplication(sys.argv)
    splash = gui.splash.SplashScreen()
    qapp.setStyleSheet(qdarktheme.load_stylesheet())
    app = gui.main_window.MainWindow()
    app.show()
    splash.close_splash()
    app.activateWindow()
    app.raise_()
    qapp.exec_()