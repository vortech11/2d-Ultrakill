import pygame
from pygame import Vector2

from enum import Enum

from src.camera import Camera
from src.geometry import Geometry
from src.player import Player

screenSize = Vector2(800, 800)

pygame.init()
pygame.font.init()

DEBUG_FONT = pygame.font.SysFont("Arial", 20)

screen = pygame.display.set_mode(screenSize)

pygame.display.set_caption("2D Ultrakill")
clock = pygame.time.Clock()

running = True

camera = Camera(screenSize)

player = Player()

world = Geometry()

world.loadGeometryFile("level.json")

class modes(Enum):
    normal = 0
    rect = 1
    triangle = 2
    delete = 3
    color = 4
    
class colors(Enum):
    darkGrey = (50, 50, 50)
    lightGrey = (100, 100, 100)
    green = (31, 158, 27)

colorsList = [color.value for color in colors]

class Editor():
    def __init__(self):
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
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    world.saveGeometryFile()
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
                if event.key == pygame.K_ESCAPE:
                    self.mode = modes.normal
                    self.pointData = []
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseKeys = [True if event.button == index else False for index in range(3)]
                    
        keys = pygame.key.get_pressed()
        mousePos = Vector2(pygame.mouse.get_pos())
        #mouseKeys = pygame.mouse.get_pressed()
        
        player.noclip = not keys[pygame.K_LSHIFT]

        direction: Vector2 = Vector2(0, 0)
        direction.x = keys[pygame.K_d] - keys[pygame.K_a]
        direction.y = keys[pygame.K_s] - keys[pygame.K_w]

        camera.zoom += (keys[pygame.K_UP] - keys[pygame.K_DOWN]) * 2 * dt * camera.zoom

        if camera.zoom <= 0:
            camera.zoom = 0

        match self.mode:
            case modes.rect:
                self.displayText = f"{len(self.pointData)}"
                if mouseKeys[1]:
                    self.pointData.append(self.roundVector(camera.unTransformPoint(mousePos)))
                if len(self.pointData) > 0:
                    pygame.draw.polygon(screen, self.drawColor, world.generateRectPolyPoints([camera.transformPoint(self.pointData[0]), camera.transformPoint(self.roundVector(camera.unTransformPoint(mousePos)))]))
                if len(self.pointData) == 2:
                    self.pointData = self.fixRectWrapping(self.pointData)
                    world.geometry["rect"].append({
                        "points": self.pointData,
                        "renderPoints": world.generateRectPolyPoints(self.pointData),
                        "color": [self.drawColor[0], self.drawColor[1], self.drawColor[2]]
                    })
                    self.pointData = []
                    self.mode = modes.normal
            case modes.triangle:
                self.displayText = f"{len(self.pointData)}"
                if mouseKeys[1]:
                    self.pointData.append(self.roundVector(camera.unTransformPoint(mousePos)))
                if len(self.pointData) == 1:
                    pygame.draw.polygon(screen, self.drawColor, [camera.transformPoint(self.pointData[0]), camera.transformPoint(self.pointData[0] + Vector2(10, -10)), camera.transformPoint(self.roundVector(camera.unTransformPoint(mousePos)))])
                if len(self.pointData) == 2:
                    pygame.draw.polygon(screen, self.drawColor, [camera.transformPoint(self.pointData[0]), camera.transformPoint(self.pointData[1]), camera.transformPoint(self.roundVector(camera.unTransformPoint(mousePos)))])
                if len(self.pointData) == 3:
                    self.pointData = self.fixTriWrapping(self.pointData)
                    world.geometry["tri"].append({
                        "points": self.pointData,
                        "color": [self.drawColor[0], self.drawColor[1], self.drawColor[2]]
                    })
                    self.pointData = []
                    self.mode = modes.normal
            case modes.delete:
                if mouseKeys[1]:
                    toBeDel = world.isPointColliding(camera.unTransformPoint(mousePos))
                    if len(toBeDel["rect"]) > 0:
                        del world.geometry["rect"][toBeDel["rect"][-1]]
                    if len(toBeDel["tri"]) > 0:
                        del world.geometry["tri"][toBeDel["tri"][-1]]
            case modes.color:
                self.displayText = f"{colors(self.drawColor).name}"
                if keys[pygame.K_1]:
                    self.drawColor = pygame.Color(colorsList[0])
                if keys[pygame.K_2]:
                    self.drawColor = pygame.Color(colorsList[1])
                if keys[pygame.K_3]:
                    self.drawColor = pygame.Color(colorsList[2])
                    
            case modes.normal:
                self.displayText = ""
                

        player.movePlayerDirection(dt, direction, camera, world)


    
editor = Editor()

def displayMode():
    text_surface = DEBUG_FONT.render(f"{modes(editor.mode).name} {editor.displayText}", True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))

dt = 1

player.noclip = True
player.speed = 450

while running:
    dt = clock.tick(60) / 1000.0
    
    screen.fill((0, 0, 0))
    
    displayMode()

    world.render(camera, screen)
    
    player.renderPlayer(screen, camera)
    
    editor.userInput()
    
    pygame.display.update()

pygame.quit()