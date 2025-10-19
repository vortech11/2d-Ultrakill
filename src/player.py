from pygame import Vector2

from pygame import draw
import pygame

from math import copysign

def clamp(minimum, x, maximum):
    return max(minimum, min(x, maximum))

class Player:
    def __init__(self):
        self.velosity: Vector2 = Vector2(0, 0)
        self.position: Vector2 = Vector2(100, 100)
        #self.airResistance = 0
        self.speed = 0
        self.maxSpeed = 0
        self.slowSpeed = 0
        self.runAirSpeed = 20
        self.size = 20
        self.color = (240, 24, 24)
        self.noclip = False
        self.gravity = 1
        self.jumpping = False
        self.jumpSpeed = -25
        self.grounded = False
        self.slam = False

    def isPlayerColliding(self, world):
        rectColliding = world.isRectColliding(self.getPlayerRectBB())
        polyColliding = world.isPolyColliding(self.getPlayerWorldBB())
        return rectColliding or polyColliding
    
    def updateGrounded(self, world):
        self.position.y += 5
        if self.isPlayerColliding(world):
            self.grounded = True
        else:
            self.grounded = False
        self.position.y -= 5
        
    def movePlayerDirection(self, dt, direction: Vector2, camera, world):
        if self.noclip:
            self.position += direction * 1000 * dt
            camera.position += (self.position - camera.position)
            return
        
        self.updateGrounded(world)
        
        if self.grounded:
            self.maxSpeed = 15
            self.speed = 200
            #self.airResistance = 0.9
            self.slowSpeed = 12
        else:
            self.maxSpeed = 20
            self.speed = 50
            #self.airResistance = 0.8
            self.slowSpeed = 1
            
        oldxVelocity = self.velosity.x

        if direction == Vector2(0, 0):
            self.velosity.x -= self.velosity.x * self.slowSpeed * dt
        else:
            self.velosity.x += direction.x * self.speed * dt
        
        if abs(self.velosity.x) > self.maxSpeed:
                if abs(oldxVelocity) < abs(self.velosity.x):
                    self.velosity.x -= direction.x * self.speed * dt
        
        #self.velosity = Vector2(clamp(-self.maxSpeed, self.velosity.x, self.maxSpeed), self.velosity.y)
        
        self.velosity.y += self.gravity
        
        if self.jumpping:
            if self.grounded:
                self.velosity.y += self.jumpSpeed
            self.jumpping = False

        self.position.x += self.velosity.x
        if self.isPlayerColliding(world):
            stepup = int(abs(2 * self.velosity.x))
            for x in range(stepup):
                self.position.y -= 1
                if not self.isPlayerColliding(world):
                    break
                if x >= stepup - 1:
                    self.position.y += stepup
                
                    self.position.x -= self.velosity.x
                    self.velosity.x = 0
                    break
        
        self.position.y += self.velosity.y

        if self.isPlayerColliding(world):
            self.position.y -= self.velosity.y
            self.velosity.y = 0

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