import pygame
import sys


from scripts.utils import load_images
from scripts.tilemap import Tilemap

RENDER_SCALE = 1.0


class Editor:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("editor")
        self.screen = pygame.display.set_mode((1280, 720))
        self.running = True
        self.display = pygame.Surface((1280, 720))


        self.clock = pygame.time.Clock()

        self.movement = [False, False]


        self.assets = { 
            'grass': load_images('tiles/grass'),
            'castle': load_images('tiles/castle', scale=(32, 32)),
            'walls': load_images('tiles/walls', scale = (32,32)),
            'clouds': load_images('clouds'),
            'decor': load_images('tiles/decor'),
            'large_decor':load_images('tiles/large_decor'),
            'spawners': load_images('spawners'),
            'portal': load_images('portal'),
            'campfire': load_images('campfire'),
            'boss_spawner': load_images('boss_spawner'),
        }

        self.movement = [False, False, False, False]


   
        self.tilemap = Tilemap(self, tile_size=32)

        self.scroll = [0, 0]
        
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError: 
            pass

        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0 

        self.clicking = False
        self.right_clicking = False
        self.shift = False
        self.ongrid = True

        self.ground_y = 11
        self.zoom = 1
    def run(self):  
        while True:
            self.display.fill((69,69,69))
            

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 8
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 8

            
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            self.tilemap.render(self.display, offset = render_scroll, hide_spawners=False)
            tile_size = self.tilemap.tile_size
            ground_img = self.assets['grass'][0]

            for x in range(-100, 200):
                self.display.blit(ground_img,(x * tile_size - self.scroll[0],self.ground_y * tile_size - self.scroll[1]))

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(1000)

            if self.tile_list[self.tile_group] in ('spawners', 'portal', 'campfire', 'boss_spawner'):
                self.ongrid = False

            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            if self.ongrid:
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)


            if self.clicking and self.ongrid:
                if tile_pos[1] != self.ground_y:
                    self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    if tile_pos[1] != self.ground_y:
                        del self.tilemap.tilemap[tile_loc]

                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(
                        tile['pos'][0] - self.scroll[0],
                        tile['pos'][1] - self.scroll[1],
                        tile_img.get_width(),
                        tile_img.get_height()
                    )
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)
            self.display.blit(current_tile_img, (5, 5))


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                        if not self.ongrid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos':(mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])

                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])      
                        
                    else:    
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0

                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)        
                            self.tile_variant = 0

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid   
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True    
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_o:
                        self.tilemap.save('map.json')

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False 
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False    
                        


            scaled_width = int(self.display.get_width() * self.zoom)
            scaled_height = int(self.display.get_height() * self.zoom)

            scaled_display = pygame.transform.scale(self.display, (scaled_width, scaled_height))

            self.screen.blit(scaled_display, (0, 0))          
            pygame.display.update()
            self.clock.tick(60)

Editor().run()