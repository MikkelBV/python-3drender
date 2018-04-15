import unittest
import cv2
import numpy as np
import json
import engine
import model
from unittest.mock import patch

class EngineTest (unittest.TestCase):

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

        vertex = model.Vertex(point, key)
        self.assertEqual(vertex.point(), point)
        self.assertEqual(vertex.key(), key)
    

    def test_world_object_runs(self):
        try:
            world_object = model.WorldObject(vertices = [], lines = [], scale = 1)
            self.assertEqual(world_object.vertices(), [])
        except:
            self.fail()

        
    def test_world_object_scales_oninit(self):
        world_object = model.WorldObject(vertices = [
            model.Vertex((0, 0, 0), None),
            model.Vertex((1, 2, 3), None),
            model.Vertex((2, 4, 6), None)
        ], lines = [], scale = 2)

        expected_output = [
            (0 , 0, 0),
            (2, 4, 6),
            (4, 8, 12)
        ]
        
        actual_output = [node.point() for node in world_object.vertices()]
        self.assertListEqual(actual_output, expected_output)


    def test_loads_json_model(self):
        try:
            model.load_model('models/box.json')
        except:
            self.fail()

        self.assertRaises(FileNotFoundError, model.load_model, 'models/filethatdoesnotexist.json')


    def test_convert_json_to_object(self):
        try:
            world_object = model.load_model('models/test.json')
            points = world_object.vertices()

            self.assertTrue(type(world_object) is model.WorldObject)
            self.assertTrue(type(points) is list)
            self.assertTrue(type(points[0]) is model.Vertex)
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


    def test_scale_model(self):
        world_object = model.WorldObject(vertices = [
            model.Vertex((0, 0, 0), None),
            model.Vertex((1, 2, 3), None),
            model.Vertex((2, 4, 6), None)
        ], lines = [], scale = 1)

        expected_output = [
            (0 , 0, 0),
            (2, 4, 6),
            (4, 8, 12)
        ]

        world_object.scale(2)
        actual_output = [vertex.point() for vertex in world_object.vertices()]
        self.assertListEqual(actual_output, expected_output)


if __name__ == '__main__':
    unittest.main()