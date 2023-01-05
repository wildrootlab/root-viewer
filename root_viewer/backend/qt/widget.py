from typing import List, Optional
from uuid import UUID, uuid4

from qtpy.QtWidgets import QWidget


class Widget:
    """Widget is a pydantic model that represents a widget in the application layout.

    Parameters
    ----------
        widget : Optional[QWidget]
            The widget to add to the layout.
        uid : UUID
            The unique identifier for the widget.
        name : str
            The name of the widget.
        parent : Optional[str]
            The name of the parent widget.
        area : str
            The area of the layout to add the widget to.
        allowed_areas : List[str]
            The areas the widget is allowed to be placed in.
        visible : bool
            Whether the widget is visible.
        floating : bool
            Whether the widget is floating.
        closable : bool
            Whether the widget is closable.
        docked : bool
            Whether the widget is docked.
        collapsed : bool
            Whether the widget is collapsed.
    """

    def __init__(
        self,
        widget: Optional[QWidget] = QWidget,
        uid: UUID = uuid4(),
        name: str = "Widget",
        parent: Optional[str] = None,
        area: str = "left",
        allowed_areas: List[str] = ["left", "right"],
        visible: bool = True,
        floating: bool = False,
        closable: bool = True,
        docked: bool = True,
        collapsed: bool = False,
    ):
        super().__init__()
        self.widget = widget
        self.uid = uid
        self.name = name
        self.parent = parent
        self.area = area
        self.allowed_areas = allowed_areas
        self.visible = visible
        self.floating = floating
        self.closable = closable
        self.docked = docked
        self.collapsed = collapsed
