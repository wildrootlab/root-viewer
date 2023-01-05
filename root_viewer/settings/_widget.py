from pydantic import BaseModel

from root_viewer.backend.qt.widget import Widget


class WidgetModel(BaseModel):
    widget: Widget
