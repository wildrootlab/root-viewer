from PyQt5.QtWidgets import QApplication
import qdarktheme
import sys
import app, splash


if __name__ == "__main__":
    splash = splash.SplashScreen()
    qapp = QApplication.instance()
    if not qapp:
        qapp = QApplication(sys.argv)
    qapp.setStyleSheet(qdarktheme.load_stylesheet())
    app = app.MainWindow()
    app.show()
    splash.close_splash()
    app.activateWindow()
    app.raise_()
    qapp.exec_()