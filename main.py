import pygame
from pygame import Vector2

from src.camera import Camera
from src.geometry import Geometry
from src.player import Player

screenSize = Vector2(800, 800)

pygame.init()

screen = pygame.display.set_mode(screenSize)

pygame.display.set_caption("2D Ultrakill")
clock = pygame.time.Clock()

running = True

camera = Camera(screenSize)

player = Player()

world = Geometry()

world.loadGeometryFile("level.json")

dt = 1

 

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    dt = clock.tick(60) / 1000.0
    
    keys = pygame.key.get_pressed()

    direction: Vector2 = Vector2(0, 0)
    direction.x = keys[pygame.K_d] - keys[pygame.K_a]
    direction.y = keys[pygame.K_s] - keys[pygame.K_w]

    camera.rotation += (keys[pygame.K_LEFT] - keys[pygame.K_RIGHT]) * 1 * dt
    camera.zoom += (keys[pygame.K_UP] - keys[pygame.K_DOWN]) * 2 * dt * camera.zoom

    if camera.zoom <= 0:
        camera.zoom = 0

    player.movePlayerDirection(dt, direction, camera, world)

    screen.fill((0, 0, 0))

    world.render(camera, screen)

    player.renderPlayer(screen, camera)
    
    camera.renderFPS(clock, screen)

    pygame.display.update()

pygame.quit()