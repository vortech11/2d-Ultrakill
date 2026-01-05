from src.camera import Camera
from src.geometry import Geometry
from src.player import Player
from src.ui import UiHandler
import src.enemies

import pygame
from pygame import Vector2

from pathlib import Path
from enum import Enum
import json

class slowState(Enum):
    normal = 0
    slow = 1
    wait = 2
    speedup = 3

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
        for trigger in self.world.fullGeometry["triggers"]:
            trigger["active"] = True

    def triggerEntities(self, triggerIndex):
        for entity in self.world.entityGeometry:
            if entity["triggerParentIndex"] == triggerIndex:
                entity["moving"] = True
            
    def spawnTriggerEnemies(self, triggerIndex):
        for enemyTrigger in self.world.fullGeometry["enemySpawner"]:
            if enemyTrigger["triggerParentIndex"] == triggerIndex:
                spawnedEnemy = None
                startPos = enemyTrigger["position"]
                match enemyTrigger["enemyType"]:
                    case "Filth":
                        spawnedEnemy = src.enemies.Filth(self, Vector2(startPos))
                    case "Stray":
                        spawnedEnemy = src.enemies.Stray(self, Vector2(startPos))
                    case "Maurice":
                        spawnedEnemy = src.enemies.Maurice(self, Vector2(startPos))
                self.enemies.append(spawnedEnemy)
                
    def startLevel(self, levelName):
        self.world.loadGeometryFile(levelName)
        self.player.restartLevel()

    def drawRect(self, screen, color, rect: pygame.Rect):
        tempSurface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        tempSurface.fill(color)
        self.screen.blit(tempSurface, (rect.x, rect.y))

    def drawPoly(self, screen, color, points: list[Vector2]):
        x_values = [point.x for point in points]
        y_values = [point.y for point in points]

        minX = min(x_values)
        maxX = max(x_values)
        minY = min(y_values)
        maxY = max(y_values)

        tempSurface = pygame.Surface((maxX - minX, maxY - minY), pygame.SRCALPHA)
        pygame.draw.polygon(tempSurface, color, self.camera.transformPolyToSurfaceSpace(points, minX, minY), self.renderBoarderSize)
        screen.blit(tempSurface, (minX, minY))

    def renderScreen(self):
        self.screen.blit(self.screenFrame, (0, 0))
        pygame.display.update()
        self.screenFrame.fill((0, 0, 0))
        self.screen.fill((0, 0, 0))

    def updateGameSpeed(self):
        if self.currentSlowState == slowState.normal:
            return

        worldDt = self.dt / self.speed
        self.currentSlowValue += worldDt

        match self.currentSlowState:
            case slowState.slow:
                self.speed -= (self.speed - self.gameSlowInfo["duration"][0]) * self.gameSlowInfo["attack"][0]
                if self.currentSlowValue >= self.gameSlowInfo["attack"][1]:
                    self.currentSlowState = slowState.wait
                    self.currentSlowValue = 0
            case slowState.wait:
                self.speed = self.gameSlowInfo["duration"][0]
                if self.currentSlowValue >= self.gameSlowInfo["duration"][1]:
                    self.currentSlowState = slowState.speedup
                    self.currentSlowValue = 0
            case slowState.speedup:
                self.speed += (1 - self.speed) * self.gameSlowInfo["resume"][0]
                if self.currentSlowValue >= self.gameSlowInfo["resume"][1]:
                    self.currentSlowState = slowState.normal
                    self.speed = 1
                    self.currentSlowValue = 0

        return

    def slowdownTime(self, attack: tuple, duration: tuple, resume: tuple):
        self.gameSlowInfo = {
            "attack": attack,
            "duration": duration,
            "resume": resume
        }

        self.currentSlowValue = 0
        self.currentSlowState = slowState.slow
    
    def __init__(self, gameName="2D Ultrakill", screenSize=Vector2(800, 800), startLevel="levelSelect.json") -> None:
        self.screenSize = screenSize
        
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenSize, vsync=1)
        self.screenFrame = pygame.Surface(self.screenSize, pygame.SRCALPHA)
        pygame.display.set_caption(gameName)
        self.clock = pygame.time.Clock()
        self.running = True

        self.dt = 0
        self.speed = 1
        self.gameSlowInfo = []
        self.currentSlowState = slowState.normal
        self.currentSlowValue = 0

        self.renderBoarderSize = 0
        
        self.currentLevel = startLevel
        self.levelWin = False
        self.levelToBeLoaded = ""
        
        self.camera = Camera(self.screenSize)
        self.world = Geometry(self)
        self.player = Player(self)
        self.uiHandler = UiHandler(self)

        self.enemies = []
        self.enemiesToBeDeleted = []
        self.images = self.loadImages()
        
        self.startLevel(startLevel)

    def updateDeltaTime(self):
        self.dt = self.clock.tick(60) / 1000.0 * self.speed

    def hurtEnemy(self, enemyIndex, damage):
        self.enemies[enemyIndex].health -= damage
        if self.enemies[enemyIndex].health <= 0:
            #enemy = self.enemies[enemyIndex]
            self.enemiesToBeDeleted.append(enemyIndex)
            #del enemy

    def tickTriggers(self):
        for trigger in self.world.fullGeometry["triggers"]:
            if not trigger["active"]:
                continue
            match trigger["onEvent"]:
                case "playerEnter":
                    if self.world.isRectRectColliding(self.player.getRectBB(), trigger["points"]):
                        self.player.handleTrigger(trigger)
                case "deadEnemies":
                    if len(self.enemies) == 0:
                        self.player.handleTrigger(trigger)
            
            
        
    def killDeadEnemies(self):
        for index in self.enemiesToBeDeleted:
            self.enemies[index] = None
        self.enemiesToBeDeleted = []
        self.enemies = [enemy for enemy in self.enemies if not enemy is None]

    def tickWorld(self, dt):
        self.tickTriggers()
        self.world.updateEntityPositions()
        for enemy in self.enemies:
            enemy.move(dt)

    def renderEnemies(self):
        for enemy in self.enemies:
            enemy.renderSprite()
            #enemy.renderHitbox((255, 255, 255))
            
    def deleteAllEnemies(self):
        self.enemies = []
        self.enemiesToBeDeleted = []
        #for index in range(len(self.enemies)):
        #    del self.enemies[index]
    
    def shutdown(self):
        pygame.quit()
        