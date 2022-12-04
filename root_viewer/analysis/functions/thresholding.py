from napari.types import ImageData, LabelsData
import numpy as np

def threshold_otsu(image:ImageData) -> LabelsData:
    """Returns thresholded image based on Otsu's method.
    
    Parameters
    ----------
    image : (N, M[, ..., P]) ndarray, optional
        Grayscale input image.
    
    Returns
    -------
    threshold : ndarray
        Upper threshold value. All pixels with an intensity higher than
        this value are assumed to be foreground.
    
    References
    ----------
    .. [1] Wikipedia, https://en.wikipedia.org/wiki/Otsu's_Method
    
    Examples
    --------
    >>> from skimage.data import camera
    >>> image = camera()
    >>> thresh = threshold_otsu(image)
    >>> binary = image <= thresh
    
    .. image:: ../../images/skimage/sphx_glr_plot_thresholding_001.png

    Notes
    -----
    The input image must be grayscale.
    """
    from skimage.filters import threshold_otsu
    threshold = threshold_otsu(np.asarray(image))
    binary_otsu = image > threshold

    return binary_otsu * 1


def threshold_yen(image:ImageData) -> LabelsData:
    """Returns thresholded image based on Yen's method.

    Parameters
    ----------
    image : (N, M[, ..., P]) ndarray
        Grayscale input image.

    Returns
    -------
    threshold : ndarray
        Upper threshold value. All pixels with an intensity higher than
        this value are assumed to be foreground.

    References
    ----------
    .. [1] Yen J.C., Chang F.J., and Chang S. (1995) "A New Criterion
           for Automatic Multilevel Thresholding" IEEE Trans. on Image
           Processing, 4(3): 370-378. :DOI:`10.1109/83.366472`
    .. [2] Sezgin M. and Sankur B. (2004) "Survey over Image Thresholding
           Techniques and Quantitative Performance Evaluation" Journal of
           Electronic Imaging, 13(1): 146-165, :DOI:`10.1117/1.1631315`
           http://www.busim.ee.boun.edu.tr/~sankur/SankurFolder/Threshold_survey.pdf
    .. [3] ImageJ AutoThresholder code, http://fiji.sc/wiki/index.php/Auto_Threshold
    """
    from skimage.filters import threshold_yen
    return image > threshold_yen(image)


def threshold_isodata(image:ImageData, return_all:bool = False) -> LabelsData:
    """Returns thresholded image based on ISODATA method.

    Histogram-based threshold, known as Ridler-Calvard method or inter-means.
    Threshold values returned satisfy the following equality::
        
        threshold = (image[image <= threshold].mean() +
                     image[image > threshold].mean()) / 2.0
    
    That is, returned thresholds are intensities that separate the image into
    two groups of pixels, where the threshold intensity is midway between the
    mean intensities of these groups.

    For integer images, the above equality holds to within one; for floating-
    point images, the equality holds to within the histogram bin-width.
    Either image or hist must be provided. In case hist is given, the actual
    histogram of the image is ignored.

    Parameters
    ----------
    image : (N, M[, ..., P]) ndarray
        Grayscale input image.

    return_all : bool, optional
        If False (default), return only the lowest threshold that satisfies
        the above equality. If True, return all valid thresholds.

    Returns
    -------
    threshold : ndarray
        Threshold value(s).
    
    References
    ----------
    .. [1] Ridler, TW & Calvard, S (1978), "Picture thresholding using an
           iterative selection method"
           IEEE Transactions on Systems, Man and Cybernetics 8: 630-632,
           :DOI:`10.1109/TSMC.1978.4310039`
    .. [2] Sezgin M. and Sankur B. (2004) "Survey over Image Thresholding
           Techniques and Quantitative Performance Evaluation" Journal of
           Electronic Imaging, 13(1): 146-165,
           http://www.busim.ee.boun.edu.tr/~sankur/SankurFolder/Threshold_survey.pdf
           :DOI:`10.1117/1.1631315`
    .. [3] ImageJ AutoThresholder code,
           http://fiji.sc/wiki/index.php/Auto_Threshold
    """
    from skimage.filters import threshold_isodata
    return image > threshold_isodata(image, return_all)


def threshold_li(image:ImageData, tolerance:float = 2, initial_guess:float = 2) -> LabelsData:
    """Returns thresholded image by Li's iterative Minimum Cross Entropy method.
    
    Parameters
    ----------
    image : (N, M[, ..., P]) ndarray
        Grayscale input image.
    tolerance : float, optional
        Finish the computation when the change in the threshold in an iteration
        is less than this value. By default, this is half the smallest
        difference between intensity values in ``image``.
    initial_guess : float, optional
        Li's iterative method uses gradient descent to find the optimal
        threshold. If the image intensity histogram contains more than two
        modes (peaks), the gradient descent could get stuck in a local optimum.
        An initial guess for the iteration can help the algorithm find the
        globally-optimal threshold. A float value defines a specific start
        point, while a callable should take in an array of image intensities
        and return a float value. Example valid callables include
        ``numpy.mean`` (default), ``lambda arr: numpy.quantile(arr, 0.95)``,
        or even :func:`skimage.filters.threshold_otsu`.
    
    Returns
    -------
    threshold : ndarray
        Upper threshold value. All pixels with an intensity higher than
        this value are assumed to be foreground.
    
    References
    ----------
    .. [1] Li C.H. and Lee C.K. (1993) "Minimum Cross Entropy Thresholding"
           Pattern Recognition, 26(4): 617-625
           :DOI:`10.1016/0031-3203(93)90115-D`
    .. [2] Li C.H. and Tam P.K.S. (1998) "An Iterative Algorithm for Minimum
           Cross Entropy Thresholding" Pattern Recognition Letters, 18(8): 771-776
           :DOI:`10.1016/S0167-8655(98)00057-9`
    .. [3] Sezgin M. and Sankur B. (2004) "Survey over Image Thresholding
           Techniques and Quantitative Performance Evaluation" Journal of
           Electronic Imaging, 13(1): 146-165
           :DOI:`10.1117/1.1631315`
    .. [4] ImageJ AutoThresholder code, http://fiji.sc/wiki/index.php/Auto_Threshold
    """
    from skimage.filters import threshold_li
    return image > threshold_li(image, tolerance, initial_guess)


def threshold_mean(image :ImageData) -> LabelsData:
    """Returns thresholded image based on the mean of grayscale values.
    
    Parameters
    ----------
    image : (N, M[, ..., P]) ndarray
        Grayscale input image.
    
    Returns
    -------
    threshold : ndarray
        Upper threshold value. All pixels with an intensity higher than
        this value are assumed to be foreground.
    
    References
    ----------
    .. [1] C. A. Glasbey, "An analysis of histogram-based thresholding
        algorithms," CVGIP: Graphical Models and Image Processing,
        vol. 55, pp. 532-537, 1993.
        :DOI:`10.1006/cgip.1993.1040`
    """
    from skimage.filters import threshold_mean
    return image > threshold_mean(image)


def threshold_minimum(image :ImageData) -> LabelsData:
    """Return threshold value based on minimum method.
    The histogram of the input ``image`` is computed if not provided and
    smoothed until there are only two maxima. Then the minimum in between is
    the threshold value.
    Either image or hist must be provided. In case hist is given, the actual
    histogram of the image is ignored.
    Parameters
    ----------
    image : (N, M[, ..., P]) ndarray, optional
        Grayscale input image.
    nbins : int, optional
        Number of bins used to calculate histogram. This value is ignored for
        integer arrays.
    max_num_iter : int, optional
        Maximum number of iterations to smooth the histogram.
    hist : array, or 2-tuple of arrays, optional
        Histogram to determine the threshold from and a corresponding array
        of bin center intensities. Alternatively, only the histogram can be
        passed.
    
    Returns
    -------
    threshold : float
        Upper threshold value. All pixels with an intensity higher than
        this value are assumed to be foreground.
    
    Raises
    ------
    RuntimeError
        If unable to find two local maxima in the histogram or if the
        smoothing takes more than 1e4 iterations.
    
    References
    ----------
    .. [1] C. A. Glasbey, "An analysis of histogram-based thresholding
           algorithms," CVGIP: Graphical Models and Image Processing,
           vol. 55, pp. 532-537, 1993.
    .. [2] Prewitt, JMS & Mendelsohn, ML (1966), "The analysis of cell
           images", Annals of the New York Academy of Sciences 128: 1035-1053
           :DOI:`10.1111/j.1749-6632.1965.tb11715.x`
    """
    from skimage.filters import threshold_minimum
    try:
        return image > threshold_minimum(image)
    except RuntimeError:
        from napari.utils.notifications import Notification 
        Notification(message='Unable to threshold image. Please try another method.', severity='INFO', title='Thresholding Error')
        return image > 0


def threshold_triangle(image:ImageData) -> LabelsData:
    """Return threshold value based on the triangle algorithm.
    
    Parameters
    ----------
    image : (N, M[, ..., P]) ndarray
        Grayscale input image.

    Returns
    -------
    threshold : ndarray
        Upper threshold value. All pixels with an intensity higher than
        this value are assumed to be foreground.
    
    References
    ----------
    .. [1] Zack, G. W., Rogers, W. E. and Latt, S. A., 1977,
       Automatic Measurement of Sister Chromatid Exchange Frequency,
       Journal of Histochemistry and Cytochemistry 25 (7), pp. 741-753
       :DOI:`10.1177/25.7.70454`
    .. [2] ImageJ AutoThresholder code,
       http://fiji.sc/wiki/index.php/Auto_Threshold
    """
    from skimage.filters import threshold_triangle
    return image > threshold_triangle(image)