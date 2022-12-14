## Advanced Segmentations

Implements a custom version of the [Stardist](https://github.com/stardist/stardist) segmentation algorithm. This is a deep learning based segmentation algorithm that can be used to segment objects in 2D and 3D images, it is specifcally adept for segmenting dense clusters. The algorithm is based on:
- Uwe Schmidt, Martin Weigert, Coleman Broaddus, and Gene Myers.  
[*Cell Detection with Star-convex Polygons*](https://arxiv.org/abs/1806.03535).  
International Conference on Medical Image Computing and Computer-Assisted Intervention (MICCAI), Granada, Spain, September 2018.

- Martin Weigert, Uwe Schmidt, Robert Haase, Ko Sugawara, and Gene Myers.  
[*Star-convex Polyhedra for 3D Object Detection and Segmentation in Microscopy*](http://openaccess.thecvf.com/content_WACV_2020/papers/Weigert_Star-convex_Polyhedra_for_3D_Object_Detection_and_Segmentation_in_Microscopy_WACV_2020_paper.pdf).  
The IEEE Winter Conference on Applications of Computer Vision (WACV), Snowmass Village, Colorado, March 2020

### Opening the plugin
To open the Stardist segmentation algorithm, select the `Advanced Segmentation` tab in the `Analysis Widget`. This will open the window shown below:
```{image} ../images/analysis/advanced_segmentation.png
:name: advanced segmentation widget
```

**Restore Defaults**: Restore default values for [inputs](#inputs) (exceptions: *Input Image*, *Image Axes*, *Custom Model*).

**Run**: Start the prediction with the selected inputs and create the [outputs](#outputs) when done.

All plugin activity is shown in the napari *activity dock*, which can be shown/hidden by clicking on the word `activity` next to the little arrow at the bottom right of the napari window.

### Inputs

The plugin does perform input validation, i.e. it will disable the `Run` button if it detects a problem with the selected inputs. Problematic input fields are highlighted with a "lightcoral" background color ![](https://via.placeholder.com/15/f08080/f08080.png), and their [*tooltips*](https://en.wikipedia.org/wiki/Tooltip) typically explain what the problem is. Some error messages are shown at the bottom in napari's status bar, such as for incompatibilities between multiple input fields. Input fields with warnings (also explained via tooltips) are highlighted with an orange background color ![](https://via.placeholder.com/15/ffa500/ffa500.png).

**Input Image**: Select a napari layer of type `Image` as the input.  
*Tooltip:* Shows the shape of the image.

**Image Axes**: String that describes the semantic image axes and their order, e.g. `YX` for a 2D image. This parameter is automatically chosen (i.e. guessed) when a new input image is selected and should work in most cases. Permissible axis values are: `X` (width/columns), `Y` (height/rows), `Z` (depth/planes), `C` (channels), `T` (frames/time).  
*Tooltip:* Shows the mapping of semantic axes to the shape of the selected input image.

**Predict on field of view (only for 2D models in 2D view)**: If enabled, the StarDist prediction is only applied to the current field of view of the napari viewer. As the name of this checkbox indicates, this only works for 2D StarDist models and when the napari viewer is in 2D viewing mode. The checkbox is not even shown if those conditions are not met.

#### *Neural Network Prediction*

**Model Type**: Choice whether to use registered pre-trained models (`2D`, `3D`) or provide a path to a model folder (`Custom 2D/3D`). Based on this choice, either the input for *Pre-trained Model* or *Custom Model* is shown below.  
(Further information regarding pre-trained models: [how to register your own model](https://nbviewer.org/github/CSBDeep/CSBDeep/blob/master/examples/other/technical.ipynb#Registry-for-pretrained-models), [model registration in StarDist](https://github.com/stardist/stardist/blob/f73cdc44f718d36844b38c1f1662dbb66d157182/stardist/models/__init__.py#L17-L29).)

**Pre-trained Model**: Select a registered pre-trained model from a list. The first time a model is selected, it is downloaded and cached locally.

**Custom Model**: Provide a path to a StarDist model folder, containing at least `config.json` and a compatible neural network weights file (with suffix `.h5` or `.hdf5`). If present, `thresholds.json` is also loaded and its values can be used via the button *Set optimized postprocessing thresholds (for selected model)*.

**Model Axes**: A read-only text field that shows the semantic axes that the currently selected model expects as input. Additionally, we show the number of expected input channels, e.g. `YXC[2]` to indicate that the model expects a 2D input image with 2 channels. Seeing the model axes is helpful to understand whether the axes of the input image are compatible or not.

**Normalize Image**: A checkbox to indicate whether to perform [percentile-based input image normalization](https://forum.image.sc/t/normalization-in-stardist/41696/2) or not. This should be checked if the input image wasn't [manually normalized](https://forum.image.sc/t/stardist-extension/37696/7) such that most pixel values are in the range 0 to 1. If unchecked, inputs *Percentile low* and *Percentile high* are hidden.

**Percentile low**: Percentile value of input pixel distribution that is mapped to 0 (~min value). If there aren't any outlier pixels in your image, you may use percentile `0` to do a standard [min-max image normalization](https://www.codecademy.com/article/normalization).

**Percentile high**: Percentile value of input pixel distribution that is mapped to 1 (~max value). If there aren't any outlier pixels in your image, you may use percentile `100` to do a standard [min-max image normalization](https://www.codecademy.com/article/normalization).

**Input image scaling**: Number or list of numbers (one per input axis) to scale the input image before prediction and rescale the output accordingly. For example, a value of `0.5` indicates that all spatial axes are downscaled to half their size before prediction, and that the outputs are scaled to double their size. This is useful to adapt to different object sizes in the input image.  
*Tooltip:* Shows the mapping of scale values to the semantic axes of the selected input image.

#### *NMS Postprocessing*

**Probability/Score Threshold**: Determine the number of object candidates to enter non-maximum suppression. Higher values lead to fewer segmented objects, but will likely avoid false positives. The selected model may have an associated threshold value, which can be loaded via the *Set optimized postprocessing thresholds (for selected model)* button.

**Overlap Threshold**: Determine when two objects are considered the same during non-maximum suppression. Higher values allow segmented objects to overlap substantially. The selected model may have an associated threshold value, which can be loaded via the *Set optimized postprocessing thresholds (for selected model)* button.

**Output Type**: Choose format of [outputs](#outputs) (see below for details). Selecting `Label Image` will create the outputs *StarDist labels* and *StarDist class labels* (for multi-class models only) as napari `Labels` layers. Selecting `Polygons / Polyhedra` will instead return the output *StarDist polygons* as a napari `Shapes` layer for a 2D model, or *StarDist polyhedra* as a napari `Surface` layer for a 3D model. Selecting `Both` will return both types of outputs.

#### *Advanced Options*

**Number of Tiles**: String `None` (to disable tiling) or list of integer numbers (one per axis of input image) to determine how the input image is tiled before the CNN prediction is computed on each tile individually. This is needed to avoid (GPU) memory issues that can occur for large input images. Note that the NMS postprocessing is still run only once with candidates from the predictions of all image tiles.  
*Tooltip:* Shows the mapping of tile values to the semantic axes of the selected input image.

**Normalization Axes**: String of semantic axes which are jointly normalized (if they are present in the input image). For example, the default value `ZYX` indicates that all spatial axes are always normalized together; if an image has multiple channels, the pixels will be normalized separately per channel (e.g. this is what typically makes sense for fluorescence microscopy where channels are independent). On the other hand, the channels in RGB color images typically need to be normalized jointly, hence using `ZYXC` makes sense in this case. Note: if an image is explicitly opened with `rgb=True` in napari, the channels are automatically normalized together.  
*Tooltip:* Shows a brief explanation.

**Time-lapse Labels**: If the input is a time-lapse/movie, each frame is first independently processed by StarDist. If `Separate per frame (no processing)` is chosen, the object ids in the label images of each frame are not modified, i.e. they are consecutive integers that always start at 1. Selecting `Unique through time` will cause object ids to be unique over time, i.e. the smallest object id in a given frame is larger than the largest object id of the previous frame. Finally, choosing `Match to previous frame (via overlap)` will perform a simple form of [greedy](https://en.wikipedia.org/wiki/Greedy_algorithm) matching/tracking, where object ids are propagated from one frame to the next based on object overlap.

**Show CNN Output**: Create additional [outputs](#outputs) (see below for details) *StarDist probability* and *StarDist distances* that show the direct results of the CNN prediction which are the inputs to the NMS postprocessing. Additionally, *StarDist class probabilities* is created for multi-class models.

**Set optimized postprocessing thresholds (for selected model)**: Button to set *Probability/Score Threshold* and *Overlap Threshold* to the values provided by the selected model. Nothing is changed if the model does not provide threshold values.

### Outputs

**StarDist polygons**: The detected/segmented 2D objects as polygons (napari `Shapes` layer).

**StarDist polyhedra**: The detected/segmented 3D objects as surfaces (napari `Surface` layer).

**StarDist labels**: The detected/segmented 2D/3D objects as a *label image* (napari `Labels` layer). In an integer-valued label image, the value of a given pixel denotes the id of the object that it belongs to. For example, all pixels with value 5 belong to the object with id 5. All background pixels (that don't belong to any object) have value 0.

**StarDist class labels** ([multi-class models](https://nbviewer.org/github/stardist/stardist/blob/master/examples/other2D/multiclass.ipynb) only): The classes of detected/segmented 2D/3D objects as a *semantic segmentation labeling* (napari `Labels` layer). The integer value of a given pixel denotes the class id of the object that it belongs to. For example, all pixels with value 3 belong to the object class 3. Note that all pixels that belong to a specific object instance (as returned by *StarDist labels*) do have the same object class here. All background pixels (that don't belong to an object class) have value 0.

**StarDist probability**: The object probabilities predicted by the neural network as a single-channel image (napari `Image` layer).

**StarDist distances**: The radial distances predicted by the neural network as a multi-channel image (napari `Image` layer).

**StarDist class probabilities** ([multi-class models](https://nbviewer.org/github/stardist/stardist/blob/master/examples/other2D/multiclass.ipynb) only): The object class probabilities predicted by the neural network as a multi-channel image (napari `Image` layer).