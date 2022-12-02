import napari

import numpy as np
from scipy import ndimage as ndi
from skimage.filters import threshold_otsu as sk_threshold_otsu, gaussian, sobel
from skimage.segmentation import watershed
from skimage.feature import peak_local_max
from skimage.morphology import binary_opening
from skimage.measure import label
from skimage.morphology import local_maxima, local_minima
from skimage.restoration import rolling_ball
from skimage.measure import regionprops, marching_cubes, mesh_surface_area
from skimage.segmentation import relabel_sequential
from skimage.segmentation import clear_border
from skimage.segmentation import expand_labels as sk_expand_labels
from skimage import filters
import scipy
from scipy import ndimage

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

def split_touching_objects(binary:"napari.types.LabelsData", sigma: float = 3.5) -> "napari.types.LabelsData":
    """
    Takes a binary image and draws cuts in the objects similar to the ImageJ watershed algorithm [1].
    This allows cutting connected objects such as not to dense nuclei. If the nuclei are too dense,
    consider using stardist [2] or cellpose [3].
    See also
    --------
    .. [1] https://imagej.nih.gov/ij/docs/menus/process.html#watershed
    .. [2] https://www.napari-hub.org/plugins/stardist-napari
    .. [3] https://www.napari-hub.org/plugins/cellpose-napari
    """
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


def threshold_otsu(image:"napari.types.ImageData") -> "napari.types.LabelsData":
    """
    Applies Otsu's threshold selection method to an intensity image and returns a binary image with pixels==1 where
    intensity is above the determined threshold.
    See also
    """
    threshold = sk_threshold_otsu(np.asarray(image))
    binary_otsu = image > threshold

    return binary_otsu * 1


def threshold_yen(image :"napari.types.ImageData") -> "napari.types.LabelsData":
    """
    Binarize an image using Yen's method.
    Parameters
    ----------
    image: Image
    binary_image: napari.types.LabelsData
    """
    return image > filters.threshold_yen(image)


def threshold_isodata(image :"napari.types.ImageData") -> "napari.types.LabelsData":
    """
    Binarize an image using the IsoData / Ridler's method.
    The method is similar to ImageJ's "default" threshold.
    Parameters
    ----------
    image: Image
    binary_image: napari.types.LabelsData
    """
    return image > filters.threshold_isodata(image)


def threshold_li(image:"napari.types.ImageData") -> "napari.types.LabelsData":
    """
    Binarize an image using Li's method method.
    Parameters
    ----------
    image: Image
    binary_image: napari.types.LabelsData
    """
    return image > filters.threshold_li(image)


def threshold_mean(image :"napari.types.ImageData") -> "napari.types.LabelsData":
    """
    Binarize an image using the Mean method.
    Parameters
    ----------
    image: Image
    binary_image: napari.types.LabelsData
    """
    return image > filters.threshold_mean(image)


def threshold_minimum(image :"napari.types.ImageData") -> "napari.types.LabelsData":
    """
    Binarize an image using the Minimum method.
    Parameters
    ----------
    image: Image
    binary_image: napari.types.LabelsData
    """
    return image > filters.threshold_minimum(image)


def threshold_triangle(image:"napari.types.ImageData") -> "napari.types.LabelsData":
    """
    Binarize an image using the Triangle method.
    Parameters
    ----------
    image: Image
    binary_image: napari.types.LabelsData
    """
    return image > filters.threshold_triangle(image)


def gaussian_blur(image:"napari.types.ImageData", sigma: float = 1) -> "napari.types.ImageData":
    """
    Applies a Gaussian blur to an image with a defined sigma. Useful for denoising.
    """
    return gaussian(image, sigma)


def gaussian_laplace(image:"napari.types.ImageData", sigma: float = 2)-> "napari.types.ImageData":
    """
    Apply Laplace filter for edge detection / edge enhancement after applying a Gaussian-blur
    Parameters
    ----------
    image: array-like
        Image to detect edges in
    sigma: float
        The filter will be applied with this specified Gaussian-blur sigma
    Returns
    -------
    array-like
    """
    return scipy.ndimage.gaussian_laplace(image.astype(float), sigma)


def median_filter(image:"napari.types.ImageData", radius: float = 2)-> "napari.types.ImageData":
    """
    The median-filter allows removing noise from images. While locally averaging intensity, it
    is an edge-preserving filter.
    It is equal to a percentile-filter with percentile==50.
    In case applying the filter takes to much time, consider using a Gaussian blur instead.
    """
    return scipy.ndimage.median_filter(image.astype(float), size=int(radius * 2 + 1))


def percentile_filter(image:"napari.types.ImageData", percentile : float = 50, radius: float = 2)-> "napari.types.ImageData":
    """The percentile filter is similar to the median-filter but it allows specifying the percentile.
    The percentile-filter with percentile==50 is equal to the median-filter.
    """
    return scipy.ndimage.percentile_filter(image.astype(float), percentile=percentile, size=int(radius * 2 + 1))


def white_tophat(image:"napari.types.ImageData", radius: float = 2)-> "napari.types.ImageData":
    """
    The white top-hat filter removes bright regions from an image showing black islands.
    In the context of fluorescence microscopy, it allows removing intensity resulting from out-of-focus light.
    """
    return scipy.ndimage.white_tophat(image.astype(float), size=int(radius * 2 + 1))


def black_tophat(image:"napari.types.ImageData", radius: float = 2)-> "napari.types.ImageData":
    """
    The black top-hat filter removes bright regions from an image showing black islands.
    """
    return scipy.ndimage.black_tophat(image.astype(float), size=int(radius * 2 + 1))


def minimum_filter(image:"napari.types.ImageData", radius: float = 2)-> "napari.types.ImageData":
    """
    Local minimum filter
    Can be used for noise and background removal.
    """
    return scipy.ndimage.minimum_filter(image.astype(float), size=radius * 2 + 1)


def maximum_filter(image:"napari.types.ImageData", radius: float = 2)-> "napari.types.ImageData":
    """
    Local maximum filter
    In the context of cell segmentation it can be used to make membranes wider
    and close small gaps of insufficient staining.
    """
    return scipy.ndimage.maximum_filter(image.astype(float), size=radius * 2 + 1)


def morphological_gradient(image:"napari.types.ImageData", radius: float = 2)-> "napari.types.ImageData":
    """
    Apply gradient filter (similar to the Sobel operator) for edge detection / edge enhancement.
    This is similar to applying a Gaussian-blur to an image and afterwards the gradient operator
    Parameters
    ----------
    image: array-like
        Image to detect edges in
    radius: float
        The filter will be applied with a kernel size of (radius * 2 + 1)
    Returns
    -------
    array-like
    """
    return scipy.ndimage.morphological_gradient(image.astype(float), size=int(radius * 2 + 1))


def subtract_background(image:"napari.types.ImageData", rolling_ball_radius: float = 5) -> "napari.types.ImageData":
    """
    Subtract background in an image using the rolling-ball algorithm.
    """
    background = rolling_ball(image, radius = rolling_ball_radius)
    return image - background


def binary_invert(binary_image:"napari.types.LabelsData") -> "napari.types.LabelsData":
    """
    Inverts a binary image.
    """
    return (np.asarray(binary_image) == 0) * 1


def connected_component_labeling(binary_image: "napari.types.LabelsData", exclude_on_edges: bool = False) -> "napari.types.LabelsData":
    """
    Takes a binary image and produces a label image with all separated objects labeled with
    different integer numbers.
    Parameters
    ----------
    exclude_on_edges : bool, optional
        Whether or not to clear objects connected to the label image border/planes (either xy, xz or yz).
    """
    if exclude_on_edges:
        # processing the image, which is not a timelapse
        return remove_labels_on_edges(label(np.asarray(binary_image)))

    else:
        return label(np.asarray(binary_image))


def remove_labels_on_edges(label_image: "napari.types.LabelsData") -> "napari.types.LabelsData":
    """
    Takes a label image and removes objects that touch the image border.
    The remaining labels are relabeled sequentially.
    """

    result = clear_border(np.asarray(label_image))
    relabeled_result, _, _ = relabel_sequential(result)
    return relabeled_result


def expand_labels(label_image: "napari.types.LabelsData", distance: float = 1) -> "napari.types.LabelsData":
    """
    Takes a label image and makes labels larger up to a given radius (distance).
    Labels will not overwrite each other while expanding. This operation is also known as label dilation.
    """

    return sk_expand_labels(np.asarray(label_image), distance=distance)


def voronoi_otsu_labeling(image:"napari.types.ImageData", spot_sigma: float = 2, outline_sigma: float = 2) -> "napari.types.LabelsData":
    """Voronoi-Otsu-Labeling is a segmentation algorithm for blob-like structures such as nuclei and granules with high signal intensity on low-intensity background. The two sigma parameters allow tuning the segmentation result. The first sigma controls how close detected cells     can be (spot_sigma) and the second controls how precise segmented objects are outlined (outline_sigma).
    """
    image = np.asarray(image)

    # blur and detect local maxima
    blurred_spots = gaussian(image, spot_sigma)
    spot_centroids = local_maxima(blurred_spots)

    # blur and threshold
    blurred_outline = gaussian(image, outline_sigma)
    threshold = sk_threshold_otsu(blurred_outline)
    binary_otsu = blurred_outline > threshold

    # determine local maxima within the thresholded area
    remaining_spots = spot_centroids * binary_otsu

    # start from remaining spots and flood binary image with labels
    labeled_spots = label(remaining_spots)
    labels = watershed(binary_otsu, labeled_spots, mask=binary_otsu)

    return labels


def gauss_otsu_labeling(image:"napari.types.ImageData", outline_sigma: float = 2) -> "napari.types.LabelsData":
    """Gauss-Otsu-Labeling can be used to segment objects such as nuclei with bright intensity on
    low intensity background images.
    The outline_sigma parameter allows tuning how precise segmented objects are outlined. Under the
    hood, this filter applies a Gaussian blur, Otsu-thresholding and connected component labeling.
    """
    image = np.asarray(image)

    # blur
    blurred_outline = gaussian(image, outline_sigma)

    # threshold
    threshold = sk_threshold_otsu(blurred_outline)
    binary_otsu = blurred_outline > threshold

    # connected component labeling
    labels = label(binary_otsu)

    return labels


def seeded_watershed(membranes:"napari.types.ImageData", labeled_nuclei:"napari.types.LabelsData") -> "napari.types.LabelsData":
    """
    Takes a image with bright (high intensity) membranes and an image with labeled objects such as nuclei.
    The latter serves as seeds image for a watershed labeling.
    """
    cells = watershed(
        np.asarray(membranes),
        np.asarray(labeled_nuclei)
    )
    return cells

def seeded_watershed_with_mask(membranes:"napari.types.ImageData", labeled_nuclei:"napari.types.LabelsData", mask:"napari.types.LabelsData") -> "napari.types.LabelsData":
    """
    Takes a image with bright (high intensity) membranes, an image with labeled objects such as nuclei and a mask imge, e.g. a binary image of the entire tissue of interest.
    The labeled nuclei serve as seeds image for a watershed labeling and the mask for constrainting the flooding.
    """
    cells = watershed(
        np.asarray(membranes),
        np.asarray(labeled_nuclei),
        mask=mask
    )
    return cells


def local_minima_seeded_watershed(image:"napari.types.ImageData", spot_sigma: float = 10, outline_sigma: float = 0) -> "napari.types.LabelsData":
    """
    Segment cells in images with fluorescently marked membranes.
    The two sigma parameters allow tuning the segmentation result. The first sigma controls how close detected cells
    can be (spot_sigma) and the second controls how precise segmented objects are outlined (outline_sigma). Under the
    hood, this filter applies two Gaussian blurs, local minima detection and a seeded watershed.
    """

    image = np.asarray(image)

    spot_blurred = gaussian(image, sigma=spot_sigma)

    spots = label(local_minima(spot_blurred))

    if outline_sigma == spot_sigma:
        outline_blurred = spot_blurred
    else:
        outline_blurred = gaussian(image, sigma=outline_sigma)

    return watershed(outline_blurred, spots)


def thresholded_local_minima_seeded_watershed(image:"napari.types.ImageData", spot_sigma: float = 3, outline_sigma: float = 0, minimum_intensity: float = 500) -> "napari.types.LabelsData":
    """
    Segment cells in images with marked membranes that have a high signal intensity.
    The two sigma parameters allow tuning the segmentation result. The first sigma controls how close detected cells
    can be (spot_sigma) and the second controls how precise segmented objects are outlined (outline_sigma). Under the
    hood, this filter applies two Gaussian blurs, local minima detection and a seeded watershed.
    Afterwards, all objects are removed that have an average intensity below a given minimum_intensity
    """
    labels = local_minima_seeded_watershed(image, spot_sigma=spot_sigma, outline_sigma=outline_sigma)

    # measure intensities
    stats = regionprops(labels, image)
    intensities = [r.mean_intensity for r in stats]

    # filter labels with low intensity
    new_label_indices, _, _ = relabel_sequential((np.asarray(intensities) > minimum_intensity) * np.arange(labels.max()))
    new_label_indices = np.insert(new_label_indices, 0, 0)
    new_labels = np.take(np.asarray(new_label_indices, np.uint32), labels)

    return new_labels

def sum_images(image1: "napari.types.ImageData", image2: "napari.types.ImageData", factor1: float = 1, factor2: float = 1) -> "napari.types.ImageData":
    """Add two images"""
    return image1 * factor1 + image2 * factor2


def multiply_images(image1: "napari.types.ImageData", image2: "napari.types.ImageData") -> "napari.types.ImageData":
    """Multiply two images"""
    return image1 * image2


def divide_images(image1: "napari.types.ImageData", image2: "napari.types.ImageData") -> "napari.types.ImageData":
    """Divide one image by another"""
    return image1 / image2


def invert_image(image: "napari.types.ImageData") -> "napari.types.ImageData":
    """Invert an image. The exact math behind depends on the image type."""
    from skimage import util
    return util.invert(image)


def skeletonize(image: "napari.types.LabelsData") -> "napari.types.LabelsData":
    """
    Skeletonize labeled objects in an image. This can be useful to reduce objects such as neurons, roots and vessels
    with variable thickness to single pixel lines for further analysis.
    """
    from skimage import morphology
    if image.max() == 1:
        return morphology.skeletonize(image)
    else:
        result = np.zeros(image.shape)
        for i in range(1, image.max() + 1):
            skeleton = morphology.skeletonize(image == i)
            result = skeleton * i + result
        return result.astype(int)


def Manually_merge_labels(labels_layer: "napari.layers.Labels", points_layer: "napari.layers.Points", viewer : "napari.Viewer"):
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

def Manually_split_labels(labels_layer: "napari.layers.Labels", points_layer: "napari.layers.Points", viewer: "napari.Viewer"):
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

def wireframe(labels_layer: "napari.layers.Labels", viewer: "napari.Viewer") -> "napari.types.SurfaceData":
    labels = np.asarray(labels_layer.data)
    verts, faces, _, values = marching_cubes(labels)
    #surface_area_pixels = mesh_surface_area(verts, faces)
    wireframe_layer = viewer.add_surface((verts, faces, np.linspace(0, 1, len(verts))))
    wireframe_layer.normals.face.visible = False
    wireframe_layer.normals.vertex.visible = False
    wireframe_layer.wireframe.visible = True


def butterworth(image: "napari.types.ImageData", cutoff_frequency_ratio: float = 0.005, high_pass: bool = False,
                order: float = 2) -> "napari.types.ImageData":
    """Apply a Butterworth filter to enhance high or low frequency features.
    This filter is defined in the Fourier domain.
    Parameters
    ----------
    image : (M[, N[, ..., P]][, C]) ndarray
        Input image.
    cutoff_frequency_ratio : float, optional
        Determines the position of the cut-off relative to the shape of the
        FFT.
    high_pass : bool, optional
        Whether to perform a high pass filter. If False, a low pass filter is
        performed.
    order : float, optional
        Order of the filter which affects the slope near the cut-off. Higher
        order means steeper slope in frequency space.
    """
    from skimage.filters import butterworth as skimage_butterworth
    return skimage_butterworth(image, cutoff_frequency_ratio, high_pass, order)


def extract_slice(image:"napari.types.ImageData", slice_index:int = 0, axis:int = 0) -> "napari.types.ImageData":
    """Extract (take) a slice from a stack."""
    return np.take(image, slice_index, axis=axis)