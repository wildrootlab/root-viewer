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
        self._init_filtering()
        self._init_thresholding()
        self._init_labeling()
        self._init_misc()
        #
        #self._init_layout()
    
    def _init_filtering(self):
        import analysis.functions.filtering as filter_functions
        self.filter_functions_list, self.filter_functions_dict = self._create_functions_attr(filter_functions)
        self.filtering_widget = FunctionsWidget(self.filter_functions_list, self.filter_functions_dict)

    
    def _init_thresholding(self):
        import analysis.functions.thresholding as thresholding_functions
        self.thresholding_functions_list, self.thresholding_functions_dict = self._create_functions_attr(thresholding_functions)
        self.thresholding_widget = FunctionsWidget(self.thresholding_functions_list, self.thresholding_functions_dict)
    


    def _init_labeling(self):
        import analysis.functions.labeling as labeling_functions
        self.labeling_functions_list, self.labeling_functions_dict = self._create_functions_attr(labeling_functions)
        self.labeling_widget = FunctionsWidget(self.labeling_functions_list, self.labeling_functions_dict)


    
    def _init_misc(self):
        import analysis.functions.misc as misc_functions
        self.misc_functions_list, self.misc_functions_dict = self._create_functions_attr(misc_functions)
        self.misc_widget = FunctionsWidget(self.misc_functions_list, self.misc_functions_dict)

    
    def _create_functions_attr(self, module):
        from inspect import getmembers, isfunction
        functions = [name for name, value in getmembers(module, isfunction) if value.__module__ == module.__name__]
        functions = [i for i in functions if i[0] != '_']
        return functions, dict([(name,value) for name, value in getmembers(module, isfunction) if value.__module__ == module.__name__])

from magicgui.widgets import RadioButtons, Container, Label, TextEdit
from PyQt5.QtCore  import pyqtSignal
from inspect import signature



class FunctionsWidget:
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
        self.function_doc = TextEdit(value="Select a function", nullable=True, enabled=False)
    
    def _init_layout(self):
        self.layout = Container(widgets=[self.function, self.function_doc], scrollable=True)
    
    def set_functions(self, functions):
        self.function.choices = functions

    def set_function_doc(self, docs, doc):
        self.function_doc.value = self.format_function_doc(self.functions_dict[self.functions[0]].__doc__)
    
    def _init_function_params(self):
        self.func = Container(widgets=[])
        pass
    
    def format_function_doc(self, doc):
        """Format the function docstring"""
        import textwrap
        try:
            doc = doc.split('----------')[0]
        except: pass
        doc = textwrap.wrap(doc, width=50)
        doc = '\n'.join(doc)
        return doc

    def _update_function_doc(self, function):
        self.function_doc.value = self.format_function_doc(self.functions_dict[function].__doc__)
    
    def open_function_dialog(self, function: str):
        self.func.clear()
        self.func = Container.from_signature(signature(self.functions_dict[function]))
        self.layout.insert(2,self.func)
