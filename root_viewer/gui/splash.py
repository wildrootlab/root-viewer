import os
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen, QWidget

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        try:
            self.splash = QSplashScreen(QPixmap(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons", "logo_dark.png")))
            self.splash.show()
        except: 
            pass
    
    def close_splash(self):
        self.splash.close()