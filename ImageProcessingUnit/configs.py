APPEND_PATH = 'yolov7'

# realtime/video
MODE = 'video'

# Camera index for realtime: 0-webcam, 4/0 - camera
# Video path for video
CAMERA_INDEX = 0
VIDEO_PATH = APPEND_PATH + '/videos/two_players_orange_yellow.mp4'

# Detection constants and configs
classes_to_detect = [ 'person', 'sports ball' ]
options  = {
    "weights": APPEND_PATH + "/weights/yolov7.pt",
    "yaml"   : APPEND_PATH + "/data/coco.yaml",
    "img-size": 640,    # default image size
    "conf-thres": 0.25, # confidence threshold for inference (0.25)
    "iou-thres" : 0.45, # NMS IoU threshold for inference (0.45)
    "device" : '0',   # device to run our model i.e. 0 or 0,1,2,3 or cpu
    "classes" : classes_to_detect
}