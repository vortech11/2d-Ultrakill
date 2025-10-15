import json
from pathlib import Path as Path
from pygame import Vector2
from pygame import draw

#from camera import Camera

class Geometry:
    def __init__(self):
        self.geometry = {}

    def loadGeometryFile(self, filePath):
        with open(Path("./levels") / filePath) as file:
            self.geometry = json.load(file)
        
        for index, rect in enumerate(self.geometry["rect"]):
            points = [Vector2(rect["points"][index], rect["points"][index + 1]) for index in range(0, len(rect["points"]), 2)]
            self.geometry["rect"][index]["points"] = points
        
        for index, rect in enumerate(self.geometry["rect"]):
            self.geometry["rect"][index]["renderPoints"] = rect["points"][0], Vector2(rect["points"][1].x, rect["points"][0].y), rect["points"][1], Vector2(rect["points"][0].x, rect["points"][1].y)
            
        for index, poly in enumerate(self.geometry["tri"]):
            points = [Vector2(poly["points"][index], poly["points"][index + 1]) for index in range(0, len(poly["points"]), 2)]
            self.geometry["tri"][index]["points"] = points
            
    def getRectPoints(self, points: list[Vector2]):
        return points[0]
        
    def renderRects(self, camera, screen):
        for rect in self.geometry["rect"]:
            draw.polygon(screen, rect["color"], [camera.transformPoint(point) for point in rect["renderPoints"]])
            
    def renderPoly(self, camera, screen):
        for poly in self.geometry["tri"]:
            draw.polygon(screen, poly["color"], [camera.transformPoint(point) for point in poly["points"]])
            
    def render(self, camera, screen):
        self.renderRects(camera, screen)
        
        self.renderPoly(camera, screen)

    def isColliding(self, point: Vector2):
        return False