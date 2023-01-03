from PyQt5.QtCore import QSettings


class Settings:
    def __init__(self):
        self.settings = QSettings("Root Viewer", "Root Viewer")
        self.settings.setFallbacksEnabled(False)
        self.get_settings()

    def get_settings(self):
        """Load Settings"""
        try:
            self.resize(self.settings.value("window_size"))
            self.move(self.settings.value("window_pos"))
        except:
            pass

    def set_settings(self):
        self.settings.setValue("window_size", self.size())
        self.settings.setValue("window_pos", self.pos())
