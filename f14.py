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
#     __  ___       _         _____                   _____         __
#    /  |/  /___ _ (_)___    / ___/___ _ __ _  ___   / ___/___  ___/ /___
#   / /|_/ // _ `// // _ \  / (_ // _ `//  ' \/ -_) / /__ / _ \/ _  // -_)
#  /_/  /_/ \_,_//_//_//_/  \___/ \_,_//_/_/_/\__/  \___/ \___/\_,_/ \__/
#
#################################################################################

###################################
# SYSTEM IMPORTS
###################################
import procgame.game
from procgame import *
import pinproc
import locale
import os
import logging
from time import strftime
import procgame.dmd
from procgame.dmd import font_named

###################################
# MODE IMPORTS
###################################
from base import *
from attract import *
from utilities import *
from tilt import *
from centerramp import *
from player import *
from ballsaver import *
from bonus import *
from mission import *
from locks import *
#from droptargets import *
#from collectzones import *
#from spinner import *
from multiball import *
from trough import *

# Used to put commas in the score.
locale.setlocale(locale.LC_ALL, "")

################################################
# GLOBAL PATH VARIABLES
################################################
game_machine_type = 'wpc'
curr_file_path = os.path.dirname(os.path.abspath( __file__ ))
settings_path = curr_file_path + "/config/settings.yaml"
game_data_path = curr_file_path + "/config/game_data.yaml"
game_data_template_path = curr_file_path + "/config/game_data_template.yaml"
settings_template_path = curr_file_path + "/config/settings_template.yaml"
game_machine_yaml = curr_file_path + "/config/f14.yaml"
game_music_path = curr_file_path + "/assets/music/"
game_sound_path = curr_file_path + "/assets/sound/"
game_dmd_path = curr_file_path + "/assets/dmd/"
game_lampshows = curr_file_path + "/assets/lamps/"
fnt_path = "/shared/dmd/"

ballsPerGame = 3 # this will eventually be called from the config file


################################################
# GAME CLASS
################################################
class F14SecondSortie(game.BasicGame):
	def __init__(self):
		super(F14SecondSortie, self).__init__(pinproc.MachineTypeWPC95)
		self.load_config(game_machine_yaml)

                self.tomcatTargetIndex = (["lowerLeftT","lowerLeftO","lowerLeftM","upperLeftT","upperLeftO","upperLeftM",
                                        "upperRightC","upperRightA","upperRightT","lowerRightC","lowerRightA","lowerRightT"])

                
        	self.logging_enabled = True
		self.balls_per_game = ballsPerGame

                ### Set Logging Info ###
		logging.basicConfig(filename='f14.txt',level=logging.INFO)

		#### Settings and Game Data ####
		self.load_settings(settings_template_path, settings_path)
		self.load_game_data(game_data_template_path, game_data_path)

		#update audit data on boot up time
		self.game_data['Time Stamps']['Last Boot-Up'] =str(strftime("%d %b %Y %H:%M"))
		if self.game_data['Time Stamps']['First Boot-Up']=='Not Set':
			self.game_data['Time Stamps']['First Boot-Up'] = self.game_data['Time Stamps']['Last Boot-Up']
		self.save_game_data()

                self.reset()

                #### Setup Sound Controller ####
		self.sound = sound.SoundController(self)
		self.RegisterSound()

                #### Pre-load animations
                self.RegisterAnimations()

		#### Setup Lamp Controller ####
		self.lampctrl = procgame.lamps.LampController(self)
		self.lampctrlflash = procgame.lamps.LampController(self)
		self.RegisterLampshows()

		#### software version number ####
		self.revision = "2.0.0"

		#### Mode Definitions ####
		self.utilities = UtilitiesMode(self,100)
		self.trough = Trough(self,0)
		self.base_mode = BaseGameMode(self,0)
		self.attract_mode = AttractMode(self,1)
                self.mission = MissionMode(self,2)
                self.locks = LocksMode(self,50)
                self.kill1mission = Kill1Mode(self,3)
		#self.centerramp_mode = CenterRampMode(self,8)
		#self.drops_mode = DropTargets(self,9)
		#self.collect_mode = CollectZones(self,10)
		#self.spinner_mode = Spinner(self,11)
		#self.skillshot_mode = SkillshotMode(self,100)
		self.ballsaver_mode = BallSaver(self,1)
		#self.tilt = Tilt(self,200)
		self.bonus_mode = Bonus(self,1000)
		self.multiball_mode = Multiball(self,101)

		#### Initial Mode Queue ####
		self.modes.add(self.utilities)
		self.modes.add(self.trough)
		self.modes.add(self.base_mode)
                self.modes.add(self.mission)
                self.modes.add(self.locks)

                #self.reset()

	def reset(self):
		super(F14SecondSortie, self).reset()
                
		self.ball = 0
		self.old_players = []
		self.old_players = self.players[:]
		self.players = []
		self.current_player_index = 0

                self.shooter_lane_status = 0
		self.tiltStatus = 0

		#setup high scores
		self.highscore_categories = []

		#### Classic High Score Data ####
		cat = highscore.HighScoreCategory()
		cat.game_data_key = 'ClassicHighScoreData'
		self.highscore_categories.append(cat)

		#### Mileage Champ ####
		cat = highscore.HighScoreCategory()
		cat.game_data_key = 'BonusLoops'
		self.highscore_categories.append(cat)

		for category in self.highscore_categories:
			category.load_from_game(self)

		
	def save_settings(self):
			super(F14SecondSortie, self).save_settings(settings_path)

	def save_game_data(self):
			super(F14SecondSortie, self).save_game_data(game_data_path)

	def RegisterSound(self):
		# Sound Settings:
		#self.sound.music_volume_offset = 10 #This will be hardcoded at 10 since I have external volume controls I will be using
		# Music Registration
		self.sound.register_sound('startup', game_sound_path+"Jet_F14_TakeOff.wav")
                self.sound.register_sound('inbound', game_sound_path+"inbound.wav")
                self.sound.register_sound('slinglow', game_sound_path+"slinglow.wav")
                self.sound.register_sound('tomcat', game_sound_path+"tomcat.wav")
                self.sound.register_sound('launch', game_sound_path+"launch.wav")
                self.sound.register_sound('launchspeech', game_sound_path+"missiles launched speech.wav")
                self.sound.register_sound('alarm', game_sound_path+"alarm.wav")
                self.sound.register_sound('explode1', game_sound_path+"explode1.wav")
                self.sound.register_sound('explode2', game_sound_path+"explode2.wav")
                self.sound.register_sound('shoot1', game_sound_path+"shoot1.wav")
                self.sound.register_music('dangerzone',game_music_path+"Kenny Loggins - Danger Zone.mp3")
                self.sound.register_music('shooterlane',game_music_path+"Tomcat shooter.mp3")
                self.sound.register_music('tomcatmain',game_music_path+"Tomcat main.mp3")
                self.sound.register_sound('spinner', game_sound_path+"spinner.wav")
                self.sound.register_sound('machine_gun_short', game_sound_path+"machine_gun_short.wav")
                self.sound.register_sound('machine_gun_long', game_sound_path+"machine_gun_long.wav")
		
		self.sound.set_volume(10)

	def RegisterLampshows(self):
		self.lampctrl.register_show('f14fireboth', game_lampshows + 'f14fireboth.lampshow')
		#self.lampctrl.register_show('center_ramp_1', game_lampshows + 'center_ramp_complete.lampshow')
		#self.lampctrlflash.register_show('bonus_total', game_lampshows + 'bonus_total.lampshow')

        def RegisterAnimations(self):

                # Scrolling 3D text when a mode is lit
                self.dmd_assets={}

                self.dmd_assets['alpha_available'] = dmd.Animation().load(game_dmd_path +'alpha_available.dmd')
                self.dmd_assets['bravo_available'] = dmd.Animation().load(game_dmd_path +'bravo_available.dmd')
                self.dmd_assets['charlie_available'] = dmd.Animation().load(game_dmd_path +'charlie_available.dmd')
                self.dmd_assets['delta_available'] = dmd.Animation().load(game_dmd_path +'delta_available.dmd')
                self.dmd_assets['echo_available'] = dmd.Animation().load(game_dmd_path +'echo_available.dmd')
                self.dmd_assets['fox_available'] = dmd.Animation().load(game_dmd_path +'fox_available.dmd')
                self.dmd_assets['golf_available'] = dmd.Animation().load(game_dmd_path +'golf_available.dmd')

                # Spinning mission text, displayed when mission active
                self.dmd_assets['alpha_spin'] = dmd.Animation().load(game_dmd_path +'alpha_rotate.dmd')
                self.dmd_assets['bravo_spin'] = dmd.Animation().load(game_dmd_path +'bravo_rotate.dmd')
                self.dmd_assets['charlie_spin'] = dmd.Animation().load(game_dmd_path +'charlie_rotate.dmd')
                self.dmd_assets['delta_spin'] = dmd.Animation().load(game_dmd_path +'delta_rotate.dmd')
                self.dmd_assets['echo_spin'] = dmd.Animation().load(game_dmd_path +'echo_rotate.dmd')
                self.dmd_assets['fox_spin'] = dmd.Animation().load(game_dmd_path +'fox_rotate.dmd')
                self.dmd_assets['golf_spin'] = dmd.Animation().load(game_dmd_path +'golf_rotate.dmd')

                # Bonus multiplier awarded
                self.dmd_assets['bonus2x'] = dmd.Animation().load(game_dmd_path +'bonus2x.dmd')
                self.dmd_assets['bonus3x'] = dmd.Animation().load(game_dmd_path +'bonus3x.dmd')
                self.dmd_assets['bonus4x'] = dmd.Animation().load(game_dmd_path +'bonus4x.dmd')
                self.dmd_assets['bonus5x'] = dmd.Animation().load(game_dmd_path +'bonus5x.dmd')
                self.dmd_assets['bonus6x'] = dmd.Animation().load(game_dmd_path +'bonus6x.dmd')
                self.dmd_assets['bonus7x'] = dmd.Animation().load(game_dmd_path +'bonus7x.dmd')
                self.dmd_assets['bonus8x'] = dmd.Animation().load(game_dmd_path +'bonus8x.dmd')
                self.dmd_assets['ball_saved'] = dmd.Animation().load(game_dmd_path +'ball_saved.dmd')

                # Various spinning jets
                self.dmd_assets['f14_roll1'] = dmd.Animation().load(game_dmd_path +'f14_roll1.dmd')
                self.dmd_assets['f14_roll2'] = dmd.Animation().load(game_dmd_path +'f14_roll2.dmd')
                self.dmd_assets['f14_roll3'] = dmd.Animation().load(game_dmd_path +'f14_roll3.dmd')
                self.dmd_assets['f14_roll4'] = dmd.Animation().load(game_dmd_path +'f14_roll4.dmd')
                self.dmd_assets['f14_roll5'] = dmd.Animation().load(game_dmd_path +'f14_roll5.dmd')
                self.dmd_assets['f14_roll6'] = dmd.Animation().load(game_dmd_path +'f14_roll6.dmd')
                self.dmd_assets['f14_roll7'] = dmd.Animation().load(game_dmd_path +'f14_roll7.dmd')
                self.dmd_assets['f14_roll8'] = dmd.Animation().load(game_dmd_path +'f14_roll8.dmd')
                self.dmd_assets['f14_roll9'] = dmd.Animation().load(game_dmd_path +'f14_roll9.dmd')

                self.dmd_assets['second_sortie_rotate'] = dmd.Animation().load(game_dmd_path +'second_sortie_rotate.dmd')

                

	def create_player(self, name):
		return Player(name)

def main():
    game = None
    log = logging.getLogger('f14.main')
    try:
        game = F14SecondSortie()
        game.run_loop()
        game.reset()
    finally:
        del game

if __name__ == '__main__':
	main()
