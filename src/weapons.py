


def applyHitscanDamage(world, position, direction, damage, pierce=1):
    collitions = world.isRayColliding(position, direction, pierce)
    for collition in collitions:
        if not collition[1] is None:
            collition[1].health -= damage
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
        endPoint = applyHitscanDamage(self.gameEngine.world, position, direction, self.baseDamage)
        self.gameEngine.world.renderLine(self.gameEngine.camera, self.gameEngine.screen, (255, 255, 255), position, endPoint)
    