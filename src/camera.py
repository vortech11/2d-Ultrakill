from pygame import Vector2

class Camera:
    def __init__(self, screenSize):
        self.position: Vector2 = Vector2(0, 0)
        self.rotation: float = 0
        self.zoom: float = 0.5
        self.screenSize = screenSize

    def transformPoint(self, point:Vector2):
        transformed: Vector2 = point - self.position
        transformed.rotate_rad_ip(self.rotation)
        transformed *= self.zoom
        transformed = transformed + Vector2(self.screenSize / 2)
        return transformed
    
    def getRectPoints(self, center: Vector2, apothem: float) -> list[Vector2]:
        return [
                center - Vector2(apothem, apothem), 
                Vector2(center.x + apothem, center.y - apothem), 
                center + Vector2(apothem, apothem), 
                Vector2(center.x - apothem, center.y + apothem)
            ]