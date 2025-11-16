from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.engine import GameEngine
from pygame import Vector2
    
def test_ray():
    engine = GameEngine(startLevel="testLevel.json")
    assert engine.world.isRayColliding(Vector2(0, 0), Vector2(1, 0)) == [1490, 0]
    engine.shutdown()
    
if __name__ == "__main__":
    test_ray()