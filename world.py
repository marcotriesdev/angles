class World:

	def __init__(self,debug):

		self.debug : bool = debug
		self.object_list = []
		self.decal_list = []

	def add_objects(self,objects: list)->None:

		for object in objects:
			#print(f"added {object}")
			self.object_list.append(object)

	def add_decals(self,decals: list) -> None:

		for decal in decals:
			#print(f"added {decal}")
			self.decal_list.append(decal)

	def remove_objects(self,objects: list)->None:

		for object in objects:
			#print(f"removed {object}")
			self.object_list.remove(object)

	def world_update(self): #IMPORTANTE EN EL ORDEN DEL DIBUJADO
		
		if self.decal_list:
			for decal in self.decal_list:
				decal.update()

		if self.object_list:
			for object in self.object_list:
				object.update()
				if hasattr(object,"debug") and self.debug:
					object.debug()
