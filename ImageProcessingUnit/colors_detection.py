# Python code for Multiple Color Detection

import numpy as np
import cv2
from configs import SHOW_COLORS

def detect_colors(frame):
    """
    Detects the positions of caps based on their color.

    Args:
    - frame: A video frame in the BGR color space.

    Returns:
    - A list of players' caps indexes, each containing the player's color ID, x coordinate, and y coordinate.
    """
    framePlayersIndexes = []
    # Convert the imageFrame in
    # BGR(RGB color space) to
    # HSV(hue-saturation-value)
    # color space
    hsvFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Set range for red color and
    # define mask
    red_lower = np.array([136, 87, 111], np.uint8)
    red_upper = np.array([180, 255, 255], np.uint8)
    red_mask = cv2.inRange(hsvFrame, red_lower, red_upper)

    # Set range for orange color and
    # define mask
    orange_lower = np.array([5, 100, 100], np.uint8)
    orange_upper = np.array([20, 255, 255], np.uint8)
    orange_mask = cv2.inRange(hsvFrame, orange_lower, orange_upper)

    # Set range for pink color and
    # define mask
    pink_lower = np.array([20, 70, 200], np.uint8)
    pink_upper = np.array([35, 255, 255], np.uint8)
    pink_mask = cv2.inRange(hsvFrame, pink_lower, pink_upper)
    # pink_lower = np.array( [140, 50, 180], np.uint8)
    # pink_upper = np.array( [170, 255, 255], np.uint8)
    # pink_mask = cv2.inRange(hsvFrame, pink_lower, pink_upper)

    # Set range for blue color and
    # define mask
    blue_lower = np.array([100, 150, 150], np.uint8)
    blue_upper = np.array([130, 255, 255], np.uint8)
    blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper)

    # Morphological Transform, Dilation
    # for each color and bitwise_and operator
    # between imageFrame and mask determines
    # to detect only that particular color
    kernal = np.ones((5, 5), "uint8")

    # For red color
    red_mask = cv2.dilate(red_mask, kernal)
    res_red = cv2.bitwise_and(frame, frame,
                              mask=red_mask)

    # For pink color
    pink_mask = cv2.dilate(pink_mask, kernal)
    pink_red = cv2.bitwise_and(frame, frame,
                                 mask=pink_mask)
    # For orange color
    orange_mask = cv2.dilate(orange_mask, kernal)
    res_orange = cv2.bitwise_and(frame, frame, mask=orange_mask)

    # For blue color
    blue_mask = cv2.dilate(blue_mask, kernal)
    res_blue = cv2.bitwise_and(frame, frame,
                               mask=blue_mask)

    # Creating contour to track red color
    contours, hierarchy = cv2.findContours(red_mask,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)

    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if (area > 0 and area < 120):
            x, y, w, h = cv2.boundingRect(contour)

            if SHOW_COLORS:
                frame = cv2.rectangle(frame, (x, y),
                                    (x + w, y + h),
                                    (0, 0, 255), 2)
                
            moments = cv2.moments(contour)
            x1 = int(moments["m10"] / moments["m00"])
            y1 = int(moments["m01"] / moments["m00"])

    # Creating contour to track orange color
    contours, hierarchy = cv2.findContours(orange_mask,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)

    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if (area > 0 and area < 120):
            x, y, w, h = cv2.boundingRect(contour)

            if SHOW_COLORS:
                frame = cv2.rectangle(frame, (x, y),
                                    (x + w, y + h),
                                    (0, 145, 255), 2)
                
            moments = cv2.moments(contour)
            x1 = int(moments["m10"] / moments["m00"])
            y1 = int(moments["m01"] / moments["m00"])

            player_index = {
                "id": 0,
                "x":x1,
                "y":y1,                
            }

            framePlayersIndexes.append(player_index)

    # Creating contour to track pink color
    contours, hierarchy = cv2.findContours(pink_mask,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)

    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if (area > 0 and area < 120):
            x, y, w, h = cv2.boundingRect(contour)

            if SHOW_COLORS:
                frame = cv2.rectangle(frame, (x, y),
                                    (x + w, y + h),
                                    (140, 50, 180), 2)
                
            moments = cv2.moments(contour)
            x1 = int(moments["m10"] / moments["m00"])
            y1 = int(moments["m01"] / moments["m00"])

            player_index = {
                "id": 1,
                "x": x1,
                "y": y1,                
            }

            framePlayersIndexes.append(player_index)


    # Creating contour to track blue color
    contours, hierarchy = cv2.findContours(blue_mask,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if (area > 0 and area < 120):
            x, y, w, h = cv2.boundingRect(contour)

            if SHOW_COLORS:
                frame = cv2.rectangle(frame, (x, y),
                                    (x + w, y + h),
                                    (255, 0, 0), 2)

            moments = cv2.moments(contour)
            x1 = int(moments["m10"] / moments["m00"])
            y1 = int(moments["m01"] / moments["m00"])

    return framePlayersIndexes
        
