from enum import Enum

class Ammo_type(Enum):
	
	bullets = 1
	cal50 = 2
	rockets = 3

class Enemy_type(Enum):

	small = 1
	medium = 2
	big = 3
	boss = 4

class Enemy_state(Enum):

	idle = 1
	chasing = 2
	attack = 3
	dead = 4
	gib = 5

