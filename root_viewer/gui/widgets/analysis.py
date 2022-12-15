from __future__ import annotations
from PyQt5.QtCore  import pyqtSignal
import re
from magicgui.widgets import Container, FunctionGui, RadioButtons, Container, TextEdit, Label
import textwrap
class AnalysisWidget:
    def __init__(self):

        #self._init_signals()

        import analysis.functions.filtering as filter_functions
        import analysis.functions.thresholding as thresholding_functions
        import analysis.functions.labeling as labeling_functions
        import analysis.functions.misc as misc_functions

        self.filter_functions_list, self.filter_functions_dict = self._create_functions_attr(filter_functions)
        self.thresholding_functions_list, self.thresholding_functions_dict = self._create_functions_attr(thresholding_functions)
        self.labeling_functions_list, self.labeling_functions_dict = self._create_functions_attr(labeling_functions)
        self.misc_functions_list, self.misc_functions_dict = self._create_functions_attr(misc_functions)

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI"""
        self._init_segmentation()
        self._init_filtering()
        self._init_thresholding()
        self._init_labeling()
        self._init_misc()
    
    def _init_segmentation(self):
        """Initialize the basic segmentation tab"""
        import analysis.basic_seg as basic_segmentation
        import analysis.adv_seg as advanced_segmentation
        self.basic_segmentation_widget = basic_segmentation.widget_wrapper()
        self.advanced_segmentation_widget = advanced_segmentation.plugin_dock_widget()
    
    def _init_filtering(self):
        """Initialize the filtering tab"""
        import analysis.functions.filtering as filter_functions
        self.filter_functions_list, self.filter_functions_dict = self._create_functions_attr(filter_functions)
        self.filtering_widget = FunctionsWidget(self.filter_functions_list, self.filter_functions_dict)
    
    def _init_thresholding(self):
        """Initialize the thresholding tab"""
        import analysis.functions.thresholding as thresholding_functions
        self.thresholding_functions_list, self.thresholding_functions_dict = self._create_functions_attr(thresholding_functions)
        self.thresholding_widget = FunctionsWidget(self.thresholding_functions_list, self.thresholding_functions_dict)

    def _init_labeling(self):
        """Initialize the labeling tab"""
        import analysis.functions.labeling as labeling_functions
        self.labeling_functions_list, self.labeling_functions_dict = self._create_functions_attr(labeling_functions)
        self.labeling_widget = FunctionsWidget(self.labeling_functions_list, self.labeling_functions_dict)

    def _init_misc(self):
        """Initialize the misc tab"""
        import analysis.functions.misc as misc_functions
        self.misc_functions_list, self.misc_functions_dict = self._create_functions_attr(misc_functions)
        self.misc_widget = FunctionsWidget(self.misc_functions_list, self.misc_functions_dict)

    def _create_functions_attr(self, module):
        """Create a list of function names and a dictionary of functions from a module"""
        from inspect import getmembers, isfunction
        functions = [name for name, value in getmembers(module, isfunction) if value.__module__ == module.__name__]
        functions = [i for i in functions if i[0] != '_']
        return functions, dict([(name,value) for name, value in getmembers(module, isfunction) if value.__module__ == module.__name__])

class FunctionsWidget:
    """Create a widget for selecting a function displaying its parameters"""
    function_changed = pyqtSignal(str)
    
    def __init__(self, functions=None, functions_dict=None):
        self.functions = functions
        self.functions_dict = functions_dict
        self._init_ui()
        
    def _init_ui(self):
        self._init_function()
        self._init_function_params()
        self._init_function_doc()
        self._init_layout()
    
    def _init_function(self):
        self.function = RadioButtons(choices=self.functions)
        self.function.changed.connect(self._update_function_doc)
        self.function.changed.connect(self.open_function_dialog)
    
    def _init_function_doc(self):
        self.function_doc = Label(value="Select a function", nullable=True)
    
    def _init_layout(self):
        self.layout = Container(widgets=[self.function, self.function_doc], scrollable=True)
    
    def set_functions(self, functions):
        self.function.choices = functions

    def set_function_doc(self, docs, doc):
        self.function_doc.value = self.format_function_doc(self.functions_dict[self.functions[0]].__doc__)
    
    def _init_function_params(self):
        self.func = Container(widgets=[])
        self.func_call = Container(widgets=[])

    def format_function_doc(self, doc):
        """Format the function docstring, converting
         the docstring into rich text html"""
        import inspect
        import os
        file_name = os.path.splitext(os.path.basename(inspect.getmodule(doc).__file__))[0]
        return f"""<h3>{doc.__name__}</h3><a href="https://wildrootlab.github.io/root-viewer/usage/{file_name}/root_viewer.analysis.functions.filtering.{doc.__name__}.html" style='color: gray';>{file_name} documentation</a></tt>"""

    def _update_function_doc(self, function):
        self.function_doc.value = self.format_function_doc(self.functions_dict[function])
    
    def open_function_dialog(self, function: str):
        self.func = Container(widgets=[])
        self.func_call = Container(widgets=[])
        self.func_call = FunctionGui(self.functions_dict[function], visible=False)
        self.func = FunctionGui.from_callable(self.functions_dict[function])
        self.layout.insert(2,self.func)
        self.layout.insert(3,self.func_call.call_button)

    def _format_function_doc(self, doc):
        """Format the function docstring, converting
         the docstring into rich text html"""
        from docstring_parser import parse
        ds = parse(doc)
        print(ds.params)
        ptemp = "<li><p><strong>{}</strong> (<em>{}</em>) - {}</p></li>"
        plist = [ptemp.format(p.arg_name, p.type_name, p.description) for p in ds.params]
        params = textwrap.wrap(f'<h3>Parameters</h3><ul>{"".join(plist)}</ul>', width=30)
        short = textwrap.wrap(f"<p>{ds.short_description}</p>" if ds.short_description else "", width=30)
        long = textwrap.wrap(f"<p>{ds.long_description}</p>" if ds.long_description else "", width=30)
        return re.sub(r"``?([^`]+)``?", r"<code>\1</code>", f"{short}{long}{params}")