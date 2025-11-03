from src.engine import GameEngine

from pygame import Vector2
import pygame

engine = GameEngine()

while engine.running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            engine.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                engine.player.jumpping = True
            if event.key == pygame.K_LCTRL:
                engine.player.Keys["K_LCTRL"] = True
            if event.key == pygame.K_LSHIFT:
                engine.player.Keys["K_LSHIFT"] = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LCTRL:
                engine.player.Keys["K_LCTRL"] = False
            if event.key == pygame.K_LSHIFT:
                engine.player.Keys["K_LSHIFT"] = False

    dt = engine.clock.tick(60) / 1000.0

    keys = pygame.key.get_pressed()

    direction: Vector2 = Vector2(0, 0)
    direction.x = keys[pygame.K_d] - keys[pygame.K_a]
    direction.y = keys[pygame.K_w] - keys[pygame.K_s]


    engine.camera.rotation += (keys[pygame.K_LEFT] - keys[pygame.K_RIGHT]) * 1 * dt
    engine.camera.zoom += (keys[pygame.K_UP] - keys[pygame.K_DOWN]) * 2 * dt * engine.camera.zoom

    if engine.camera.zoom <= 0:
        engine.camera.zoom = 0

    engine.player.movePlayerDirection(dt, direction, engine.camera, engine.world)

    engine.screen.fill((0, 0, 0))

    engine.world.render(engine.camera, engine.screen)

    engine.renderEnemies()

    engine.player.renderSprite()

    engine.camera.renderFPS(engine.clock, engine.screen)

    engine.uiHandler.renderUi(engine.player, engine.screen, engine.screenSize)

    pygame.display.update()

engine.shutdown()