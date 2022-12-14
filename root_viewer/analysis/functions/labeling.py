from napari.types import ImageData, LabelsData
import numpy as np
from skimage.filters import threshold_otsu, gaussian
from skimage.morphology import local_maxima, local_minima
from skimage.measure import label, regionprops
from skimage.segmentation import relabel_sequential as _relabel_sequential, clear_border as _clear_border, expand_labels, watershed as _watershed, random_walker as _random_walker

def remove_labels_on_edges(label_image: LabelsData, buffer_size:int = 1) -> LabelsData:
    """Clear objects connected to the label image border.
    
    Parameters
    ----------
    labels : (M[, N[, ..., P]]) array of int or bool
        Imaging data labels.
    
    buffer_size : int, optional
        The width of the border examined.  By default, only objects
        that touch the outside of the image are removed.

    Returns
    -------
    out : ndarray
        Imaging data labels with cleared borders
    
    Examples
    --------
    >>> import numpy as np
    >>> from skimage.segmentation import clear_border
    >>> labels = np.array([[0, 0, 0, 0, 0, 0, 0, 1, 0],
    ...                    [1, 1, 0, 0, 1, 0, 0, 1, 0],
    ...                    [1, 1, 0, 1, 0, 1, 0, 0, 0],
    ...                    [0, 0, 0, 1, 1, 1, 1, 0, 0],
    ...                    [0, 1, 1, 1, 1, 1, 1, 1, 0],
    ...                    [0, 0, 0, 0, 0, 0, 0, 0, 0]])
    >>> clear_border(labels)
    array([[0, 0, 0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 1, 0, 0, 0, 0],
           [0, 0, 0, 1, 0, 1, 0, 0, 0],
           [0, 0, 0, 1, 1, 1, 1, 0, 0],
           [0, 1, 1, 1, 1, 1, 1, 1, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0]])
    >>> mask = np.array([[0, 0, 1, 1, 1, 1, 1, 1, 1],
    ...                  [0, 0, 1, 1, 1, 1, 1, 1, 1],
    ...                  [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ...                  [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ...                  [1, 1, 1, 1, 1, 1, 1, 1, 1],
    ...                  [1, 1, 1, 1, 1, 1, 1, 1, 1]]).astype(bool)
    >>> clear_border(labels, mask=mask)
    array([[0, 0, 0, 0, 0, 0, 0, 1, 0],
           [0, 0, 0, 0, 1, 0, 0, 1, 0],
           [0, 0, 0, 1, 0, 1, 0, 0, 0],
           [0, 0, 0, 1, 1, 1, 1, 0, 0],
           [0, 1, 1, 1, 1, 1, 1, 1, 0],
           [0, 0, 0, 0, 0, 0, 0, 0, 0]])
    """

    result = _clear_border(np.asarray(label_image), buffer_size=buffer_size)
    relabeled_result, _, _ = _relabel_sequential(result)
    return relabeled_result


def expand_labels(label_image: LabelsData, distance: float = 1) -> LabelsData:
    """Expand labels in label image by ``distance`` pixels without overlapping.
    Given a label image, ``expand_labels`` grows label regions (connected components)
    outwards by up to ``distance`` pixels without overflowing into neighboring regions.
    More specifically, each background pixel that is within Euclidean distance
    of <= ``distance`` pixels of a connected component is assigned the label of that
    connected component.
    Where multiple connected components are within ``distance`` pixels of a background
    pixel, the label value of the closest connected component will be assigned (see
    Notes for the case of multiple labels at equal distance).
    
    Parameters
    ----------
    label_image : ndarray of dtype int
        label image
    distance : float
        Euclidean distance in pixels by which to grow the labels. Default is one.
    
    Returns
    -------
    enlarged_labels : ndarray of dtype int
        Labeled array, where all connected regions have been enlarged
    
    Notes
    -----
    Where labels are spaced more than ``distance`` pixels are apart, this is
    equivalent to a morphological dilation with a disc or hyperball of radius ``distance``.
    However, in contrast to a morphological dilation, ``expand_labels`` will
    not expand a label region into a neighboring region.
    This implementation of ``expand_labels`` is derived from CellProfiler [1]_, where
    it is known as module "IdentifySecondaryObjects (Distance-N)" [2]_.
    There is an important edge case when a pixel has the same distance to
    multiple regions, as it is not defined which region expands into that
    space. Here, the exact behavior depends on the upstream implementation
    of ``scipy.ndimage.distance_transform_edt``.
    
    See Also
    --------
    :func:`skimage.measure.label`, :func:`skimage.segmentation.watershed`, :func:`skimage.morphology.dilation`
    
    References
    ----------
    .. [1] https://cellprofiler.org
    .. [2] https://github.com/CellProfiler/CellProfiler/blob/082930ea95add7b72243a4fa3d39ae5145995e9c/cellprofiler/modules/identifysecondaryobjects.py#L559
    
    Examples
    --------
    >>> labels = np.array([0, 1, 0, 0, 0, 0, 2])
    >>> expand_labels(labels, distance=1)
    array([1, 1, 1, 0, 0, 2, 2])
    Labels will not overwrite each other:
    >>> expand_labels(labels, distance=3)
    array([1, 1, 1, 1, 2, 2, 2])
    In case of ties, behavior is undefined, but currently resolves to the
    label closest to ``(0,) * ndim`` in lexicographical order.
    >>> labels_tied = np.array([0, 1, 0, 2, 0])
    >>> expand_labels(labels_tied, 1)
    array([1, 1, 1, 2, 2])
    >>> labels2d = np.array(
    ...     [[0, 1, 0, 0],
    ...      [2, 0, 0, 0],
    ...      [0, 3, 0, 0]]
    ... )
    >>> expand_labels(labels2d, 1)
    array([[2, 1, 1, 0],
           [2, 2, 0, 0],
           [2, 3, 3, 0]])
    
    .. image:: ../../images/skimage/sphx_glr_plot_expand_labels_001.png
    """

    return expand_labels(np.asarray(label_image), distance=distance)


def voronoi_otsu_labeling(image:ImageData, spot_sigma: float = 2, outline_sigma: float = 2) -> LabelsData:
    """Voronoi-Otsu-Labeling is a segmentation algorithm for blob-like structures such as nuclei and granules with high signal intensity on low-intensity background. 
    
    Parameters
    ----------
    image : ndarray
        Input image.
    spot_sigma : float, optional
        Standard deviation of the Gaussian kernel used to smooth the image. Controls how close detected cells can be
    outline_sigma : float, optional
        Standard deviation of the Gaussian kernel used to smooth the outlines. Controls how precise segmented objects are.
    
    Returns
    -------
    labels : ndarray
        Labeled image.
    
    References
    ----------
    .. [1] https://github.com/clEsperanto/pyclesperanto_prototype/blob/master/demo/segmentation/voronoi_otsu_labeling.ipynb
    """
    image = np.asarray(image)

    # blur and detect local maxima
    blurred_spots = gaussian(image, spot_sigma)
    spot_centroids = local_maxima(blurred_spots)

    # blur and threshold
    blurred_outline = gaussian(image, outline_sigma)
    threshold = threshold_otsu(blurred_outline)
    binary_otsu = blurred_outline > threshold

    # determine local maxima within the thresholded area
    remaining_spots = spot_centroids * binary_otsu

    # start from remaining spots and flood binary image with labels
    labeled_spots = label(remaining_spots)
    labels = _watershed(binary_otsu, labeled_spots, mask=binary_otsu)

    return labels


def gauss_otsu_labeling(image:ImageData, outline_sigma: float = 2) -> LabelsData:
    """Gauss-Otsu-Labeling can be used to segment objects such as nuclei with bright intensity on
    low intensity background images.

    Parameters
    ----------
    image : ndarray
        Input image.
    outline_sigma : float, optional
        Standard deviation of the Gaussian kernel used to smooth the outlines. Controls how precise segmented objects are.
    
    Returns
    -------
    labels : ndarray
        Labeled image.
    """
    image = np.asarray(image)

    # blur
    blurred_outline = gaussian(image, outline_sigma)

    # threshold
    threshold = threshold_otsu(blurred_outline)
    binary_otsu = blurred_outline > threshold

    # connected component labeling
    labels = label(binary_otsu)

    return labels


def seeded_watershed(membranes:ImageData, labels:LabelsData) -> LabelsData:
    """Finds the watershed basins in `image` flooded from given `labels`.

    Parameters
    ----------
    image : ndarray (2-D, 3-D, ...)
        Data array where the lowest value points are labeled first.
    labels : int, or ndarray of int, same shape as `image`, optional
        The desired number of markers, or an array marking the basins with the
        values to be assigned in the label matrix. Zero means not a marker. If
        ``None`` (no markers given), the local minima of the image are used as
        markers.
    
    Returns
    -------
    out : ndarray
        A labeled matrix of the same type and shape as markers
    
    See Also
    --------
    random_walker : random walker segmentation
        A segmentation algorithm based on anisotropic diffusion, usually
        slower than the watershed but with good results on noisy data and
        boundaries with holes.
    
    Notes
    -----
    This function implements a watershed algorithm [1]_ [2]_ that apportions
    pixels into marked basins. The algorithm uses a priority queue to hold
    the pixels with the metric for the priority queue being pixel value, then
    the time of entry into the queue - this settles ties in favor of the
    closest marker.
    Some ideas taken from
    Soille, "Automated Basin Delineation from Digital Elevation Models Using
    Mathematical Morphology", Signal Processing 20 (1990) 171-182
    The most important insight in the paper is that entry time onto the queue
    solves two problems: a pixel should be assigned to the neighbor with the
    largest gradient or, if there is no gradient, pixels on a plateau should
    be split between markers on opposite sides.
    This implementation converts all arguments to specific, lowest common
    denominator types, then passes these to a C algorithm.
    Markers can be determined manually, or automatically using for example
    the local minima of the gradient of the image, or the local maxima of the
    distance function to the background for separating overlapping objects
    (see example).
    
    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Watershed_%28image_processing%29
    .. [2] http://cmm.ensmp.fr/~beucher/wtshed.html
    .. [3] Peer Neubert & Peter Protzel (2014). Compact Watershed and
           Preemptive SLIC: On Improving Trade-offs of Superpixel Segmentation
           Algorithms. ICPR 2014, pp 996-1001. :DOI:`10.1109/ICPR.2014.181`
           https://www.tu-chemnitz.de/etit/proaut/publications/cws_pSLIC_ICPR.pdf
    """
    cells = _watershed(
        np.asarray(membranes),
        np.asarray(labels)
    )
    return cells

def seeded_watershed_with_mask(membranes:ImageData, labels:LabelsData, mask:LabelsData) -> LabelsData:
    """ Finds the watershed basins in `image` flooded from given `labels` and masks is.

    Parameters
    ----------
    image : ndarray (2-D, 3-D, ...)
        Data array where the lowest value points are labeled first.
    markers : int, or ndarray of int, same shape as `image`, optional
        The desired number of markers, or an array marking the basins with the
        values to be assigned in the label matrix. Zero means not a marker. If
        ``None`` (no markers given), the local minima of the image are used as
        markers.
    mask : ndarray of bools or 0s and 1s, optional
        Array of same shape as `image`. Only points at which mask == True
        will be labeled.

    Returns
    -------
    out : ndarray
        A labeled matrix of the same type and shape as markers
    
    See Also
    --------
    random_walker : random walker segmentation
        A segmentation algorithm based on anisotropic diffusion, usually
        slower than the watershed but with good results on noisy data and
        boundaries with holes.
    
    Notes
    -----
    This function implements a watershed algorithm [1]_ [2]_ that apportions
    pixels into marked basins. The algorithm uses a priority queue to hold
    the pixels with the metric for the priority queue being pixel value, then
    the time of entry into the queue - this settles ties in favor of the
    closest marker.
    Some ideas taken from
    Soille, "Automated Basin Delineation from Digital Elevation Models Using
    Mathematical Morphology", Signal Processing 20 (1990) 171-182
    The most important insight in the paper is that entry time onto the queue
    solves two problems: a pixel should be assigned to the neighbor with the
    largest gradient or, if there is no gradient, pixels on a plateau should
    be split between markers on opposite sides.
    This implementation converts all arguments to specific, lowest common
    denominator types, then passes these to a C algorithm.
    Markers can be determined manually, or automatically using for example
    the local minima of the gradient of the image, or the local maxima of the
    distance function to the background for separating overlapping objects
    (see example).
    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Watershed_%28image_processing%29
    .. [2] http://cmm.ensmp.fr/~beucher/wtshed.html
    .. [3] Peer Neubert & Peter Protzel (2014). Compact Watershed and
           Preemptive SLIC: On Improving Trade-offs of Superpixel Segmentation
           Algorithms. ICPR 2014, pp 996-1001. :DOI:`10.1109/ICPR.2014.181`
           https://www.tu-chemnitz.de/etit/proaut/publications/cws_pSLIC_ICPR.pdf
    Examples
    --------
    The watershed algorithm is useful to separate overlapping objects.
    We first generate an initial image with two overlapping circles:
    
    >>> x, y = np.indices((80, 80))
    >>> x1, y1, x2, y2 = 28, 28, 44, 52
    >>> r1, r2 = 16, 20
    >>> mask_circle1 = (x - x1)**2 + (y - y1)**2 < r1**2
    >>> mask_circle2 = (x - x2)**2 + (y - y2)**2 < r2**2
    >>> image = np.logical_or(mask_circle1, mask_circle2)
    Next, we want to separate the two circles. We generate markers at the
    maxima of the distance to the background:
    >>> from scipy import ndimage as ndi
    >>> distance = ndi.distance_transform_edt(image)
    >>> from skimage.feature import peak_local_max
    >>> max_coords = peak_local_max(distance, labels=image,
    ...                             footprint=np.ones((3, 3)))
    >>> local_maxima = np.zeros_like(image, dtype=bool)
    >>> local_maxima[tuple(max_coords.T)] = True
    >>> markers = ndi.label(local_maxima)[0]
    Finally, we run the watershed on the image and markers:
    >>> labels = watershed(-distance, markers, mask=image)
    The algorithm works also for 3-D images, and can be used for example to
    separate overlapping spheres.
    """
    cells = _watershed(
        np.asarray(membranes),
        np.asarray(labels),
        mask=mask
    )
    return cells

def random_walker(membranes:ImageData, labels:LabelsData):
    """Random walker algorithm for segmentation from markers.
    
    Parameters
    ----------
    data : array_like
        Image to be segmented in phases. Gray-level `data` can be two- or
        three-dimensional; multichannel data can be three- or four-
        dimensional with `channel_axis` specifying the dimension containing
        channels. Data spacing is assumed isotropic unless the `spacing`
        keyword argument is used.
    labels : array_like
        Array of seed markers labeled with different positive integers
        for different phases. Zero-labeled pixels are unlabeled pixels.
        Negative labels correspond to inactive pixels that are not taken
        into account (they are removed from the graph). If labels are not
        consecutive integers, the labels array will be transformed so that
        labels are consecutive. In the multichannel case, `labels` should have
        the same shape as a single channel of `data`, i.e. without the final
        dimension denoting channels.

    Returns
    -------
    output : ndarray
        * If `return_full_prob` is False, array of ints of same shape
          and data type as `labels`, in which each pixel has been
          labeled according to the marker that reached the pixel first
          by anisotropic diffusion.
        * If `return_full_prob` is True, array of floats of shape
          `(nlabels, labels.shape)`. `output[label_nb, i, j]` is the
          probability that label `label_nb` reaches the pixel `(i, j)`
          first.
    
    See Also
    --------
    seeded_watershed : watershed segmentation
        A segmentation algorithm based on mathematical morphology
        and "flooding" of regions from markers.
    
    Notes
    -----
    Multichannel inputs are scaled with all channel data combined. Ensure all
    channels are separately normalized prior to running this algorithm.
    The `spacing` argument is specifically for anisotropic datasets, where
    data points are spaced differently in one or more spatial dimensions.
    Anisotropic data is commonly encountered in medical imaging.
    The algorithm was first proposed in [1]_.
    The algorithm solves the diffusion equation at infinite times for
    sources placed on markers of each phase in turn. A pixel is labeled with
    the phase that has the greatest probability to diffuse first to the pixel.
    The diffusion equation is solved by minimizing x.T L x for each phase,
    where L is the Laplacian of the weighted graph of the image, and x is
    the probability that a marker of the given phase arrives first at a pixel
    by diffusion (x=1 on markers of the phase, x=0 on the other markers, and
    the other coefficients are looked for). Each pixel is attributed the label
    for which it has a maximal value of x. The Laplacian L of the image
    is defined as:
       - L_ii = d_i, the number of neighbors of pixel i (the degree of i)
       - L_ij = -w_ij if i and j are adjacent pixels
    The weight w_ij is a decreasing function of the norm of the local gradient.
    This ensures that diffusion is easier between pixels of similar values.
    When the Laplacian is decomposed into blocks of marked and unmarked
    pixels::
        L = M B.T
            B A
    with first indices corresponding to marked pixels, and then to unmarked
    pixels, minimizing x.T L x for one phase amount to solving::
        A x = - B x_m
    where x_m = 1 on markers of the given phase, and 0 on other markers.
    This linear system is solved in the algorithm using a direct method for
    small images, and an iterative method for larger images.
    
    References
    ----------
    .. [1] Leo Grady, Random walks for image segmentation, IEEE Trans Pattern
        Anal Mach Intell. 2006 Nov;28(11):1768-83.
        :DOI:`10.1109/TPAMI.2006.233`.
    
    Examples
    --------
    >>> rng = np.random.default_rng()
    >>> a = np.zeros((10, 10)) + 0.2 * rng.random((10, 10))
    >>> a[5:8, 5:8] += 1
    >>> b = np.zeros_like(a, dtype=np.int32)
    >>> b[3, 3] = 1  # Marker for first phase
    >>> b[6, 6] = 2  # Marker for second phase
    >>> random_walker(a, b)  # doctest: +SKIP
    array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 2, 2, 2, 1, 1],
           [1, 1, 1, 1, 1, 2, 2, 2, 1, 1],
           [1, 1, 1, 1, 1, 2, 2, 2, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], dtype=int32)
    """
    return _random_walker(membranes, labels)

def local_minima_seeded_watershed(image:ImageData, spot_sigma: float = 10, outline_sigma: float = 0) -> LabelsData:
    """
    Segment cells in images with fluorescently marked membranes.
    The two sigma parameters allow tuning the segmentation result. The first sigma controls how close detected cells
    can be (spot_sigma) and the second controls how precise segmented objects are outlined (outline_sigma). Under the
    hood, this filter applies two Gaussian blurs, local minima detection and a seeded watershed.
    
    Finds the watershed basins in `image` flooded from given `labels`.

    Parameters
    ----------
    image : ndarray (2-D, 3-D, ...)
        Data array.
    spot_sigma: float
        The sigma parameter for the Gaussian blur applied to the image before local minima detection. Controls how close detected cells
    outline_sigma: float
        The sigma parameter for the Gaussian blur applied to the image before watershed segmentation. Controls how precise segmented objects are outlined.
    can be

    
    Returns
    -------
    out : ndarray
        A labeled matrix of the same type and shape as markers
    
    See Also
    --------
    random_walker : random walker segmentation
        A segmentation algorithm based on anisotropic diffusion, usually
        slower than the watershed but with good results on noisy data and
        boundaries with holes.
    
    Notes
    -----
    This function implements a watershed algorithm [1]_ [2]_ that apportions
    pixels into marked basins. The algorithm uses a priority queue to hold
    the pixels with the metric for the priority queue being pixel value, then
    the time of entry into the queue - this settles ties in favor of the
    closest marker.
    Some ideas taken from
    Soille, "Automated Basin Delineation from Digital Elevation Models Using
    Mathematical Morphology", Signal Processing 20 (1990) 171-182
    The most important insight in the paper is that entry time onto the queue
    solves two problems: a pixel should be assigned to the neighbor with the
    largest gradient or, if there is no gradient, pixels on a plateau should
    be split between markers on opposite sides.
    This implementation converts all arguments to specific, lowest common
    denominator types, then passes these to a C algorithm.
    Markers can be determined manually, or automatically using for example
    the local minima of the gradient of the image, or the local maxima of the
    distance function to the background for separating overlapping objects
    (see example).
    
    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Watershed_%28image_processing%29
    .. [2] http://cmm.ensmp.fr/~beucher/wtshed.html
    .. [3] Peer Neubert & Peter Protzel (2014). Compact Watershed and
           Preemptive SLIC: On Improving Trade-offs of Superpixel Segmentation
           Algorithms. ICPR 2014, pp 996-1001. :DOI:`10.1109/ICPR.2014.181`
           https://www.tu-chemnitz.de/etit/proaut/publications/cws_pSLIC_ICPR.pdf

    """

    image = np.asarray(image)

    spot_blurred = gaussian(image, sigma=spot_sigma)

    spots = label(local_minima(spot_blurred))

    if outline_sigma == spot_sigma:
        outline_blurred = spot_blurred
    else:
        outline_blurred = gaussian(image, sigma=outline_sigma)

    return _watershed(outline_blurred, spots)


def thresholded_local_minima_seeded_watershed(image:ImageData, spot_sigma: float = 3, outline_sigma: float = 0, minimum_intensity: float = 500) -> LabelsData:
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
    new_label_indices, _, _ = _relabel_sequential((np.asarray(intensities) > minimum_intensity) * np.arange(labels.max()))
    new_label_indices = np.insert(new_label_indices, 0, 0)
    new_labels = np.take(np.asarray(new_label_indices, np.uint32), labels)

    return new_labels


def connected_component_labeling(binary_image: LabelsData, exclude_on_edges: bool = False) -> LabelsData:
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

def skeletonize(image: LabelsData) -> LabelsData:
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