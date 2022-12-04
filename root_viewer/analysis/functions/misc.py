from napari import layers, Viewer
from napari.types import ImageData, LabelsData, SurfaceData
import numpy as np
from scipy import ndimage as ndi
from skimage.filters import gaussian, sobel
from skimage.feature import peak_local_max
from skimage.morphology import binary_opening
from skimage.measure import label, marching_cubes
from skimage.segmentation import watershed

def split_touching_objects(binary:LabelsData, sigma: float = 3.5) -> LabelsData:
    """
    Takes a binary image and creates cuts in the objects similar to the ImageJ watershed algorithm. This splits connected objects when not to dense. 
    NOTE: If the nuclei are too dense, consider using stardist or cellpose.
    
    See also
    --------
    .. [1] https://imagej.nih.gov/ij/docs/menus/process.html#watershed
    .. [2] https://www.napari-hub.org/plugins/stardist-napari
    .. [3] https://www.napari-hub.org/plugins/cellpose-napari
    """
    def _sobel_3d(image):
        kernel = np.asarray([
            [
                [0, 0, 0],
                [0, 1, 0],
                [0, 0, 0]
            ], [
                [0, 1, 0],
                [1, -6, 1],
                [0, 1, 0]
            ], [
                [0, 0, 0],
                [0, 1, 0],
                [0, 0, 0]
            ]
        ])
        return ndi.convolve(image, kernel)
    binary = np.asarray(binary)

    # typical way of using scikit-image watershed
    distance = ndi.distance_transform_edt(binary)
    blurred_distance = gaussian(distance, sigma=sigma)
    fp = np.ones((3,) * binary.ndim)
    coords = peak_local_max(blurred_distance, footprint=fp, labels=binary)
    mask = np.zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    markers = label(mask)
    labels = watershed(-blurred_distance, markers, mask=binary)

    # identify label-cutting edges
    if len(binary.shape) == 2:
        edges = sobel(labels)
        edges2 = sobel(binary)
    else: # assuming 3D
        edges = _sobel_3d(labels)
        edges2 = _sobel_3d(binary)

    almost = np.logical_not(np.logical_xor(edges != 0, edges2 != 0)) * binary
    return binary_opening(almost)

def manually_merge_labels(labels_layer: layers.Labels, points_layer: layers.Points, viewer : Viewer):
    """
    Merge labels in a labels layer by clicking on them with a points layer.
    
    """
    if points_layer is None:
        points_layer = viewer.add_points([])
        points_layer.mode = 'ADD'
        return
    labels = np.asarray(labels_layer.data)
    points = points_layer.data

    label_ids = [labels.item(tuple([int(j) for j in i])) for i in points]

    # replace labels with minimum of the selected labels
    new_label_id = min(label_ids)
    for l in label_ids:
        if l != new_label_id:
            labels[labels == l] = new_label_id

    labels_layer.data = labels
    points_layer.data = []

def manually_split_labels(labels_layer: layers.Labels, points_layer: layers.Points, viewer: Viewer):
    """
    Split a label at the position of a point. The point is removed after splitting.
    
    Parameters
    ----------
    labels_layer: napari.layers.Labels
        The labels layer to split
    points_layer: napari.layers.Points
        The points layer to use as split positions
    
    Returns
    -------
    The new labels layer"""
    if points_layer is None:
        points_layer = viewer.add_points([])
        points_layer.mode = 'ADD'
        return

    labels = np.asarray(labels_layer.data)
    points = points_layer.data

    label_ids = [labels.item(tuple([int(j) for j in i])) for i in points]

    # make a binary image first
    binary = np.zeros(labels.shape, dtype=bool)
    new_label_id = min(label_ids)
    for l in label_ids:
        binary[labels == l] = True

    # origin: https://scikit-image.org/docs/dev/auto_examples/segmentation/plot_watershed.html
    from scipy import ndimage as ndi
    from skimage.segmentation import watershed
    #from skimage.feature import peak_local_max

    #distance = ndi.distance_transform_edt(binary)
    #coords = peak_local_max(distance, footprint=np.ones((3, 3)), labels=binary)
    mask = np.zeros(labels.shape, dtype=bool)
    for i in points:
        #mask[tuple(points)] = True
        mask[tuple([int(j) for j in i])] = True

    markers, _ = ndi.label(mask)
    new_labels = watershed(binary, markers, mask=binary)
    labels[binary] = new_labels[binary] + labels.max()

    labels_layer.data = labels
    points_layer.data = []

def extract_slice(image:ImageData, slice_index:int = 0, axis:int = 0) -> ImageData:
    """Extract (take) a slice from a stack."""
    return np.take(image, slice_index, axis=axis)

def wireframe(labels_layer: layers.Labels, viewer: Viewer) -> SurfaceData:
    """
    Use marching cubes to create a wireframe surface from a label image. This is useful to visualize the overlab between labels. 
    NOTE: This will nativly turn off the normals for faces and vertices.

    Parameters
    ----------
    labels_layer : napari.layers.Labels
        The labels layer to create the surface from
    Returns
    -------
    vertices : np.ndarray
        The vertices of the surface
    faces : np.ndarray
        The faces of the surface
    """
    labels = np.asarray(labels_layer.data)
    
    verts, faces, _, values = marching_cubes(labels)
    
    wireframe_layer = viewer.add_surface((verts, faces, np.linspace(0, 1, len(verts))))
    wireframe_layer.normals.face.visible = False
    wireframe_layer.normals.vertex.visible = False
    wireframe_layer.wireframe.visible = True