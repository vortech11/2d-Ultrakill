from pygame import Vector2
from pygame import draw
from pygame import transform

from math import copysign

class Character:
    def __init__(self, gameEngine, startPos:Vector2, hitbox: list[Vector2], totalHealth, gravity=3000, collisionDamage=0):
        self.gameEngine = gameEngine
        self.hitbox: list[Vector2] = hitbox
        self.position: Vector2 = startPos
        self.velosity: Vector2 = Vector2(0, 0)
        self.facing = 1
        self.moveSubDiv: list[int] = [7, 4]
        self.stepup = 1
        self.grounded = 10

        self.collisionDamage = collisionDamage

        self.velosityUpdaters: list[callable[[int], None]] = [] # type: ignore
        self.collisionResolvers: list[callable[[int], None]] = [] # type: ignore

        self.collisionResolvers.append(self.updatePositionResolveCollition)
        self.targetPos: Vector2 = Vector2(0, 0)
        
        self.totalhealth = totalHealth
        self.health = self.totalhealth
        
        self.gravity = gravity
        
        self.imageDir = "cat"

    def getIndex(self):
        for index, enemy in enumerate(self.gameEngine.enemies):
            if enemy is self:
                return index

        """
            Uh oh! Thats not supposed to happen!!!!
        """

        return "fuck"
        
    def getPolyBB(self):
        return [self.position + point for point in self.hitbox]
    
    def getRectBB(self):
        return [
            self.position + self.hitbox[0],
            self.position + self.hitbox[2]
        ]
    
    def renderHitbox(self, color):
        self.gameEngine.drawPoly(self.gameEngine.screenFrame, color, [self.gameEngine.camera.transformPoint(point) for point in self.getPolyBB()])
        
    def renderSprite(self):
        imageData = self.gameEngine.images[self.imageDir]["Goofball.png"]
        self.gameEngine.screenFrame.blit(transform.flip(transform.scale_by(imageData["image"], imageData["scale"] * self.gameEngine.camera.zoom), not bool(self.facing), 0), self.gameEngine.camera.transformPoint(self.position + imageData["center"]))
        
    def isAABBColliding(self, world):
        rectColliding = world.isRectColliding(self.getRectBB())
        polyColliding = world.isPolyColliding(self.getPolyBB())
        entityColliding = world.isRectCollidingWithEntity(self.getRectBB())
        return [rectColliding, polyColliding, entityColliding]
        
    def clamp(self, minimum, x, maximum):
        return max(minimum, min(x, maximum))

    def updateGrounded(self, world):
        self.position.y += 20
        if any(self.isAABBColliding(world)):
            self.grounded = min(self.grounded + 1, 10)
        else:
            self.grounded = max(self.grounded - 1, 0)
        self.position.y -= 20

    def updatePositionResolveCollition(self, dt, world):
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
                    break
        elif collision[0] or collision[2]:
            for x in range(self.moveSubDiv[0]):
                self.position.x -= self.velosity.x / self.moveSubDiv[0] * dt
                if not any(self.isAABBColliding(world)):
                    break
            self.velosity.x = copysign(0.01, self.velosity.x)
        
        self.position.y += self.velosity.y * dt

        if any(self.isAABBColliding(world)):
            for x in range(self.moveSubDiv[1]):
                self.position.y -= self.velosity.y / self.moveSubDiv[1] * dt
                if not any(self.isAABBColliding(world)):
                    break
            self.velosity.y = 0

    def move(self, dt):
        for func in self.velosityUpdaters:
            func(dt)
        for func in self.collisionResolvers:
            func(dt, self.gameEngine.world)

class Flying(Character):
    def __init__(self, gameEngine, startPos: Vector2, hitbox: list[Vector2], totalHealth, collisionDamage):
        super().__init__(gameEngine, startPos, hitbox, totalHealth, 0, collisionDamage)
        self.moveSpeed = 100
        self.velosityUpdaters.append(self.moveBase)

    def moveBase(self, dt):
        moveDirection: Vector2 = self.targetPos - self.position
        if moveDirection.length() == 0:
            return
        moveDirection.scale_to_length(self.moveSpeed * dt)
        self.velosity = moveDirection * self.moveSpeed

class RedOrb(Flying):
    def __init__(self, gameEngine, startPos: Vector2, direction: Vector2):
        super().__init__(gameEngine, startPos, [Vector2(-20, -20), Vector2(20, -20), Vector2(20, 20), Vector2(-20, 20)], 99999, 20)
        self.moveSpeed = 300
        self.movingDirection = direction
        self.velosityUpdaters.insert(0, self.updateTargetPos)
        self.collisionResolvers.pop()
        self.collisionResolvers.append(self.updatePosition)

    def updateTargetPos(self, dt):
        self.targetPos = self.position + self.movingDirection

    def updatePosition(self, dt, world):
        self.position += self.velosity * dt
        collisions = self.isAABBColliding(self.gameEngine.world)
        if any(collisions):
            self.gameEngine.enemiesToBeDeleted.append(self.getIndex())

class Maurice(Flying):
    def __init__(self, gameEngine, startPos: Vector2):
        super().__init__(gameEngine, startPos, [Vector2(-100, -100), Vector2(100, -100), Vector2(100, 100), Vector2(-100, 100)], 10, 0)
        self.velosityUpdaters.insert(0, self.updateTargetPos)
        self.moveSpeed = 10
        self.longShootingWait = 2
        self.shootingWait = 0.25
        self.numberOfProjectilesShot = 3
        self.shotProjectiles = 0
        self.longShootingTimer = self.longShootingWait
        self.shootingTimer = self.shootingWait

    
    def shootProjectile(self, direction: Vector2):
        self.gameEngine.enemies.append(RedOrb(self.gameEngine, self.position.copy(), direction.copy()))

    def updateTargetPos(self, dt):
        directionToPlayer: Vector2 = self.position - self.gameEngine.player.position
        self.targetPos = self.gameEngine.player.position

        if self.shotProjectiles <= self.numberOfProjectilesShot:
            self.shootingTimer -= dt
            if self.shootingTimer <= 0:
                self.shootProjectile(-directionToPlayer)
                self.shootingTimer = self.shootingWait
                self.shotProjectiles += 1
        else:
            self.longShootingTimer -= dt
            if self.longShootingTimer <= 0:
                self.longShootingTimer = self.longShootingWait
                self.shootingTimer = self.shootingWait
                self.shotProjectiles = 0

class Walking(Character):
    def __init__(self, gameEngine, startPos: Vector2, hitbox: list[Vector2], totalHealth, walkspeed, collisionDamage=0):
        super().__init__(gameEngine, startPos, hitbox, totalHealth, collisionDamage=collisionDamage)
        self.maxWalkSpeed = walkspeed
        self.velosityUpdaters.append(self.updateVelocity)

    def updateVelocity(self, dt):
        self.velosity.y += self.gravity
        self.updateGrounded(self.gameEngine.world)
        if not self.grounded:
            return
        distance = self.targetPos.x - self.position.x
        distance *= 4
        distance = self.clamp(-self.maxWalkSpeed, distance, self.maxWalkSpeed)
        self.velosity.x = distance

class Filth(Walking):
    def __init__(self, gameEngine, startPos: Vector2):
        super().__init__(gameEngine, startPos, [Vector2(-20, 0), Vector2(20, 0), Vector2(20, 80), Vector2(-20, 80)], 0.5 * 4, 500, 1)
        self.velosityUpdaters.insert(0, self.updateTargetPos)
        
    def updateTargetPos(self, dt):
        self.targetPos = self.gameEngine.player.position
    
class Stray(Walking):
    def __init__(self, gameEngine, startPos: Vector2):
        super().__init__(gameEngine, startPos, [Vector2(-20, 0), Vector2(20, 0), Vector2(20, 80), Vector2(-20, 80)], 0.5 * 4, 500)
        self.velosityUpdaters.insert(0, self.updateTargetPos)
        self.walkingDistance = 500
        self.shootingWait = 2
        self.shootingTimer = self.shootingWait

    def shootProjectile(self, direction: Vector2):
        self.gameEngine.enemies.append(RedOrb(self.gameEngine, self.position.copy(), direction.copy()))
        
    def updateTargetPos(self, dt):
        directionToPlayer: Vector2 = self.position - self.gameEngine.player.position
        directionToPlayer.normalize_ip()

        self.shootingTimer -= dt
        if self.shootingTimer <= 0:
            self.shootProjectile(-directionToPlayer)
            self.shootingTimer = self.shootingWait

        self.targetPos = self.gameEngine.player.position + directionToPlayer * self.walkingDistance
    
        

