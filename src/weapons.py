


def applyHitscanDamage(gameEngine, position, direction, damage, pierce=1):
    collitions = gameEngine.world.isRayColliding(position, direction, pierce)
    if not collitions:
        return position + (direction * 100000)
    for collition in collitions:
        if not collition[1] is None:
            gameEngine.hurtEnemy(collition[1], damage)
    endPoint = collitions[-1][0]
    return endPoint

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
        self.gameEngine.world.renderLine(self.gameEngine.camera, self.gameEngine.screen, (255, 255, 255), position, endPoint)
    