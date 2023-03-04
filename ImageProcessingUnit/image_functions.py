# The Python file contains functions for adjusting the frame size

import cv2

def rescale_frame(frame, scale):
    """
    Rescales the input frame by the specified scale factor.

    Args:
    - frame (numpy.ndarray): A numpy array representing a single frame of a video.
    - scale (float): A positive floating-point value specifying the scale factor by which to resize the frame.
    
    Returns:
    - numpy.ndarray: A numpy array representing the resized frame.

    Raises:
        None
    """
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)
    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)


def adjust_image_to_desired_shape(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    """
    Resizes and pads an image, while making sure the size of the image is a multiple of the 'stride' parameter.

    Args:
    - img (ndarray): The input image to be resized and padded.
    - new_shape (tuple): The desired output shape of the image, defaults to (640, 640).
    - color (tuple): The color of the padding, defaults to (114, 114, 114).
    - auto (bool): If True, adds padding to ensure the output image has minimum rectangle size, defaults to True.
    - scaleFill (bool): If True, stretches the image to fill the desired output shape, defaults to False.
    - scaleup (bool): If True, scales the image up to meet the desired output shape, defaults to True.
    - stride (int): The stride of the output image, defaults to 32.
    
    Returns:
    - tuple: A tuple containing the resized and padded image (ndarray), the scale ratio (tuple), and the amount of padding added to the width and height (tuple).

    Raises:
        None
    """
    # Ensure that new_shape is a tuple with two elements
    current_shape = img.shape[:2]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Calculate the scaling ratio for the image
    scale_ratio = min(new_shape[0] / current_shape[0], new_shape[1] / current_shape[1])
    if not scaleup:
        scale_ratio = min(scale_ratio, 1.0)

    # Compute padding
    ratio = scale_ratio, scale_ratio
    new_unpad = int(round(current_shape[1] * scale_ratio)), int(round(current_shape[0] * scale_ratio))
    width_padding = new_shape[1] - new_unpad[0]
    height_padding = new_shape[0] - new_unpad[1]
    if auto:
        width_padding %= stride
        height_padding %= stride
    elif scaleFill:
        width_padding, height_padding = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / current_shape[1], new_shape[0] / current_shape[0]

    # divide padding into 2 sides
    width_padding /= 2
    height_padding /= 2

    # resize
    if current_shape[::-1] != new_unpad:
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)

    top, bottom = int(round(height_padding - 0.1)), int(round(height_padding + 0.1))
    left, right = int(round(width_padding - 0.1)), int(round(width_padding + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    return img, ratio, (width_padding, height_padding)