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

class Editor():
    def __init__(self):
        self.mode = modes.normal
        self.pointData = []
        self.drawColor = (100, 100, 100)

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
                if event.key == pygame.K_ESCAPE:
                    self.mode = modes.normal
                    self.pointData = []
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseKeys = [True if event.button == index else False for index in range(3)]
                    
        keys = pygame.key.get_pressed()
        mousePos = Vector2(pygame.mouse.get_pos())
        #mouseKeys = pygame.mouse.get_pressed()

        direction: Vector2 = Vector2(0, 0)
        direction.x = keys[pygame.K_d] - keys[pygame.K_a]
        direction.y = keys[pygame.K_s] - keys[pygame.K_w]

        camera.zoom += (keys[pygame.K_UP] - keys[pygame.K_DOWN]) * 2 * dt * camera.zoom

        if camera.zoom <= 0:
            camera.zoom = 0

        match self.mode:
            case modes.rect:
                if mouseKeys[1]:
                    self.pointData.append(camera.unTransformPoint(mousePos))
                if len(self.pointData) > 0:
                    pygame.draw.polygon(screen, self.drawColor, world.generateRectPolyPoints([camera.transformPoint(self.pointData[0]), mousePos]))
                if len(self.pointData) == 2:
                    world.geometry["rect"].append({
                        "points": self.pointData,
                        "renderPoints": world.generateRectPolyPoints(self.pointData),
                        "color": [self.drawColor[0], self.drawColor[1], self.drawColor[2]]
                    })
                    self.pointData = []
                    self.mode = modes.normal
            case modes.triangle:
                if mouseKeys[1]:
                    self.pointData.append(camera.unTransformPoint(mousePos))
                if len(self.pointData) > 0:
                    pygame.draw.polygon(screen, self.drawColor, world.generateRectPolyPoints([camera.transformPoint(self.pointData[0]), mousePos]))
                if len(self.pointData) == 3:
                    world.geometry["tri"].append({
                        "points": self.pointData,
                        "color": [self.drawColor[0], self.drawColor[1], self.drawColor[2]]
                    })
                    self.pointData = []
                    self.mode = modes.normal
            case modes.delete:
                if mouseKeys[1]:
                    print(world.isPointColliding(camera.unTransformPoint(mousePos)))
                    #print(world.isPointColliding(Vector2(150, 50)))

        player.movePlayerDirection(dt, direction, camera, world)

class modes(Enum):
    normal = 0
    rect = 1
    triangle = 2
    delete = 3
    
editor = Editor()

def displayMode():
    text_surface = DEBUG_FONT.render(f"{modes(editor.mode).name} {len(editor.pointData)}", True, (255, 255, 255))
    screen.blit(text_surface, (10, 10))

dt = 1

while running:
    dt = clock.tick(60) / 1000.0
    
    screen.fill((0, 0, 0))
    
    displayMode()

    world.render(camera, screen)
    
    editor.userInput()
    
    pygame.display.update()

pygame.quit()