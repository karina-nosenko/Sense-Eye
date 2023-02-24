import cv2
import torch
import numpy as np
from scipy.spatial import distance
from yolov7.utils.general import non_max_suppression, scale_coords, check_img_size
from yolov7.utils.torch_utils import time_synchronized, select_device
from yolov7.models.experimental import attempt_load

from configs import options
from image_functions import adjust_image_to_desired_shape


def initialize_player_detection_model():
    """
    Initializes the player detection model with the provided weights and configuration options.

    Args:
        None

    Returns:
        weights (str): The path of the weight file used for the model.
        img_size (int): The image size used for the model.
        device (torch.device): The device on which the model is running.
        use_half_precision (bool): A boolean value indicating whether half precision is used for the model.
        model (torch.nn.Module): The player detection model.
        stride (int): The stride value used for the model.
        names (list): The list of class names used for the model.
        classes (list): The list of class indexes corresponding to the class names.

    Raises:
        None
    """
    weights, img_size = options['weights'], options['img-size']
    device = select_device(options['device'])
    use_half_precision = device.type != 'cpu'
    model = attempt_load(weights, map_location=device)
    stride = int(model.stride.max())
    img_size = check_img_size(img_size, s=stride)
    if use_half_precision:
        model.half()

    names = model.module.names if hasattr(model, 'module') else model.names
    if device.type != 'cpu':
        model(torch.zeros(1, 3, img_size, img_size).to(device).type_as(next(model.parameters())))

    # Convert class names to class indexes
    classes = []
    for class_name in options['classes']:
        classes.append(names.index(class_name))

    return weights, img_size, device, use_half_precision, model, stride, names, classes


def detect_objects(frame, player_with_the_ball_center_point, img_size, device, use_half_precision, model, stride, names, classes):
    """
    Detects objects in a frame using a PyTorch model.

    Args:
        frame (numpy.ndarray): The frame to detect objects in.
        player_with_the_ball_center_point (tuple of int): The center point of the player with the ball.
        img_size (int): The size of the input image for the model.
        device (str): The device to use for inference.
        use_half_precision (bool): Whether to use half-precision or not.
        model (torch.nn.Module): The PyTorch model to use for object detection.
        stride (int): The stride used for adjusting the image shape.
        names (list of str): The class names of the objects to detect.
        classes (list of int): The class IDs of the objects to detect.

    Returns:
        None

    Raises:
        None
    """
    # Convert image to desired shape and format
    img = adjust_image_to_desired_shape(frame, img_size, stride=stride)[0]
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)

    # Convert image to PyTorch tensor
    img = torch.from_numpy(img).to(device)
    img = img.half() if use_half_precision else img.float()

    # Normalize image pixel values to 0-1 range
    img /= 255.0

    # Add a forth dimention to the image object (batch_size=1)
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # Inference
    t1 = time_synchronized()
    detection_results = model(img, augment= False)[0]        
    detection_results = non_max_suppression(detection_results, options['conf-thres'], options['iou-thres'], classes=classes, agnostic= False)
    t2 = time_synchronized()

    print(detection_results)

    # Plotting the detections
    for detection in detection_results:
        if not len(detection):
            continue

        # Scale box coordinates to the size of current frame
        detection[:, :4] = scale_coords(img.shape[2:], detection[:, :4], frame.shape).round()
   
        player_with_the_ball_center_point = _detect_player_with_the_ball(detection, names, player_with_the_ball_center_point)     

        # Draw the class name label and center point for each object
        for i, (x1, y1, x2, y2, confidence_score, class_id) in enumerate(detection):
            center_x = int((x1 + x2) // 2)
            center_y = int((y1 + y2) // 2)  

            # Assign color based on object class
            class_name = names[int(class_id)]
            if center_x == player_with_the_ball_center_point[0] and center_y == player_with_the_ball_center_point[1]:
                text_color = (255, 255, 0)  # blue for player with the ball
            elif class_name == 'sports ball':
                text_color = (0, 255, 0)  # green for ball
                class_name = 'ball'
            else:
                text_color = (0, 0, 255)  # red for rest of the players

            # Create text label and display it on the frame
            text_label = f'{class_name} ({center_x}, {center_y}) {confidence_score}'
            cv2.putText(frame, text_label, (center_x, center_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

            # Draw center point circle on the frame
            cv2.circle(frame, (center_x, center_y), 3, (0, 0, 255), -1)

    return player_with_the_ball_center_point


def _find_nearest_player_to_the_ball(ball_center_point, all_detections, names):
    if not ball_center_point:
        return None

    # Precompute ball coordinates as a NumPy array
    ball_coordinates_np = np.array([ball_center_point[0].cpu(), ball_center_point[1].cpu()])

    # Filter out non-person detections before the loop
    person_detections = [(x, y, w, h, conf, cls_id) for x, y, w, h, conf, cls_id in all_detections if names[int(cls_id)] == 'person']

    min_distance_to_ball = float('inf')
    nearest_player_center_point = None

    for x, y, w, h, conf, cls_id in reversed(person_detections):
        player_center_point = ((x + w) // 2, (y + h) // 2)
        player_coordinates_np = np.array([player_center_point[0].cpu(), player_center_point[1].cpu()])
        euclidean_distance_sq = distance.sqeuclidean(ball_coordinates_np, player_coordinates_np)

        if euclidean_distance_sq < min_distance_to_ball:
            min_distance_to_ball = euclidean_distance_sq
            nearest_player_center_point = (x, y, w, h)

    return nearest_player_center_point if min_distance_to_ball != float('inf') else None


def _detect_player_with_the_ball(detection, names, player_with_the_ball_center_point):
    # Detect the player with the ball - the player whose coordinates are
    # the nearest to the found ball.
    ball_found_in_current_frame = False
    nearest_player_to_the_ball = None
    for *xyxy, confidence_score, class_id in reversed(detection):
        if (names[int(class_id)] == 'sports ball'):
            ball_found_in_current_frame = True
            center_point = ((xyxy[0] + xyxy[2]) // 2, (xyxy[1] + xyxy[3]) // 2)
            nearest_player_to_the_ball = _find_nearest_player_to_the_ball(center_point, detection, names)
    
    # If the ball was not found in the current frame - the 'player with the ball'
    # will be the player whose coordinates are the nearest to the 'player with the ball'
    # in the previous frame.
    if not ball_found_in_current_frame:
        for *xyxy, confidence_score, class_id in reversed(detection):
            nearest_player_to_the_ball = _find_nearest_player_to_the_ball(player_with_the_ball_center_point, detection, names)

    if nearest_player_to_the_ball:
        player_with_the_ball_center_point = ((nearest_player_to_the_ball[0] + nearest_player_to_the_ball[2]) // 2, (nearest_player_to_the_ball[1] + nearest_player_to_the_ball[3]) // 2)

    return player_with_the_ball_center_point


