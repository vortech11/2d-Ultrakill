

from pygame import Vector2

import pygame




class UiHandler:
    def __init__(self, screenSize: Vector2):
        self.displayFont = pygame.font.SysFont("Arial", 20)
        self.screenSize = screenSize

    def getBarRect(self, value, total, position: Vector2, endPosition: Vector2):
        return pygame.Rect(position.x, position.y, (endPosition.x) * value / total, endPosition.y)

    def renderBar(self, screen, color, value, total, position: Vector2, relativeEnd: Vector2):
        pygame.draw.rect(screen, color, self.getBarRect(value, total, position, relativeEnd))
        
    def renderUi(self, player, screen):
        
        #staminaText = self.displayFont.render(f"{player.stamina}", False, (58, 224, 219))

        #screen.blit(staminaText, (100, 100))

        playerWigitStart: Vector2 = Vector2(50, self.screenSize.y - 150)
        playerWigitEnd: Vector2 = Vector2(200, 100)

        pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(playerWigitStart.x, playerWigitStart.y, playerWigitEnd.x, playerWigitEnd.y))

        staminaBarPadding = Vector2(25, 25)
        staminaBarXPadding = 25

        self.renderBar(screen, (58, 224, 219), player.stamina, 100, 
            Vector2(playerWigitStart.x + staminaBarPadding.x, playerWigitStart.y + playerWigitEnd.y - staminaBarPadding.y), 
            Vector2(playerWigitEnd.x - staminaBarPadding.x * 2, 20)
        )

        

