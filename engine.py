import cv2
import numpy as np
from model import load_model
import time


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
    return [point_to_pixel(node.point(), world_object.position()) for node in world_object.points()]


def point_to_pixel(point, position):
    x, y, z = global_to_camera_point(point)
    x += position[0]
    y += position[1]
    z += position[2]

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
        y1, x1 = point_to_pixel(start.point(), world_object.position())
        y2, x2 = point_to_pixel(finish.point(), world_object.position())
        draw_line(canvas, (x1, y1), (x2, y2))


def start(loop):
    canvas = np.zeros(
        shape = (WINDOW_HEIGHT, WINDOW_WIDTH),
        dtype = np.uint8 # unsigned integer 0-255 (grayscale)
    )

    canvas.itemset((int(WINDOW_HEIGHT / 2), int(WINDOW_WIDTH / 2)), COLOR_GRAY)
    cv2.startWindowThread()
    cv2.namedWindow(WINDOW_NAME)

    for i in range(10):
        canvas[:] = 0
        loop(canvas)
        cv2.imshow(WINDOW_NAME, canvas)
        cv2.waitKey(0)