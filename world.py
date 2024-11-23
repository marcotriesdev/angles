import raylibpy as rl

class World:

	def __init__(self,debug,cursor):

		self.debug : bool = debug
		self.object_list = []
		self.decal_list = []
		self.background_decals = []
		self.hud_list = []
		self.cursor = cursor
		self.global_delta = rl.get_frame_time()

		if self.cursor:
			rl.hide_cursor()

	def add_objects(self,objects: list)->None:

		for object in objects:
			#print(f"added {object}")
			self.object_list.append(object)

	def add_decals(self,decals: list) -> None:

		for decal in decals:
			#print(f"added {decal}")
			self.decal_list.append(decal)

	def add_background_decals(self,bdecals) -> None:

		for decal in bdecals:
			self.background_decals.append(decal)

	def add_hud(self,hud):

		self.hud_list.append(hud)

	def remove_objects(self,objects: list)->None:

		for object in objects:
			#print(f"removed {object}")
			self.object_list.remove(object)

	def remove_decals(self,decal):

		self.decal_list.remove(decal)

	def remove_background(self,background):

		self.background_decals.remove(background)

	def world_update(self): #IMPORTANTE EN EL ORDEN DEL DIBUJADO

		self.global_delta = rl.get_frame_time()
		
		if self.background_decals:
			for decal in self.background_decals:
				decal.update()

		if self.decal_list:
			for decal in self.decal_list:
				decal.update()

		if self.object_list:
			for object in self.object_list:
				object.update()
				if hasattr(object,"debug") and self.debug:
					object.debug()

		if self.object_list:

			for hud in self.hud_list:
				hud.update()
