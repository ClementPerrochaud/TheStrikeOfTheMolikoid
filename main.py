import pygame
import random
from Vector import Vector
from math import cos, sin, exp, pi




### CLASS ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
### _______________________________________________________________________________________________




class Stockage: pass
# class Sound in the "Sounds" section



class Grid: # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, width):
        self.width = width
        self.dict  = {}
    
    def store(self, element):
        i, j = int(element.position[0]//self.width), int(element.position[1]//self.width)
        if i in self.dict:
            if j in self.dict[i]: self.dict[i][j] += [element]
            else: self.dict[i][j] = [element]
        else:
            self.dict[i] = {j:[element]}
    
    def remove(self, element):
        i, j = int(element.position[0]//self.width), int(element.position[1]//self.width)
        self.dict[i][j].remove(element)
    
    def case(self, reference):
        i, j = int(reference.position[0]//self.width), int(reference.position[1]//self.width)
        return self.dict[i][j]
    
    def neighbour(self, reference):
        i, j = int(reference.position[0]//self.width), int(reference.position[1]//self.width)
        L = []
        for a in range(i-1,i+2):
            for b in range(j-1,j+2):
                if a in self.dict and b in self.dict[a]:
                    L += self.dict[a][b]
        return L




class Camera: # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, center, scale, screen):
        self.center = center
        self.scale  = scale
        self.screen = screen
        self.frame_count = 0
    
    def convert(self, position): return position*self.scale - self.center




class Player: # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    list = []

    def __init__(self, position, speed, angle, HP=3000, energy=1000, p_speed=800):
        self.position = position
        self.speed    = speed
        self.angle    = angle
        self.angle2   = angle/2
        self.momentum = 0
        self.p_speed  = p_speed
        Player.list  += [self]

        self.laser = Laser(self)
        self.HP         = HP
        self.HP_max     = HP
        self.energy     = energy
        self.energy_max = energy
        self.heat       = 0
        self.missile_gauge  = 0
        self.missile_number = 6
        self.lure_gauge     = 0
        self.lure_number    = 6
        
        self.kill_count = 0
        self.alive      = True
        self.dies       = False
        
        self.is_rotating_l   = False
        self.is_rotating_r   = False
        self.motor_on        = False
        self.shield_on       = False
        self.do_fire         = False
        self.do_fire_missile = False
        self.do_lunch_lure   = False
        self.precision_mode  = False
        self.do_boost        = 0
        self.laser_on        = False
        self.no_power        = False

        player_grid.store(self)


    def update(self):
        player_grid.remove(self)
        if self.HP <= 0 and self.alive: self.explode()
        self.shield_on = self.shield_on and (not self.no_power)
        self.laser.on  = self.laser_on and (not self.no_power)
        if not self.no_power:
            if self.do_boost: 
                self.speed    -= Vector(sin(self.angle),cos(self.angle))*12
                self.do_boost -= 1
                self.energy   -= 15
            elif self.motor_on: 
                self.speed    -= Vector(sin(self.angle),cos(self.angle))*4
                self.energy   -= 2
            if self.is_rotating_l:
                self.momentum += 0.5 - 0.4*self.precision_mode
                self.energy   -= 1
            if self.is_rotating_r:
                self.momentum -= 0.5 - 0.4*self.precision_mode
                self.energy   -= 1
            if self.laser_on:
                self.energy   -= 19
            if self.shield_on:
                self.energy   -= 4

            if self.do_fire:
                self.fire()
                self.energy -= 40
            if self.do_fire_missile and self.missile_number > 0:
                self.lunch_missile()
                self.energy         -= 30
                self.missile_number -= 1
            if self.do_lunch_lure and self.lure_number > 0:
                self.lunch_lure(1+(self.lure_number>1))
                self.energy      -= 30
                self.lure_number -= 1+(self.lure_number>1)
        
        self_orb = self.position - orb.position
        if self_orb.magnitude < 250: self.speed += (exp((250-self_orb.magnitude)/25)-1)*self_orb/self_orb.magnitude

        self.position += self.speed*dt
        self.angle    += self.momentum*dt
        self.angle2   += self.momentum*dt/2
            
        if self.heat > 0:     self.heat -= 1
        if not self.no_power: self.momentum *= 0.92
        self.speed    *= 0.995
        self.angle    -= 2*pi*((self.angle +pi)//(2*pi))
        self.angle2   -= 2*pi*((self.angle2+pi)//(2*pi))
        
        if self.energy <= 0:
            self.do_boost = 0
            self.no_power = True
            sound.power_off.play()
        elif player.alive and self.no_power and self.energy > 500:
            self.no_power = False
            sound.power_on.play()
        if player.alive: self.energy = min(self.energy + 5, self.energy_max)
        if self.energy == self.energy_max:
            self.HP            = min(self.HP + 1 + (self.HP_max-self.HP)*3/self.HP_max, self.HP_max)
            self.missile_gauge = min(self.missile_gauge + 0.3, 100)
            self.lure_gauge    = min(self.lure_gauge + 0.3,    100)
        if self.missile_gauge == 100 and self.missile_number < 6:
            self.missile_gauge   = 0
            self.missile_number += 1
        if self.lure_gauge == 100 and self.lure_number < 6:
            self.lure_gauge   = 0
            self.lure_number += 1

        player_surfaces["heat"].set_alpha(self.heat)
        
        self.is_rotating_l   = False
        self.is_rotating_r   = False
        self.motor_on        = False
        self.do_fire         = False
        self.precision_mode  = False
        self.do_fire_missile = False
        self.do_lunch_lure   = False
        self.laser_on        = False

        player_grid.store(self)
    
    def fire(self):
        self.speed += Vector(sin(self.angle),cos(self.angle))*4
        self.heat += int(0.1*(255-self.heat))
        Player_Projectile( self.position+Vector( 6,-9).rotate(-self.angle), self.speed-Vector(sin(self.angle),cos(self.angle))*self.p_speed )
        Player_Projectile( self.position+Vector(-6,-9).rotate(-self.angle), self.speed-Vector(sin(self.angle),cos(self.angle))*self.p_speed )
    
    def lunch_lure(self, n):
        sound.lure.play()
        if n == 1:
            sgn = random.choice([-1,1])
            Lure(self.position, self.speed + sgn*150*Vector(cos(self.angle),-sin(self.angle)), random.uniform(-10,10))
        else:
            Lure(self.position, self.speed - 150*Vector(cos(self.angle),-sin(self.angle)), random.uniform(-10,10))
            Lure(self.position, self.speed + 150*Vector(cos(self.angle),-sin(self.angle)), random.uniform(-10,10))
    
    def lunch_missile(self):
        Player_Missile( self.position, self.speed - 80*Vector(sin(self.angle),cos(self.angle)), self.angle, self.momentum/2)
        self.speed += 10*Vector(sin(self.angle),cos(self.angle))
        sound.missile.play()
    
    def explode(self):
        self.dies = True
        Fixed_Animation(self.position, self.speed, player_surfaces["explosions"],2)

    def draw(self, camera):
        surface = player_surfaces["vessel"].copy()
        if not self.no_power:
            if self.do_boost:      surface.blit(player_surfaces["boosts"][camera.frame_count%4//2], (0,0))
            elif self.motor_on:    surface.blit(player_surfaces["flames"][camera.frame_count%4//2], (0,0))
            if self.is_rotating_l: surface.blit(player_surfaces["rcs_l"],                           (0,0))
            if self.is_rotating_r: surface.blit(player_surfaces["rcs_r"],                           (0,0))
            if self.do_fire:       surface.blit(player_surfaces["canon_fire"],                      (0,0))
        surface.blit(player_surfaces["heat"], (0,0))
        center_blit(camera.screen, scale_rotate(surface, self.angle, camera.scale).convert_alpha(), camera.convert(self.position))
        if self.shield_on: center_blit(camera.screen, scale_rotate(player_surfaces["shield"], self.angle2, camera.scale), camera.convert(self.position))




class Enemy: #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    list = []

    def __init__(self, position, speed, angle, HP=100, p_speed=300):
        self.position    = position
        self.speed       = speed
        self.angle       = angle
        self.momentum    = 0
        self.p_speed     = p_speed
        self.trust_value = 0
        Enemy.list      += [self]

        self.HP       = HP
        self.HP_max   = HP
        self.motor_on = False
        self.target   = None
        
        enemy_grid.store(self)

    def update(self):
        enemy_grid.remove(self)
        if self.HP <= 0: self.explode()
        if self.target != None: self.aim()
        self_orb = self.position - orb.position
        if self_orb.magnitude < 250: self.speed += (exp((250-self_orb.magnitude)/25)-1)*self_orb/self_orb.magnitude

        self.speed    -= self.trust_value*Vector(sin(self.angle),cos(self.angle))
        self.position += self.speed*dt
        self.angle    += self.momentum*dt
            
        self.momentum *= 0.95
        self.speed    *= 0.995
        self.angle    -= 2*pi*((self.angle+pi)//(2*pi))

        self.motor_on = self.trust_value > 0.1

        enemy_grid.store(self)
    
    def aim(self):
        if self.target is orb:
            dest   = self.position - orb.position + 2*self.speed
            Dangle = Vector.angle(Vector(sin(self.angle),cos(self.angle)), dest-self.speed)
            if Dangle != 0: self.momentum -= Dangle
            if dest.magnitude > 300:
                if abs(Dangle) < pi/2:
                    self.trust_value = (pi/2 - abs(Dangle))*2
            else:
                self.trust_value = 0
                if random.random() > 0.95: self.fire()
        if self.target is player:
            dest_0  = self.position - player.position
            d_spe   = player.speed - self.speed
            d, k, a = dest_0.magnitude, d_spe.magnitude/self.p_speed, Vector.angle(dest_0, player.speed)
            dest    = dest_0 + d_spe/self.p_speed * (d*(k*cos(a)+((k**2*(cos(2*a)-7)+8)/2)**(1/2))/(2*(k**2-1))).real # dinguerie !!
            Dangle  = Vector.angle(Vector(sin(self.angle),cos(self.angle)), dest)
            if Dangle != 0: self.momentum -= Dangle
            if dest.magnitude > 200:
                if abs(Dangle) < pi/2:
                    self.trust_value = (pi/2 - abs(Dangle))*1.5
                    if dest.magnitude < 500:
                        if random.random() > 0.99:  self.fire()
                        if random.random() > 0.998: self.lunch_missile()
            else:
                self.trust_value = 0
                if random.random() > 0.96: self.fire()

    def fire(self):
        self.speed += Vector(sin(self.angle),cos(self.angle))*3
        Enemy_Projectile( self.position+Vector( 5,-11).rotate(-self.angle), self.speed-Vector(sin(self.angle),cos(self.angle))*self.p_speed )
        Enemy_Projectile( self.position+Vector(-5,-11).rotate(-self.angle), self.speed-Vector(sin(self.angle),cos(self.angle))*self.p_speed )

    def lunch_missile(self):
        Enemy_Missile( self.position, self.speed - 80*Vector(sin(self.angle),cos(self.angle)), self.angle)
        self.speed += 100*Vector(sin(self.angle),cos(self.angle))
    
    def explode(self):
        player.kill_count += 1
        if self in Enemy.list: Enemy.list.remove(self)
        Fixed_Animation(self.position, self.speed, enemy_surfaces["explosions"],2)
        for surface in enemy_surfaces["debrits"]: 
            eje = 100
            Debrit(self.position, self.speed+Vector(random.uniform(-eje,eje),random.uniform(-eje,eje)), random.uniform(-10,10), surface)
        for enemy in Enemy.list:
            v = enemy.position - self.position
            if v.magnitude < 80:
                enemy.HP       -= 80-v.magnitude
                enemy.momentum += random.uniform(-0.2*(80-v.magnitude),0.2*(80-v.magnitude))
                enemy.speed    += (80-v.magnitude)*v/v.magnitude
        
    def draw(self, camera):
        surface = enemy_surfaces["vessel"].copy()
        if self.motor_on: surface.blit(enemy_surfaces["frames"][camera.frame_count%4//2], (0,0))
        surface.blit(enemy_surfaces["lights"][camera.frame_count%10//5], (0,0))
        center_blit(camera.screen, scale_rotate(surface, self.angle, camera.scale).convert_alpha(), camera.convert(self.position))
        if self.HP < self.HP_max:
            hb_surf = health_bar_surface.copy()
            pygame.draw.rect(hb_surf, "red", pygame.Rect(7,6,23*self.HP/self.HP_max,2))
            center_blit(camera.screen, hb_surf, camera.convert(self.position)-Vector(0,30))




class Orb: #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    list = []

    def __init__(self, position, HP=20000):
        self.position = position
        self.speed    = Vector(0,0)
        self.HP       = HP
        self.HP_max   = HP
        self.died     = False
        self.dies     = False
        Orb.list     += [self]
            
    def draw(self, camera):
        center_blit(camera.screen, scale_rotate(orb_surfaces["dying"], 0, camera.scale).convert_alpha(), camera.convert(self.position))
        center_blit(camera.screen, scale_rotate(orb_surfaces["orb"],   0, camera.scale).convert_alpha(), camera.convert(self.position))
    
    def update(self):
        if not orb.died:
            if self.HP <= 0: self.dies = True
            self.HP = min(self.HP + 3 + (self.HP_max-self.HP)*17/self.HP_max, self.HP_max)
            orb_surfaces["orb"].set_alpha(255*self.HP/self.HP_max)
        



class Player_Projectile: #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    list = []

    def __init__(self, position, speed):
        self.position = position
        self.speed    = speed
        Player_Projectile.list += [self]
        player_projectile_grid.store(self)

    def update(self):
        player_projectile_grid.remove(self)
        mag = (self.position - Orb.list[0].position).magnitude
        if mag < 200: self.speed += (exp((250-mag)/20)-1)*(self.position + Orb.list[0].position)/mag
        self.position += self.speed*dt
        for vessel in enemy_grid.neighbour(self)+player_missile_grid.neighbour(self)+enemy_missile_grid.neighbour(self):
            if (self.position-vessel.position).magnitude < 9: self.explode(vessel)
        player_projectile_grid.store(self)
    
    def explode(self, vessel):
        vessel.HP -= 40
        vessel.speed += self.speed/50
        vessel.momentum += random.uniform(-1,1)
        if self in Player_Projectile.list: Player_Projectile.list.remove(self)
        Fixed_Animation(self.position, vessel.speed, player_projectile_surfaces["explosions"], 2)

    def draw(self, camera):
        angle = Vector.angle(self.speed, Vector(0,-1))
        center_blit(camera.screen, scale_rotate(player_projectile_surfaces["projectile"], angle, camera.scale).convert_alpha(), camera.convert(self.position))




class Enemy_Projectile: #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    list = []

    def __init__(self, position, speed):
        self.position = position
        self.speed    = speed
        Enemy_Projectile.list += [self]
        enemy_projectile_grid.store(self)

    def update(self):
        enemy_projectile_grid.remove(self)
        if player.shield_on:
            self_player = self.position - player.position
            if self_player.magnitude < 60:
                self.speed += 30000*self_player/self_player.magnitude**3
                player.energy -= self_player.magnitude/60
                sound.shield.set_volume( min(1, sound.shield.get_volume() + self_player.magnitude/2000) )

        self.position += self.speed*dt

        for vessel in [player]+player_missile_grid.neighbour(self):
            if (self.position-vessel.position).magnitude < 9: self.explode(vessel)
        if (self.position-orb.position).magnitude < 125:      self.explode(orb)

        enemy_projectile_grid.store(self)
    
    def explode(self, vessel):
        vessel.HP -= 40
        if vessel in [player]+Player_Missile.list:
            vessel.speed += self.speed/20
            vessel.momentum += random.uniform(-3,3)
        if self in Enemy_Projectile.list: Enemy_Projectile.list.remove(self)
        Fixed_Animation(self.position, vessel.speed, enemy_projectile_surfaces["explosions"], 2)
        if vessel is player: sound.impact.play()

    def draw(self, camera):
        angle = Vector.angle(self.speed, Vector(0,-1))
        center_blit(camera.screen, scale_rotate(enemy_projectile_surfaces["projectile"][camera.frame_count%12//4], angle, camera.scale).convert_alpha(), camera.convert(self.position))




class Player_Missile: #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    list = []

    def __init__(self, position, speed, angle, momentum=0, HP=50):
        self.position  = position
        self.speed     = speed
        self.angle     = angle
        self.momentum  = momentum
        self.rcs_value = 0
        Player_Missile.list += [self]
        player_missile_grid.store(self)

        self.target   = None
        self.HP       = HP
        self.HP_max   = HP
        self.motor_on = True
        
    def update(self):
        player_missile_grid.remove(self)
        self_orb = self.position - orb.position
        if self_orb.magnitude < 250: self.speed += (exp((250-self_orb.magnitude)/25)-1)*self_orb/self_orb.magnitude
        self.aim()
        for vessel in enemy_grid.neighbour(self)+lure_grid.neighbour(self):
            if (self.position-vessel.position).magnitude < 9: self.explode(vessel)

        self.position += self.speed*dt
        self.angle    += self.momentum*dt
        self.speed    *= 0.995
        self.momentum *= 0.90
        self.angle    -= 2*pi*((self.angle+pi)//(2*pi))
        
        player_missile_grid.store(self)
    
    def choose_target(self):
        min_value  = 3000
        for enemy in Enemy.list:
            v = enemy.position - self.position
            angle_value = abs(Vector.angle(v, -Vector(sin(self.angle),cos(self.angle))))/pi
            enemy_value = v.magnitude*( 1 + 4*angle_value**2 )
            if enemy_value < min_value:
                min_value = enemy_value
                self.target = enemy

    def aim(self):
        if self.HP <= 0 and self in Player_Missile.list: self.explode()
        if not self.target in Enemy.list:
            self.rcs_value = 0
            self.motor_on = False
            if camera.frame_count%60 == 0: self.choose_target()
        else:
            self.motor_on = True
            angle  = Vector.angle(Vector(sin(self.angle),cos(self.angle)), self.position-self.target.position)
            angle2 = Vector.angle(Vector(sin(self.angle),cos(self.angle)), self.speed-self.target.speed)
            if angle == 0: self.rcs_value = 0
            else:          self.rcs_value = angle + 0.1*angle/abs(angle)
            self.momentum -= self.rcs_value
            self.speed    -= 2*Vector(sin(self.angle),cos(self.angle)) + Vector(sin(self.angle),cos(self.angle)).rotate(angle2/4)*angle2**2
    
    def explode(self, vessel=None):
        if not vessel == None:
            vessel.HP       -= 150
            vessel.speed    += (self.speed-vessel.speed)/4
            vessel.momentum += random.uniform(-6,6)
            Fixed_Animation(self.position, vessel.speed, player_missile_surfaces["explosion"],2)
        else: Fixed_Animation(self.position, Vector(0,0), player_missile_surfaces["explosion"],2)
        if self in Player_Missile.list: Player_Missile.list.remove(self)

    def draw(self, camera):
        surface = player_missile_surfaces["missile"].copy()
        if self.motor_on:          surface.blit(player_missile_surfaces["flames"][camera.frame_count%4//2], (0,0))
        if self.rcs_value < -0.15: surface.blit(player_missile_surfaces["rcs_l"], (0,0))
        if self.rcs_value >  0.15: surface.blit(player_missile_surfaces["rcs_r"], (0,0))
        center_blit(camera.screen, scale_rotate(surface, self.angle, camera.scale).convert_alpha(), camera.convert(self.position))




class Enemy_Missile: #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    list = []

    def __init__(self, position, speed, angle, HP=30):
        self.position  = position
        self.speed     = speed
        self.angle     = angle
        self.momentum  = 0
        self.rcs_value = 0
        self.birth     = camera.frame_count
        Enemy_Missile.list += [self]
        enemy_missile_grid.store(self)

        self.target   = None
        self.HP       = HP
        self.HP_max   = HP
    
    def update(self):
        enemy_missile_grid.remove(self)
        self_orb = self.position - orb.position
        if self_orb.magnitude < 250: self.speed += (exp((250-self_orb.magnitude)/25)-1)*self_orb/self_orb.magnitude
        self.aim()
        for vessel in [player]+lure_grid.neighbour(self):
            if (self.position-vessel.position).magnitude < 9: self.explode(vessel)

        self.position += self.speed*dt
        self.angle    += self.momentum*dt
        self.speed    *= 0.995
        self.momentum *= 0.90
        self.angle    -= 2*pi*((self.angle+pi)//(2*pi))

        enemy_missile_grid.store(self)

    def aim(self):
        if self.HP <= 0 or camera.frame_count > self.birth + 15*frame_rate: self.explode()
        if len(Lure.list) > 0 and not self.target in Lure.list: self.target = random.choice(Lure.list)
        if not self.target in [player]+Lure.list:
            if player.alive: self.target = player
        else:
            angle  = Vector.angle(Vector(sin(self.angle),cos(self.angle)), self.position-self.target.position)
            angle2 = Vector.angle(Vector(sin(self.angle),cos(self.angle)), self.speed-self.target.speed)
            if angle != 0: self.momentum -= angle + 0.1*angle/abs(angle)
            self.speed -= (2*Vector(sin(self.angle),cos(self.angle)) + Vector(sin(self.angle),cos(self.angle)).rotate(angle2/4)*angle2**2)/5
    
    def explode(self, vessel=None):
        if vessel != None:
            vessel.HP       -= 800
            vessel.speed    += (self.speed-vessel.speed)/2
            vessel.momentum += random.uniform(-15,15)
            Fixed_Animation(self.position, vessel.speed, enemy_missile_surfaces["explosion"],2)
        else: Fixed_Animation(self.position, Vector(0,0), enemy_missile_surfaces["explosion"],2)
        if self in Enemy_Missile.list: Enemy_Missile.list.remove(self)
        if vessel is player: sound.miss_exp.play()

    def draw(self, camera):
        surface = enemy_missile_surfaces["missile"].copy()
        surface.blit(enemy_missile_surfaces["flames"][camera.frame_count%4//2], (0,0))
        if camera.frame_count%2 == 0: surface.blit(enemy_missile_surfaces["light"], (0,0))
        center_blit(camera.screen, scale_rotate(surface, self.angle, camera.scale).convert_alpha(), camera.convert(self.position))




class Lure: # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    list = []

    def __init__(self, position, speed, momentum, HP=10):
        self.position  = position
        self.speed     = speed
        self.angle     = 0
        self.momentum  = momentum
        self.birth     = camera.frame_count
        Lure.list     += [self]
        lure_grid.store(self)

        self.HP      = HP
        self.HP_max  = HP

    def update(self):
        lure_grid.remove(self)
        if (self.HP <=0 or camera.frame_count - self.birth > 1000) and self in Lure.list: Lure.list.remove(self)
        
        self_orb = self.position - orb.position
        if self_orb.magnitude < 250: self.speed += (exp((250-self_orb.magnitude)/25)-1)*self_orb/self_orb.magnitude
        self.position += self.speed*dt
        self.angle    += self.momentum*dt
            
        self.speed *= 0.99
        self.momentum *= 0.99
        self.angle    -= 2*pi*((self.angle+pi)//(2*pi))

        lure_grid.store(self)

    def draw(self, camera):
        center_blit(camera.screen, scale_rotate(lure_surface, self.angle + pi*((camera.frame_count//20)%2), camera.scale).convert_alpha(), camera.convert(self.position))

    
            

class Laser: #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    list = []

    def __init__(self, source):
        self.source     = source
        self.positions  = []
        self.directions = []
        self.on         = False
        self.dl         = 15
        Laser.list     += [self]
    
    def update(self):
        if self.on:
            self.positions  = [self.source.position]
            self.directions = [self.dl*Vector(sin(self.source.angle),cos(self.source.angle))]
            B = True
            while B:
                self.positions  += [self.positions[-1] - self.directions[-1]]
                B = (self.positions[-1]-player.position).magnitude < 1500
                for object in Enemy.list+Enemy_Missile.list:
                    if (object.position - self.positions[-1]).magnitude < 14:
                        B = False
                        object.HP -= 10
                        break
                else:
                    orb_dist = self.positions[-1]-orb.position
                    if orb_dist.magnitude < 250: self.directions += [self.directions[-1] - (exp((250-orb_dist.magnitude)/100000*self.dl)-1)*(self.positions[-1] + orb.position)]
                    else:                        self.directions += [self.directions[-1]]
    
    def draw(self, camera):
        if self.on:
            for i in range(len(self.positions)-1):
                pygame.draw.aaline(camera.screen, "white", camera.convert(self.positions[i]).coo, camera.convert(self.positions[i+1]).coo)





class Debrit: # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    list = []

    def __init__(self, position, speed, momentum, surface):
        self.position  = position
        self.speed     = speed
        self.angle     = 0
        self.momentum  = momentum

        self.birth   = camera.frame_count
        self.surface = surface
        self.alpha   = 255
        Debrit.list += [self]
        
    def update(self):
        if self.alpha <= 0: Debrit.list.remove(self)
        self_orb = self.position - orb.position
        if self_orb.magnitude < 250: self.speed += (exp((250-self_orb.magnitude)/25)-1)*self_orb/self_orb.magnitude

        self.position += self.speed*dt
        self.angle    += self.momentum*dt
        self.angle    -= 2*pi*((self.angle+pi)//(2*pi))
            
        self.speed *= 0.995
        self.alpha -= 1
        self.surface.set_alpha(self.alpha)
    
    def draw(self, camera):
        center_blit(camera.screen, scale_rotate(self.surface, self.angle, camera.scale).convert_alpha(), camera.convert(self.position))




class Fixed_Animation: #  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    list = []

    def __init__(self, position, speed, surfaces, tempo=1):
        self.position = position
        self.speed    = speed
        self.surfaces = surfaces
        self.frame    = 0
        self.tempo    = tempo
        Fixed_Animation.list += [self]
    
    def draw(self, camera):
        if self.frame < len(self.surfaces):
            center_blit(camera.screen, scale_rotate(self.surfaces[int(self.frame)], 0, camera.scale).convert_alpha(), camera.convert(self.position + self.speed*self.frame*dt))
            self.frame += 1/self.tempo
        else: Fixed_Animation.list.remove(self)




### FUNCTION DUMP ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
### _______________________________________________________________________________________________




def spawn_enemies(number, target):
    spawn_position = player.position
    while (spawn_position-player.position).magnitude < 1000:
        spawn_position = Vector(random.uniform(-2500,2500), random.uniform(-2500,2500))
    enemies = [Enemy(spawn_position+Vector(random.uniform(-300,300), random.uniform(-150,150)), Vector(0,0), 0) for _ in range(number)]
    for enemy in enemies: enemy.target = target

def dead_player_update():
    sound.ship_exlosion.play()
    player.alive = False
    player.is_rotating_l   = False
    player.is_rotating_r   = False
    player.motor_on        = False
    player.do_fire         = False
    player.precision_mode  = False
    player.do_fire_missile = False
    player.do_lunch_lure   = False
    player.laser_on        = False
    player.energy = 0
    player.missile_gauge, player.missile_number = 0, 0
    player.lure_gauge,    player.lure_number    = 0, 0
    for enemy   in Enemy.list:         enemy.target = orb
    for missile in Enemy_Missile.list: missile.target = orb
    camera.key_frame_GO = camera.frame_count
    sound.music_on = False
    for surface in player_surfaces["debrits"]: 
        eje = 100
        Debrit(player.position, player.speed+Vector(random.uniform(-eje,eje),random.uniform(-eje,eje)), random.uniform(-10,10), surface)

def dead_orb_update():
    camera.key_frame_GO = camera.frame_count
    orb.died = True
    orb.dies = False
    sound.music_on = False
    sound.orb_exlosion.play()

def center_blit(screen, surface, coordinate):
    screen.blit(surface, [ x-y/2 for x,y in zip(coordinate, surface.get_size())])

def do_close(event):
    if event.type == pygame.QUIT:
        pygame.quit()
        return True
    return False

def resize(event):
    if event.type == pygame.VIDEORESIZE:
        width, height = event.size
        if width  < 1000: width  = 1000
        if height < 1000: height = 1000
        screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

def clic_button(left_top, right_bottom, position):
    return left_top[0] <= position[0] <= right_bottom[0] and left_top[1] <= position[1] <= right_bottom[1]

def center_blit(screen, surface, coordinate):
    screen.blit(surface, [ x-y/2 for x,y in zip(coordinate, surface.get_size())])

def scale_rotate(surface, angle, scale):
    return pygame.transform.rotate(pygame.transform.scale_by(surface,scale), angle*180/pi)

def draw_wave_indicator():
        wave_surface = font40.render(f"Vague de molikoïdes n°{wave_number}", True, "white")
        screen.blit(protect_the_orb_surface, (25,80))
        screen.blit(wave_surface,            (33,175))

def draw_you_died():
    wave_surface = font40.render(f"Vous avez survécu {wave_number-1} vague{'s'*(wave_number>2)} de {enemy_name}...", True, "white")
    center_blit(screen, you_died_surface, Vector(*screen.get_size())/2)
    center_blit(screen, wave_surface,     Vector(*screen.get_size())/2+Vector(0,80))

def draw_orb_exploded():
    wave_surface = font40.render(f"Vous avez survécu {wave_number-1} vague{'s'*(wave_number>2)} de {enemy_name}...", True, "grey")
    center_blit(screen, orb_exploded_surface, Vector(*screen.get_size())/2)
    center_blit(screen, wave_surface,         Vector(*screen.get_size())/2+Vector(0,80))

def draw_background():
    coo   = (-camera.center   ).coo
    coo10 = (-camera.center/10).coo
    coo20 = (-camera.center/20).coo
    neb   = pygame.transform.scale_by(background_neb_surface, camera.scale)
    for i in range(-1,2):
        for j in range(-1,2):
            screen.blit(background_surface, (coo20[0]%1000+1000*i, coo20[1]%1000+1000*j))
    for i in range(-1,2):
        for j in range(-1,2):
            screen.blit(background_stars_surface, (coo10[0]%1000+1000*i, coo10[1]%1000+1000*j))
    for i in range(-1,2):
        for j in range(-1,2):
            screen.blit(neb, (coo[0]%(1000*camera.scale)+1000*i*camera.scale, coo[1]%(1000*camera.scale)+1000*j*camera.scale))

def draw_hud():
    for enemy in Enemy.list:
        player_enemy = (player.position - enemy.position).magnitude
        if player_enemy > 800/camera.scale:
            angle = Vector.angle(player.position - enemy.position, Vector(0,-1))
            center_blit(camera.screen, pygame.transform.rotate(enemy_indicator_surface, angle*180/pi), Vector(*screen.get_size())/2 + 360*Vector(sin(angle),cos(angle)))
    
    for missile in Enemy_Missile.list:
        player_missile = (player.position - missile.position).magnitude
        if player_missile > 600/camera.scale:
            angle = Vector.angle(player.position - missile.position, Vector(0,-1))
            center_blit(camera.screen, pygame.transform.rotate(miss_indicator_surfaces[camera.frame_count%20//10], angle*180/pi), Vector(*screen.get_size())/2 + 330*Vector(sin(angle),cos(angle)))

    player_orb = (player.position - orb.position).magnitude
    if player_orb > 1000/camera.scale:
        angle = Vector.angle(player.position - orb.position, Vector(0,-1))
        center_blit(camera.screen, pygame.transform.rotate(orb_indicator_surface, angle*180/pi), Vector(*screen.get_size())/2 + 400*Vector(sin(angle),cos(angle)))

    if player.no_power: pygame.draw.rect(screen, (100,100,100),  pygame.Rect(1425, 52, 468*player.energy/player.energy_max, 5))
    else:               pygame.draw.rect(screen, (0,255,255), pygame.Rect(1425, 52, 468*player.energy/player.energy_max, 5))
    pygame.draw.rect(screen, (255,0,0),   pygame.Rect(1425, 27,  468*player.HP/player.HP_max,  13))
    pygame.draw.rect(screen, (0,255,255), pygame.Rect(27,   27,  639*orb.HP/orb.HP_max,        13))
    pygame.draw.rect(screen, (0,255,0),   pygame.Rect(1792, 87,  101*player.missile_gauge/100, 5 ))
    pygame.draw.rect(screen, (255,255,0), pygame.Rect(1792, 122, 101*player.lure_gauge/100,    5 ))
    for i in range(player.missile_number): pygame.draw.rect(screen, (0,255,0),   pygame.Rect(1792+18*i, 69,  11, 11))
    for i in range(player.lure_number):    pygame.draw.rect(screen, (255,255,0), pygame.Rect(1792+18*i, 104, 11, 11))
    screen.blit(hud_surface, (0,0))
    if sound.music_on: screen.blit(music_on_surface,  (1855,1015))
    else:              screen.blit(music_off_surface, (1855,1015))




### IMPORTANT FUNCIONS  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
### _______________________________________________________________________________________________




def global_update():
    if orb.dies and not orb.died: dead_orb_update()
    player.update()
    if player.alive and player.dies: dead_player_update()
    for projectile in Player_Projectile.list :
        projectile.update()
        if (projectile.position-player.position).magnitude > despawn_distance and projectile in Player_Projectile.list: Player_Projectile.list.remove(projectile)
    for projectile in Enemy_Projectile.list :
        projectile.update()
        if (projectile.position-player.position).magnitude > despawn_distance and projectile in Enemy_Projectile.list: Enemy_Projectile.list.remove(projectile)
    for missile in Enemy_Missile.list: missile.update()
    for missile in Player_Missile.list:
        missile.update()
        if (missile.position-player.position).magnitude > despawn_distance and missile in Player_Missile.list: Player_Missile.list.remove(missile)
    for lure in Lure.list:
        lure.update()
        if (lure.position-player.position).magnitude > despawn_distance and lure in Lure.list: Lure.list.remove(lure)
    for enemy in Enemy.list:     enemy.update()
    for debrit in Debrit.list:   debrit.update()
    for laser in Laser.list :    laser.update()
    for vessel in Player.list+Enemy.list:
        for other in Player.list+Enemy.list:
            if not vessel is other:
                v = vessel.position-other.position
                if 0 < v.magnitude < 25:
                    vessel.speed += 15*v/v.magnitude
    orb.update()
        

def global_draw(camera):
    if orb.died: screen.fill("white")
    else:
        draw_background()
        screen.blit(layer_surface, (0,0))
        for laser in Laser.list : laser.draw(camera)
        for debrit in Debrit.list:
            debrit.draw(camera)
        for missile in Player_Missile.list+Enemy_Missile.list: missile.draw(camera)
        for lure in Lure.list: lure.draw(camera)
        if player.alive: player.draw(camera)
        for enemy in Enemy.list: enemy.draw(camera)
        for projectile in Player_Projectile.list+Enemy_Projectile.list : projectile.draw(camera)
        for anim in Fixed_Animation.list : anim.draw(camera)
        orb.draw(camera)
        draw_hud()


def drop_enemy_wave(n):
    if   n < 2: spawn_enemies(1,orb)
    elif n < 3: spawn_enemies(2,orb)
    elif n < 4: spawn_enemies(1,player)
    elif n < 5: spawn_enemies(2,orb); spawn_enemies(1,player)
    elif n < 6: spawn_enemies(3,orb); spawn_enemies(3,orb)
    elif n < 7: spawn_enemies(4,orb); spawn_enemies(2,player)
    elif n < 8: spawn_enemies(3,orb); spawn_enemies(3,orb); spawn_enemies(2,player)
    else:        
        spawn_enemies_number_0 = int(random.uniform(n/4, n/3))
        spawn_enemies_number_1 = int(random.uniform(n/4, n/3))
        spawn_enemies_number_2 = int(random.uniform(n/4, n/3))
        spawn_enemies(spawn_enemies_number_0, random.choice([orb, player]))
        spawn_enemies(spawn_enemies_number_1, random.choice([orb, player]))
        spawn_enemies(spawn_enemies_number_2, random.choice([orb, player]))




### INIT  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
### _______________________________________________________________________________________________




enemy_name = "Molikoïds"

pygame.init()
pygame.mixer.init()
screen      = pygame.display.set_mode((1920,1080))
pygame.display.set_caption(f'The Strike Of The {enemy_name} !')
pygame.display.set_icon(pygame.image.load('assets/icon.png'))
clock       = pygame.time.Clock()

frame_rate  = 45
dt          = 1/frame_rate
camera      = Camera(Vector(0,0), 2, screen)
despawn_distance = 2000
wave_tempo       = 5*frame_rate
game_over_tempo  = 5*frame_rate
grid_width  = 30

test_mode = False



### SURFACES LOAD ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
### _______________________________________________________________________________________________
        
        


font40  = pygame.font.SysFont("centurygothicbold", 40)
font120 = pygame.font.SysFont("centurygothicbold", 120)

protect_the_orb_surface   = font120.render("PROTÉGEZ L'ORBE !!",     True, "white")
you_died_surface          = font120.render("Vaisseau détruit.",      True, "white")
orb_exploded_surface      = font120.render("L'Orbe à été détruite.", True, "grey" )
 
background_surface       =  pygame.image.load( 'assets/background.png'                  )
background_neb_surface   =  pygame.image.load( 'assets/background_nebula.png'           ).convert_alpha()
background_stars_surface =  pygame.image.load( 'assets/background_stars.png'            ).convert_alpha()
layer_surface            =  pygame.image.load( 'assets/layer.png'                       ).convert_alpha()
hud_surface              =  pygame.image.load( 'assets/HUD.png'                         ).convert_alpha()
music_on_surface         =  pygame.image.load( 'assets/music_on_icon.png'               ).convert_alpha()
music_off_surface        =  pygame.image.load( 'assets/music_off_icon.png'              ).convert_alpha()
 
orb_indicator_surface    =  pygame.image.load( 'assets/orb/indicator.png'               ).convert_alpha()
enemy_indicator_surface  =  pygame.image.load( 'assets/enemy/indicator.png'             ).convert_alpha()
miss_indicator_surfaces  = [pygame.image.load(f'assets/enemy/missile_indicator_{i}.png' ).convert_alpha() for i in range(2)]
health_bar_surface       =  pygame.image.load( 'assets/health_bar.png'                  ).convert_alpha()
lure_surface             =  pygame.image.load( 'assets/player/lure.png'                 ).convert_alpha()

player_surfaces = {
        "vessel"     :      pygame.image.load( 'assets/player/vessel.png'               ).convert_alpha(),
        "heat"       :      pygame.image.load( 'assets/player/heat.png'                 ).convert_alpha(),
        "flames"     :     [pygame.image.load(f'assets/player/flame_{i}.png'            ).convert_alpha() for i in range(2)],
        "boosts"     :     [pygame.image.load(f'assets/player/boost_{i}.png'            ).convert_alpha() for i in range(2)],
        "rcs_l"      :      pygame.image.load( 'assets/player/rcs_l.png'                ).convert_alpha(),
        "rcs_r"      :      pygame.image.load( 'assets/player/rcs_r.png'                ).convert_alpha(),
        "canon_fire" :      pygame.image.load( 'assets/player/canon_fire.png'           ).convert_alpha(),
        "shield"     :      pygame.image.load( 'assets/player/shield.png'               ).convert_alpha(),
        "explosions" :     [pygame.image.load(f'assets/player/explosion_{i}.png'        ).convert_alpha() for i in range(8)],
        "debrits"    :     [pygame.image.load(f'assets/player/debrit_{i}.png'           ).convert_alpha() for i in range(5)]
} 
enemy_surfaces = { 
        "vessel"     :      pygame.image.load( 'assets/enemy/vessel.png'                ).convert_alpha(),
        "frames"     :     [pygame.image.load(f'assets/enemy/flame_{i}.png'             ).convert_alpha() for i in range(2)],
        "lights"     :     [pygame.image.load(f'assets/enemy/light_{i}.png'             ).convert_alpha() for i in range(2)],
        "debrits"    :     [pygame.image.load(f'assets/enemy/debrit_{i}.png'            ).convert_alpha() for i in range(3)],
        "explosions" :     [pygame.image.load(f'assets/enemy/explosion_{i}.png'         ).convert_alpha() for i in range(8)]
} 
orb_surfaces = { 
        "orb"        :      pygame.image.load( 'assets/orb/orb.png'                   ).convert_alpha(),
        "dying"      :      pygame.image.load( 'assets/orb/orb_dying.png'             ).convert_alpha()
} 
player_projectile_surfaces = {
        "projectile" :      pygame.image.load( 'assets/player/projectile.png'           ).convert_alpha(),
        "explosions" :     [pygame.image.load(f'assets/player/projectile_impact_{i}.png').convert_alpha() for i in range(3)]
} 
enemy_projectile_surfaces = {
        "projectile" :     [pygame.image.load(f'assets/enemy/projectile_{i}.png'        ).convert_alpha() for i in range(3)],
        "explosions" :     [pygame.image.load(f'assets/enemy/projectile_impact_{i}.png').convert_alpha() for i in range(3)]
} 
player_missile_surfaces = {
        "missile"    :      pygame.image.load( 'assets/player/missile.png'              ).convert_alpha(),
        "flames"     :     [pygame.image.load(f'assets/player/missile_flame_{i}.png'    ).convert_alpha() for i in range(2)],
        "rcs_l"      :      pygame.image.load( 'assets/player/missile_rcs_l.png'        ).convert_alpha(),
        "rcs_r"      :      pygame.image.load( 'assets/player/missile_rcs_r.png'        ).convert_alpha(),
        "explosion"  :     [pygame.image.load(f'assets/player/missile_explosion_{i}.png').convert_alpha() for i in range(5)],
} 
enemy_missile_surfaces = { 
        "missile"    :      pygame.image.load( 'assets/enemy/missile.png'               ).convert_alpha(),
        "flames"     :     [pygame.image.load(f'assets/enemy/missile_flame_{i}.png'     ).convert_alpha() for i in range(2)],
        "light"      :      pygame.image.load(f'assets/enemy/missile_light.png'         ).convert_alpha(),
        "explosion"  :     [pygame.image.load(f'assets/enemy/missile_explosion_{i}.png' ).convert_alpha() for i in range(5)]

}




### SOUNDS  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
### _______________________________________________________________________________________________




class Sound:
    id = 0
    list = []

    def __init__(self, sound):
        self.sound = sound
        self.channel = pygame.mixer.Channel(Sound.id)
        pygame.mixer.set_num_channels(Sound.id+2)
        Sound.id += 1
        Sound.list += [self]
    
    def play(self, loops=0):     self.channel.play(self.sound, loops)
    def set_volume(self, vol):   self.sound.set_volume(vol)
    def get_volume(self): return self.sound.get_volume()

sound = Stockage()

sound.music_on     = not test_mode
sound.motor_max    = False
sound.HP_alarm_on  = False
sound.orb_alarm_on = False

sound.motor  = Sound(pygame.mixer.Sound("assets/sound/motor.mp3" ))
sound.boost  = Sound(pygame.mixer.Sound("assets/sound/boost.mp3" ))
sound.rcs_l  = Sound(pygame.mixer.Sound("assets/sound/rcs_l.mp3" ))
sound.rcs_r  = Sound(pygame.mixer.Sound("assets/sound/rcs_r.mp3" ))
sound.beam   = Sound(pygame.mixer.Sound("assets/sound/beam.mp3"  ))
sound.shield = Sound(pygame.mixer.Sound("assets/sound/shield.mp3"))
for sd in Sound.list: sd.set_volume(0)
sound.music  = Sound(pygame.mixer.Sound("assets/sound/music.mp3" ))
sound.music.set_volume(sound.music_on)

sound.wave_alarm    = Sound(pygame.mixer.Sound("assets/sound/wave_alarm.mp3"       ))
sound.laser         = Sound(pygame.mixer.Sound("assets/sound/laser.mp3"            ))
sound.missile       = Sound(pygame.mixer.Sound("assets/sound/missile.mp3"          ))
sound.miss_exp      = Sound(pygame.mixer.Sound("assets/sound/missile_explosion.mp3"))
sound.lure          = Sound(pygame.mixer.Sound("assets/sound/lure.mp3"             ))
sound.impact        = Sound(pygame.mixer.Sound("assets/sound/impact.mp3"           ))
sound.motor_off     = Sound(pygame.mixer.Sound("assets/sound/motor_off.mp3"        ))
sound.HP_alarm      = Sound(pygame.mixer.Sound("assets/sound/HP_alarm.mp3"         ))
sound.orb_alarm     = Sound(pygame.mixer.Sound("assets/sound/orb_alarm.mp3"        ))
sound.power_off     = Sound(pygame.mixer.Sound("assets/sound/power_off.mp3"        ))
sound.power_on      = Sound(pygame.mixer.Sound("assets/sound/power_on.mp3"         ))
sound.ship_exlosion = Sound(pygame.mixer.Sound("assets/sound/ship_explosion.mp3"   ))
sound.orb_exlosion  = Sound(pygame.mixer.Sound("assets/sound/orb_explosion.mp3"    ))

def sound_update():
    if not player.no_power and player.do_fire: sound.laser.play()
    sound.music.set_volume(min(1,max(0, sound.music.get_volume() + ( sound.music_on*2-1)/30                               )))
    sound.motor.set_volume(min(1,max(0, sound.motor.get_volume() + ((player.motor_on      and not player.no_power)*2-1)/5 )))
    sound.boost.set_volume(min(1,max(0, sound.boost.get_volume() + ((player.do_boost      and not player.no_power)*2-1)/15)))
    sound.rcs_l.set_volume(min(1,max(0, sound.rcs_l.get_volume() + ((player.is_rotating_l and not player.no_power)*2-1)/5 )))
    sound.rcs_r.set_volume(min(1,max(0, sound.rcs_r.get_volume() + ((player.is_rotating_r and not player.no_power)*2-1)/5 )))
    sound.beam.set_volume( min(1,max(0,  sound.beam.get_volume() + ((player.laser_on      and not player.no_power)*2-1)/3 )))
    if sound.shield.get_volume() <= 0.2: sound.shield.set_volume( min(0.2,max(0, sound.shield.get_volume() + ((player.shield_on and not player.no_power)*2-1)/20 )))
    else:                                sound.shield.set_volume( sound.shield.get_volume() - 0.03 )
    if player.alive and not orb.died:
        if sound.HP_alarm_on:
            if camera.frame_count%(frame_rate/3) == 0: sound.HP_alarm.play()
            if player.HP/player.HP_max > 0.3: sound.HP_alarm_on = False
        elif 0 < player.HP/player.HP_max < 0.2: sound.HP_alarm_on = True
        if sound.orb_alarm_on:
            if camera.frame_count%(frame_rate/4) == 5: sound.orb_alarm.play()
            if orb.HP/orb.HP_max > 0.3: sound.orb_alarm_on = False
        elif 0 < orb.HP/orb.HP_max < 0.2: sound.orb_alarm_on = True

    if sound.motor_max and sound.motor.get_volume() != 1: sound.motor_off.play()
    sound.motor_max = sound.motor.get_volume() == 1




### MAIN LOOP ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
### _______________________________________________________________________________________________




player_grid            = Grid(grid_width)
enemy_grid             = Grid(grid_width)
player_projectile_grid = Grid(grid_width)
enemy_projectile_grid  = Grid(grid_width)
player_missile_grid    = Grid(grid_width)
enemy_missile_grid     = Grid(grid_width)
lure_grid              = Grid(grid_width)

player = Player(Vector(400,0), Vector(0,0), 0)
orb    = Orb(Vector(0,0))

wave_number = 0
key_frame_tempo = -( 3 - 3597*test_mode )*frame_rate
mouse_pressed = False

sound.music.play(-1)
sound.motor.play(-1)
sound.boost.play(-1)
sound.rcs_l.play(-1)
sound.rcs_r.play(-1)
sound.beam.play(-1)
sound.shield.play(-1)


while True:
    screen.fill("black")



    for event in pygame.event.get():
        if do_close(event): break
        #resize(event)
        if event.type == pygame.KEYDOWN:
            if player.alive:
                if event.key == pygame.K_SPACE: player.do_fire         = True
                if event.key == pygame.K_m:     player.do_fire_missile = True
                if event.key == pygame.K_p:     player.do_lunch_lure   = True
                if event.key == pygame.K_o:     player.shield_on       = not player.shield_on
                if event.key == pygame.K_e:     player.do_boost        = 60
            if event.key == pygame.K_KP_PLUS:  camera.scale = 2
            if event.key == pygame.K_KP_MINUS: camera.scale = 1

            if event.key == pygame.K_x: pass
            if event.key == pygame.K_w: pass

    keys = pygame.key.get_pressed()    
    if keys[pygame.K_q]:      player.is_rotating_l  = True
    if keys[pygame.K_d]:      player.is_rotating_r  = True
    if keys[pygame.K_z]:      player.motor_on       = True
    if keys[pygame.K_LSHIFT]: player.precision_mode = True
    if keys[pygame.K_l]:      player.laser_on       = True

    if pygame.mouse.get_pressed()[0]:
        if not mouse_pressed:
            if clic_button((1865,1025), (1895,1055), pygame.mouse.get_pos()): sound.music_on = not sound.music_on
        mouse_pressed = True
    else: mouse_pressed = False



    camera.center = player.position*camera.scale - Vector(*screen.get_size())/2
    
    sound_update()
    global_draw(camera)
    global_update()

    if camera.frame_count > key_frame_tempo + wave_tempo:
        if len(Enemy.list) == 0: key_frame_tempo = camera.frame_count
        elif camera.frame_count < key_frame_tempo + wave_tempo + 3*frame_rate and player.alive: draw_wave_indicator()
    elif camera.frame_count == key_frame_tempo + wave_tempo:
        wave_number += 1
        drop_enemy_wave(wave_number)
        sound.wave_alarm.play()
    if orb.died:
        draw_orb_exploded()
        if camera.frame_count == camera.key_frame_GO + game_over_tempo: break
    elif not player.alive:
        draw_you_died()
        if camera.frame_count == camera.key_frame_GO + game_over_tempo: break



    camera.frame_count += 1

    pygame.display.update()
    clock.tick(frame_rate)