from napari.types import ImageData, LabelsData
import numpy as np
from scipy import ndimage as ndi
from skimage.restoration import rolling_ball


def gaussian_blur(image:ImageData, sigma: float = 1) -> ImageData:
    """Multi-dimensional Gaussian filter

    Parameters
    ----------
    image : array-like
        Input image (grayscale or color) to filter.
    sigma : scalar or sequence of scalars, optional
        Standard deviation for Gaussian kernel. The standard
        deviations of the Gaussian filter are given for each axis as a
        sequence, or as a single number, in which case it is equal for
        all axes.

    Returns
    -------
    filtered_image : ndarray
        the filtered image
    
    Notes
    -----
    This function is a wrapper around :func:`scipy.ndi.gaussian_filter`.
    Integer arrays are converted to float.
    The ``output`` should be floating point data type since gaussian converts
    to float provided ``image``. If ``output`` is not provided, another array
    will be allocated and returned as the result.
    
    The multi-dimensional filter is implemented as a sequence of
    one-dimensional convolution filters. The intermediate arrays are
    stored in the same data type as the output. Therefore, for output
    types with a limited precision, the results may be imprecise
    because intermediate results may be stored with insufficient
    precision.
    """
    from skimage.filters import gaussian
    return gaussian(image, sigma)


def gaussian_laplace(image:ImageData, sigma: float = 2)-> ImageData:
    """Multidimensional Laplace filter using Gaussian second derivatives.

    Parameters
    ----------
    input : ndarray
        The input array.
    sigma : float
        The standard deviations of the Gaussian filter are given for
        each axis as a sequence, or as a single number, in which case
        it is equal for all axes.

    Returns
    -------
    laplace : ndarray
        The array in which to place the output, or the dtype of the returned array. By default an array of the same dtype as input will be created.
    
    .. image:: ../../images/skimage/scipy-ndimage-gaussian_laplace-1.png
    """
    return ndi.gaussian_laplace(image.astype(float), sigma)

def percentile_filter(image:ImageData, percentile : float = 50, size: float = 2)-> ImageData:
    """The percentile filter is similar to the median-filter but it allows specifying the percentile.
    The percentile-filter with percentile==50 is equal to the median-filter.
    
    Parameters
    ----------
    percentile : scalar
        The percentile parameter may be less than zero, i.e.,
        percentile = -20 equals percentile = 80
    size_foot : flaot
        Gives the shape that is taken from the input array, at every element position, to define the input to the filter function. We adjust size to the number of dimensions of the input array, so that, if the size is 2, then the actual size used for the filtering is (2,2,2). 

    Returns
    -------
    percentile_filter : ndarray
        Filtered array. Has the same shape as `input`.
    
    .. image:: ../../images/skimage/scipy-ndimage-percentile_filter-1.png
    """
    return ndi.percentile_filter(image.astype(float), percentile=percentile, size=int(size * 2 + 1))

def sobel(image:ImageData, axis : int = 0) -> ImageData:
    """Sobel edge filter.

    Parameters
    ----------
    image : ndarray
        Input image.
    axis : int, optional
        Axis along which the gradient is calculated. Default is 0.

    Returns
    -------
    sobel : ndarray
        The result of the filter.

    Notes
    -----
    The Sobel filter is a discrete differentiation operator, computing an
    approximation of the gradient of the image intensity function. It is
    based on convolving the image with a small, separable, and integer
    valued filter in the horizontal and vertical directions. The
    derivative approximations are more accurate when the filter is
    applied to smoothed images (using, for example, a Gaussian filter
    before applying the Sobel filter in each direction). The Sobel
    operator uses a 3x3 pixel neighborhood.

    .. image:: ../../images/skimage/scipy-ndimage-sobel-1.png
    """
    return ndi.sobel(image.astype(float))

def sobel_3d(image: ImageData) -> ImageData:
    """Sobel edge filter in 3D
    
    Parameters
    ----------
    image : ndarray
        Input image.
    axis : int, optional
        Axis along which the gradient is calculated. Default is 0.
    mode : str, optional
        The ``mode`` parameter determines how the array borders are
        handled, where ``cval`` is the value when mode is equal to
        'constant'. Default is 'reflect'.
    cval : scalar, optional
        Value to fill past edges of input if ``mode`` is 'constant'.
        Default is 0.0

    .. image:: ../../images/skimage/scipy-ndimage-sobel-1.png
    """
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


def white_tophat(image:ImageData, size: float = 2)-> ImageData:
    """Multidimensional white tophat filter.
    
    Parameters
    ----------
    input : array_like
        Input.
    size : tuple of ints
        Shape of a flat and full structuring element used for the filter.
        Optional if `footprint` or `structure` is provided.
    
    Returns
    -------
    output : ndarray
        Result of the filter of `input` with `structure`.

    See also
    --------
    black_tophat
    """
    return ndi.white_tophat(image.astype(float), size=int(size * 2 + 1), )


def black_tophat(image:ImageData, size: float = 2)-> ImageData:
    """Multidimensional black tophat filter.

    Parameters
    ----------
    input : array_like
        Input.
    size : tuple of ints, optional
        Shape of a flat and full structuring element used for the filter.
        Optional if `footprint` or `structure` is provided.

    Returns
    -------
    black_tophat : ndarray
        Result of the filter of `input` with `structure`.
    
    See also
    --------
    white_tophat

    """
    return ndi.black_tophat(image.astype(float), size=int(size * 2 + 1))


def minimum_filter(image:ImageData, size: float = 2)-> ImageData:
    """Calculate a multidimensional minimum filter. Can be used for noise and background removal.
    
    Parameters
    ----------
    image : ImageData
    size : flaot
        Gives the shape that is taken from the input array, at every element position, to define the input to the filter function. We adjust size to the number of dimensions of the input array, so that, if the size is 2, then the actual size used for the filtering is (2,2,2). 

    Returns
    -------
    minimum_filter : ndarray
        Filtered array. Has the same shape as `input`.
    
    Notes
    -----
    A sequence of modes (one per axis) is only supported when the footprint is
    separable. Otherwise, a single mode string must be provided.
    
    .. image:: ../../images/skimage/scipy-ndimage-minimum_filter-1.png
    """
    return ndi.minimum_filter(image.astype(float), size=size * 2 + 1)


def median_filter(image:ImageData, size: float = 2)-> ImageData:
    """Calculate a multidimensional median filter.

    Parameters
    ----------
    image : ImageData
    size : flaot
        Gives the shape that is taken from the input array, at every element position, to define the input to the filter function. We adjust size to the number of dimensions of the input array, so that, if the size is 2, then the actual size used for the filtering is (2,2,2). 
    
    Returns
    -------
    median_filter : ndarray
        Filtered array. Has the same shape as `input`.
    
    Notes
    -----
    For 2-dimensional images with ``uint8``, ``float32`` or ``float64`` dtypes
    the specialised function `scipy.signal.medfilt2d` may be faster. It is
    however limited to constant mode with ``cval=0``.
    
    .. image:: ../../images/skimage/scipy-ndimage-median_filter-1.png
    """
    return ndi.median_filter(image.astype(float), size=int(size * 2 + 1))


def maximum_filter(image:ImageData, size: float = 2)-> ImageData:
    """Calculate a multidimensional maximum filter. In the context of cell segmentation it can be used to make membranes wider and close small gaps of insufficient staining.

    Parameters
    ----------
    image : ImageData
    size : flaot
        Gives the shape that is taken from the input array, at every element position, to define the input to the filter function. We adjust size to the number of dimensions of the input array, so that, if the size is 2, then the actual size used for the filtering is (2,2,2). 

    Returns
    -------
    maximum_filter : ndarray
        Filtered array. Has the same shape as `input`.

    Notes
    -----
    A sequence of modes (one per axis) is only supported when the footprint is
    separable. Otherwise, a single mode string must be provided.
   
    .. image:: ../../images/skimage/scipy-ndimage-maximum_filter-1.png
    """
    return ndi.maximum_filter(image.astype(float), size=size * 2 + 1)


def morphological_gradient(image:ImageData, size: float = 2)-> ImageData:
    """ Apply gradient filter (similar to the Sobel operator) for edge detection / edge enhancement. This is similar to applying a Gaussian-blur to an image and afterwards the gradient operator.
    
    The morphological gradient is calculated as the difference between a
    dilation and an erosion of the input with a given structuring element.
    
    Parameters
    ----------
    image: array-like
        Image to detect edges in
    radius: float
        The filter will be applied with a kernel size of (radius * 2 + 1)
    
    Returns
    -------
    morphological_gradient : ndarray
        Morphological gradient of `input`.
    
    Notes
    -----
    For a flat structuring element, the morphological gradient
    computed at a given point corresponds to the maximal difference
    between elements of the input among the elements covered by the
    structuring element centered on the point.
    
    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Mathematical_morphology
    
    Examples
    --------
    >>> from scipy import ndimage
    >>> a = np.zeros((7,7), dtype=int)
    >>> a[2:5, 2:5] = 1
    >>> ndimage.morphological_gradient(a, size=(3,3))
    array([[0, 0, 0, 0, 0, 0, 0],
           [0, 1, 1, 1, 1, 1, 0],
           [0, 1, 1, 1, 1, 1, 0],
           [0, 1, 1, 0, 1, 1, 0],
           [0, 1, 1, 1, 1, 1, 0],
           [0, 1, 1, 1, 1, 1, 0],
           [0, 0, 0, 0, 0, 0, 0]])
    >>> # The morphological gradient is computed as the difference
    >>> # between a dilation and an erosion
    >>> ndimage.grey_dilation(a, size=(3,3)) -\\
    ...  ndimage.grey_erosion(a, size=(3,3))
    array([[0, 0, 0, 0, 0, 0, 0],
           [0, 1, 1, 1, 1, 1, 0],
           [0, 1, 1, 1, 1, 1, 0],
           [0, 1, 1, 0, 1, 1, 0],
           [0, 1, 1, 1, 1, 1, 0],
           [0, 1, 1, 1, 1, 1, 0],
           [0, 0, 0, 0, 0, 0, 0]])
    >>> a = np.zeros((7,7), dtype=int)
    >>> a[2:5, 2:5] = 1
    >>> a[4,4] = 2; a[2,3] = 3
    >>> a
    array([[0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0],
           [0, 0, 1, 3, 1, 0, 0],
           [0, 0, 1, 1, 1, 0, 0],
           [0, 0, 1, 1, 2, 0, 0],
           [0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0]])
    >>> ndimage.morphological_gradient(a, size=(3,3))
    array([[0, 0, 0, 0, 0, 0, 0],
           [0, 1, 3, 3, 3, 1, 0],
           [0, 1, 3, 3, 3, 1, 0],
           [0, 1, 3, 2, 3, 2, 0],
           [0, 1, 1, 2, 2, 2, 0],
           [0, 1, 1, 2, 2, 2, 0],
           [0, 0, 0, 0, 0, 0, 0]])
    """
    return ndi.morphological_gradient(image.astype(float), size=int(size * 2 + 1))


def subtract_background(image:ImageData, rolling_ball_radius: float = 5) -> ImageData:
    """Estimate background intensity by rolling/translating a kernel. This rolling ball algorithm estimates background intensity for a ndimage in case of uneven exposure. It is a generalization of the frequently used rolling ball algorithm [1]_.
    
    Parameters
    ----------
    image : ndarray
        The image to be filtered.
    rolling_ball_radius : int, optional
        Radius of a ball shaped kernel to be rolled/translated in the image.
        Used if ``kernel = None``.
   
    Returns
    -------
    background : ndarray
        The estimated background of the image.
    
    Notes
    -----
    For the pixel that has its background intensity estimated (without loss
    of generality at ``center``) the rolling ball method centers ``kernel``
    under it and raises the kernel until the surface touches the image umbra
    at some ``pos=(y,x)``. The background intensity is then estimated
    using the image intensity at that position (``image[pos]``) plus the
    difference of ``kernel[center] - kernel[pos]``.
    This algorithm assumes that dark pixels correspond to the background. If
    you have a bright background, invert the image before passing it to the
    function, e.g., using `utils.invert`. See the gallery example for details.
    This algorithm is sensitive to noise (in particular salt-and-pepper
    noise). If this is a problem in your image, you can apply mild
    gaussian smoothing before passing the image to this function.
    
    References
    ----------
    .. [1] Sternberg, Stanley R. "Biomedical image processing." Computer 1
           (1983): 22-34. :DOI:`10.1109/MC.1983.1654163`
   
    .. image:: ../../images/skimage/sphx_glr_plot_rolling_ball_001.png
    """
    background = rolling_ball(image, radius = rolling_ball_radius)
    return image - background


def binary_invert(binary_image:LabelsData) -> LabelsData:
    """Inverts a binary image
    
    Parameters
    ----------
    binary_image : ndarray
        The binary image to be inverted.
    
    Returns
    -------
    inverted : ndarray
        The inverted binary image.
    """
    return (np.asarray(binary_image) == 0) * 1


def sum_images(image1: ImageData, image2: ImageData, factor1: float = 1, factor2: float = 1) -> ImageData:
    """Add two images
    Parameters
    ----------
    image1 : ndarray
        The first image to be added.
    image2 : ndarray
        The second image to be added.
    factor1 : float
        The factor to multiply the first image with.
    factor2 : float
        The factor to multiply the second image with.
    
    Returns
    -------
    summed : ndarray
        The summed image.
    """
    return image1 * factor1 + image2 * factor2


def multiply_images(image1: ImageData, image2: ImageData) -> ImageData:
    """Multiply two images
    Parameters
    ----------
    image1 : ndarray
        The first image to be multiplied.
    image2 : ndarray
        The second image to be multiplied.
    
    Returns
    -------
    multiplied : ndarray
        The multiplied image.
    """
    return image1 * image2


def divide_images(image1: ImageData, image2: ImageData) -> ImageData:
    """Divide one image by another
    
    Parameters
    ----------
    image1 : ndarray
        The image to be divided.
    image2 : ndarray
        The image to divide by.
    
    Returns
    -------
    divided : ndarray
        The divided image.
    """
    return image1 / image2


def invert_image(image: ImageData, signed: bool = False) -> ImageData:
    """Inverts the intensity range of the input image, so that the dtype maximum
    is now the dtype minimum, and vice-versa. 
    
    This operation is slightly different depending on the input dtype:
    - unsigned integers: subtract the image from the dtype maximum
    - signed integers: subtract the image from -1 (see Notes)
    - floats: subtract the image from 1 (if signed_float is False, so we
      assume the image is unsigned), or from 0 (if signed_float is True).
    
    See the examples for clarification.
    
    Parameters
    ----------
    image : ndarray
        Input image.
    signed_float : bool, optional
        If True and the image is of type float, the range is assumed to
        be [-1, 1]. If False and the image is of type float, the range is
        assumed to be [0, 1].
    
    Returns
    -------
    inverted : ndarray
        Inverted image.
    
    Notes
    -----
    Ideally, for signed integers we would simply multiply by -1. However,
    signed integer ranges are asymmetric. For example, for np.int8, the range
    of possible values is [-128, 127], so that -128 * -1 equals -128! By
    subtracting from -1, we correctly map the maximum dtype value to the
    minimum.
    
    Examples
    --------
    >>> img = np.array([[100,  0, 200],
    ...                 [  0, 50,   0],
    ...                 [ 30,  0, 255]], np.uint8)
    >>> invert(img)
    array([[155, 255,  55],
           [255, 205, 255],
           [225, 255,   0]], dtype=uint8)
    >>> img2 = np.array([[ -2, 0, -128],
    ...                  [127, 0,    5]], np.int8)
    >>> invert(img2)
    array([[   1,   -1,  127],
           [-128,   -1,   -6]], dtype=int8)
    >>> img3 = np.array([[ 0., 1., 0.5, 0.75]])
    >>> invert(img3)
    array([[1.  , 0.  , 0.5 , 0.25]])
    >>> img4 = np.array([[ 0., 1., -1., -0.25]])
    >>> invert(img4, signed_float=True)
    array([[-0.  , -1.  ,  1.  ,  0.25]])
    """
    from skimage import util
    return util.invert(image, signed)

def butterworth(image: ImageData, cutoff_frequency_ratio: float = 0.005, high_pass: bool = False,
                order: float = 2) -> ImageData:
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

    Returns
    -------
    result : ndarray
        The Butterworth-filtered image.
    
    Notes
    -----
    A band-pass filter can be achieved by combining a high-pass and low-pass
    filter. The user can increase `npad` if boundary artifacts are apparent.
    The "Butterworth filter" used in image processing textbooks (e.g. [1]_,
    [2]_) is often the square of the traditional Butterworth filters as
    described by [3]_, [4]_. The squared version will be used here if
    `squared_butterworth` is set to ``True``. The lowpass, squared Butterworth
    filter is given by the following expression for the lowpass case:

    .. math::

        H_{low}(f) = \\frac{1}{1 + \\left(\\frac{f}{c f_s}\\right)^{2n}}
    
    with the highpass case given by

    .. math::

        H_{hi}(f) = 1 - H_{low}(f)
    
    where :math:`f=\\sqrt{\\sum_{d=0}^{\\mathrm{ndim}} f_{d}^{2}}` is the
    absolute value of the spatial frequency, :math:`f_s` is the sampling
    frequency, :math:`c` the ``cutoff_frequency_ratio``, and :math:`n` is the
    filter `order` [1]_. When ``squared_butterworth=False``, the square root of
    the above expressions are used instead.
    Note that ``cutoff_frequency_ratio`` is defined in terms of the sampling
    frequency, :math:`f_s`. The FFT spectrum covers the Nyquist range
    (:math:`[-f_s/2, f_s/2]`) so ``cutoff_frequency_ratio`` should have a value
    between 0 and 0.5. The frequency response (gain) at the cutoff is 0.5 when
    ``squared_butterworth`` is true and :math:`1/\\sqrt{2}` when it is false.
    
    Examples
    --------
    Apply a high-pass and low-pass Butterworth filter to a grayscale and
    color image respectively:
    >>> from skimage.data import camera, astronaut
    >>> from skimage.filters import butterworth
    >>> high_pass = butterworth(camera(), 0.07, True, 8)
    >>> low_pass = butterworth(astronaut(), 0.01, False, 4, channel_axis=-1)

    .. image:: ../../images/skimage/sphx_glr_plot_butterworth_001.png
    
    References
    ----------
    .. [1] Russ, John C., et al. The Image Processing Handbook, 3rd. Ed.
           1999, CRC Press, LLC.
    .. [2] Birchfield, Stan. Image Processing and Analysis. 2018. Cengage
           Learning.
    .. [3] Butterworth, Stephen. "On the theory of filter amplifiers."
           Wireless Engineer 7.6 (1930): 536-541.
    .. [4] https://en.wikipedia.org/wiki/Butterworth_filter
    """
    from skimage.filters import butterworth
    return butterworth(image, cutoff_frequency_ratio, high_pass, order)