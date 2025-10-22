


from pygame import Vector2


class Character:
    def __init__(self, startPos:Vector2, hitbox: list[Vector2], totalHealth, gravity=3000):
        self.hitbox: list[Vector2] = hitbox
        self.position: Vector2 = startPos
        self.velosity: Vector2 = Vector2(0, 0)
        
        self.totalhealth = totalHealth
        self.health = self.totalhealth
        
        self.gravity = gravity
