import raylibpy as rl
import math 
from math import radians
from enum import Enum

#CAMBIO DE PRUEBA
#Cambio de prueba 2
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
			object.update(self.object_list)



class Player:
	
	def __init__(self, init_position: rl.Vector2, init_angle: float, init_color,world) -> None:
          
		self.position: rl.Vector2 = init_position
		self.angle: float = init_angle
		self.size: int = 30
		self.movement: rl.Vector2 = rl.Vector2(0,0)
		self.color = init_color
		self.speed = 5
		self.original_speed = self.speed
		self.frict = 0.1
		self.max_speed = 10
		self.rotation_speed = 3
		self.weapons = [Ammo_type.bullets,Ammo_type.cal50,Ammo_type.rockets]
		self.world = world

		self.ammo = {Ammo_type.bullets:100,Ammo_type.cal50:50,Ammo_type.rockets:5}
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

	def speed_friction(self):

		if self.speed > 0:
			self.speed -= self.frict

		if self.speed < 0:
			self.speed = 0

	

	def input(self):


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



		#NORMALIZAR MANUALMENTE PORQUE NO HAY UNA FUNCION DE MIERDA 
		magnitude = math.sqrt(self.movement.x ** 2 + self.movement.y ** 2)
		if magnitude != 0:
			
			self.movement = rl.Vector2((self.movement.x/magnitude),(self.movement.y/magnitude))
	
		#SI NO HAY TECLA DE ADELANTE O ATRAS, APLICAR FRICCION


		#CONVERTIR A ENTERO PARA EVITAR EL JITTERNESS
		self.movement.x,self.movement.y = round(self.movement.x,2),round(self.movement.y,2)
		

		#REGRESAR EL MOVEMENT MULTIPLICADO POR LA VELOCIDAD REAL
		
		return self.movement * self.speed

	def collision_ammo(self,group):

		

		for object in group:
			if hasattr(object,"rect"):
				if rl.check_collision_circle_rec(self.position,self.size,object.rect):
					if not object.open:
						self.receive_ammo(self.ammo_per_type[object.type])
						object.open = True
						new_message = MessagePickup(self.ammo_messages[object.type],object.position)
						self.messages.append(new_message)







	def update_children(self):

		for child in self.children:
			child.update()

	def draw(self):

		rl.draw_circle_v(self.position,self.size,self.color)
		
		

	def update(self,group):
        
		self.speed_friction()
		self.position += self.input()

		self.draw()
		self.update_children()
		self.input_attack()
		self.collision_ammo(group)
		


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

		self.caliber_colors = {Ammo_type.bullets:rl.BLACK,Ammo_type.cal50:rl.GRAY,Ammo_type.rockets:rl.DARKBROWN}
		self.caliber_size = {Ammo_type.bullets: 5,Ammo_type.cal50: 10, Ammo_type.rockets: 25}
		self.caliber_lifetime = {Ammo_type.bullets:100, 
								Ammo_type.cal50:80, 
								Ammo_type.rockets:50} 
		self.lifetime = self.caliber_lifetime[self.caliber]

	def move_bullet(self):

		#ACCELERATE MOVEMENT VECTOR
		self.movement = rl.Vector2(math.cos(self.angle),math.sin(self.angle)) * self.speed
		
		#UPDATE POSITION
		self.position += self.movement 

		#LIMIT TO A MAXIMUM SPEED
		rl.vector2_clamp(self.movement,-global_max_speed,global_max_speed)

	def draw(self):

		rl.draw_circle_v(self.position,self.caliber_size[self.caliber],self.caliber_colors[self.caliber])

	def update(self,group):

		self.move_bullet()
		self.draw()

class GUI:

	def __init__(self,player):

		self.player = player
		self.weapon_box = {Ammo_type.bullets:rl.Rectangle(158,51,250,23), 
							Ammo_type.cal50:rl.Rectangle(158,82,250,23),
								Ammo_type.rockets:rl.Rectangle(158,112,250,23)}
		self.messages = []

	def draw_hud(self):

		rl.draw_rectangle_lines_ex(self.weapon_box[self.player.weapon_selector], 3, rl.Color(50,250,0,200)) 
		rl.draw_text_pro(rl.get_font_default(),f"AMMO:",rl.Vector2(50,35),rl.Vector2(0,0),40,30,2,rl.Color(55,55,55,200))
		rl.draw_text(f"AK47 BULLETS   : {self.player.ammo[Ammo_type.bullets]} ",160,55,20,rl.Color(55,55,55,200))
		rl.draw_text(f"CAL 50 BULLETS : {self.player.ammo[Ammo_type.cal50]} ",160,85,20,rl.Color(150,150,0,200))
		rl.draw_text(f"ROCKETS        : {self.player.ammo[Ammo_type.rockets]} ",160,115,20,rl.Color(200,0,0,200))

	

	
	def update(self):

		self.messages = self.player.messages

		for msg in self.messages:
			if msg.active:
				msg.update()
			else:
				self.player.messages.remove(msg)
				print("killed a text message")

		self.draw_hud()


class MessagePickup:

	def __init__(self,text,init_position):

		self.text = text
		self.position = init_position
		self.color = rl.Color(10,100,10,255)
		self.active = True


	def fade(self):

		if self.color.a > 1:
			print(self.color.a)
			self.color.a -= 2
			self.position.y -= 0.5
		else:
			self.active = False

	def draw(self):

		rl.draw_text(self.text,self.position.x,self.position.y,20,self.color)
		

	def update(self):
		
		self.fade()
		self.draw()





class Ammo_pup:

	def __init__(self,type: Ammo_type,position):

		self.type = type

		self.open = False

		self.position = position

		self.rects = {Ammo_type.bullets:rl.Rectangle(self.position.x,self.position.y,30,50),
						Ammo_type.cal50:rl.Rectangle(self.position.x,self.position.y,35,50),
						Ammo_type.rockets:rl.Rectangle(self.position.x,self.position.y,40,80)}
		self.colors = {Ammo_type.bullets:rl.Color(100,100,20,255),
						Ammo_type.cal50:rl.Color(80,150,20,255),
						Ammo_type.rockets:rl.Color(80,150,80,255)}
		
		self.rect = self.rects[self.type]

	def draw(self):

		if self.open:
			rl.draw_rectangle_pro(self.rects[self.type],rl.Vector2(0,0),0,rl.Color(100,100,100,100))
		else:	
			rl.draw_rectangle_pro(self.rects[self.type],rl.Vector2(0,0),0,self.colors[self.type])

	def update(self,group):

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