import raylibpy as rl
import math 
from enum import Enum

# Inicialización de la ventana
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 800

global_max_speed = rl.Vector2(100,100)

class Ammo_type(Enum):
	
	bullets = 1
	cal50 = 2
	rockets = 3


rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Ejemplo de Boilerplate con raylibpy")
rl.set_target_fps(60)

class World:

	def __init__(self,init_objects):

		self.object_list = init_objects

	def add_objects(self,objects: list)->None:

		for object in objects:
			self.object_list.append(object)

	def world_update(self):

		for object in self.object_list:
			object.update()



class Player:
	
	def __init__(self, init_position: rl.Vector2, init_angle: float, init_color,world) -> None:
          
		self.position: rl.Vector2 = init_position
		self.angle: float = init_angle
		self.size: int = 30
		self.movement: rl.Vector2 = rl.Vector2(0,0)
		self.color = init_color
		self.speed = 5
		self.frict = 1
		self.max_speed = 10
		self.rotation_speed = 3
		self.weapons = [5,10,25]
		self.world = world

		self.ammo = {5:100,10:50,25:5}

		self.weapon_selector = self.weapons[0]

		self.children = []

		self.create_lines()
		
	def replenish_ammo(self):

		pass

	def receive_ammo(self,cal5,cal10,cal25):

		self.ammo[5] += cal5
		self.ammo[10] += cal10
		self.ammo[25] += cal25


	def create_lines(self):

		self.line1 = Linesofplayer(self,self.angle,0,rl.RED)
		self.line2 = Linesofplayer(self,self.angle,8,rl.RED)
		self.line3 = Linesofplayer(self,self.angle,16,rl.RED)
		self.line4 = Linesofplayer(self,self.angle,24,rl.RED)
		self.line5 = Linesofplayer(self,self.angle,360-8,rl.RED)
		self.line6 = Linesofplayer(self,self.angle,360-16,rl.RED)
		self.line7 = Linesofplayer(self,self.angle,360-24,rl.RED)

		self.children.append(self.line1)
		self.children.append(self.line2)
		self.children.append(self.line3)
		self.children.append(self.line4)
		self.children.append(self.line5)
		self.children.append(self.line6)
		self.children.append(self.line7)

	def input_attack(self):

		if rl.is_key_pressed(rl.KEY_ONE):
			self.weapon_selector = self.weapons[0]
		if rl.is_key_pressed(rl.KEY_TWO):
			self.weapon_selector = self.weapons[1]
		if rl.is_key_pressed(rl.KEY_THREE):
			self.weapon_selector = self.weapons[2]	

		if rl.is_key_pressed(rl.KEY_SPACE):
			if self.ammo[self.weapon_selector] > 0:
				new_bullet = Bullet(self.position,self.movement,self,self.weapon_selector)
				self.world.add_objects([new_bullet])
				self.ammo[self.weapon_selector] -= 1

	def input(self):


		
		#YA APRENDI A HACER MOVIMIENTO BASADO EN EL ANGULO
		if rl.is_key_down(rl.KEY_W):
			self.movement += rl.Vector2(math.cos(math.radians(self.angle))*self.speed,math.sin(math.radians(self.angle))*self.speed)
		if rl.is_key_down(rl.KEY_S):
			self.movement -= rl.Vector2(math.cos(math.radians(self.angle))*self.speed,math.sin(math.radians(self.angle))*self.speed)

		

		#CAMBIAR ROTACION CON TECLAS A Y D
		if rl.is_key_down(rl.KEY_A):
			self.angle -= self.rotation_speed
		if rl.is_key_down(rl.KEY_D):
			self.angle += self.rotation_speed

		#FRICCION ASÍ MANUAL
		if self.movement.x < 0:
			self.movement.x = round(self.movement.x+self.frict)
		if self.movement.x > 0:
			self.movement.x = round(self.movement.x-self.frict)

		if self.movement.y < 0:
			self.movement.y = round(self.movement.y+self.frict)
		if self.movement.y > 0:
			self.movement.y = round(self.movement.y-self.frict)

		rl.vector2_normalize(self.movement)
		#ASIGNAR VALOR AL VECTOR MOVEMENT Y CLAMPEARLO A UN LIMITE DE VELOCIDAD
		self.movement = rl.vector2_clamp(self.movement,rl.Vector2(-self.max_speed,-self.max_speed),rl.Vector2(self.max_speed,self.max_speed))
		
		#APROXIMAR DECIMALES PA QUE NO LOKEE
		self.movement = rl.Vector2(round(self.movement.x,2),round(self.movement.y,2))

		return self.movement

	def update_children(self):

		for child in self.children:
			child.update()

	def draw(self):

		rl.draw_circle_v(self.position,self.size,self.color)
		
		

	def update(self):
        
		self.position += self.input()
		self.draw()
		self.update_children()
		self.input_attack()
		


class Linesofplayer:

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

class Bullet:

	def __init__(self,init_position,parent_movement,player,caliber):

		self.player = player

		
		self.movement = parent_movement
		self.angle = math.radians(player.angle)
		self.offset = 10
		self.position = init_position + rl.Vector2(math.cos(self.angle)*self.offset,math.sin(self.angle)*self.offset)
		
		self.speed = 20
		
		self.caliber = caliber

		self.caliber_colors = {5:rl.BLACK,10:rl.GRAY,25:rl.DARKBROWN}
		self.caliber_lifetime = {5:100, 
								10:80, 
								25:50} 
		self.lifetime = self.caliber_lifetime[self.caliber]

	def move_bullet(self):

		#ACCELERATE MOVEMENT VECTOR
		self.movement = rl.Vector2(math.cos(self.angle),math.sin(self.angle)) * self.speed
		
		#UPDATE POSITION
		self.position += self.movement 

		#LIMIT TO A MAXIMUM SPEED
		rl.vector2_clamp(self.movement,-global_max_speed,global_max_speed)

	def draw(self):

		rl.draw_circle_v(self.position,self.caliber,self.caliber_colors[self.caliber])

	def update(self):

		self.move_bullet()
		self.draw()

class GUI:

	def __init__(self,player):

		self.player = player
		self.weapon_box = {5:rl.Rectangle(158,51,250,23), 
							10:rl.Rectangle(158,82,250,23),
								25:rl.Rectangle(158,112,250,23)}

	def draw_hud(self):

		rl.draw_rectangle_lines_ex(self.weapon_box[self.player.weapon_selector], 3, rl.Color(50,250,0,200)) 
		rl.draw_text_pro(rl.get_font_default(),f"AMMO:",rl.Vector2(50,35),rl.Vector2(0,0),40,30,2,rl.Color(55,55,55,200))
		rl.draw_text(f"AK47 BULLETS   : {self.player.ammo[5]} ",160,55,20,rl.Color(55,55,55,200))
		rl.draw_text(f"CAL 50 BULLETS : {self.player.ammo[10]} ",160,85,20,rl.Color(150,150,0,200))
		rl.draw_text(f"ROCKETS        : {self.player.ammo[25]} ",160,115,20,rl.Color(200,0,0,200))

	
	def update(self):

		self.draw_hud()

class Ammo_pup:

	def __init__(self,type: Ammo_type,position):

		self.type = type
		self.position = position

		self.rects = {Ammo_type.bullets:rl.Rectangle(self.position.x,self.position.y,30,50),
						Ammo_type.cal50:rl.Rectangle(self.position.x,self.position.y,35,50),
						Ammo_type.rockets:rl.Rectangle(self.position.x,self.position.y,40,80)}
		self.colors = {Ammo_type.bullets:rl.Color(100,100,20,255),
						Ammo_type.cal50:rl.Color(80,150,20,255),
						Ammo_type.rockets:rl.Color(80,150,80,255)}

	def draw(self):

		rl.draw_rectangle_pro(self.rects[self.type],rl.Vector2(0,0),0,self.colors[self.type])

	def update(self):

		self.draw()


game_world = World([])
player1 = Player(rl.Vector2(200,300),0,rl.GREEN,game_world)

ammo1 = Ammo_pup(Ammo_type.bullets,rl.Vector2(500,500))
ammo2 = Ammo_pup(Ammo_type.cal50,rl.Vector2(580,600))
ammo3 = Ammo_pup(Ammo_type.rockets,rl.Vector2(10,400))


game_world.add_objects([player1,ammo1,ammo2,ammo3])

game_gui  = GUI(player1)



# Bucle principal del juego
while not rl.window_should_close():
	# Lógica de actualización
	# (Aquí va la lógica del juego, como mover personajes o detectar colisiones)

	# Dibujar
	rl.begin_drawing()
	rl.clear_background(rl.RAYWHITE)

	game_world.world_update()
	game_gui.update()

	
	rl.end_drawing()

# Cerrar ventana y liberar recursos
rl.close_window()