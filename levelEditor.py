import pygame
from pygame import Vector2

from enum import Enum

from src.engine import GameEngine

screenSize = Vector2(800, 800)
pygame.font.init()

DEBUG_FONT = pygame.font.SysFont("Arial", 20)

class modes(Enum):
    normal = 0
    rect = 1
    triangle = 2
    delete = 3
    color = 4
    trigger = 5
    enemySpawn = 6
    playerSpawn = 7
    
class colors(Enum):
    darkGrey = (50, 50, 50)
    lightGrey = (100, 100, 100)
    green = (31, 158, 27)
    red = (255, 0, 0)
    yellow = (255, 194, 13)
    lightGreen = (0, 255, 0)
    lightBlue = (36, 168, 224)

colorsList = [color.value for color in colors]

class Editor():
    def __init__(self, gameEngine):
        self.engine = gameEngine
        self.mode = modes.normal
        self.pointData = []
        self.displayText = "0"
        self.drawColor = (100, 100, 100)
        
    def fixRectWrapping(self, rect: list[Vector2]):
        if rect[0].x > rect[1].x:
            rect[0].x, rect[1].x = rect[1].x, rect[0].x
        if rect[0].y > rect[1].y:
            rect[0].y, rect[1].y = rect[1].y, rect[0].y
        return rect
    
    def fixTriWrapping(self, tri: list[Vector2]):
        p1 = tri[0]
        p2 = tri[1]
        p3 = tri[2]
        cross_product = (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x)
        if cross_product > 0:
            tri = [p1, p3, p2]
            return tri
        tri = [p1, p2, p3]
        return tri
    
    def roundVector(self, vec: Vector2):
        return Vector2(round(vec.x, -1), round(vec.y, -1))

    def userInput(self):
        global running
        mouseKeys = [False, False, False]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.engine.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.engine.world.saveGeometryFile()
                    print("File Writen To!")
                if event.key == pygame.K_r:
                    self.mode = modes.rect
                    self.pointData = []
                if event.key == pygame.K_t:
                    self.mode = modes.triangle
                if event.key == pygame.K_TAB:
                    self.mode = modes.delete
                if event.key == pygame.K_q:
                    self.mode = modes.color
                if event.key == pygame.K_f:
                    self.mode = modes.trigger
                if event.key == pygame.K_c:
                    self.mode = modes.enemySpawn
                if event.key == pygame.K_p:
                    self.mode = modes.playerSpawn
                if event.key == pygame.K_ESCAPE:
                    self.mode = modes.normal
                    self.pointData = []
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseKeys = [True if event.button == index else False for index in range(3)]
                    
        keys = pygame.key.get_pressed()
        mousePos = Vector2(pygame.mouse.get_pos())
        #mouseKeys = pygame.mouse.get_pressed()
        
        if keys[pygame.K_LSHIFT]:
            self.engine.player.currentState = self.engine.player.State.NORMAL
        else:
            self.engine.player.currentState = self.engine.player.State.NOCLIP

        direction: Vector2 = Vector2(0, 0)
        direction.x = keys[pygame.K_d] - keys[pygame.K_a]
        direction.y = keys[pygame.K_s] - keys[pygame.K_w]

        self.engine.camera.zoom += (keys[pygame.K_UP] - keys[pygame.K_DOWN]) * 2 * dt * self.engine.camera.zoom

        if self.engine.camera.zoom <= 0:
            self.engine.camera.zoom = 0

        match self.mode:
            case modes.rect:
                self.displayText = f"{len(self.pointData)}"
                if mouseKeys[1]:
                    self.pointData.append(self.roundVector(self.engine.camera.unTransformPoint(mousePos)))
                if len(self.pointData) > 0:
                    pygame.draw.polygon(
                        self.engine.screen, 
                        self.drawColor, 
                        self.engine.world.generateRectPolyPoints([
                            self.engine.camera.transformPoint(self.pointData[0]),
                            self.engine.camera.transformPoint(self.roundVector(self.engine.camera.unTransformPoint(mousePos)))
                            ])
                    )
                if len(self.pointData) == 2:
                    self.pointData = self.fixRectWrapping(self.pointData)
                    self.engine.world.collisionGeometry["rect"].append({
                        "points": self.pointData,
                        "renderPoints": self.engine.world.generateRectPolyPoints(self.pointData),
                        "color": [self.drawColor[0], self.drawColor[1], self.drawColor[2]]
                    })
                    self.pointData = []
                    self.mode = modes.normal
            case modes.triangle:
                self.displayText = f"{len(self.pointData)}"
                if mouseKeys[1]:
                    self.pointData.append(self.roundVector(self.engine.camera.unTransformPoint(mousePos)))
                if len(self.pointData) == 1:
                    pygame.draw.polygon(
                        self.engine.screen, 
                        self.drawColor, 
                        [
                            self.engine.camera.transformPoint(self.pointData[0]), 
                            self.engine.camera.transformPoint(self.pointData[0] + Vector2(10, -10)), 
                            self.engine.camera.transformPoint(self.roundVector(self.engine.camera.unTransformPoint(mousePos)))
                        ]
                    )
                if len(self.pointData) == 2:
                    pygame.draw.polygon(
                        self.engine.screen, 
                        self.drawColor, 
                        [
                            self.engine.camera.transformPoint(self.pointData[0]), 
                            self.engine.camera.transformPoint(self.pointData[1]),
                            self.engine.camera.transformPoint(self.roundVector(self.engine.camera.unTransformPoint(mousePos)))
                        ]
                    )
                if len(self.pointData) == 3:
                    self.pointData = self.fixTriWrapping(self.pointData)
                    self.engine.world.collisionGeometry["tri"].append({
                        "points": self.pointData,
                        "color": [self.drawColor[0], self.drawColor[1], self.drawColor[2]]
                    })
                    self.pointData = []
                    self.mode = modes.normal
            case modes.trigger:
                self.displayText = f"{len(self.pointData)}"
                if mouseKeys[1]:
                    self.pointData.append(self.roundVector(self.engine.camera.unTransformPoint(mousePos)))
                if len(self.pointData) > 0:
                    pygame.draw.polygon(
                        self.engine.screen, 
                        (235, 199, 19), 
                        self.engine.world.generateRectPolyPoints([
                            self.engine.camera.transformPoint(self.pointData[0]),
                            self.engine.camera.transformPoint(self.roundVector(self.engine.camera.unTransformPoint(mousePos)))
                            ])
                    )
                if len(self.pointData) == 2:
                    self.pointData = self.fixRectWrapping(self.pointData)
                    self.engine.world.fullGeometry["triggers"].append({
                        "points": self.pointData,
                        "func": "Nothing",
                        "perameters": [len(self.engine.world.fullGeometry["triggers"])],
                        "triggerOnce": False,
                        "active": True
                    })
                    self.pointData = []
                    self.mode = modes.normal
            case modes.delete:
                if mouseKeys[1]:
                    toBeDel = self.engine.world.isPointColliding(self.engine.camera.unTransformPoint(mousePos))
                    if len(toBeDel["rect"]) > 0:
                        del self.engine.world.collisionGeometry["rect"][toBeDel["rect"][-1]]
                    if len(toBeDel["tri"]) > 0:
                        del self.engine.world.collisionGeometry["tri"][toBeDel["tri"][-1]]
                    elif len(toBeDel["triggers"]) > 0:
                        del self.engine.world.fullGeometry["triggers"][toBeDel["triggers"][-1]]
            case modes.playerSpawn:
                if mouseKeys[1]:
                    self.engine.world.fullGeometry["player"]["startpos"] = Vector2(self.engine.camera.unTransformPoint(mousePos))
            case modes.color:
                self.displayText = f"{colors(self.drawColor).name}"
                if keys[pygame.K_1]:
                    self.drawColor = pygame.Color(colorsList[0])
                if keys[pygame.K_2]:
                    self.drawColor = pygame.Color(colorsList[1])
                if keys[pygame.K_3]:
                    self.drawColor = pygame.Color(colorsList[2])
                if keys[pygame.K_4]:
                    self.drawColor = pygame.Color(colorsList[3])
                if keys[pygame.K_5]:
                    self.drawColor = pygame.Color(colorsList[4])
                if keys[pygame.K_6]:
                    self.drawColor = pygame.Color(colorsList[5])
                if keys[pygame.K_7]:
                    self.drawColor = pygame.Color(colorsList[6])
                    
            case modes.normal:
                self.displayText = ""
                

        self.engine.player.movePlayerDirection(dt, direction, self.engine.camera, self.engine.world)
        
    def displayMode(self):
        text_surface = DEBUG_FONT.render(f"{modes(editor.mode).name} {editor.displayText}", True, (255, 255, 255))
        self.engine.screen.blit(text_surface, (10, 10))

engine = GameEngine("2D Ultrakill Level Editor", screenSize)
editor = Editor(engine)

dt = 1

engine.player.currentState = engine.player.State.NOCLIP
engine.player.airAccel = 450

while engine.running:
    dt = engine.clock.tick(60) / 1000.0
    
    engine.screen.fill((0, 0, 0))

    engine.world.render(engine.camera, engine.screen)

    engine.world.renderDevInfo(engine.camera, engine.screen)

    editor.userInput()

    engine.player.renderSprite()

    #engine.camera.renderFPS(engine.clock, engine.screen)

    editor.displayMode()

    pygame.display.update()

engine.shutdown()