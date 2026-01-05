from pygame import Vector2

from src.enemies import Character
from src.weapons import Pistol

from math import sqrt, copysign

from enum import Enum

def same_sign(a, b):
    if (a > 0 and b > 0) or \
       (a < 0 and b < 0) or \
       (a == 0 and b == 0):
        return True
    return False

class Player(Character):
    class State(Enum):
        NORMAL = 0
        NOCLIP = 1
        SLIDE = 2
        DASH = 3
        SLAM = 4
        
    def __init__(self, gameEngine):
        
        self.normalHitbox = [Vector2(-20, 0), Vector2(20, 0), Vector2(20, 80), Vector2(-20, 80)]
        self.slidingHitbox = [Vector2(-20, 40), Vector2(20, 40), Vector2(20, 80), Vector2(-20, 80)]
        
        super().__init__(
            gameEngine,
            Vector2(0, 0), 
            self.normalHitbox, 
            100,
            3000
        )

        self.collectables = [False, False]
        self.allWeapons = [
            Pistol(self.gameEngine)
        ]
        self.unlockedWeapons = [
            self.allWeapons[0]
        ]
        self.currentWeapon = 0
        
        self.currentState = self.State.NORMAL
        self.Keys = {"K_LCTRL": False, "K_LSHIFT": False}
        self.jumpping = False
                
        self.airAccel = 7500
        self.maxSpeed = 750
        self.airResistance = 1
        self.jumpSpeed = -1200
        self.slamJumpSpeed = -1500
        self.slamSpeed = 2750
        self.slideSpeed = 1500
        self.totalSlamCoyoteTime = 500
        self.dashSpeed = 2500
        self.startDashTime = 0.18
        self.wallJumpX = 1500
        self.wallSlideMult = 0.90
        
        self.staminaRegenSpeed = 20
        
        self.stamina = 100
        self.wallJumps = 3
        
        self.powerupSpeed = 0
        self.dashTime = 0
        self.slamCoyoteTime = 0
        self.startSlam = 0
        self.walled = False
        self.closeGrounded = False
        
    def restartLevel(self):
        self.teleportPlayer(self.gameEngine.world.fullGeometry["player"]["startpos"])
        self.velosity = Vector2(0, 0)
        
        self.gameEngine.deleteAllEnemies()
        self.gameEngine.resetTriggers()
    
        self.health = 100
        self.stamina = 100
        self.currentState = self.State.NORMAL
    
    def updateGrounded(self, world):
        self.position.y += 20
        if any(self.isAABBColliding(world)):
            self.grounded = min(self.grounded + 1, 10)
            self.wallJumps = 3
        else:
            self.grounded = max(self.grounded - 1, 0)
        self.position.y -= 20
        
    def updateCloseGrounded(self, world):
        self.position.y += 100
        if any(self.isAABBColliding(world)):
            self.closeGrounded = True
        else:
            self.closeGrounded = False
        self.position.y -= 100
    
    def updateWalled(self, world):
        self.walled = 0
        self.position.x += 10
        if any(self.isAABBColliding(world)):
            self.walled = -1
        self.position.x -= 10
        self.position.x -= 10
        if any(self.isAABBColliding(world)):
            self.walled = 1
        self.position.x += 10

    def teleportPlayer(self, teleportPosition: Vector2):
        cameraOffset = self.gameEngine.camera.position - self.position
        self.position = teleportPosition.copy()
        self.gameEngine.camera.position = self.position + cameraOffset
        
        
    def updatePlayerPosition(self, world, dt):
        self.position.x += self.velosity.x * dt
        collision = self.isAABBColliding(world)
        if collision[1]:
            stepup = int(abs(self.stepup * self.velosity.x * dt) + 1)
            #print(stepup)
            for x in range(stepup):
                self.position.y -= 1
                if not any(self.isAABBColliding(world)):
                    break
                if x >= stepup - 1:
                    self.position.y += stepup
                
                    self.position.x -= self.velosity.x * dt
                    self.velosity.x = copysign(0.01, self.velosity.x)
                    self.velosity.y *= self.wallSlideMult
                    if self.currentState == self.State.SLIDE:
                        self.currentState = self.State.NORMAL
                        self.Keys["K_LCTRL"] = False
                    break
        elif collision[0] or collision[2]:
            for x in range(self.moveSubDiv[0]):
                self.position.x -= self.velosity.x / self.moveSubDiv[0] * dt
                if not any(self.isAABBColliding(world)):
                    break
            self.velosity.x = copysign(0.01, self.velosity.x)
            self.velosity.y *= self.wallSlideMult
            if self.currentState == self.State.SLIDE:
                self.currentState = self.State.NORMAL
                self.Keys["K_LCTRL"] = False
        
        self.position.y += self.velosity.y * dt

        if any(self.isAABBColliding(world)):
            for x in range(self.moveSubDiv[1]):
                self.position.y -= self.velosity.y / self.moveSubDiv[1] * dt
                if not any(self.isAABBColliding(world)):
                    break
            self.slamCoyoteTime = max(self.slamCoyoteTime -1, 0)
            self.velosity.y = 0

    def handleTrigger(self, trigger):
        if trigger["active"]:
            for index, func in enumerate(trigger["funcs"]):
                match func:
                    case "hurt":
                        self.health -= trigger["perameters"][index][0]
                    case "levelEnd":
                        if any(self.collectables):
                            self.gameEngine.levelWin = True
                            self.gameEngine.levelToBeLoaded = trigger["perameters"][index][0]
                    case "collectable":
                        self.collectables[trigger["perameters"][index][0]] = True
                    case "powerup":
                        match trigger["perameters"][0]:
                            case "speed":
                                self.powerupSpeed = trigger["perameters"][index][1]
                    case "spawnEnemies":
                        self.gameEngine.spawnTriggerEnemies(trigger["perameters"][index][0])
                    case "activateTrigger":
                        self.gameEngine.world.fullGeometry["triggers"][trigger["perameters"][index][0]]["active"] = True
                    case "move":
                        self.gameEngine.triggerEntities(trigger["perameters"][index][0])

        if trigger["triggerOnce"]:
            trigger["active"] = False

    def handleTriggers(self, world):
        collidingTriggers = world.isTriggerColliding(self.getRectBB())
        if any(collidingTriggers):
            for trigger in collidingTriggers:
                self.handleTrigger(trigger)
                                
    def handleDamage(self):
        if not self.currentState == self.State.DASH:
            self.health -= self.gameEngine.world.calcContactDamage(self.getRectBB())
        
        if self.health <= 0:
            self.restartLevel()
            
    def movePlayerDirection(self, dt, direction: Vector2, camera, world):
        if self.currentState == self.State.NOCLIP:
            self.position += direction * dt * 1000
            camera.position += (self.position - camera.position)
            return
        
        self.updateGrounded(world)
        self.updateCloseGrounded(world)
        self.updateWalled(world)

        if self.Keys["K_LSHIFT"] and self.stamina > 33:
            self.currentState = self.State.DASH
            self.stamina -= 33
            if not direction.x == 0:
                self.velosity.x = copysign(self.velosity.x, direction.x)
            self.Keys["K_LSHIFT"] = False
            self.dashTime = self.startDashTime
                
        if (not (self.closeGrounded or self.grounded > 0)) and self.Keys["K_LCTRL"]:
            if not (self.currentState == self.State.SLAM or self.currentState == self.State.SLIDE):
                self.Keys["K_LCTRL"] = False
                self.currentState = self.State.SLAM
                self.slamCoyoteTime = self.totalSlamCoyoteTime * dt
                self.startSlam = self.position.y
                
        elif (self.closeGrounded and self.grounded > 0) and self.Keys["K_LCTRL"]:
            if not self.currentState == self.State.SLIDE:
                self.currentState = self.State.SLIDE
                
        if not self.Keys["K_LCTRL"]:
            if self.currentState == self.State.SLIDE:
                self.currentState = self.State.NORMAL

        self.velosity.y += self.gravity * dt

        if not direction.x == 0: 
            self.facing = self.clamp(0, direction.x, 1)
            
        match self.currentState:
            case self.State.SLAM:
                self.velosity = Vector2(0, self.slamSpeed)
                if self.grounded > 0:
                    self.currentState = self.State.NORMAL
                    self.Keys["K_LCTRL"] = False
            case self.State.SLIDE:
                self.velosity.x = copysign(self.slideSpeed, self.velosity.x)
                self.hitbox = self.slidingHitbox
                self.facing = self.clamp(0, copysign(1, self.velosity.x), 1)
            case self.State.DASH:
                self.velosity = Vector2(copysign(self.dashSpeed, self.velosity.x), 0)
                self.dashTime = max(self.dashTime - dt, 0)
                if self.dashTime == 0:
                    self.currentState = self.State.NORMAL
                    self.velosity.x = self.clamp(0, copysign(self.maxSpeed, self.velosity.x), 1)
            case self.State.NORMAL:
                self.hitbox = self.normalHitbox
                if self.grounded > 0:
                    if direction == Vector2(0, 0):
                        self.velosity.x -= self.velosity.x
                    else:
                        self.velosity.x = (self.maxSpeed + self.powerupSpeed) * direction.x
                        #if abs(self.velosity.x) < self.maxSpeed:
                        #    self.velosity.x += direction.x * (self.maxSpeed - abs(self.velosity.x))
                        #elif not same_sign(direction.x, self.velosity.x):
                        #    self.velosity.x = self.maxSpeed * direction.x
                else:
                    if direction == Vector2(0, 0):
                        self.velosity.x -= self.velosity.x * self.airResistance * dt
                    else:
                        if abs(self.velosity.x) < self.maxSpeed or not same_sign(direction.x, self.velosity.x):
                            self.velosity.x += direction.x * self.airAccel * dt
                            
        if not self.currentState == self.State.SLIDE:
            self.stamina = min(self.stamina + self.staminaRegenSpeed * dt, 100)
        
        
        if self.jumpping:
            if self.currentState == self.State.SLIDE:
                self.currentState = self.State.NORMAL
                self.Keys["K_LCTRL"] = False
            if self.currentState == self.State.DASH:
                self.currentState = self.State.NORMAL
            if self.slamCoyoteTime > 0:
                if self.closeGrounded:
                    self.velosity.y = min(-2*sqrt(max(self.position.y - self.startSlam, 0) * self.gravity/2), self.slamJumpSpeed) 
                    self.slamCoyoteTime = 0
                    self.currentState = self.State.NORMAL
            elif self.grounded > 0:
                self.velosity.y = self.jumpSpeed
                self.grounded = 0
            elif not self.walled == 0:
                if self.wallJumps > 0:
                    self.velosity.y = self.jumpSpeed
                    self.velosity.x = copysign(self.wallJumpX, self.walled)
                    self.wallJumps -= 1
            self.jumpping = False

        #self.handleTriggers(world)
        
        self.handleDamage()

        self.updatePlayerPosition(world, dt)

        camera.position += (self.position - camera.position) * 0.2
        
    def shootWeapons(self, mousePos:Vector2, currentMouseButttons, mouseDownEvents):
        globalMousePos = self.gameEngine.camera.unTransformPoint(mousePos)
        if mouseDownEvents[1]:
            self.unlockedWeapons[self.currentWeapon].shootPrimary(self.position, globalMousePos - self.position)
        