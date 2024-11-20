import raylibpy as rl

class SoundManager:

	def __init__(self):

		rl.init_audio_device()
		rl.set_master_volume(0.5)
		self.explosion_sound = rl.load_sound("audio/boom.ogg")
		self.cal50_sound = rl.load_sound("audio/cal50.ogg")
		self.ak47_sound = rl.load_sound("audio/ak47.ogg")
		
	def play_sound(self,sound):

		rl.play_sound(sound)