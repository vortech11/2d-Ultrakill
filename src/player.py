from pygame import Vector2

from pygame import draw
import pygame

from math import sqrt, copysign

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))

def same_sign(a, b):
    if (a > 0 and b > 0) or \
       (a < 0 and b < 0) or \
       (a == 0 and b == 0):
        return True
    return False

class Player:
    def __init__(self):
        self.velosity: Vector2 = Vector2(0, 0)
        self.position: Vector2 = Vector2(100, 100)
        self.airAccel = 0
        self.maxSpeed = 0
        self.airResistance = 0
        self.size = 20
        self.color = (240, 24, 24)
        self.noclip = False
        self.gravity = 1
        self.jumpping = False
        self.jumpSpeed = -25
        self.slamJumpSpeed = -30
        self.slamSpeed = 50
        self.grounded = 0
        self.closeGrounded = False
        self.slide = False
        self.slam = False
        self.startSlam = 0
        self.sliding = False
        self.slideSpeed = 30

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
        
    def updatePlayerPosition(self, world):
        self.position.x += self.velosity.x
        if self.isPlayerColliding(world)[1]:
            stepup = int(abs(3 * self.velosity.x) + 1)
            for x in range(stepup):
                self.position.y -= 1
                if not any(self.isPlayerColliding(world)):
                    break
                if x >= stepup - 1:
                    self.position.y += stepup
                
                    self.position.x -= self.velosity.x
                    self.velosity.x = 0
                    break
        elif self.isPlayerColliding(world)[0]:
            self.position.x -= self.velosity.x
            self.velosity.x = 0
        
        self.position.y += self.velosity.y

        if any(self.isPlayerColliding(world)):
            self.slam = max(self.slam -1, 0)
            self.position.y -= self.velosity.y
            self.velosity.y = 0
            
    def movePlayerDirection(self, dt, direction: Vector2, camera, world):
        if self.noclip:
            self.position += direction * 1000 * dt
            camera.position += (self.position - camera.position)
            return
        
        self.updateGrounded(world)
        self.updateCloseGrounded(world)
        
        if self.grounded > 0:
            self.maxSpeed = 15
        else:
            self.maxSpeed = 15
            self.airAccel = 80
            self.airResistance = 1
                
        if not (self.closeGrounded or self.grounded > 0):
            if self.slide and self.slam == 0 and not self.sliding:
                self.slam = 10
                self.startSlam = self.position.y
                
        elif self.closeGrounded and self.grounded > 0:
            if self.slide and not self.sliding:
                self.sliding = True
                
        if not self.slide:
            self.sliding = False
            
        if self.slam > 0:
            self.velosity = Vector2(0, self.slamSpeed)
        elif self.sliding:
            self.velosity.x = copysign(self.slideSpeed, self.velosity.x)
            
        elif self.grounded > 0:
            if direction == Vector2(0, 0):
                self.velosity.x -= self.velosity.x
            else:
                if abs(self.velosity.x) < self.maxSpeed:
                    self.velosity.x += direction.x * (self.maxSpeed - abs(self.velosity.x))
                elif not same_sign(direction.x, self.velosity.x):
                    self.velosity.x = self.maxSpeed * direction.x
        else:
            if direction == Vector2(0, 0):
                self.velosity.x -= self.velosity.x * self.airResistance * dt
            else:
                if abs(self.velosity.x) < self.maxSpeed or not same_sign(direction.x, self.velosity.x):
                    self.velosity.x += direction.x * self.airAccel * dt
        
        self.velosity.y += self.gravity
        
        if self.jumpping:
            if self.slam > 0:
                if self.closeGrounded:
                    self.velosity.y = min(-2*sqrt(max(self.position.y - self.startSlam, 0) * self.gravity/2), self.slamJumpSpeed)
                    self.slam = 0
                    self.slide = False
            elif self.grounded > 0:
                self.velosity.y = self.jumpSpeed
                self.grounded = 0
            self.jumpping = False

        self.updatePlayerPosition(world)

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