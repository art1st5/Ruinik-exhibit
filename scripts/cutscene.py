import pygame
import sys


CUTSCENE_LINES = [
    ("IN A WORLD INVOLVED IN MAGIC FOR THE SOLE PURPOSE TO HELP THE PEOPLE...", 230),
    ("IT'S BEEN 2521 YEARS SINCE THE TRUE-MAGIC WAR HAS ENDED", 210),
    ("WAR AND VIOLENCE HAS VANISHED IN THE FACE OF THE, WORLD ONLY PEACE..", 220),
    ("NOT UNTIL JAG SAW SOMETHING THAT CHANGED HIS BELIEF...", 180),
    ("AND HIS FATE...", 70),
]

FONT_NAME   = 'Arial'
FONT_SIZE   = 32
FONT_BOLD   = True
TEXT_COLOR  = (220, 210, 180)   # warm parchment white
BG_COLOR    = (0, 0, 0)        
FADE_FRAMES = 30               
ALLOW_SKIP  = False          


class Cutscene:
    def __init__(self, screen):
        self.screen = screen
        self.font   = pygame.font.SysFont(FONT_NAME, FONT_SIZE, bold=FONT_BOLD)
        self.clock  = pygame.time.Clock()

    def _render_line(self, text, alpha):
        sw, sh = self.screen.get_size()
        self.screen.fill(BG_COLOR)

        surf = self.font.render(text, True, TEXT_COLOR)
        surf.set_alpha(alpha)
        rect = surf.get_rect(center=(sw // 2, sh // 2))
        self.screen.blit(surf, rect)
        pygame.display.update()

    def run(self):
        for text, hold_frames in CUTSCENE_LINES:
            skip_line = False

            # fade in
            for f in range(FADE_FRAMES):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        skip_line = True
                if skip_line:
                    break
                self._render_line(text, int(255 * (f / FADE_FRAMES)))
                self.clock.tick(60)

        
            if not skip_line:
                for f in range(hold_frames):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit(); sys.exit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            skip_line = True
                    if skip_line:
                        break
                    self._render_line(text, 255)
                    self.clock.tick(60)

            
            if not skip_line:
                for f in range(FADE_FRAMES):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit(); sys.exit()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            skip_line = True
                    if skip_line:
                        break
                    self._render_line(text, int(255 * (1 - f / FADE_FRAMES)))
                    self.clock.tick(60)

        # brief black pause at the end
        self.screen.fill(BG_COLOR)
        pygame.display.update()
        pygame.time.wait(300)
