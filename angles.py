import raylibpy as rl
import math 
from math import radians
from random import randrange, choice, uniform
from sound_manager import SoundManager
from world import World
#from styles import font_main

print(rl.RAYLIB_VERSION)
rl.set_trace_log_level(rl.LOG_ERROR)

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 800

global_max_speed = rl.Vector2(100,100)

rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Juego de disparos 1.0")

from styles import *
from enums import *

rl.set_target_fps(60)


#region SINGLETONS

world = World(True,True)
sounds = SoundManager()

#endregion

#region GENERATORS

class AmmoGenerator:
	global world
	def __init__(self,bullets,cal50,rockets):

		self.amounts = {Ammo_type.bullets: bullets,Ammo_type.cal50: cal50, Ammo_type.rockets: rockets}

	def generate(self,ammo_type):

		for amt in range (self.amounts[ammo_type]):
			newx = randrange(0,SCREEN_WIDTH,1)
			newy = randrange(0,SCREEN_HEIGHT,1)
			new_ammo = Ammo_pup(ammo_type,rl.Vector2(newx,newy))
			world.object_list.append(new_ammo)


class EnemyGenerator:
	global world
	def __init__(self,small,mid,big,boss):

		self.amounts = {Enemy_type.small: small, Enemy_type.medium: mid, Enemy_type.big: big, Enemy_type.boss: boss}
	

	def generate(self,enemy_type):

		for amt in range (self.amounts[enemy_type]):
			newx = randrange(0,SCREEN_WIDTH)
			newy = randrange(0,SCREEN_HEIGHT)
			new_enemy = Enemy(rl.Vector2(newx,newy),enemy_type)
			world.add_objects([new_enemy])

# endregion
 
 # region DUCTAPE CLASES

class TimerDecals:

	def _timer(self):

		if self.color.a > 0:
			if hasattr(self,"grow_speed"): #BLOODSTAIN
				self.color.a -= 0.05
			elif hasattr(self,"size_multiplier"): #HOLE
				self.color.a -= 0.02
			elif hasattr(self,"explosion"):
				self.color.a -= 0.5


		else:
			if hasattr(self,"grow_speed"): #BLOODSTAIN
				world.remove_decals(self)
			elif hasattr(self,"size_multiplier"): #HOLE
				world.remove_background(self)
			elif hasattr(self,"explosion"):
				world.remove_objects([self])
#endregion

# region PLAYER

class Player:
	global world
	def __init__(self, init_position: rl.Vector2, init_angle: float, init_color):
        
		self.position: rl.Vector2 = init_position
		self.angle: float = init_angle
		self.size: int = 30
		self.movement: rl.Vector2 = rl.Vector2(0,0)
		self.color = init_color
		self.speed = 400
		self.original_speed = self.speed
		self.frict = 10
		self.max_speed = 10
		self.rotation_speed = 3
		self.weapons = [Ammo_type.bullets,Ammo_type.cal50,Ammo_type.rockets]


		self.ammo = {Ammo_type.bullets:1000,Ammo_type.cal50:500,Ammo_type.rockets:500}
		self.ammo_per_type = {Ammo_type.bullets:[25,0,0],Ammo_type.cal50:[0,10,0],Ammo_type.rockets:[0,0,1]}
		self.ammo_messages = {Ammo_type.bullets: "You Pickup [25] Bullets!",Ammo_type.cal50: "You Pickup [10] Cal .50 Bullets!",Ammo_type.rockets: "You Pickup a ROCKET!"}

		self.weapon_selector = self.weapons[0]

		self.children = []
		self.messages = []


		self.create_lines()
		
	def replenish_ammo(self):

		pass

	def receive_ammo(self,ammo_array):

		print(ammo_array)
		self.ammo[Ammo_type.bullets] += ammo_array[0]
		self.ammo[Ammo_type.cal50] += ammo_array[1]
		self.ammo[Ammo_type.rockets] += ammo_array[2]


	def create_lines(self):

		self.line1 = Linesofplayer(self,self.angle,0,rl.RED)
		self.children.append(self.line1)

	def input_attack(self):

		if rl.is_key_pressed(rl.KEY_ONE):
			self.weapon_selector = self.weapons[0]
		if rl.is_key_pressed(rl.KEY_TWO):
			self.weapon_selector = self.weapons[1]
		if rl.is_key_pressed(rl.KEY_THREE):
			self.weapon_selector = self.weapons[2]	

		if rl.is_mouse_button_pressed(rl.MOUSE_LEFT_BUTTON):
			if self.ammo[self.weapon_selector] > 0:
				new_bullet = Bullet(self.position,self.movement,self,self.weapon_selector)
				world.add_objects([new_bullet])
				(f"{world.object_list}")
				self.ammo[self.weapon_selector] -= 1

	def speed_friction(self):

		if self.speed > 0:
			self.speed -= self.frict 

		if self.speed < 0:
			self.speed = 0


	def normalize_and_output(self):

		#NORMALIZAR MANUALMENTE PORQUE NO HAY UNA FUNCION DE MIERDA 
		magnitude = math.sqrt(self.movement.x ** 2 + self.movement.y ** 2)
		if magnitude != 0:
			
			self.movement = rl.Vector2((self.movement.x/magnitude),(self.movement.y/magnitude))
	
		#SI NO HAY TECLA DE ADELANTE O ATRAS, APLICAR FRICCION

		#CONVERTIR A ENTERO PARA EVITAR EL JITTERNESS
		self.movement.x,self.movement.y = round(self.movement.x,2),round(self.movement.y,2)

		#REGRESAR EL MOVEMENT MULTIPLICADO POR LA VELOCIDAD REAL
		return self.movement * self.speed 

	def  strafe_input(self): 

		self.speed_friction()

		if rl.is_key_down(rl.KEY_A):
			self.movement.x = -1
			self.speed = self.original_speed
		if rl.is_key_down(rl.KEY_D):
			self.movement.x = 1
			self.speed = self.original_speed
		if rl.is_key_down(rl.KEY_W):
			self.movement.y = -1
			self.speed = self.original_speed
		if rl.is_key_down(rl.KEY_S):
			self.movement.y = 1
			self.speed = self.original_speed

		print(self.movement)
		return self.normalize_and_output()

	def mouse_aim(self):

		mouse_vector = rl.Vector2(rl.get_mouse_x(),rl.get_mouse_y())
		aim_vector = mouse_vector - self.position 

		aim_angle = math.atan2(aim_vector.y,aim_vector.x)
		self.angle = rl.lerp(self.angle,math.degrees(aim_angle),0.9)

	def input(self): #DEPRECATED


		self.speed_friction()

		#CAMBIAR ROTACION CON TECLAS A Y D
		if rl.is_key_down(rl.KEY_A):
			self.angle -= self.rotation_speed
		if rl.is_key_down(rl.KEY_D):
			self.angle += self.rotation_speed


		if rl.is_key_down(rl.KEY_W):
			self.speed = self.original_speed
			self.movement.x = math.cos(radians(self.angle))
			self.movement.y = math.sin(radians(self.angle))

		if rl.is_key_down(rl.KEY_S):
			self.speed = self.original_speed
			self.movement.x = -math.cos(radians(self.angle))
			self.movement.y = -math.sin(radians(self.angle))


	def collision_ammo(self):

		group = world.object_list

		for object in group:
			if hasattr(object,"rect"):
				if rl.check_collision_circle_rec(self.position,self.size,object.rect):
					if not object.open:
						self.receive_ammo(self.ammo_per_type[object.type])
						object.open = True
						new_message = MessagePickup(self.ammo_messages[object.type],object.position)
						world.add_objects([new_message])


	def update_children(self):

		for child in self.children:
			child.update()

	def draw(self):

		rl.draw_circle_v(self.position,self.size,self.color)
		
		

	def update(self):
        
		self.speed_friction()
		self.position += self.strafe_input() *world.global_delta	
		self.mouse_aim()
		self.update_children()
		self.draw()
		self.input_attack()
		self.collision_ammo()
		
#endregion 

#region LINES

class Linesofplayer:
	global world
	def __init__(self,player, parent_angle, own_angle,color):

		self.parent = player
		self.point1 = player.position
		self.length = 50
		self.point2 = rl.Vector2(0,0)
		self.parent_angle = math.radians(parent_angle)
		self.angle = math.radians(own_angle)
		self.color = color
		self.thic = 4

	def point2_position(self):

		self.point2.x = (self.length * math.cos(self.angle+self.parent_angle)) + self.parent.position.x
		self.point2.y = (self.length * math.sin(self.angle+self.parent_angle)) + self.parent.position.y

	def draw(self):

		rl.draw_line_ex(self.point1,self.point2, self.thic, self.color)



	def update(self):

		self.parent_angle = math.radians(self.parent.angle)
		self.point1 = self.parent.position
		self.point2_position()

		self.draw()

class LinesofEnemy:
	global world
	def __init__(self,enemy, parent_angle, own_angle,color):

		self.parent = enemy
		self.point1 = rl.Vector2(enemy.position.x,enemy.position.y)
		self.length = 50
		self.point2 = rl.Vector2(0,0)
		self.parent_angle = math.radians(parent_angle)
		self.angle = math.radians(own_angle)
		self.color = color
		self.thic = 4

	def point2_position(self):

		self.point2.x = (self.length * math.cos(self.angle+self.parent_angle)) + self.parent.position.x
		self.point2.y = (self.length * math.sin(self.angle+self.parent_angle)) + self.parent.position.y

	def draw(self):

		rl.draw_line_ex(self.point1,self.point2, self.thic, self.color)



	def update(self):

		self.parent_angle = math.radians(self.parent.angle)
		self.point1 = self.parent.position
		self.point2_position()

		self.draw()


#endregion

#region ENEMY

class Enemy:
	global world
	def __init__(self,init_position,enemy_type):

		self.position = rl.Vector2(init_position.x,init_position.y)
		self.type_data ={Enemy_type.small: {
							"hp": 10,
							"color":rl.Color(150,190,150,255),
							"atk":5,
							"size":30,
							"range_radius":120,
							"speed":200
							},
						Enemy_type.medium: {
							"hp": 15,
							"color":rl.Color(140,140,120,255),
							"atk":8,
							"size":32,
							"range_radius":120,
							"speed":400
							},
						Enemy_type.big: {
							"hp": 25,
							"color":rl.Color(150,150,20,255),
							"atk":20,
							"size":40,
							"range_radius":120,
							"speed":500
							},
						Enemy_type.boss: {
							"hp": 50,
							"color":rl.Color(50,15,15,255),
							"atk":15,
							"size":50,
							"range_radius":150,
							"speed":500
							}
						}

		if enemy_type not in self.type_data:
			raise ValueError(f"Enemy type {enemy_type} not recognized.")


		self.state = Enemy_state.idle
		self.type = enemy_type
		self.hp = self.type_data[self.type]          ["hp"]
		self.color = self.type_data[self.type]       ["color"]
		self.color_hurt = rl.Color(255,0,0,255)
		self.original_color = self.color
		self.dead_color = rl.Color(self.original_color.r-10,self.original_color.g-10,self.original_color.b-10,self.original_color.a)
		self.atk = self.type_data[self.type]         ["atk"]
		self.size = self.type_data[self.type]        ["size"]
		self.range_radius = self.type_data[self.type]["range_radius"] # 50 - 50 - 25 - 80 
		self.forget_multiplier = 1.8
		self.speed = self.type_data[self.type]       ["speed"] * 0.4  


		self.shield = False
		self.target = None

		self.initial_timer = choice([50,120])
		self.timer = self.initial_timer

		self.hurt_timer = 0
		self.original_hurt_timer = 10
		self.bled = False
		self.gib_life = -10

		self.direction_value = choice([1,-1])
		self.direction = choice(["x","y"])

		self.pushback_x = 0
		self.pushback_y = 0
		self.friction = 0.1

		self.movement_buffer = randrange(50,120)
		self.angle = 0
		self.angle_buffer = randrange(30,100)
		self.angle_amount = randrange(1,3)
		self.angle_sign = choice([1,-1])
		self.movement_speed = choice([0,self.speed])

		self.angle_line = LinesofEnemy(self,self.angle,0,rl.RED)


	def timer_function(self):

		if self.timer > 0:
			self.timer -= 1
		else:
			self.timer =  choice([50,120])



	def select_behavior(self):

		match self.state:

			case Enemy_state.idle:
				self.idle_behavior()

			case Enemy_state.chasing:
				self.chasing_behavior()

			case Enemy_state.attack:
				self.attack_behavior()

			case Enemy_state.dead:
				self.dead_behavior()

			case Enemy_state.gib:
				self.gib_behavior()

	def push_back(self,object): #CORRE SOLO UNA VEZ PARA ESTABLECER EMPUJE

		self.pushback_x = math.cos(object.angle) * object.power
		self.pushback_y = math.sin(object.angle) * object.power

	def check_pushback(self,modifier = 1.0): #CORRE SIEMPRE PARA AGREGAR EMPUJE

		if self.pushback_x > 0:
			self.pushback_x -= self.friction
			self.position.x += self.pushback_x *modifier
		elif self.pushback_x < 0:
			self.pushback_x += self.friction
			self.position.x += self.pushback_x *modifier

		if self.pushback_y > 0:
			self.pushback_y -= self.friction
			self.position.y += self.pushback_y *modifier
		elif self.pushback_y < 0:
			self.pushback_y += self.friction
			self.position.y += self.pushback_y *modifier

	def check_collision(self):

		group = world.object_list

		if self.hp > 0:
			for obj in group:
				if hasattr(obj,"caliber"):
					if rl.check_collision_circles(self.position,self.size,obj.position,obj.size):
						self.hp -= obj.power
						self.push_back(obj)
						new_damage_mgs = DamageMessage(f"-{obj.power}",obj.position)
						world.add_objects([new_damage_mgs])
						self.hurt_timer = self.original_hurt_timer
						obj.determine_particle()
						

				if hasattr(obj,"explosion"):
					if rl.check_collision_circles(self.position,self.size,obj.position,obj.size):
						if obj.explosion:
							self.hp -= obj.power
							self.push_back(obj)
							new_damage_mgs = DamageMessage(f"-{obj.power} area dmg!",self.position+rl.Vector2(10,-20))
							world.add_objects([new_damage_mgs])
							self.hurt_timer = self.original_hurt_timer
							
							

		
		elif self.gib_life < self.hp <= 0  and self.state != Enemy_state.dead:

			#print(f"murió un {self.type} salvaje")
			self.state = Enemy_state.dead

		elif self.hp <= self.gib_life:
			self.state = Enemy_state.gib
			#print(f"explotó {self.type} salvajemente")


	def check_sight(self):

		group = world.object_list

		if self.hp > 0:
			for player in group:
				if hasattr(player,"weapon_selector"):
					if rl.check_collision_circles(self.position,self.range_radius,player.position,player.size) and self.state == Enemy_state.idle:
						self.state = Enemy_state.chasing
						self.target = player
					if not rl.check_collision_circles(self.position,self.range_radius*self.forget_multiplier,player.position,player.size) and self.state == Enemy_state.chasing:
						self.state = Enemy_state.idle

	def modern_movement(self):

		if self.angle_buffer > 0:
			self.angle_buffer -= 1
			self.angle += self.angle_amount * self.angle_sign
		else:
			self.angle_buffer = randrange(30,100)
			self.angle_amount = randrange(1,3)
			self.angle_sign = choice([1,-1])

		if self.movement_buffer > 0:
			self.movement_buffer -= 1
			self.position += rl.Vector2(math.cos(radians(self.angle)),
										math.sin(radians(self.angle))) *self.movement_speed *world.global_delta	
		else:
			self.movement_buffer = randrange(50,120)
			self.movement_speed = choice([0,self.speed])

	def targeted_movement(self):

		target_vector = self.target.position - self.position
		self.angle = math.atan2(target_vector.y,target_vector.x)
		#rl.lerp(self.angle,new_angle,0.2)
		self.angle = math.degrees(self.angle)
		self.position += rl.Vector2(math.cos(radians(self.angle)),
							math.sin(radians(self.angle))) *self.speed *1.1 *world.global_delta	


	def platform_movement(self): #OLD MOVEMENT DEPRECATED

		if self.timer > 0:

			if self.direction == "x":
				self.position.x += self.speed * self.direction_value

			if self.direction == "y":
				self.position.y += self.speed * self.direction_value
			
			self.timer -= 1

		else:

			self.direction_value = choice([1,-1])
			self.direction = choice(["x","y"])
			self.timer = self.initial_timer

	def lerp_movement(self): #OLD MOVEMENT DEPRECATED

		self.position.x = rl.lerp(self.position.x,self.target.position.x-self.target.size,self.speed * 0.02)
		self.position.y = rl.lerp(self.position.y,self.target.position.y-self.target.size,self.speed * 0.02)


	def idle_behavior(self):

		self.modern_movement()	
		self.check_pushback()
		self.check_sight()

	def chasing_behavior(self):
		
		self.check_sight()
		self.targeted_movement()

	def attack_behavior(self):
		pass


	def dead_behavior(self):
		self.color = self.dead_color

		if not self.bled:
			new_bloodstain = Bloodstain(self.position,self.size,False,self.color)
			world.add_decals([new_bloodstain])
			self.bled = True
		
		self.check_pushback(0.5) 

	def gib_behavior(self):

		self.color = rl.Color(100,0,0,200)
		if not self.bled:
			new_bloodstain = Bloodstain(self.position,self.size,True,self.original_color)
			
			world.add_decals([new_bloodstain])
			more_blood = BloodParticles(self.position,[self.color,self.dead_color],0)
			world.add_objects([more_blood])
			self.bled = True
		
		self.check_pushback(0.5)

	def hurt_color(self):

		if self.hurt_timer > 0:

			self.color = self.color_hurt
			self.hurt_timer -= 1
		
		elif self.hurt_timer == 0:

			self.color = self.original_color

		elif self.hurt_timer < 0:

			self.hurt_timer = 0

	def debug(self):

		rl.draw_circle_v(self.position,self.range_radius,rl.Color(200,200,200,60)) #RANGO DE VISION
		rl.draw_circle_v(self.position,self.range_radius*self.forget_multiplier,rl.Color(200,200,200,60)) #RANGO DE DEJAR DE SEGUIR
		rl.draw_text(f"{self.hp}",self.position.x,self.position.y,20,rl.BLACK)
		rl.draw_text(f"{self.angle}",self.position.x,self.position.y+20,20,rl.BLACK)


	def draw(self):

		rl.draw_circle_v(self.position,self.size,self.color)
			

	def update(self):

		self.angle_line.update()
		self.timer_function()
		self.hurt_color()
		self.select_behavior()
		self.check_collision()
		self.draw()

#endregion

#region BULLET

class Bullet:
	global world
	def __init__(self,init_position,parent_movement,player,caliber):

		self.player = player
		
		self.movement = parent_movement
		self.angle = math.radians(player.angle)
		self.offset = 10
		self.position = init_position + rl.Vector2(math.cos(self.angle)*self.offset,math.sin(self.angle)*self.offset)
		
		self.caliber = caliber

		self.caliber_colors = {Ammo_type.bullets:rl.BLACK,
								Ammo_type.cal50:rl.GRAY,
								Ammo_type.rockets:rl.DARKBROWN
								}

		self.caliber_size = {Ammo_type.bullets: 5,
							Ammo_type.cal50: 10, 
							Ammo_type.rockets: 25
							}

		self.caliber_speed = {Ammo_type.bullets: 1500,
							Ammo_type.cal50: 1800, 
							Ammo_type.rockets: 800
							}

		self.caliber_lifetime = {Ammo_type.bullets:100, 
								Ammo_type.cal50:80, 
								Ammo_type.rockets:50
								} 

		self.caliber_power ={Ammo_type.bullets: 2,
							Ammo_type.cal50: 5, 
							Ammo_type.rockets: 10
							}

		self.color = self.caliber_colors[self.caliber]
		self.lifetime = self.caliber_lifetime[self.caliber]
		self.power = self.caliber_power[self.caliber]
		self.size = self.caliber_size[self.caliber]
		self.speed = self.caliber_speed[self.caliber]

	def move_bullet(self):

		#ACCELERATE MOVEMENT VECTOR
		self.movement = rl.Vector2(math.cos(self.angle),math.sin(self.angle)) 
		
		#UPDATE POSITION
		self.position += self.movement * self.speed *world.global_delta	

		#LIMIT TO A MAXIMUM SPEED
		rl.vector2_clamp(self.movement,-global_max_speed,global_max_speed)

	def determine_particle(self):

		if self.caliber == Ammo_type.rockets:
			new_explosion = ExplosionParticles(self.position,None,self.player.angle)
			new_blood1 = BloodParticles(self.position,None,self.player.angle)
			new_blood2 = BloodParticles(self.position,None,self.player.angle+30)
			new_blood3 = BloodParticles(self.position,None,self.player.angle+60)
			new_blood4 = BloodParticles(self.position,None,self.player.angle-60)

			new_explosion = Explosion(self.position,200,5,self.angle)

			sounds.play_sound(sounds.explosion_sound)
			world.add_objects([new_blood1,new_blood2,new_blood3,new_blood4,new_explosion])	

		if self.caliber == Ammo_type.bullets:
			new_blood = BloodParticles(self.position,None,self.player.angle)
			sounds.play_sound(sounds.ak47_sound)
			world.add_objects([new_blood])

		if self.caliber == Ammo_type.cal50:
			new_sparks = SparkParticles(self.position,None,self.player.angle)
			new_blood1 = BloodParticles(self.position,None,self.player.angle+20)
			new_blood2 = BloodParticles(self.position,None,self.player.angle+20)
			sounds.play_sound(sounds.cal50_sound)
			world.add_objects([new_sparks,new_blood1,new_blood2])	

		world.remove_objects([self])
	

	def draw(self):

		rl.draw_circle_v(self.position,self.caliber_size[self.caliber],self.color)


	def update(self):

		if self.lifetime > 0:

			self.move_bullet()
			self.draw()
			self.lifetime -= 1	
		else:
			print(f"removed bullet {self.caliber}")
			if self.caliber == Ammo_type.rockets:
				new_explosion = Explosion(self.position,200,5,self.angle)
				world.add_objects([new_explosion])
				sounds.play_sound(sounds.explosion_sound)
			world.remove_objects([self])

#endregion

#region AMMO PICKUP

class Ammo_pup:

	def __init__(self,type: Ammo_type,position):

		self.type = type

		self.open = False

		self.position = rl.Vector2(position.x,position.y)

		self.size_modifier = 1

		self.rects = {Ammo_type.bullets:rl.Rectangle(self.position.x,self.position.y,30*self.size_modifier,50*self.size_modifier),
						Ammo_type.cal50:rl.Rectangle(self.position.x,self.position.y,35*self.size_modifier,50*self.size_modifier),
						Ammo_type.rockets:rl.Rectangle(self.position.x,self.position.y,40*self.size_modifier,80*self.size_modifier)}
		self.colors = {Ammo_type.bullets:rl.Color(100,100,20,255),
						Ammo_type.cal50:rl.Color(80,150,20,255),
						Ammo_type.rockets:rl.Color(80,150,80,255)}
		
		self.rect = self.rects[self.type]

	def draw(self):
		self.rects = {Ammo_type.bullets:rl.Rectangle(self.position.x,self.position.y,30*self.size_modifier,50*self.size_modifier),
						Ammo_type.cal50:rl.Rectangle(self.position.x,self.position.y,35*self.size_modifier,50*self.size_modifier),
						Ammo_type.rockets:rl.Rectangle(self.position.x,self.position.y,40*self.size_modifier,80*self.size_modifier)}
		if self.open:
			self.size_modifier = 0.7
			rl.draw_rectangle_pro(self.rects[self.type],rl.Vector2(0,0),0,rl.Color(100,100,100,100))
		else:	
			rl.draw_rectangle_pro(self.rects[self.type],rl.Vector2(0,0),0,self.colors[self.type])

	def update(self):

		self.draw()

#endregion

#region GUI OBJECTS

class Cursor:

	def __init__(self):

		#self.position = rl.Vector2(position.x,position.y)
		self.size = 5
		self.thic = 3
		self.color1 = rl.Color(100,100,100,255)
		self.color2 = rl.Color(100,100,100,255)
		self.line1_h = [rl.Vector2(0,5),rl.Vector2(0,15)]
		self.line1_v = [rl.Vector2(5,0),rl.Vector2(15,0)]
				
	def draw(self):

		sum = 0

		for t in range(self.thic):
			rl.draw_circle_lines(self.position.x,self.position.y, self.size+sum,self.color1)
			rl.draw_circle_lines(self.position.x,self.position.y, self.size+sum+2,rl.WHITE)
			sum += 2
		
		rl.draw_line_ex(self.position-self.line1_v[0],self.position-self.line1_v[1],self.thic,self.color2)
		rl.draw_line_ex(self.position+self.line1_v[0],self.position+self.line1_v[1],self.thic,self.color2)
		rl.draw_line_ex(self.position-self.line1_h[0],self.position-self.line1_h[1],self.thic,self.color2)
		rl.draw_line_ex(self.position+self.line1_h[0],self.position+self.line1_h[1],self.thic,self.color2)


	def update(self): 

		self.position = rl.get_mouse_position()
		self.draw()


class HUD:

	def __init__(self,player):

		self.player = player
		self.ammo_gray = rl.Rectangle(0,0,520,170)
		self.ruler1_h = rl.Rectangle(0,0,SCREEN_WIDTH,50)
		self.ruler1_v = rl.Rectangle(0,0,50,SCREEN_HEIGHT)

		self.shadow1 = rl.Rectangle(520,50,SCREEN_WIDTH-170,10)
		self.shadow2 = rl.Rectangle(50,170,520-50,10)

		self.ruler_light_h = rl.Rectangle(0,0,SCREEN_WIDTH,20)
		self.ruler1_light_v = rl.Rectangle(0,0,20,SCREEN_HEIGHT)
		self.ammo_lightgray = rl.Rectangle(0,0,500,150)

		self.background_hud = [self.ruler1_h,self.ruler1_v,self.ammo_gray]
		self.shadow_hud = [self.shadow1,self.shadow2]
		self.foreground_hud = [self.ruler_light_h,self.ruler1_light_v,self.ammo_lightgray]

		self.weapon_box = {Ammo_type.bullets:rl.Rectangle(158,41,310,33), 
							Ammo_type.cal50:rl.Rectangle(158,72,310,33),
								Ammo_type.rockets:rl.Rectangle(158,102,270,33)}

		self.cursor = Cursor()

	def draw_background_hud(self):

		for shadow in self.shadow_hud:
			rl.draw_rectangle_rec(shadow,rl.DARKGRAY)	

		for background in self.background_hud:
			rl.draw_rectangle_rec(background,rl.GRAY)

		for foreground in self.foreground_hud:
			rl.draw_rectangle_rec(foreground,rl.LIGHTGRAY)

	def draw_hud(self):

		
		rl.draw_rectangle_lines_ex(self.weapon_box[self.player.weapon_selector], 3, rl.Color(50,250,0,200)) 
		rl.draw_text_pro(font_main,f"AMMO:",rl.Vector2(50,35),rl.Vector2(0,0),40,30,2,rl.Color(55,55,55,200))
	
		rl.draw_text_ex(font_main,
						f"AK47 BULLETS   : {self.player.ammo[Ammo_type.bullets]} ",
						rl.Vector2(160,45),
						30,
						1,
						rl.Color(55,55,55,200))

		rl.draw_text_ex(font_main,
						f"CAL 50 BULLETS : {self.player.ammo[Ammo_type.cal50]} ",
						rl.Vector2(160,75),
						30,
						1,
						rl.Color(150,150,0,200))

		rl.draw_text_ex(font_main,
						f"ROCKETS        : {self.player.ammo[Ammo_type.rockets]} ",
						rl.Vector2(160,105),
						30,
						1,
						rl.Color(200,0,0,200))

	
	def update(self):

		self.draw_background_hud()
		self.draw_hud()
		self.cursor.update()
		rl.draw_fps(5,5)

#endregion

#region VFX

class MessagePickup:
	global world
	def __init__(self,text,position):

		self.text = text
		self.position = rl.Vector2(position.x,position.y)
		self.color = rl.Color(10,100,10,255)
		self.active = True

	def fade(self):

		if self.color.a > 1:
			self.color.a -= 2
			self.position.y -= 40 *world.global_delta
		else:
			world.remove_objects([self])

	def draw(self):

		rl.draw_text(self.text,self.position.x,self.position.y,20,self.color)
		

	def update(self):
		
		self.fade()
		self.draw()


class DamageMessage(MessagePickup):
	global world
	def __init__(self,text,init_position):

		super().__init__(text,init_position)
		self.color = rl.Color(200,10,10,255)


class Explosion(TimerDecals):
	global world
	def __init__(self,position: rl.Vector2,size: int,power: int,angle):
		
		self.position = rl.Vector2(position.x,position.y)
		self.angle = angle
		self.size = size
		self.color = rl.Color(200,200,0,30)
		self.power = power
		self.explosion = True
		self.timer = 100
		self.deactivate = self.timer - 1

		new_explosion_stain = Explosionstain(self.position)
		world.add_background_decals([new_explosion_stain])

	def update(self):

		self.draw()

		self._timer()
		if self.timer > 0:
			self.timer -= 1

		if self.timer == self.deactivate:
			self.explosion = False
			

	def draw(self):

		rl.draw_circle_v(self.position,self.size,self.color)

	def terminate_explosion(self):

		world.remove_objects([self])


#region PARTICLES

class ParticleEmitter:
	global world
	def __init__(self,init_position,color,original_angle):


		self.position = rl.Vector2(init_position.x, init_position.y)
		self.color = None
		self.type = None
		self.emitters_amount = 0
		self.angle_offset = 0


		self.amount_ranges = {"blood": (5,10),
							"sparks":(1,5),
							"explosion":(1,3)}

		self.size_ranges = {"blood": (2,8),
							"sparks":(2,3),
							"explosion":(10,20)}
		
		self.color_ranges = {"blood": [RED_1,RED_2,RED_3, RED_4],
							"sparks":[rl.MAGENTA,rl.YELLOW],
							"explosion":[ORANGE_1,ORANGE_2,GRAY_1,GRAY_2]}

		self.life_ranges = {"blood": [5,15],
							"sparks":[5,10],
							"explosion": [10,15]}

		self.speed_ranges = {"blood": [5,15],
							"sparks":[10,20],
							"explosion": [5,10]}

		self.timer = 1
		self.timer_init = self.timer

		self.main_angle = (original_angle +180) % 360 #INVERTING THE ORIGINAL ANGLE WITH MODIUULOOO

	def _timer(self):

		if self.timer < 0:
			self.create_particles()
			world.remove_objects([self])
			
		else:	
			self.timer -= 1


	def create_particles(self):

		angle_add = 0
		
		for number in range(self.emitters_amount):
			
			new_particle = Particle(self.position,
									self.size_ranges[self.type],
									self.color_ranges[self.type],
									self.main_angle+angle_add,
									self.speed_ranges[self.type],
									self.life_ranges[self.type])

			world.add_objects([new_particle])

			angle_add += self.angle_offset


	def update(self):

		self._timer()
		self.draw()
		

	def draw(self):

		rl.draw_circle_lines_v(self.position,50,rl.Color(200,200,0,100))
		rl.draw_text(str(self.life),self.position.x,self.position.y,20,rl.BLACK)

class Particle:
	global world
	def __init__(self,init_pos,size,color,angle,speed,life):

		self.position = rl.Vector2(init_pos.x,init_pos.y)
		self.radius = randrange(size[0],size[1])
		self.color = choice(color)
		
		self.angle = angle
		self.speed = randrange(speed[0],speed[1])
		self.life = randrange(life[0],life[1])
		self.color.a = self.life
		self.movement = rl.Vector2(math.cos(radians(self.angle)),math.sin(radians(self.angle)))
		

	def draw(self):

		rl.draw_circle_v(self.position,self.radius,self.color)


	def update(self):

		if self.life > 0:
			
			self.color.a -= 1 
			self.position += self.movement * self.speed
			self.draw()
			self.life -= 1

		else:
			world.remove_objects([self])


class ExplosionParticles(ParticleEmitter):

	def __init__(self, init_position, color, original_angle):
		super().__init__(init_position, color, original_angle)

		self.emitters_amount = 16 
		self.angle_offset = 360/self.emitters_amount
		self.type = "explosion"
		self.life = randrange(self.life_ranges[self.type][0],
								self.life_ranges[self.type][1])

		self.timer = 20

		self.create_particles()


class BloodParticles(ParticleEmitter):

	def __init__(self, init_position, color, original_angle):
		super().__init__(init_position, color, original_angle)

		self.emitters_amount = 5
		self.angle_offset = 30/self.emitters_amount
		self.type = "blood"
		self.life = randrange(self.life_ranges[self.type][0],
								self.life_ranges[self.type][1])

		self.timer = 5

		self.create_particles()


class SparkParticles(ParticleEmitter):

	def __init__(self, init_position, color, original_angle):
		super().__init__(init_position, color, original_angle)

		self.emitters_amount = 3
		self.angle_offset = 15/3
		self.type = "sparks"
		self.life = randrange(self.life_ranges[self.type][0],
								self.life_ranges[self.type][1])

		self.timer = 3

		self.create_particles()

#endregion

# region DECALS	

class Bloodstain(TimerDecals):

	def __init__(self,position,size,gibs: bool,skin_color):

		self.position = rl.Vector2(position.x,position.y)
		
		self.size_h = uniform(size * 1.0,size* 1.4)
		self.size_w = uniform(size * 1.1,size* 1.8) 
		self.max_size_h = self.size_h *2.0
		self.max_size_w = self.size_w * 2.0
		self.grow_speed = uniform(0.05,0.3)
		self.color = rl.Color(150,0,0,180)
		self.shadow_color = rl.Color(120,0,0,self.color.a)
		self.shine_color = rl.Color(180,0,0,self.color.a)

		self.gibs = gibs
		self.skin_color = rl.Color(skin_color.r,skin_color.g,skin_color.b,skin_color.a)

		#FOR DROPS:

		self.drop_amount = randrange(10,35)
		self.drop_list = []
		self.gib_list = []

		if not self.gibs:
			self.generate_drops(self.drop_amount)
		else:
			self.generate_drops(self.drop_amount+50)
			self.generate_gibs(self.drop_amount)


	def grow_bloodstain(self):


		self.size_h += self.grow_speed
		self.size_w += self.grow_speed
		
		if self.size_h >= self.max_size_h:
			self.size_h = self.max_size_h
		if self.size_w >= self.max_size_w:
			self.size_w = self.max_size_w

	def generate_drops(self,amount):

		for number in range(amount):

			new_size = randrange(3,12)
			new_angle = radians(randrange(1,360))
			new_vector = rl.Vector2(math.cos(new_angle),math.sin(new_angle))
			new_distance = new_vector  * uniform(self.size_w-5,self.max_size_w+20)
			new_color = choice([self.color,self.shine_color,self.shadow_color])
			
			new_drop = [new_size,new_distance,new_color]
			self.drop_list.append(new_drop)

	def generate_gibs(self,amount):

		for number in range(amount):  #GENERAR GIBS
			new_size = randrange(5,10)
			new_angle = radians(randrange(1,360))
			new_vector = rl.Vector2(math.cos(new_angle),math.sin(new_angle))
			new_distance = new_vector  * uniform(self.size_w-5,self.max_size_w+20)
			
			new_gib = [new_size,new_distance,self.skin_color]
			
			self.gib_list.append(new_gib)

		for number in range(amount-5): #GENERAR TRIPAS
			new_size = randrange(2,8)
			new_angle = radians(randrange(1,360))
			new_vector = rl.Vector2(math.cos(new_angle),math.sin(new_angle))
			new_distance = new_vector  * uniform(self.size_w-5,self.max_size_w+5)
			
			new_gib = [new_size,new_distance,rl.Color(200,150,155,255)]
			
			self.gib_list.append(new_gib)			

	def draw_drops(self):

		for drop in self.drop_list:
		
			rl.draw_circle_v(self.position+drop[1],
							drop[0],
							drop[2]
							)

	def draw_gibs(self):

		if self.gibs:
			for gib in self.gib_list:

				rl.draw_circle_v(self.position+gib[1],
								gib[0],
								gib[2]
								)
		else:
			pass


	def draw(self):

		self.shadow_color = rl.Color(120,0,0,self.color.a)
		self.shine_color = rl.Color(180,0,0,self.color.a)
		
		rl.draw_ellipse(self.position.x-10,self.position.y+5,self.size_h,self.size_w,self.shine_color)
		rl.draw_ellipse(self.position.x+10,self.position.y-5,self.size_h,self.size_w,self.shadow_color)
		rl.draw_ellipse(self.position.x,self.position.y,self.size_h,self.size_w,self.color)

		self.draw_drops()
		self.draw_gibs()

	def update(self):

		self.grow_bloodstain()
		self.draw()


class Explosionstain(TimerDecals):

	def __init__(self,position):

		self.position = rl.Vector2(position.x,position.y)
		self.color = rl.Color(20,10,0,50)
		self.size_multiplier = uniform(1.2,2.5)
		self.radiuses =[20,
						25,
						30,
						35,
						40,
						45,
						50]


	def draw(self):

		for radius in self.radiuses:

			rl.draw_circle(self.position.x,
							self.position.y,
							radius*self.size_multiplier,
							self.color)

	def update(self):

		self._timer()
		self.draw()

#endregion

#region INIT GAME

player1 = Player(rl.Vector2(200,300),0,rl.GREEN)

world.add_objects([player1])

game_gui  = HUD(player1)
world.add_hud(game_gui)
ammo_gen = AmmoGenerator(10,8,5)
enemy_gen = EnemyGenerator(10,5,2,0)

ammo_gen.generate(Ammo_type.bullets)
ammo_gen.generate(Ammo_type.cal50)
ammo_gen.generate(Ammo_type.rockets)

enemy_gen.generate(Enemy_type.small)
enemy_gen.generate(Enemy_type.medium)
enemy_gen.generate(Enemy_type.big)

#endregion

#region GAMELOOP

while not rl.window_should_close():

	rl.begin_drawing()
	rl.clear_background(rl.RAYWHITE)

	world.world_update()
	
	rl.end_drawing()

# Cerrar ventana y liberar recursos
rl.close_window()

#endregion