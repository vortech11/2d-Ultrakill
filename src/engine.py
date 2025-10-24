from src.camera import Camera
from src.geometry import Geometry
from src.player import Player
from src.ui import UiHandler

import pygame
from pygame import Vector2

class GameEngine:
    def __init__(self, screenSize=Vector2(800, 800)) -> None:
        self.screenSize = screenSize
        
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenSize)
        pygame.display.set_caption("2D Ultrakill")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.camera = Camera(self.screenSize)
        self.world = Geometry(self)
        self.player = Player(self)
        self.uiHandler = UiHandler(self)
        
        self.world.loadGeometryFile("level.json")
        
    def runMainLoop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.jumpping = True
                    if event.key == pygame.K_LCTRL:
                        self.player.Keys["K_LCTRL"] = True
                    if event.key == pygame.K_LSHIFT:
                        self.player.Keys["K_LSHIFT"] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LCTRL:
                        self.player.Keys["K_LCTRL"] = False
                    if event.key == pygame.K_LSHIFT:
                        self.player.Keys["K_LSHIFT"] = False

            dt = self.clock.tick(60) / 1000.0

            keys = pygame.key.get_pressed()

            direction: Vector2 = Vector2(0, 0)
            direction.x = keys[pygame.K_d] - keys[pygame.K_a]
            direction.y = keys[pygame.K_w] - keys[pygame.K_s]


            self.camera.rotation += (keys[pygame.K_LEFT] - keys[pygame.K_RIGHT]) * 1 * dt
            self.camera.zoom += (keys[pygame.K_UP] - keys[pygame.K_DOWN]) * 2 * dt * self.camera.zoom

            if self.camera.zoom <= 0:
                self.camera.zoom = 0

            self.player.movePlayerDirection(dt, direction, self.camera, self.world)

            self.screen.fill((0, 0, 0))

            self.world.render(self.camera, self.screen)

            self.player.renderHitbox(self.player.color)

            self.camera.renderFPS(self.clock, self.screen)

            self.uiHandler.renderUi(self.player, self.screen, self.screenSize)

            pygame.display.update()
            
    def shutdown(self):
        pygame.quit()
        