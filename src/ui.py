

from pygame import Vector2

import pygame




class UiHandler:
    def __init__(self, gameEngine):
        self.gameEngine = gameEngine
        self.screen = self.gameEngine.screen
        self.displayFont = pygame.font.SysFont("Arial", 20)
        self.titleCard = pygame.font.SysFont("Arial", 50)
        self.caption = pygame.font.SysFont("Arial", 20)

    def getBarRect(self, value, total, position: Vector2, endPosition: Vector2):
        return pygame.Rect(position.x, position.y, (endPosition.x) * value / total, endPosition.y)

    def renderBar(self, screen, color, value, total, position: Vector2, relativeEnd: Vector2):
        pygame.draw.rect(screen, color, self.getBarRect(value, total, position, relativeEnd))
        
    def renderPlayerUi(self, player, screen, screenSize):

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
        
    def renderWinScreen(self, screen, screenSize):
        titleCard = self.titleCard.render("You Win", True, (255, 255, 255))
        titlerect = titleCard.get_rect()
        titlerect.center = (screenSize.x // 2, screenSize.y // 2)
        caption = self.caption.render("Press space to load next level", True, (255, 255, 255))
        captionrect = caption.get_rect()
        captionrect.center = (screenSize.x // 2, screenSize.y // 2 + 40)
        screen.blit(titleCard, titlerect)
        screen.blit(caption, captionrect)
        
    def handleMainMenu(self, screen, screenSize, mousePos, mouseDown):
        titleCard = self.titleCard.render("2D Ultrakill", True, (255, 255, 255))
        titlerect = titleCard.get_rect()
        titlerect.center = (screenSize.x // 2, screenSize.y // 2)
        caption = self.caption.render("Click screen to load into first level", True, (255, 255, 255))
        captionrect = caption.get_rect()
        captionrect.center = (screenSize.x // 2, screenSize.y // 2 + 40)
        screen.blit(titleCard, titlerect)
        screen.blit(caption, captionrect)
        if mouseDown[1]:
            self.gameEngine.startLevel("level.json")
        
    def renderUi(self, player, screen, screenSize:Vector2):
        self.renderPlayerUi(player, screen, screenSize)
        
        if self.gameEngine.levelWin:
            self.renderWinScreen(screen, screenSize)

        

