import pygame
from pygame import Vector2

from src.engine import GameEngine

engine = GameEngine()

engine.runMainLoop()

engine.shutdown()