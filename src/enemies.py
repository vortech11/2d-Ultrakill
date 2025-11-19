from pygame import Vector2
from pygame import draw
from pygame import transform

class Character:
    def __init__(self, gameEngine, startPos:Vector2, hitbox: list[Vector2], totalHealth, gravity=3000):
        self.gameEngine = gameEngine
        self.hitbox: list[Vector2] = hitbox
        self.position: Vector2 = startPos
        self.velosity: Vector2 = Vector2(0, 0)
        self.facing = 1
        self.moveSubDiv: list[int] = [7, 4]
        
        self.totalhealth = totalHealth
        self.health = self.totalhealth
        
        self.gravity = gravity
        
        self.imageDir = "cat"
        
    def getPolyBB(self):
        return [self.position + point for point in self.hitbox]
    
    def getRectBB(self):
        return [
            self.position + self.hitbox[0],
            self.position + self.hitbox[2]
        ]
    
    def renderHitbox(self, color):
        draw.polygon(self.gameEngine.screenFrame, color, [self.gameEngine.camera.transformPoint(point) for point in self.getPolyBB()])
        
    def renderSprite(self):
        imageData = self.gameEngine.images[self.imageDir]["Goofball.png"]
        self.gameEngine.screenFrame.blit(transform.flip(transform.scale_by(imageData["image"], imageData["scale"] * self.gameEngine.camera.zoom), bool(self.facing), 0), self.gameEngine.camera.transformPoint(self.position + imageData["center"]))
        
    def isAABBColliding(self, world):
        rectColliding = world.isRectColliding(self.getRectBB())
        polyColliding = world.isPolyColliding(self.getPolyBB())
        return [rectColliding, polyColliding]
        
class Filth(Character):
    def __init__(self, gameEngine, startPos: Vector2):
        super().__init__(gameEngine, startPos, [Vector2(-20, 0), Vector2(20, 0), Vector2(20, 80), Vector2(-20, 80)], 0.5)
        
        self.moveSpeed = 200
        
    def move(self, dt):
        moveDirection: Vector2 = self.gameEngine.player.position - self.position
        moveDirection.scale_to_length(self.moveSpeed * dt)
        self.position.x += moveDirection.x
        if any(self.isAABBColliding(self.gameEngine.world)):
            for _ in range(self.moveSubDiv[0]):
                self.position.x -= moveDirection.x / self.moveSubDiv[0]
                if not any(self.isAABBColliding(self.gameEngine.world)):
                    break
        self.position.y += moveDirection.y
        if any(self.isAABBColliding(self.gameEngine.world)):
            for _ in range(self.moveSubDiv[1]):
                self.position.y -= moveDirection.y / self.moveSubDiv[1]
                if not any(self.isAABBColliding(self.gameEngine.world)):
                    break
            

