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
#     ___   __   __                   __    __  ___         __
#    / _ | / /_ / /_ ____ ___ _ ____ / /_  /  |/  /___  ___/ /___
#   / __ |/ __// __// __// _ `// __// __/ / /|_/ // _ \/ _  // -_)
#  /_/ |_|\__/ \__//_/   \_,_/ \__/ \__/ /_/  /_/ \___/\_,_/ \__/
#
#################################################################################

import procgame.game
from procgame import *
import procgame.dmd
from procgame.dmd import font_named
from procgame.dmd import hdfont_named
import pinproc
import locale
import math
import random
import logging

#### Set Locale ####
locale.setlocale(locale.LC_ALL, "")

class AttractMode(game.Mode):
    def __init__(self, game, priority):
            super(AttractMode, self).__init__(game, priority)
            self.modeTickCounter = 0
            self.attractTest = False
                        #setup logging
            self.log = logging.getLogger('f14.attract')

    def change_lampshow(self):
                
                self.game.lampctrl.stop_show()
                if self.show == 1:
					self.game.lamps.gired.schedule(schedule=0xFFFFFFFF,now=True)
					self.game.lampctrl.play_show('pulse', repeat=True)
					self.game.lamps.radar_rotate_green.enable()
					self.show = 2
                elif self.show == 2:
					self.game.lampctrl.play_show('rotate', repeat=True)
					self.game.lamps.gigreen.schedule(schedule=0xFFFFFFFF,now=True)
					self.show = 3
					self.game.lamps.radar_rotate_red.enable()
                else:
					self.game.lampctrl.play_show('wipeupdown', repeat=True)
					self.game.lamps.giblue.schedule(schedule=0xFFFFFFFF,now=True)
					self.show = 1
					self.game.lamps.radar_blue.schedule(schedule=0xAAAAAA, now=True);

                    
                self.delay(name='lampshow', event_type=None, delay=12, handler=self.change_lampshow)

    def mode_started(self):

        #### Start Attract Mode Lamps ####
                self.log.info("Start Lamps")
        #self.startAttractLamps2()
        #self.game.lampctrl.play_show('pulse', repeat=True)
                self.show = 1
                self.change_lampshow()


        #### Create and Set Display Content ####
                self.log.info("Start Content")
                self.setDisplayContent()

        #### Ensure GI is on ####
                #self.log.info("Enable GI")
        #self.game.utilities.enableGI()
                #self.seg7_1()
                #self.game.utilities.arduino_blank_all()

    def seg7_1(self):
                self.game.utilities.write_arduino('D'+chr(0)+chr(115)+chr(56)+chr(119)+chr(110))
                self.game.utilities.write_arduino('D'+chr(1)+chr(113)+chr(64)+chr(6)+chr(102))
                self.delay(delay=2,handler=self.seg7_2)

    def seg7_2(self):
                self.game.utilities.write_arduino('D'+chr(0)+chr(64)+chr(64)+chr(64)+chr(64))
                self.game.utilities.write_arduino('D'+chr(1)+chr(64)+chr(64)+chr(64)+chr(64))
                self.delay(delay=2,handler=self.seg7_1)





    def mode_stopped(self):
        self.log.info("Stop mode")
        #### Disable All Lamps ####
        #for lamp in self.game.lamps:
    #		lamp.disable()

        self.game.lampctrl.stop_show()
                #self.game.utilities.arduino_blank_all()
                #self.game.utilities.radar_spin_green()

                #self.game.utilities.write_arduino('D'+chr(0)+chr(0)+chr(0)+chr(0)+chr(0))


        #### Enable AC Relay for Flashers ####
        #### This is only needed for using lampshows that contain flashers on the AC Relay ####
        self.game.coils.acSelect.enable()


    def setDisplayContent(self):
        #### Script List Variable Initialization ####
        self.log.info("Gets scores")
        self.player1Score = self.game.game_data['LastGameScores']['LastPlayer1Score']
        self.player2Score = self.game.game_data['LastGameScores']['LastPlayer2Score']
        self.player3Score = self.game.game_data['LastGameScores']['LastPlayer3Score']
        self.player4Score = self.game.game_data['LastGameScores']['LastPlayer4Score']

        self.log.info("Get f14launch")
        #anim = dmd.Animation().load("/P-ROC/games/F14SecondSortie/assets/dmd/f14launch.dmd")
                #self.takeoff_layer = dmd.AnimatedLayer(frames=anim.frames, hold=False, repeat=False, frame_time=5)
        self.takeoff_layer = self.game.animations['credit_background']
        anim2 = dmd.Animation().load("/P-ROC/games/F14SecondSortie/assets/dmd/alpha2.dmd")
        self.first_layer = self.game.animations['second_sortie_rotate']



        self.second_layer = dmd.TextLayer(128/2, 14, font_named("Font_CC_5px_az.dmd"),"center").set_text("SHOOT THE MOVING TARGET")
        self.third_layer = dmd.TextLayer(128/2, 20, font_named("Font09x7.dmd"),"center").set_text("BEFORE FUEL RUNS OUT")
        self.second_layer.composite_op = 'blacksrc'
        self.third_layer.composite_op = 'blacksrc'

        #self.f14_splash_layer = dmd.GroupedLayer(128, 32, [self.first_layer,self.second_layer,self.third_layer])
        self.f14_splash_layer = self.first_layer
        #self.f14_splash_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load('/P-ROC/games/F14SecondSortie/assets/dmd/f14bw2.dmd').frames[0])
        self.f14_sunset_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load('/P-ROC/games/F14SecondSortie/assets/dmd/f14_logo.png').frames[0])
        self.f14_layer = dmd.FrameLayer(opaque=True, frame=dmd.Animation().load('/P-ROC/games/F14SecondSortie/assets/dmd/tomcat20beware.dmd').frames[0])

        self.press_layer = dmd.HDTextLayer(1200/2, 50, hdfont_named("BlackoakStd",30), "center", opaque=True,line_color=(132,132,132), line_width=1, interior_color=(128,255,128)).set_text("PRESS")
        self.start_layer = dmd.HDTextLayer(1200/2, 100, hdfont_named("BlackoakStd",30), "center",line_color=(132,132,132), line_width=1, interior_color=(128,255,128)).set_text("START")
        self.press_layer.composite_op = 'blacksrc'
        self.press_start_layer = dmd.GroupedLayer(1200, 600, [self.press_layer,self.start_layer], opaque=True)

        self.second_layer = dmd.TextLayer(1200/2, 50, hdfont_named("BlackoakStd",30), "center").set_text("SECOND")
        self.sortie_layer = dmd.TextLayer(1200/2, 100, hdfont_named("BlackoakStd",30), "center").set_text("SORTIE")
        self.second_layer.composite_op = 'blacksrc'
        self.second_sortie_layer = dmd.GroupedLayer(1200, 600, [self.second_layer,self.sortie_layer])
                
        gen = dmd.MarkupFrameGenerator(width=1200)
        #gen.font_plain=hdfont_named("Beware",25)
        gen.font_bold=hdfont_named("Beware",120)


        gen.set_plain_font(hdfont_named("BlackoakStd", 45), interior_color=[255,0,0], border_width=1, border_color=[255,255,255])
        gen.set_bold_font(hdfont_named("BlackoakStd", 60), interior_color=[0, 0, 255], border_width=1, border_color=[255,255,255])
        credits_frame = gen.frame_for_markup("""


#F-14 CREDITS#

[Rules + Coding]
[Mark Sunnucks]

[Special thanks]
[G. Stellenberg]
[A. Preble]
[S. v/d Staaij]
[M. Ocean]
[S. Danesi]


""")

        self.credits_layer = dmd.PanningLayer(width=1200, height=600, frame=credits_frame, origin=(0,0), translate=(0,1), bounce=False)
        self.credits_layer.composite_op = 'blacksrc'
        self.credits_overlay_layer = dmd.GroupedLayer(1200, 600, [self.takeoff_layer,self.credits_layer])
        script = [{'seconds':5.0, 'layer':self.second_sortie_layer},
                    {'seconds':5.0, 'layer':self.f14_splash_layer},
                      {'seconds':5.0, 'layer':self.press_start_layer},
                      {'seconds':20.0, 'layer':self.credits_overlay_layer},
                      {'seconds':5.0, 'layer':self.f14_sunset_layer},
                      {'seconds':5.0, 'layer':self.press_start_layer}]

        self.layer = dmd.ScriptedLayer(width=1200, height=600, script=script, opaque=True)

    def startAttractLamps(self):
        ##############################################################
        #### Start Attract Lamps Version 1 ###########################
        #### This basic attract lamp show uses a schedule to cycle
        #### through the lamps in the game.  This surprisingly creates
        #### a nice attract mode for those looking to get something
        #### basic up and running.  It uses a mod function to cycle
        #### through every 4 lamps.
        ##############################################################
        i = 0
        self.log.info("Start Lamps")
        for lamp in self.game.lamps:
            if i % 4 == 3:
                lamp.schedule(schedule=0xf000f000, cycle_seconds=0, now=False)
            elif i % 4 == 2:
                lamp.schedule(schedule=0x0f000f00, cycle_seconds=0, now=False)
            elif i % 4 == 1:
                lamp.schedule(schedule=0x00f000f0, cycle_seconds=0, now=False)
            elif i % 4 == 0:
                lamp.schedule(schedule=0x000f000f, cycle_seconds=0, now=False)
            i = i + 1

    def startAttractLamps2(self):
        ##############################################################
        #### Start Attract Lamps Version 2 ###########################
        #### This basic attract lamp show uses a schedule to cycle
        #### through the lamps in the game.  This surprisingly creates
        #### a nice attract mode for those looking to get something
        #### basic up and running.  It uses a mod function to cycle
        #### through every 8 lamps.
        ##############################################################
        i = 0
        for lamp in self.game.lamps:
            if i % 8 == 7:
                lamp.schedule(schedule=0xf0000000, cycle_seconds=0, now=False)
            elif i % 8 == 6:
                lamp.schedule(schedule=0x0f000000, cycle_seconds=0, now=False)
            elif i % 8 == 5:
                lamp.schedule(schedule=0x00f00000, cycle_seconds=0, now=False)
            elif i % 8 == 4:
                lamp.schedule(schedule=0x000f0000, cycle_seconds=0, now=False)
            elif i % 8 == 3:
                lamp.schedule(schedule=0x0000f000, cycle_seconds=0, now=False)
            elif i % 8 == 2:
                lamp.schedule(schedule=0x00000f00, cycle_seconds=0, now=False)
            elif i % 8 == 1:
                lamp.schedule(schedule=0x000000f0, cycle_seconds=0, now=False)
            elif i % 8 == 0:
                lamp.schedule(schedule=0x0000000f, cycle_seconds=0, now=False)
            i = i + 1

    def startAttractLamps3(self):
        ##############################################################
        #### Start Attract Lamps Version 2 ###########################
        #### This basic attract lamp show uses a schedule to cycle
        #### through the lamps in the game.  This surprisingly creates
        #### a nice attract mode for those looking to get something
        #### basic up and running.  It uses a mod function to cycle
        #### through every 8 lamps.
        ##############################################################
        i = 0
        self.log.info("Start Attract3")
        for lamp in self.game.lamps:
            if i % 8 == 7:
                lamp.schedule(schedule=0xf00000ff, cycle_seconds=0, now=False)
            elif i % 8 == 6:
                lamp.schedule(schedule=0xff00000f, cycle_seconds=0, now=False)
            elif i % 8 == 5:
                lamp.schedule(schedule=0xfff00000, cycle_seconds=0, now=False)
            elif i % 8 == 4:
                lamp.schedule(schedule=0x0fff0000, cycle_seconds=0, now=False)
            elif i % 8 == 3:
                lamp.schedule(schedule=0x00fff000, cycle_seconds=0, now=False)
            elif i % 8 == 2:
                lamp.schedule(schedule=0x000fff00, cycle_seconds=0, now=False)
            elif i % 8 == 1:
                lamp.schedule(schedule=0x0000fff0, cycle_seconds=0, now=False)
            elif i % 8 == 0:
                lamp.schedule(schedule=0x00000fff, cycle_seconds=0, now=False)
            i = i + 1


        def sw_enter_active(self, sw):
            for lamp in self.game.lamps:
                lamp.disable()
            self.game.modes.add(self.game.service_mode)
            return True