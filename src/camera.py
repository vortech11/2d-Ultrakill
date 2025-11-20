from pygame import Vector2
from pygame import font

class Camera:
    def __init__(self, screenSize):
        self.position: Vector2 = Vector2(0, 0)
        self.rotation: float = 0
        self.zoom: float = 0.5
        self.screenSize = screenSize
        self.DEBUG_FONT = font.SysFont("Arial", 12)
        

    def transformPoint(self, point:Vector2):
        transformed: Vector2 = point - self.position
        transformed.rotate_rad_ip(self.rotation)
        transformed *= self.zoom
        transformed = transformed + Vector2(self.screenSize / 2)
        return transformed
    
    def unTransformPoint(self, point:Vector2):
        transformed: Vector2 = point - Vector2(self.screenSize / 2)
        transformed /= self.zoom
        transformed.rotate_rad_ip(-self.rotation)
        transformed += self.position
        return transformed

    def transformPolyToSurfaceSpace(self, points: list[Vector2], minX, minY):
        return [Vector2(point.x - minX, point.y - minY) for point in points]
    
    def getRectPoints(self, center: Vector2, apothem: float) -> list[Vector2]:
        return [
                center - Vector2(apothem, apothem), 
                Vector2(center.x + apothem, center.y - apothem), 
                center + Vector2(apothem, apothem), 
                Vector2(center.x - apothem, center.y + apothem)
            ]
        
    def renderFPS(self, clock, screen):
        fps = round(clock.get_fps(), 1)
        text = self.DEBUG_FONT.render(f"{fps}", False, (0, 255, 0))
        screen.blit(text, (10, 10))