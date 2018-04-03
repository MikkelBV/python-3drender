import cv2
import numpy as np
from model import load_model


WINDOW_NAME = 'canvas'
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 500
CAMERA_POSITION = (0.5, 0.8, -1)
FOCAL_LENGTH = 70
COLOR_WHITE = 255
COLOR_GRAY = 127
COLOR_LIGHTGRAY = 200


def global_to_camera_point(point):
    return tuple(np.subtract(point, CAMERA_POSITION))


def map_model_to_screen(world_object):
    return [point_to_pixel(node.point()) for node in world_object.points()]


def point_to_pixel(point):
    x, y, z = global_to_camera_point(point)

    screen_x = (FOCAL_LENGTH * x / z) + WINDOW_WIDTH / 2
    screen_y = (WINDOW_HEIGHT / 2) - (FOCAL_LENGTH * y / z)
    
    return int(screen_y), int(screen_x)


def is_point_in_frame(canvas, point):
    y, x = point
    return y >= 0 and x >= 0 and y < len(canvas) and x < len(canvas[0])


def draw_points(canvas, pixels):
    for pixel in pixels:
        if is_point_in_frame(canvas, pixel):
            canvas.itemset(pixel, COLOR_WHITE)


def draw_line(canvas, point1, point2, thickness = 1, color = COLOR_WHITE):
    cv2.line(
        canvas,
        point1,
        point2,
        color = COLOR_WHITE,
        thickness = thickness
    )


def draw_world_object(canvas, world_object):
    for start, finish in world_object.lines():
        y1, x1 = point_to_pixel(start.point())
        y2, x2 = point_to_pixel(finish.point())
        draw_line(canvas, (x1, y1), (x2, y2))


def start():
    box = None

    try:
        box = load_model('models/box.json')
    except:
        print('file does not exist')
        return None

    canvas = np.zeros(
        shape = (WINDOW_HEIGHT, WINDOW_WIDTH),
        dtype = np.uint8 # unsigned integer 0-255 (grayscale)
    )

    draw_points(canvas, map_model_to_screen(box))
    draw_world_object(canvas, box)

    # draw center
    canvas.itemset((int(WINDOW_HEIGHT / 2), int(WINDOW_WIDTH / 2)), COLOR_GRAY)

    cv2.startWindowThread()
    cv2.namedWindow(WINDOW_NAME)
    cv2.imshow(WINDOW_NAME, canvas)
    cv2.waitKey(0)
    # https://stackoverflow.com/questions/5288536/how-to-change-3d-point-to-2d-pixel-location
    # http://www.nh.cas.cz/people/lazar/celler/online_tools.php?start_vec=-10,%20-10,%2010&rot_ax=0,1,1&rot_ang=30