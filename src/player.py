from pygame import Vector2

from pygame import draw
import pygame

from math import sqrt, copysign

from enum import Enum

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))

def same_sign(a, b):
    if (a > 0 and b > 0) or \
       (a < 0 and b < 0) or \
       (a == 0 and b == 0):
        return True
    return False

class Player:
    class State(Enum):
        NORMAL = 0
        NOCLIP = 1
        SLIDE = 2
        DASH = 3
        SLAM = 4
        
    def __init__(self):
        self.velosity: Vector2 = Vector2(0, 0)
        self.position: Vector2 = Vector2(100, 100)
        self.color = (240, 24, 24)
        self.size = 20
        
        self.currentState = self.State.NORMAL
        self.Keys = {"K_LCTRL": False, "K_LSHIFT": False}
        self.jumpping = False
        
        self.moveSubDiv: list[int] = [7, 4]
        self.stepup = 1
        
        self.airAccel = 7500
        self.maxSpeed = 750
        self.airResistance = 1
        self.gravity = 3000
        self.jumpSpeed = -1200
        self.slamJumpSpeed = -1500
        self.slamSpeed = 2500
        self.slideSpeed = 1500
        self.totalSlamCoyoteTime = 500
        self.dashSpeed = 2500
        self.startDashTime = 0.20
        
        self.dashTime = 0
        self.slamCoyoteTime = 0
        self.startSlam = 0
        self.grounded = 0
        self.walled = False
        self.closeGrounded = False

    def isPlayerColliding(self, world):
        rectColliding = world.isRectColliding(self.getPlayerRectBB())
        polyColliding = world.isPolyColliding(self.getPlayerWorldBB())
        return [rectColliding, polyColliding]
    
    def updateGrounded(self, world):
        self.position.y += 20
        if any(self.isPlayerColliding(world)):
            self.grounded = min(self.grounded + 1, 10)
        else:
            self.grounded = max(self.grounded - 1, 0)
        self.position.y -= 20
        
    def updateCloseGrounded(self, world):
        self.position.y += 100
        if any(self.isPlayerColliding(world)):
            self.closeGrounded = True
        else:
            self.closeGrounded = False
        self.position.y -= 100
    
    def updateWalled(self, world):
        walled = False
        self.position.y += 10
        if any(self.isPlayerColliding(world)):
            walled = True
        self.position.y -= 10
        self.position.y -= 10
        if any(self.isPlayerColliding(world)):
            walled = True
        self.position.y += 10
        self.walled = walled
        
    def updatePlayerPosition(self, world, dt):
        self.position.x += self.velosity.x * dt
        if self.isPlayerColliding(world)[1]:
            stepup = int(abs(self.stepup * self.velosity.x * dt) + 1)
            #print(stepup)
            for x in range(stepup):
                self.position.y -= 1
                if not any(self.isPlayerColliding(world)):
                    break
                if x >= stepup - 1:
                    self.position.y += stepup
                
                    self.position.x -= self.velosity.x * dt
                    self.velosity.x = 0
                    if self.currentState == self.State.SLIDE:
                        self.currentState = self.State.NORMAL
                        self.Keys["K_LCTRL"] = False
                    break
        elif self.isPlayerColliding(world)[0]:
            for x in range(self.moveSubDiv[0]):
                self.position.x -= self.velosity.x / self.moveSubDiv[0] * dt
                if not any(self.isPlayerColliding(world)):
                    break
            self.velosity.x = 0
            if self.currentState == self.State.SLIDE:
                self.currentState = self.State.NORMAL
                self.Keys["K_LCTRL"] = False
        
        self.position.y += self.velosity.y * dt

        if any(self.isPlayerColliding(world)):
            for x in range(self.moveSubDiv[1]):
                self.position.y -= self.velosity.y / self.moveSubDiv[1] * dt
                if not any(self.isPlayerColliding(world)):
                    break
            self.slamCoyoteTime = max(self.slamCoyoteTime -1, 0)
            self.velosity.y = 0
            
    def movePlayerDirection(self, dt, direction: Vector2, camera, world):
        if self.currentState == self.State.NOCLIP:
            self.position += direction * dt * 1000
            camera.position += (self.position - camera.position)
            return
        
        self.updateGrounded(world)
        self.updateCloseGrounded(world)
        self.updateWalled(world)

        if self.Keys["K_LSHIFT"]:
            self.currentState = self.State.DASH
            if not direction.x == 0:
                self.velosity.x = copysign(self.velosity.x, direction.x)
            self.Keys["K_LSHIFT"] = False
            self.dashTime = self.startDashTime
                
        if (not (self.closeGrounded or self.grounded > 0)) and self.Keys["K_LCTRL"]:
            if not self.currentState == self.State.SLAM:
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
            
        match self.currentState:
            case self.State.SLAM:
                self.velosity = Vector2(0, self.slamSpeed)
                if self.grounded > 0:
                    self.currentState = self.State.NORMAL
                    self.Keys["K_LCTRL"] = False
            case self.State.SLIDE:
                self.velosity.x = copysign(self.slideSpeed, self.velosity.x)
            case self.State.DASH:
                self.velosity = Vector2(copysign(self.dashSpeed, self.velosity.x), 0)
                self.dashTime = max(self.dashTime - dt, 0)
                if self.dashTime == 0:
                    self.currentState = self.State.NORMAL
                    self.velosity.x = copysign(self.maxSpeed, self.velosity.x)
            case self.State.NORMAL:
                if self.grounded > 0:
                    if direction == Vector2(0, 0):
                        self.velosity.x -= self.velosity.x
                    else:
                        self.velosity.x = self.maxSpeed * direction.x
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
            self.jumpping = False

        self.updatePlayerPosition(world, dt)

        camera.position += (self.position - camera.position) * 0.2
        
    def getPlayerRectBB(self):
        return [
            self.position - Vector2(self.size, self.size), 
            self.position + Vector2(self.size, self.size)
        ]

    def getPlayerWorldBB(self):
        return [
            self.position - Vector2(self.size, self.size), 
            Vector2(self.position.x + self.size, self.position.y - self.size), 
            self.position + Vector2(self.size, self.size), 
            Vector2(self.position.x - self.size, self.position.y + self.size)
        ]

    def renderPlayer(self, screen, camera):
        draw.polygon(screen, self.color, [camera.transformPoint(point) for point in self.getPlayerWorldBB()])