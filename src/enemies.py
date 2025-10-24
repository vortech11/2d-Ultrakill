


from pygame import Vector2
from pygame import draw

class Character:
    def __init__(self, gameEngine, startPos:Vector2, hitbox: list[Vector2], totalHealth, gravity=3000):
        self.gameEngine = gameEngine
        self.hitbox: list[Vector2] = hitbox
        self.position: Vector2 = startPos
        self.velosity: Vector2 = Vector2(0, 0)
        
        self.totalhealth = totalHealth
        self.health = self.totalhealth
        
        self.gravity = gravity
        
        self.image = None
        
    def getPolyBB(self):
        return [self.position + point for point in self.hitbox]
    
    def getRectBB(self):
        return [
            self.position + self.hitbox[0],
            self.position + self.hitbox[2]
        ]
    
    def renderHitbox(self, color):
        draw.polygon(self.gameEngine.screen, color, [self.gameEngine.camera.transformPoint(point) for point in self.getPolyBB()])
        
    def renderSprite(self):
        ...
        
class Filth(Character):
    def __init__(self, gameEngine, startPos: Vector2):
        super().__init__(gameEngine, startPos, [Vector2(-20, -30), Vector2(20, 0)], 0.5)

