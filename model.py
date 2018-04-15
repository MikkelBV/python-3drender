import json
from pprint import pprint as pp

class Node:
    def __init__(self, point, key):
        self._point = point
        self._key = key
    def point(self):
        return self._point
    def scale(self, scalar):
        x, y, z = self._point
        self._point = (x * scalar, y * scalar, z * scalar)
    def key(self):
        return self._key


class WorldObject:
    def __init__(self, points, lines, position = (0, 0, 0), scale = 1, rotation = (0, 0 ,0)):        
        self._lines = lines
        self._position = position
        self._scale = scale
        self._rotation = rotation
        self._points = points

        # scale the input points according to specified scale
        self._scale_points(scale, points)


    def translate(self, position_change):
        x, y, z = self._position
        movex, movey, movez = position_change
        self._position = (x + movex, y + movey, z + movez)


    def scale(self, scalar):
        self._scale_points(scalar, self._points)

    
    def _scale_points(self, scalar, points):
        for point in points:
            point.scale(scalar)

    
    def points(self):
        return self._points


    def lines(self):
        return self._lines


    def position(self):
        return self._position


def load_model(path_to_json_model):
    with open(path_to_json_model) as file_data:
        json_model = json.load(file_data)
        nodes = []
        lines = []

        for json_point in json_model['points']:
            key = json_point['key']
            point = (
                json_point['x'],
                json_point['y'],
                json_point['z']
            )

            nodes.append(Node(point, key))
        
        for json_line in json_model['lines']:
            vertex1 = json_line['vertex1']
            vertex2 = json_line['vertex2']

            line = []

            for node in nodes:
                if node.key() == vertex1 or node.key() == vertex2:
                    line.append(node)

            lines.append(tuple(line))
        # print(lines)
        return WorldObject(nodes, lines, scale = 1)

    

        
        
