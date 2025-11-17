import json
from pathlib import Path as Path
from pygame import Vector2
from pygame import draw
import pygame

from copy import deepcopy

#from camera import Camera

class Geometry:
    def __init__(self, gameEngine):
        self.gameEngine = gameEngine
        self.collisionGeometry = {}
        self.renderGeometry = {}
        self.fullGeometry = {}
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

    def unpackRectTriData(self, geometryData):
        for index, rect in enumerate(geometryData["rect"]):
            points = self.generateRectVecorPoints(rect["points"])
            geometryData["rect"][index]["points"] = points
        
        for index, rect in enumerate(geometryData["rect"]):
            geometryData["rect"][index]["renderPoints"] = self.generateRectPolyPoints(rect["points"])
            
        for index, poly in enumerate(geometryData["tri"]):
            points = [Vector2(poly["points"][index], poly["points"][index + 1]) for index in range(0, len(poly["points"]), 2)]
            geometryData["tri"][index]["points"] = points

    def loadGeometryFile(self, filePath):
        self.gameEngine.currentLevel = filePath
        self.currentFilePath = Path("./levels") / filePath
        with open(self.currentFilePath) as file:
            self.fullGeometry = json.load(file)

        #print(self.fullGeometry)

        self.collisionGeometry = deepcopy(self.fullGeometry["collisionGeometry"])
        del self.fullGeometry["collisionGeometry"]
        self.renderGeometry = deepcopy(self.fullGeometry["renderGeometry"])
        del self.fullGeometry["renderGeometry"]
        
        self.unpackRectTriData(self.collisionGeometry)
        self.unpackRectTriData(self.renderGeometry)
            
        for index, rect in enumerate(self.fullGeometry["triggers"]):
            points = self.generateRectVecorPoints(rect["points"])
            self.fullGeometry["triggers"][index]["points"] = points
            
        for index, rect in enumerate(self.fullGeometry["enemySpawner"]):
            self.fullGeometry["enemySpawner"][index]["position"] = Vector2(self.fullGeometry["enemySpawner"][index]["position"])
            
        self.fullGeometry["player"]["startpos"] = Vector2(self.fullGeometry["player"]["startpos"])

    def saveRectTriData(self, geometryData):
        for index, rect in enumerate(geometryData["rect"]):
            points = [rect["points"][0].x, rect["points"][0].y, rect["points"][1].x, rect["points"][1].y]
            geometryData["rect"][index]["points"] = points
            del geometryData["rect"][index]["renderPoints"]
            
        for index, poly in enumerate(geometryData["tri"]):
            points = []
            [points.extend([vector.x, vector.y]) for vector in poly["points"]]
            geometryData["tri"][index]["points"] = points
            
    def saveGeometryFile(self):
        outCollisionGeometry = deepcopy(self.collisionGeometry)
        outRenderGeometry = deepcopy(self.renderGeometry)
        outFullGeometry = deepcopy(self.fullGeometry)
        
        self.saveRectTriData(outCollisionGeometry)
        self.saveRectTriData(outRenderGeometry)

        for index, rect in enumerate(outFullGeometry["triggers"]):
            points = [rect["points"][0].x, rect["points"][0].y, rect["points"][1].x, rect["points"][1].y]
            outFullGeometry["triggers"][index]["points"] = points

        outFullGeometry["collisionGeometry"] = outCollisionGeometry
        outFullGeometry["renderGeometry"] = outRenderGeometry
            
        for index, rect in enumerate(outFullGeometry["enemySpawner"]):
            outFullGeometry["enemySpawner"][index]["position"] = [rect["position"].x, rect["position"].y]
            
        outFullGeometry["player"]["startpos"] = [outFullGeometry["player"]["startpos"].x, outFullGeometry["player"]["startpos"].y]
        
        with open(self.currentFilePath, "w") as file:
            json.dump(outFullGeometry, file)
            
    def renderPoint(self, camera, screen, color, point, size=10):
        draw.circle(screen, color, camera.transformPoint(point), size)
        
    def renderLine(self, camera, screen, color, start, end, width=10):
        pygame.draw.line(screen, color, camera.transformPoint(start), camera.transformPoint(end), width)
        
    def renderRects(self, rects, camera, screen):
        for rect in rects:
            draw.polygon(screen, rect["color"], [camera.transformPoint(point) for point in rect["renderPoints"]])
            
    def renderPoly(self, polys, camera, screen):
        for poly in polys:
            draw.polygon(screen, poly["color"], [camera.transformPoint(point) for point in poly["points"]])

    def renderDevInfo(self, camera, screen):
        for rect in self.fullGeometry["triggers"]:
            points = [camera.transformPoint(point) for point in rect["points"]]
            draw.rect(screen, (235, 199, 19), pygame.Rect(points[0].x, points[0].y, points[1].x - points[0].x, points[1].y - points[0].y))

        for spawner in self.fullGeometry["enemySpawner"]:
            self.renderPoint(camera, screen, (255, 0, 0), spawner["position"])
            
        self.renderPoint(camera, screen, (0, 0, 255), self.fullGeometry["player"]["startpos"])
            
    def render(self, camera, screen):
        self.renderRects(self.renderGeometry["rect"], camera, screen)
        self.renderPoly(self.renderGeometry["tri"], camera, screen)
        self.renderRects(self.collisionGeometry["rect"], camera, screen)
        self.renderPoly(self.collisionGeometry["tri"], camera, screen)
        
    def generateRect(self, pointList: list[Vector2]):
        return pygame.Rect(pointList[0].x, pointList[0].y, pointList[1].x, pointList[1].y)
        
    def isPointRectColliding(self, point: Vector2, rect: list[Vector2]):
        return (rect[0].x < point.x < rect[1].x) and (rect[0].y < point.y < rect[1].y)
    
    def triArea(self, p1: Vector2, p2: Vector2, p3: Vector2):
        return abs((p1.x * (p2.y - p3.y) + p2.x * (p3.y - p1.y) + p3.x * (p1.y - p2.y)) / 2.0)
    
    def isPointTriColliding(self, point: Vector2, tri: list[Vector2]):
        p1 = tri[0]
        p2 = tri[1]
        p3 = tri[2]
        
        A = self.triArea(p1, p2, p3)
        
        A1 = self.triArea(point, p2, p3)
        A2 = self.triArea(p1, point, p3)
        A3 = self.triArea(p1, p2, point)
        
        return A == A1 + A2 + A3
    
    def isPointColliding(self, geometryData, point: Vector2):
        data = {"rect": [], "tri": [], "triggers": []}
        for index, item in enumerate(geometryData["rect"]):
            if self.isPointRectColliding(point, item["points"]):
                data["rect"].append(index)
        for index, item in enumerate(geometryData["tri"]):
            if self.isPointTriColliding(point, item["points"]):
                data["tri"].append(index)
        for index, item in enumerate(self.fullGeometry["triggers"]):
            if self.isPointRectColliding(point, item["points"]):
                data["triggers"].append(index)
        return data
    
    def isLineLineColliding(self, p1: Vector2, p2: Vector2, p3: Vector2, p4: Vector2):
        denom = ((p4.y - p3.y) * (p2.x - p1.x)) - ((p4.x - p3.x) * (p2.y - p1.y))
        # If denom is zero (or very close), lines are parallel or collinear — treat as no intersection here
        if abs(denom) < 1e-9:
            return False

        UA = (((p4.x - p3.x) * (p1.y - p3.y)) - ((p4.y - p3.y) * (p1.x - p3.x))) / denom
        UB = (((p2.x - p1.x) * (p1.y - p3.y)) - ((p2.y - p1.y) * (p1.x - p3.x))) / denom
        
        return 0.0 <= UA <= 1.0 and 0.0 <= UB <= 1.0
    
    def getLinesFromObjects(self, list, objects, points="points"):
        for object in objects:
            list.extend([[[point, object[points][(index + 1) % (len(object[points]))]], None] for index, point in enumerate(object[points])])
        return list
    
    def getLinesFromEnemies(self, list, enemies):
        for enemyIndex, enemy in enumerate(enemies):
            list.extend([[[point + enemy.position, enemy.hitbox[(index + 1) % (len(enemy.hitbox))] + enemy.position], enemyIndex] for index, point in enumerate(enemy.hitbox)])
        return list
    
    # Big thanks to Basstabs for this algorithm
    def rayLinesegIntersect(self, position: Vector2, ray: Vector2, start: Vector2, end: Vector2):
        rise = end.y - start.y
        run = end.x - start.x

        denominator = rise * ray.x - run * ray.y
        if denominator == 0: #The ray and the segment are parallel, so there is no intersection to find
            return None

        segment_param = (position.y * ray.x + start.x * ray.y - position.x * ray.y - start.y * ray.x) / denominator
        if segment_param < 0 or segment_param > 1.0: #The lines intersect outside the segment, so there is no intersection
            return None

        if ray.x == 0.0:
            collidingDist = (start.y - position.y + rise * segment_param) / ray.y
        else:
            collidingDist = (start.x - position.x + run * segment_param) / ray.x

        if collidingDist < 0: #The opposite of the ray intersects the segment, not the ray itself
            return None

        return collidingDist

    def isRayColliding(self, position: Vector2, ray: Vector2, pierce=1):
        ray.normalize()
        lines = []
        self.getLinesFromObjects(lines, self.collisionGeometry["rect"], "renderPoints")
        self.getLinesFromObjects(lines, self.collisionGeometry["tri"])
        self.getLinesFromEnemies(lines, self.gameEngine.enemies)
        contacts = [[self.rayLinesegIntersect(position, ray, line[0][0], line[0][1]), line[1]] for line in lines]
        contacts = [num for num in contacts if not num[0] == None]
        contacts.sort(key=lambda item: item[0])
        if not contacts:
            return []
        
        contacts = contacts[0:pierce]
        points = [[position + (ray * collide[0]), collide[1]] for collide in contacts]
        return points

    
    def isLinePolyColliding(self, p1: Vector2, p2: Vector2, poly: list[Vector2]):
        return any([self.isLineLineColliding(p1, p2, point, poly[(index + 1) % len(poly)]) for index, point in enumerate(poly)])
    
    def isLineColliding(self, p1: Vector2, p2: Vector2):
        return any([self.isLinePolyColliding(p1, p2, poly["points"]) for poly in self.collisionGeometry["tri"]])
    
    def isPolyColliding(self, poly: list[Vector2]):
        return any([self.isLineColliding(point, poly[(index + 1) % len(poly)]) for index, point in enumerate(poly)])
    
    def isRectRectColliding(self, rect1: list[Vector2], rect2: list[Vector2]):
        return rect1[0].x < rect2[1].x and rect1[1].x > rect2[0].x and rect1[0].y < rect2[1].y and rect1[1].y > rect2[0].y
            
    def isRectColliding(self, inputRect):
        #WTF is wrong with this???????
        #return any([pygame.Rect.colliderect(self.generateRect(inputRect), self.generateRect(rect["points"])) for rect in self.geometry["rect"]])
        return any([self.isRectRectColliding(inputRect, rect["points"]) for rect in self.collisionGeometry["rect"]])

    def isTriggerColliding(self, inputRect: list[Vector2]):
        return [trigger for trigger in self.fullGeometry["triggers"] if self.isRectRectColliding(inputRect, trigger["points"])]

    def calcContactDamage(self, inputRect: list[Vector2]):
        damages = [1 for enemy in self.gameEngine.enemies if self.isRectRectColliding(inputRect, enemy.getRectBB())]
        damages.append(0)
        return max(damages)