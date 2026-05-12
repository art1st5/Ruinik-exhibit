import pygame

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down':False, 'right': False, 'left': False}

        self.action = ''
        self.anim_offset = (-17, -4)
        self.set_action('idle')
        self.facing_left = False

    def rect (self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size [0], self.size[1])
    
    def set_action(self, action):
 
        if action == 'death':
            key = 'player/death'
        elif self.mode == "staff":
            key = "staff/" + action
        elif self.mode == "sword":
            if action in ("jump", "jump_left"):
                action = "idle_left" if self.facing_left else "idle"
            key = "sword/" + action
        else:
            key = "player/" + action

        if action != self.action:
            self.action = action
            self.animation = self.game.assets[key].copy()

    def update(self, tilemap, movement=(0, 0)):

        self.collisions = {'up': False, 'down':False, 'right': False, 'left': False}

        if hasattr(self, "dashing") and self.dashing > 0:
            frame_movement = (self.velocity[0], self.velocity[1])
        else:
            frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] =  True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True                    
                self.pos[0] = entity_rect.x
            

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True    
                self.pos[1] = entity_rect.y


        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        if self.collisions['down'] or self.collisions['up']:
            self.velocity [1] = 0

        GROUND_LEVEL = self.game.ground_y * self.game.tilemap.tile_size

        if self.pos[1] + self.size[1] >= GROUND_LEVEL:
            self.pos[1] = GROUND_LEVEL - self.size[1]
            self.velocity[1] = 0
            self.collisions['down'] = True


        if not (hasattr(self, "dashing") and self.dashing > 0):    
            self.animation.update()
 
    
    def render(self, surf, offset=(0, 0)):
            img = self.animation.img()
            surf.blit(img,(int(self.pos[0] - offset[0] + self.anim_offset[0]),int(self.pos[1] - offset[1] + self.anim_offset[1])))

class Player(PhysicsEntity):
    DASH_COOLDOWN       = 150  
    DASH_COOLDOWN_P2    = 60  
    DASH_DISTANCE       = 20    
    DASH_DISTANCE_P2    = 35   
    def __init__(self, game, pos, size):
        self.mode = "normal"
        super().__init__(game, 'player', pos, size)
        self.jumps = 1
        self.air_time = 0
        self.dashing = 0
        self.dash_cooldown = 0
        self.dash_ghosts = []  
        self.dash_hit = set()
        self.p2_boss_nearby = False  
        self.DASH_GHOST_ALPHA = 255
        self.attacking = False
        self.hp = 200
        self.max_hp = 200
        self.hurt_cooldown = 0
        self.mode_cooldown = 0
        self.dead = False
        self.jump_hint_timer = 0  
        self.attack_cooldown = 0

    def dash(self):
        if self.dead:
            return
        if self.mode != "staff":
            return 

        if self.dashing == 0 and self.dash_cooldown == 0:
            self.dashing = 10
            self.dash_cooldown = self.DASH_COOLDOWN_P2 if self.p2_boss_nearby else self.DASH_COOLDOWN
            self.dash_hit.clear()

            dash_distance = self.DASH_DISTANCE_P2 if self.p2_boss_nearby else self.DASH_DISTANCE

            if self.facing_left:
                self.velocity[0] -= dash_distance
            else:
                self.velocity[0] += dash_distance
    
    def update(self, tilemap, movement = (0, 0)):
        
       
        if self.dead:
            self.animation.update()
            return

        if self.attacking:
            movement = (0, movement[1])

        super().update(tilemap, movement=movement)

        if self.dashing > 0:
            self.dashing -= 1
            if self.dashing % 2 == 0:
                ghost_img = self.animation.img().copy()
                if self.p2_boss_nearby and self.mode == "staff":
                    # tint visible pixels cyan, keep transparency clean
                    tinted = pygame.Surface(ghost_img.get_size(), pygame.SRCALPHA)
                    tinted.blit(ghost_img, (0, 0))
                    tinted.fill((143, 211, 255), special_flags=pygame.BLEND_RGB_MULT)
                    ghost_img = tinted
                ghost_img.set_alpha(self.DASH_GHOST_ALPHA)
                if self.mode == "sword" and self.action in ("idle", "idle_left"):
                    aoff = (-17, -9)
                elif self.mode == "sword" and self.action in ("attack", "attack_left"):
                    aoff = (-26, -22)
                else:
                    aoff = self.anim_offset
                ghost_pos = [self.pos[0] + aoff[0], self.pos[1] + aoff[1]]
                self.dash_ghosts.append([ghost_img, ghost_pos, self.DASH_GHOST_ALPHA])
            if self.dashing == 0:
                self.velocity[0] = 0
        else:
            self.velocity[0] *= 0.9

        for ghost in self.dash_ghosts[:]:
            ghost[2] -= 25
            if ghost[2] <= 0:
                self.dash_ghosts.remove(ghost)
            else:
                ghost[0].set_alpha(ghost[2])

        
        if movement[0] > 0:
            self.facing_left = False

        if movement[0] < 0:
            self.facing_left = True

        self.air_time += 1

        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1

        if self.hurt_cooldown > 0:
            self.hurt_cooldown -= 1

        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

        if self.mode_cooldown > 0:
            self.mode_cooldown -= 1

        if self.jump_hint_timer > 0:
            self.jump_hint_timer -= 1

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.dashing > 0:

            if self.facing_left:
                self.set_action('dash_left')
            else:
                self.set_action('dash')

        elif self.attacking:
            if self.animation.done:
                self.attacking = False
                self.attack_cooldown = 40  
            else:
        
                if self.facing_left:
                    self.set_action('attack_left')
                else:
                    self.set_action('attack')

        elif self.air_time > 4:

            if self.facing_left:
                self.set_action('jump_left')
            else:
                self.set_action('jump')

        elif movement[0] != 0:

            if self.facing_left:
                self.set_action('run_left')
            else:
                self.set_action('run')

        else:

            if self.facing_left:
                self.set_action('idle_left')
            else:
                self.set_action('idle')


    def take_damage(self, amount):
        if self.hurt_cooldown == 0 and not self.dead:
            self.hp = max(0, self.hp - amount)
            self.hurt_cooldown = 60
            if self.hp == 0:
                self.dead = True
                self.attacking = False
                self.action = ''
                self.set_action('death')

    def sword_attack(self):
        if self.dead or self.mode != "sword" or self.attacking or self.attack_cooldown > 0:
            return
        self.attacking = True
        self.action = ""
        if self.facing_left:
            self.set_action("attack_left")
        else:
            self.set_action("attack")

    def render(self, surf, offset=(0, 0)):
        for ghost_img, ghost_pos, _ in self.dash_ghosts:
            surf.blit(ghost_img, (int(ghost_pos[0] - offset[0]), int(ghost_pos[1] - offset[1])))

        if self.mode == "sword" and self.action in ("idle", "idle_left"):
            anim_offset = (-17, -9)
        elif self.mode == "sword" and self.action == "attack":
            anim_offset = (-40, -22)
        elif self.mode == "sword" and self.action == "attack_left":
            anim_offset = (-40, -22)
        else:
            anim_offset = self.anim_offset
        img = self.animation.img()
        surf.blit(img, (int(self.pos[0] - offset[0] + anim_offset[0]), int(self.pos[1] - offset[1] + anim_offset[1])))

    def toggle_mode(self):
            if self.mode_cooldown > 0:
                return
            self.mode = "staff" if self.mode == "normal" else "normal"
            self.action = ""
            self.set_action("idle")
            self.mode_cooldown = 90  

    def toggle_sword_mode(self):
            if self.mode_cooldown > 0:
                return
            self.mode = "sword" if self.mode != "sword" else "normal"
            self.action = ""
            self.set_action("idle")
            self.mode_cooldown = 90  

    def jump(self):
        if self.dead or self.mode == "sword":
            if self.mode == "sword":
                self.jump_hint_timer = 120  
            return
        if self.jumps:
            self.velocity[1] = -4 if self.mode == "staff" else -2
            self.jumps -= 1
            self.air_time = 5


class Slime(PhysicsEntity):
    DETECT_RANGE = 60   # starts chasing player
    ATTACK_RANGE = 28   # starts attacking (should roughly match hitbox width)
    WALK_SPEED   = 0.9

    def __init__(self, game, pos):
        self.mode = "slime"
        self.action = ''
        self.facing_left = False
        self.game = game
        self.type = 'slime'
        self.pos = list(pos)
        self.size = (25, 23)
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        self.anim_offset = (-2, -9)  # aligns sprite canvas to hitbox
        self.hp = 100
        self.max_hp = 300
        self.hurt_cooldown = 0
        self.dead = False
        self.can_deal_damage = False  
        self.set_action('idle')

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def attack_rect(self):
        """Hitbox extended 5px on the facing side when attacking."""
        ext = 5
        if self.facing_left:
            return pygame.Rect(self.pos[0] - ext, self.pos[1], self.size[0] + ext, self.size[1])
        else:
            return pygame.Rect(self.pos[0], self.pos[1], self.size[0] + ext, self.size[1])

    def set_action(self, action):
        key = 'slime/' + action
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[key].copy()

    def take_damage(self, amount):
        if self.hurt_cooldown == 0 and not self.dead:
            self.hp = max(0, self.hp - amount)
            self.hurt_cooldown = 10
            if self.hp == 0:
                self.dead = True
                self.action = ''
                self.set_action('death')

    def update(self, tilemap, movement=(0, 0)):
     
        if self.dead:
            self.animation.update()
            return

        dx = self.game.player.pos[0] - self.pos[0]
        dist = abs(dx)
        in_range = dist < self.DETECT_RANGE
        in_attack_range = dist < self.ATTACK_RANGE

        if in_range:
            new_facing = dx < 0
            if new_facing != self.facing_left:
                self.facing_left = new_facing
                self.can_deal_damage = False
                self.action = ''

            if in_attack_range:
                # close enough — stand and attack
                super().update(tilemap, movement=(0, 0))
                if self.facing_left:
                    self.set_action('attack_left')
                else:
                    self.set_action('attack')

                anim = self.animation
                last_frame = anim.img_duration * len(anim.images) - 1
                if anim.frame >= last_frame:
                    self.can_deal_damage = True
                if self.can_deal_damage and self.attack_rect().colliderect(self.game.player.rect()):
                    self.game.player.take_damage(30)
                    self.can_deal_damage = False
            else:
                # detected but not close enough — walk toward player
                self.can_deal_damage = False
                walk_dir = -self.WALK_SPEED if self.facing_left else self.WALK_SPEED
                super().update(tilemap, movement=(walk_dir, 0))
                if self.facing_left:
                    self.set_action('idle_left')
                else:
                    self.set_action('idle')
        else:
            self.can_deal_damage = False
            walk_dir = -self.WALK_SPEED if self.facing_left else self.WALK_SPEED
            super().update(tilemap, movement=(walk_dir, 0))
            if self.collisions['right']:
                self.facing_left = True
            if self.collisions['left']:
                self.facing_left = False
            if self.facing_left:
                self.set_action('idle_left')
            else:
                self.set_action('idle')

        if self.hurt_cooldown > 0:
            self.hurt_cooldown -= 1

    def render(self, surf, offset=(0, 0)):
        img = self.animation.img().copy()
        if self.hurt_cooldown > 0:
            white_overlay = pygame.Surface(img.get_size())
            white_overlay.fill((255, 255, 255))
            img.blit(white_overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        surf.blit(img, (int(self.pos[0] - offset[0] + self.anim_offset[0]),
                        int(self.pos[1] - offset[1] + self.anim_offset[1])))
