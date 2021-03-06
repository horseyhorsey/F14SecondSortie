#####################################################################################
##     ____   _______   _________________  _  _____    ________  ___  ______________
##    / __/__<  / / /  / __/ __/ ___/ __ \/ |/ / _ \  / __/ __ \/ _ \/_  __/  _/ __/
##   / _//___/ /_  _/ _\ \/ _// /__/ /_/ /    / // / _\ \/ /_/ / , _/ / / _/ // _/
##  /_/     /_/ /_/  /___/___/\___/\____/_/|_/____/ /___/\____/_/|_| /_/ /___/___/
##
## A P-ROC Project by Mark Sunnucks
## Built on PyProcGame from Adam Preble and Gerry Stellenberg
## Thanks to Scott Danesi for inspiration from his Earthshaker Aftershock
#####################################################################################


#################################################################################
#     ___
#    / _ ) ___   ___  __ __ ___
#   / _  |/ _ \ / _ \/ // /(_-<
#  /____/ \___//_//_/\_,_//___/
#
#################################################################################

import procgame
from procgame import *
import locale
import logging
import procgame.dmd
from procgame.dmd import font_named

class Bonus(game.Mode):
	"""docstring for Bonus"""
	def __init__(self, game, priority):
			super(Bonus, self).__init__(game, priority)
			# Settings Variables #
			self.delay_time = 2
			self.bonus_value = 1000

			# System Variables #
			self.total_value = 0

                        self.log = logging.getLogger('f14.bonus')
                        anim = dmd.Animation().load("/P-ROC/games/F14SecondSortie/assets/dmd/bonus_spin.dmd")
                        self.first_layer = dmd.AnimatedLayer(frames=anim.frames, hold=False, repeat=True, frame_time=4)




	def mode_started(self):

		# Disable the flippers
		self.game.coils.flipperEnable.disable()
		#self.game.sound.stop_music()
                self.game.sound.fadeout_music(time_ms=1000)
		#self.game.utilities.disableGI()

		self.game.utilities.disableAllLamps(include_GI=False)

	def mode_stopped(self):
		# Enable the flippers
		self.game.coils.flipperEnable.enable() # Can possibly remove this and let the "Ball Start" function handle it.
		self.game.utilities.enableGI()

	def calculate(self,callback):
		self.callback = callback
		self.total_value = self.game.utilities.get_player_stats('bonus') * self.bonus_value * self.game.utilities.get_player_stats('bonus_x')
		self.bonus()

	def bonus(self):
		self.log.info('Initial Bonus')
                self.second_layer = dmd.TextLayer(26, 14, font_named("Font_CC_5px_az.dmd")).set_text("BONUS        "+str(self.game.utilities.get_player_stats('bonus') * self.bonus_value))
                self.second_layer.composite_op = 'blacksrc'

                self.layer = dmd.GroupedLayer(128, 32, [self.first_layer,self.second_layer])
                self.game.utilities.acFlashSchedule(coilname='upKicker_flasher3',schedule=0x0000000C, cycle_seconds=1, now=True)
		self.delay(name='next_frame', event_type=None, delay=self.delay_time, handler=self.multiplier)

	def multiplier(self):
                self.log.info('Multiplier')
                self.third_layer = dmd.TextLayer(26, 20, font_named("Font_CC_5px_az.dmd")).set_text("MULTIPLIER   X"+str(self.game.utilities.get_player_stats('bonus_x')))
                self.third_layer.composite_op = 'blacksrc'
                self.layer = dmd.GroupedLayer(128, 32, [self.first_layer,self.second_layer,self.third_layer])
                self.delay(name='next_frame', event_type=None, delay=self.delay_time, handler=self.total)

	def total(self):
                self.log.info('Total')
                self.fourth_layer = dmd.TextLayer(26, 26, font_named("Font_CC_5px_az.dmd")).set_text("TOTAL         "+str(self.total_value))
                self.fourth_layer.composite_op = 'blacksrc'
                
                self.layer = dmd.GroupedLayer(128, 32, [self.first_layer,self.second_layer,self.third_layer,self.fourth_layer])
		self.game.utilities.score(self.total_value) # this should upadte the player score in question
		self.delay(name='next_frame', event_type=None, delay=self.delay_time, handler=self.finish)		

	def finish(self):
		self.game.sound.stop_music()
		self.callback()
		