from pygame import Vector2
from src.enemies import Character

def applyHitscanDamage(gameEngine, position, direction, damage, pierce=1):
    collitions = gameEngine.world.isRayColliding(position, direction, pierce)
    if not collitions:
        return position + (direction * 100000)
    for collition in collitions:
        if not collition[1] is None:
            distance = collition[0].distance_to(gameEngine.player.position)
            if distance <= gameEngine.bloodRadius:
                gameEngine.player.heal(min(damage * 1000 / distance, 50))
            gameEngine.hurtEnemy(collition[1], damage)
    endPoint = collitions[-1][0]
    return endPoint

class Projectile(Character):
    def __init__(self, gameEngine, position, direction):
        #super().__init__(gameEngine, position, [], 1, 0, 0)
        self.position: Vector2 = position
        self.direction: Vector2 = direction
        self.speed = 100

    def move(self, dt):
        self.position += self.direction * self.speed

class Weapon:
    def __init__(self, gamgeEngine, damage, pierce):
        self.gameEngine = gamgeEngine
        self.baseDamage = damage
        self.pierce = pierce

class Pistol(Weapon):
    def __init__(self, gameEngine):
        super().__init__(gameEngine, 1, 1)
        
    def shootPrimary(self, position, direction):
        endPoint = applyHitscanDamage(self.gameEngine, position, direction, self.baseDamage)
        self.gameEngine.world.renderLine(self.gameEngine.camera, self.gameEngine.screenFrame, (250, 231, 22), position, endPoint)

class Shotgun(Weapon):
    def __init__(self, gameEngine):
        super().__init__(gameEngine, 0.25, 1)
        self.shots = 1

    def shootPrimary(self, position, direction:Vector2):
        for i in range(self.shots):
            self.gameEngine.projectiles.append(Projectile(self.gameEngine, position.copy(), direction.normalize().rotate_rad((i-(self.shots - 1)) * 1)))
