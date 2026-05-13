
import json
import pygame

AUTOTILE_MAP = { 
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 4,
    tuple(sorted([(-1, 0), (1, 0), (0, -1), (0, 1)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(-1, 0), (0, -1)])): 7,
    tuple(sorted([(-1, 0), (1, 0), (0, -1)])): 8,
}

NEIGHBOR_OFFSET = [(-1, 0), (-1, -1 ), (0,-1), (1, -1), (1, 0), (0, 0), ( -1, 1), (0,1), (1, 1)]
PHYSICS_TILES = {'grass', 'castle'}
AUTOTILE_TYPES = {'grass', 'castle'}

# walls variant that becomes solid when player HP <= 25%
BARRIER_TILE_TYPE    = 'walls'
BARRIER_TILE_VARIANT = 21

class Tilemap:
    def __init__(self, game, tile_size= 32):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []


    def tiles_around (self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size)), (int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSET:
            check_loc = str(tile_loc[0] + offset [0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    

    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid':self.offgrid_tiles}, f)
        f.close()

    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']


    def physics_rects_around(self, pos): 
        rects = []
        player = self.game.player
        barrier_active = (self.game.current_level == 1 and
                          (player.hp / player.max_hp) <= 0.25)

        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
            elif (barrier_active
                  and tile['type'] == BARRIER_TILE_TYPE
                  and tile['variant'] == BARRIER_TILE_VARIANT):
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects


    def autotile(self):
        for loc in self.tilemap:
            tile=self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1,0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]


    def render(self, surf, offset=(0, 0), hide_spawners=True):
        # pass 1 — walls (furthest back)
        for x in range(offset[0] // self.tile_size - 1, (offset[0] + surf.get_width()) // self.tile_size + 2):
            for y in range(offset[1] // self.tile_size - 1, (offset[1] + surf.get_height()) // self.tile_size + 2):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    if tile['type'] == 'walls':
                        surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

        # pass 2 — offgrid tiles (decor, large_decor, spawners etc.) in front of walls
        for tile in self.offgrid_tiles:
            if hide_spawners and tile['type'] in ('spawners', 'portal', 'campfire', 'boss_spawner'):
                continue
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        # pass 3 — all other on-grid tiles (grass, castle, decor) in front of everything
        for x in range(offset[0] // self.tile_size - 1, (offset[0] + surf.get_width()) // self.tile_size + 2):
            for y in range(offset[1] // self.tile_size - 1, (offset[1] + surf.get_height()) // self.tile_size + 2):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    if tile['type'] != 'walls':
                        surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))


