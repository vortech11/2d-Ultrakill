

from pygame import Vector2

import pygame




class UiHandler:
    def __init__(self, gameEngine):
        self.gameEngine = gameEngine
        self.displayFont = pygame.font.SysFont("Arial", 20)

    def getBarRect(self, value, total, position: Vector2, endPosition: Vector2):
        return pygame.Rect(position.x, position.y, (endPosition.x) * value / total, endPosition.y)

    def renderBar(self, screen, color, value, total, position: Vector2, relativeEnd: Vector2):
        pygame.draw.rect(screen, color, self.getBarRect(value, total, position, relativeEnd))
        
    def renderUi(self, player, screen, screenSize:Vector2):
        
        #staminaText = self.displayFont.render(f"{player.stamina}", False, (58, 224, 219))

        #screen.blit(staminaText, (100, 100))

        playerWigitStart: Vector2 = Vector2(50, screenSize.y - 150)
        playerWigitEnd: Vector2 = Vector2(200, 100)

        pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(playerWigitStart.x, playerWigitStart.y, playerWigitEnd.x, playerWigitEnd.y))

        staminaBarPadding = Vector2(15, 15)
        staminaBarHight = 20

        healthbarVerticalPad = 10
        
        pygame.draw.rect(screen, (25, 25, 25),
            pygame.Rect(playerWigitStart.x + staminaBarPadding.x,
                        playerWigitStart.y + playerWigitEnd.y - staminaBarPadding.y - staminaBarHight,
                        playerWigitEnd.x - staminaBarPadding.x * 2,
                        staminaBarHight))

        self.renderBar(screen, (58, 224, 219), player.stamina, 100, 
            Vector2(playerWigitStart.x + staminaBarPadding.x, playerWigitStart.y + playerWigitEnd.y - staminaBarPadding.y - staminaBarHight), 
            Vector2(playerWigitEnd.x - staminaBarPadding.x * 2, staminaBarHight)
        )

        pygame.draw.rect(screen, (50, 50, 50),
            pygame.Rect(playerWigitStart.x + staminaBarPadding.x + (playerWigitEnd.x - staminaBarPadding.x * 2) * 33.33 / 100,
                        playerWigitStart.y + playerWigitEnd.y - staminaBarPadding.y - staminaBarHight,
                        4,
                        staminaBarHight))
        
        pygame.draw.rect(screen, (50, 50, 50),
            pygame.Rect(playerWigitStart.x + staminaBarPadding.x + (playerWigitEnd.x - staminaBarPadding.x * 2) * 66.66 / 100,
                        playerWigitStart.y + playerWigitEnd.y - staminaBarPadding.y - staminaBarHight,
                        4,
                        staminaBarHight))
        
        pygame.draw.rect(screen, (25, 25, 25),
            pygame.Rect(playerWigitStart.x + staminaBarPadding.x,
                        playerWigitStart.y + playerWigitEnd.y - staminaBarPadding.y - staminaBarHight * 2 - healthbarVerticalPad,
                        playerWigitEnd.x - staminaBarPadding.x * 2,
                        staminaBarHight))


        self.renderBar(screen, (255, 0, 0), player.health, 100, 
            Vector2(playerWigitStart.x + staminaBarPadding.x, playerWigitStart.y + playerWigitEnd.y - staminaBarPadding.y - staminaBarHight * 2 - healthbarVerticalPad), 
            Vector2(playerWigitEnd.x - staminaBarPadding.x * 2, staminaBarHight)
        )

        

