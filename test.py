import unittest
import cv2
import numpy as np
import json
import engine
import model
from unittest.mock import patch

class engineTest (unittest.TestCase):

    @patch("cv2.waitKey", return_value = 0)
    def test_it_runs(self, return_value):
        try:
            engine.start(lambda canvas: None)
        except:
            self.fail()


    def test_global_to_camera_point(self):
        camx, camy, camz = engine.CAMERA_POSITION
        point = (-10, 10, -2)
        x, y, z = point
        expected_output = (x - camx, y - camy, z - camz)
        actual_output = engine.global_to_camera_point(point)

        self.assertEqual(actual_output, expected_output)


    def test_point_to_pixel_returns_ints(self):
        point = (11, 19, 2)
        expected_type = tuple
        output = engine.point_to_pixel(point, (0, 0, 0))
        output_is_int = type(output[0]) is int and type(output[1]) is int

        self.assertEqual(type(output), expected_type)
        self.assertEqual(len(output), 2)
        self.assertTrue(output_is_int)

    
    def test_correctly_maps_point_to_pixel(self):
        point = (-10, 10, -2)
        x, y, z = engine.global_to_camera_point(point)
        expected_output = (
            int((engine.WINDOW_HEIGHT / 2) - (engine.FOCAL_LENGTH * y / z)),
            int((engine.FOCAL_LENGTH * x / z) + engine.WINDOW_WIDTH / 2)
        )
        actual_output = engine.point_to_pixel(point, (0, 0, 0))

        self.assertEqual(actual_output, expected_output)


    def test_draw_runs(self):
        try: 
            canvas = np.zeros((engine.WINDOW_HEIGHT, engine.WINDOW_WIDTH), np.uint8)
            points = [(0, 0), (1, 1), (2, 2)]

            output = engine.draw_points(canvas, points)
        except:
            self.fail()

        
    def test_draw_points_right_numpoints(self):
        canvas = np.zeros((engine.WINDOW_HEIGHT, engine.WINDOW_WIDTH), np.uint8)
        points = [(0, 0), (5, 0), (10, 0)]
        engine.draw_points(canvas, points)
        num_whites = 0
        
        for y in range(engine.WINDOW_HEIGHT):
            for x in range(engine.WINDOW_WIDTH):
                if canvas.item(y, x) == engine.COLOR_WHITE:
                    num_whites += 1
        
        self.assertEqual(num_whites, len(points))


    def test_is_point_in_frame(self):
        canvas = np.zeros((5, 5), np.uint8)
        point1 = (0, 0)
        point2 = (6, 6)

        output1 = engine.is_point_in_frame(canvas, point1)
        output2 = engine.is_point_in_frame(canvas, point2)

        self.assertTrue(output1)
        self.assertFalse(output2)


    def test_draw_outside_frame(self):
        try:
            points = [(1, 1), (6, 6)]
            canvas = np.zeros((5, 5), np.uint8)
            engine.draw_points(canvas, points)
        except:
            self.fail(msg = 'trying to draw outside frame')


    def test_draw_line(self):
        canvas = np.zeros((5, 5), np.uint8)
        engine.draw_line(canvas, (0, 0), (4, 0))
        
        for i in range(len(canvas)):
            for j in range(i):
                color = canvas.item(i, j)
                if j < 5 and j > 0 and i == 0:
                    self.assertEqual(color, engine.COLOR_WHITE)
                else:
                    self.assertEqual(color, 0)
                

    def test_map_model_to_screen(self):
        world_object = model.WorldObject([
            model.Node((1, 1, 1), None),
            model.Node((1, 2, 3), None),
            model.Node((2, 4, 6), None)
        ], [])
        
        expected_output = [(243, 517), (229, 508), (218, 515)]
        actual_output = engine.map_model_to_screen(world_object);
        
        self.assertEqual(actual_output, expected_output)


    def test_draw_world_object_runs(self):
        try:
            canvas = np.zeros((engine.WINDOW_HEIGHT, engine.WINDOW_WIDTH), np.uint8)
            world_object = model.load_model('models/test.json')
            engine.draw_world_object(canvas, world_object)
        except:
            self.fail(msg = 'could not call draw_world_object()')
        

class ModelTest (unittest.TestCase):
    def test_node_object(self):
        point = (1, 1)
        key = 'key'

        node = model.Node(point, key)
        self.assertEqual(node.point(), point)
        self.assertEqual(node.key(), key)
    

    def test_world_object_runs(self):
        try:
            world_object = model.WorldObject(points = [], lines = [], scale = 1)
            self.assertEqual(world_object.points(), [])
        except:
            self.fail()

        
    def test_world_object_scales(self):
        world_object = model.WorldObject(points = [
            model.Node((0, 0, 0), None),
            model.Node((1, 2, 3), None),
            model.Node((2, 4, 6), None)
        ], lines = [], scale = 2)

        expected_output = [
            (0 , 0, 0),
            (2, 4, 6),
            (4, 8, 12)
        ]
        actual_output = world_object.points()

        for node in actual_output:
            self.assertIn(node.point(), expected_output)


    def test_loads_json_model(self):
        try:
            model.load_model('models/box.json')
        except:
            self.fail()

        self.assertRaises(FileNotFoundError, model.load_model, 'models/filethatdoesnotexist.json')


    def test_convert_json_to_object(self):
        try:
            world_object = model.load_model('models/test.json')
            points = world_object.points()

            self.assertTrue(type(world_object) is model.WorldObject)
            self.assertTrue(type(points) is list)
            self.assertTrue(type(points[0]) is model.Node)
            self.assertGreater(len(points), 1)
            self.assertEqual(len(points[0].point()), 3)

            x, y, z = points[0].point()
            self.assertTrue(type(x) is int or type(x) is float)
            self.assertTrue(type(y) is int or type(y) is float)
            self.assertTrue(type(z) is int or type(z) is float)
        except:
            self.fail()


    def test_world_objects_finds_line_points(self):
        with open('models/test.json') as file_data:
            json_keys = [point['key'] for point in json.load(file_data)['points']]
            world_object_lines = model.load_model('models/test.json').lines()

            for i in range(len(world_object_lines)):
                world_vert1, world_vert2 = world_object_lines[i]

                self.assertIn(world_vert1.key(), json_keys)
                self.assertIn(world_vert2.key(), json_keys)



if __name__ == '__main__':
    unittest.main()