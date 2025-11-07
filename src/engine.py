from src.camera import Camera
from src.geometry import Geometry
from src.player import Player
from src.ui import UiHandler
import src.enemies

import pygame
from pygame import Vector2

from pathlib import Path

import json

class GameEngine:
    def loadImages(self):
        imageDir = Path("images")
        imageDataPath = imageDir / "imageData.json"
        with open(imageDataPath) as file:
            imageData = json.load(file)
        for enemyName, enemy in imageData.items():
            for imageName, image in enemy.items():
                imageData[enemyName][imageName]["image"] = pygame.image.load(imageDir / enemyName / imageName).convert_alpha()
                imageData[enemyName][imageName]["center"] = Vector2(image["center"])
        return imageData

    def resetTriggers(self):
        for trigger in self.world.geometry["triggers"]:
            trigger["active"] = True
            
    def spawnTriggerEnemies(self, triggerIndex):
        for enemyTrigger in self.world.geometry["enemySpawner"]:
            if enemyTrigger["triggerParentIndex"] == triggerIndex:
                spawnedEnemy = None
                startPos = enemyTrigger["position"]
                match enemyTrigger["enemyType"]:
                    case "Filth":
                        spawnedEnemy = src.enemies.Filth(self, Vector2(startPos))
                self.enemies.append(spawnedEnemy)
    
    def __init__(self, gameName="2D Ultrakill", screenSize=Vector2(800, 800)) -> None:
        self.screenSize = screenSize
        
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenSize, vsync=1)
        pygame.display.set_caption(gameName)
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.levelWin = False
        
        self.camera = Camera(self.screenSize)
        self.world = Geometry(self)
        self.player = Player(self)
        self.uiHandler = UiHandler(self)

        self.enemies = []
        
        self.images = self.loadImages()
        
        self.world.loadGeometryFile("level.json")
        self.player.restartLevel()
        
    def tickWorld(self, dt):
        for enemy in self.enemies:
            enemy.move(dt)

    def renderEnemies(self):
        for enemy in self.enemies:
            enemy.renderSprite()
            
    def deleteAllEnemies(self):
        for index in range(len(self.enemies)):
            del self.enemies[index]
    
    def shutdown(self):
        pygame.quit()
        