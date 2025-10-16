import json
from pathlib import Path as Path
from pygame import Vector2
from pygame import draw
import pygame

from copy import deepcopy

#from camera import Camera

class Geometry:
    def __init__(self):
        self.geometry = {}
        self.currentFilePath: Path
        
    def generateRectVecorPoints(self, rectPoints):
        return [Vector2(rectPoints[index], rectPoints[index + 1]) for index in range(0, len(rectPoints), 2)]
    
    def generateRectPolyPoints(self, rectVectorPoints):
        return [
            rectVectorPoints[0], 
            Vector2(rectVectorPoints[1].x, rectVectorPoints[0].y), 
            rectVectorPoints[1], 
            Vector2(rectVectorPoints[0].x, rectVectorPoints[1].y)
        ]

    def loadGeometryFile(self, filePath):
        self.currentFilePath = Path("./levels") / filePath
        with open(self.currentFilePath) as file:
            self.geometry = json.load(file)
        
        for index, rect in enumerate(self.geometry["rect"]):
            points = self.generateRectVecorPoints(rect["points"])
            self.geometry["rect"][index]["points"] = points
        
        for index, rect in enumerate(self.geometry["rect"]):
            self.geometry["rect"][index]["renderPoints"] = self.generateRectPolyPoints(rect["points"])
            
        for index, poly in enumerate(self.geometry["tri"]):
            points = [Vector2(poly["points"][index], poly["points"][index + 1]) for index in range(0, len(poly["points"]), 2)]
            self.geometry["tri"][index]["points"] = points
            
    def saveGeometryFile(self):
        outGeometry = deepcopy(self.geometry)
        
        for index, rect in enumerate(outGeometry["rect"]):
            points = [rect["points"][0].x, rect["points"][0].y, rect["points"][1].x, rect["points"][1].y]
            outGeometry["rect"][index]["points"] = points
            del outGeometry["rect"][index]["renderPoints"]
            
        for index, poly in enumerate(outGeometry["tri"]):
            points = []
            [points.extend([vector.x, vector.y]) for vector in poly["points"]]
            outGeometry["tri"][index]["points"] = points
        
        with open(self.currentFilePath, "w") as file:
            json.dump(outGeometry, file)
            
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
    
    def isPointColliding(self, point: Vector2):
        data = []
        print(point)
        for index, item in enumerate(self.geometry["rect"]):
            print(item)
            if pygame.Rect.collidepoint(pygame.Rect(item["points"][0].x, item["points"][0].y, item["points"][1].x, item["points"][1].y), (point.x, point.y)):
                data.append(index)
        #if len(data) > 0:
        #    data = [data[-1]]
        #else:
        #    data = []
        return data

    def isColliding(self, point: Vector2):
        return False