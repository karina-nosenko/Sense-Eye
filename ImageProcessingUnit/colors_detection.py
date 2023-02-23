# Python code for Multiple Color Detection


import numpy as np
import cv2

def detect_colors (frame, video):
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
    orange_upper = np.array([18, 255, 255], np.uint8)
    orange_mask = cv2.inRange(hsvFrame, orange_lower, orange_upper)

    # Set range for yellow color and
    # define mask
    yellow_lower = np.array([20, 100, 100], np.uint8)
    yellow_upper = np.array([30, 255, 255], np.uint8)
    yellow_mask = cv2.inRange(hsvFrame, yellow_lower, yellow_upper)

    # Set range for blue color and
    # define mask
    blue_lower = np.array([94, 80, 2], np.uint8)
    blue_upper = np.array([120, 255, 255], np.uint8)
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

    # For yellow color
    yellow_mask = cv2.dilate(yellow_mask, kernal)
    yellow_red = cv2.bitwise_and(frame, frame,
                                 mask=yellow_mask)
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
        if (area > 300):
            x, y, w, h = cv2.boundingRect(contour)
            frame = cv2.rectangle(frame, (x, y),
                                  (x + w, y + h),
                                  (0, 0, 255), 2)
            moments = cv2.moments(contour)
            x1 = int(moments["m10"] / moments["m00"])
            y1 = int(moments["m01"] / moments["m00"])
            cv2.putText(frame, f"Red Colour x={x1}, y={y1}", (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                        (0, 0, 255))

    # Creating contour to track orange color
    contours, hierarchy = cv2.findContours(orange_mask,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)

    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if (area > 300):
            x, y, w, h = cv2.boundingRect(contour)
            frame = cv2.rectangle(frame, (x, y),
                                  (x + w, y + h),
                                  (0, 145, 255), 2)
            moments = cv2.moments(contour)
            x1 = int(moments["m10"] / moments["m00"])
            y1 = int(moments["m01"] / moments["m00"])

            cv2.putText(frame, f"orange Colour x={x1}, y={y1}", (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                        (0, 145, 255))

    # Creating contour to track yellow color
    contours, hierarchy = cv2.findContours(yellow_mask,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)

    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if (area > 300):
            x, y, w, h = cv2.boundingRect(contour)
            frame = cv2.rectangle(frame, (x, y),
                                  (x + w, y + h),
                                  (0, 239, 255), 2)
            moments = cv2.moments(contour)
            x1 = int(moments["m10"] / moments["m00"])
            y1 = int(moments["m01"] / moments["m00"])
            cv2.putText(frame, f"yellow Colour x={x1}, y={y1}", (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (0, 239, 255))

    # Creating contour to track blue color
    contours, hierarchy = cv2.findContours(blue_mask,
                                           cv2.RETR_TREE,
                                           cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if (area > 300):
            x, y, w, h = cv2.boundingRect(contour)
            frame = cv2.rectangle(frame, (x, y),
                                  (x + w, y + h),
                                  (255, 0, 0), 2)
            moments = cv2.moments(contour)
            x1 = int(moments["m10"] / moments["m00"])
            y1 = int(moments["m01"] / moments["m00"])
            cv2.putText(frame, f"Blue Colour x={x1}, y={y1}", (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (255, 0, 0))
