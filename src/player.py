from pygame import Vector2

from pygame import draw

class Player:
    def __init__(self):
        self.position: Vector2 = Vector2(100, 100)
        self.speed = 450
        self.size = 20
        self.color = (240, 24, 24)
        self.noclip = False

    def isPlayerColliding(self, world):
        collidingPoints = [world.isColliding(point) for point in self.getPlayerWorldBB()]
        return any(collidingPoints)

    def movePlayerDirection(self, dt, direction: Vector2, camera, world):
        change = direction * self.speed * dt

        self.position.x += change.x
        if self.isPlayerColliding(world):
            self.position.x -= change.x
        
        self.position.y += change.y

        if self.isPlayerColliding(world):
            self.position.y -= change.y

        camera.position += (self.position - camera.position) * 0.2
        

    def getPlayerWorldBB(self):
        return [
            self.position - Vector2(self.size, self.size), 
            Vector2(self.position.x + self.size, self.position.y - self.size), 
            self.position + Vector2(self.size, self.size), 
            Vector2(self.position.x - self.size, self.position.y + self.size)
        ]

    def renderPlayer(self, screen, camera):
        draw.polygon(screen, self.color, [camera.transformPoint(point) for point in self.getPlayerWorldBB()])