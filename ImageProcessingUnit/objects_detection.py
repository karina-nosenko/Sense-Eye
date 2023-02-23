import cv2
import torch
import numpy as np
from scipy.spatial import distance
from yolov7.utils.general import non_max_suppression, scale_coords, check_img_size
from yolov7.utils.torch_utils import time_synchronized, select_device
from yolov7.models.experimental import attempt_load

from configs import options, MODE
from image_functions import adjust_image_to_desired_shape


def initialize_player_detection_model():
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


def find_nearest_player_to_the_ball(ball_center_point, all_detections, names):
    """
    Find the nearest detected person to the ball center point.

    Args:
        ball_center_point (tuple): The center point of the ball in (x,y) format.
        all_detections (list): A list of detected objects, where each object is represented by a tuple of coordinates, confidence score, and class id.
        names (list): A list of class names, where the class id at each index corresponds to the class name at that index.

    Returns:
        tuple: The coordinates of the bounding box (in x1, y1, x2, y2 format) of the nearest detected person to the ball center point, or None if no person is detected.

    Raises:
        None
    """
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

def detect_objects(frame, player_with_the_ball_center_point, img_size, device, use_half_precision, model, stride, names, classes):
    img = adjust_image_to_desired_shape(frame, img_size, stride=stride)[0]
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)
    img = torch.from_numpy(img).to(device)
    img = img.half() if use_half_precision else img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0

    # Add a forth dimention to the image object - batch_size=1
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # Inference
    t1 = time_synchronized()
    detection_results = model(img, augment= False)[0]        
    detection_results = non_max_suppression(detection_results, options['conf-thres'], options['iou-thres'], classes=classes, agnostic= False)
    t2 = time_synchronized()

    # Plotting the detections
    for i, det in enumerate(detection_results):
        if len(det):
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round()

            # Detect the player with the ball - the player whose coordinates are
            # the nearest to the found ball.
            ball_found_in_current_frame = False
            for *xyxy, confidence_score, class_id in reversed(det):
                if (names[int(class_id)] == 'sports ball'):
                    ball_found_in_current_frame = True
                    center_point = ((xyxy[0] + xyxy[2]) // 2, (xyxy[1] + xyxy[3]) // 2)
                    nearest_player_to_the_ball = find_nearest_player_to_the_ball(center_point, det, names)
                    if nearest_player_to_the_ball:
                        player_with_the_ball_center_point = ((nearest_player_to_the_ball[0] + nearest_player_to_the_ball[2]) // 2, (nearest_player_to_the_ball[1] + nearest_player_to_the_ball[3]) // 2)
            
            # If the ball was not found in the current frame - the 'player with the ball'
            # will be the player whose coordinates are the nearest to the 'player with the ball'
            # in the previous frame.
            if not ball_found_in_current_frame:
                for *xyxy, confidence_score, class_id in reversed(det):
                    nearest_player_to_the_ball = find_nearest_player_to_the_ball(player_with_the_ball_center_point, det, names)
                    if nearest_player_to_the_ball:
                        player_with_the_ball_center_point = ((nearest_player_to_the_ball[0] + nearest_player_to_the_ball[2]) // 2, (nearest_player_to_the_ball[1] + nearest_player_to_the_ball[3]) // 2)

            # Draw the class name label and center point for each object
            for *xyxy, confidence_score, class_id in reversed(det):
                center_point = ((xyxy[0] + xyxy[2]) // 2, (xyxy[1] + xyxy[3]) // 2)

                # Class name and center point coordinates label
                center_point_coordinates_label = f"({center_point[0]}, {center_point[1]})"
                class_name_label = names[int(class_id)]  

                if center_point == player_with_the_ball_center_point:
                    text_color = (255, 255, 0) # blue for player with the ball
                elif class_name_label == 'sports ball':
                    text_color = (0, 255, 0) # green for ball
                    class_name_label = 'ball'
                else:
                    text_color = (0, 0, 255) # red for rest of the players

                text_label = f'{class_name_label} {center_point_coordinates_label}'
                cv2.putText(frame, text_label, tuple(map(int, (center_point[0], center_point[1] - 10))), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

                # Center point circle
                cv2.circle(frame, tuple(map(int, center_point)), 3, (0, 0, 255), -1)


