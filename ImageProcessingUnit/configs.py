import platform

# some constants
APPEND_PATH = 'yolov7'
MAX_PLAYERS_NUMBER = 10

#colors id
PINK_COLOR = 0
ORANGE_COLOR = 1

device = '0' if platform.system() == "Linux" else 'cpu'

# Detection options
classes_to_detect = ['person', 'sports ball']
options  = {
    "weights": APPEND_PATH + "/weights/yolov7.pt",
    "yaml"   : APPEND_PATH + "/data/coco.yaml",
    "img-size": 640,    # default image size
    "iou-thres" : 0.45, # NMS IoU threshold for inference (0.45)
    "device" : device,   # device to run our model i.e. 0 or 0,1,2,3 or cpu
    "classes": classes_to_detect,
    "class-person": {
        "class-name": 'person',
        "conf-thres": 0.8
    },
    "class-ball": {
        "class-name": 'sports ball',
        "conf-thres": 0.38
    }
}

SHOW_COLORS = True
SHOW_CENTER_POINTS = True
SHOW_DIRECTION_ARROW = True
SHOW_DIRECTION_LABEL = False
SHOW_CLASS_LABEL = False
SHOW_RECOMMENDATION_ARROW = False # (still in progress, not working well)



























































