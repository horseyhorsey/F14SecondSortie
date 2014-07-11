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
#     __  ___ _            _               __ __               __ __
#    /  |/  /(_)___  ___  (_)___   ___    / // /___ _ ___  ___/ // /___  ____
#   / /|_/ // /(_-< (_-< / // _ \ / _ \  / _  // _ `// _ \/ _  // // -_)/ __/
#  /_/  /_//_//___//___//_/ \___//_//_/ /_//_/ \_,_//_//_/\_,_//_/ \__//_/
#
#################################################################################

import procgame
from procgame import *
import locale
import logging

class MissionMode(game.Mode):
	"""docstring for Bonus"""
	def __init__(self, game, priority):
			super(MissionMode, self).__init__(game, priority)
			#self.superSpinnerSpins = self.game.user_settings['Feature']['Super Spinner Spins']
			#self.superSpinnerTime = self.game.user_settings['Feature']['Super Spinner Time']
			#self.superSpinnerLit = False
			#self.superSpinnerEnabled = False
                        self.kill_list=['kill1','kill2','kill3','kill4','kill5','kill6','kill7']
                        self.mission_name= {'kill1' : 'Alpha',
                                            'kill2' : 'Bravo',
                                            'kill3' : 'Charlie',
                                            'kill4' : 'Delta',
                                            'kill5' : 'Echo',
                                            'kill6' : 'Foxtrot',
                                            'kill7' : 'Golf'
                                            }
                        

                        #setup logging
                        self.log = logging.getLogger('f14.mission')
			
	def sw_vUK_closed_for_1s(self, sw):
            
            self.game.utilities.acCoilPulse(coilname='upKicker_flasher3',pulsetime=50)
            self.game.modes.add(self.game.kill1mission)
            return procgame.game.SwitchStop

        # Called by the base mode when lamps 1-6 have been lit.
        ## Per mission status
                        ## -1 = Initial
                        ##  0 = Available
                        ##  1 = In progress
                        ##  2 = Complete
        def completed1_6(self):
            if self.game.utilities.get_player_stats('kills_completed') < 7:
                # First look for a mission that is still in initial state
                initial_missions=[]
                for mission in self.kill_list:
                    if self.game.utilities.get_player_stats(mission) == -1:
                        initial_missions.append(mission)
                        self.log.info("Mission "+mission+" is available")

                # If we actually have one available, then process the first one
                if len(initial_missions) > 0:
                    mission_to_play = initial_missions[0]
                    self.log.info("Setting mission "+mission_to_play+" to available")
                    self.game.utilities.set_player_stats(mission_to_play,0)
                    self.game.utilities.display_text(txt=self.mission_name[mission_to_play]+" Ready",time=3)
                    self.game.utilities.set_player_stats('target1',False)
                    self.game.utilities.set_player_stats('target2',False)
                    self.game.utilities.set_player_stats('target3',False)
                    self.game.utilities.set_player_stats('target4',False)
                    self.game.utilities.set_player_stats('target5',False)
                    self.game.utilities.set_player_stats('target6',False)
                    self.game.utilities.set_player_stats('target1-6_completed',0)

                # Determine the mission the player will do next, if there is one.
                next_mission = 'None';
                for mission in self.kill_list:
                    if self.game.utilities.get_player_stats(mission) == 0 and next_mission == 'None':
                        next_mission = mission;
                self.game.utilities.set_player_stats('next_mission',next_mission)



                self.game.update_lamps()



	def update_lamps(self):
                self.log.info("Update Lamps: Mission")
                for mission in self.kill_list:
                    status=self.game.utilities.get_player_stats(mission);
                    if status == -1:
                        self.log.info("- setting "+mission+" to disabled")
                        self.game.lamps[mission].disable()
                        self.game.lamps[mission+'red'].disable()
                        self.game.lamps[mission+'green'].disable()
                        self.game.lamps[mission+'blue'].disable()
                    elif status == 0:
                        self.log.info("- setting "+mission+" to available")
                        self.game.lamps[mission].schedule(schedule=0xFF00FF00)
                        self.game.lamps[mission+'blue'].schedule(schedule=0xFF00FF00)
                        self.game.lamps[mission+'red'].disable()
                        self.game.lamps[mission+'green'].disable()
                    elif status == 1:
                        self.log.info("- setting "+mission+" to in progress")
                        self.game.lamps[mission].schedule(schedule=0xFF00FF00)
                        self.game.lamps[mission+'red'].schedule(schedule=0xFF00FF00)
                        self.game.lamps[mission+'green'].disable()
                        self.game.lamps[mission+'blue'].disable()
                    else:
                        self.log.info("- setting "+mission+" to complete")
                        self.game.lamps[mission].enable()
                        self.game.lamps[mission+'red'].disable()
                        self.game.lamps[mission+'green'].enable()
                        self.game.lamps[mission+'blue'].disable()

                # If there is a mission waiting to be played, flash the release lamp
                if self.game.utilities.get_player_stats('next_mission') != 'None':
                    self.game.lamps.release.schedule(schedule=0xF0F0F0F0)
                    self.log.info(" - next mission to play is " +self.game.utilities.get_player_stats('next_mission'))
                else:
                    self.game.lamps.release.disable()



#     ___    __       __          __  ___ _            _
#    / _ |  / /___   / /  ___ _  /  |/  /(_)___  ___  (_)___   ___
#   / __ | / // _ \ / _ \/ _ `/ / /|_/ // /(_-< (_-< / // _ \ / _ \
#  /_/ |_|/_// .__//_//_/\_,_/ /_/  /_//_//___//___//_/ \___//_//_/
#           /_/
#
# Light all TOMCAT targets.  Player must hit all targets within time limit

class Kill1Mode(game.Mode):
	"""docstring for Bonus"""
	def __init__(self, game, priority):
            super(Kill1Mode, self).__init__(game, priority)

            self.tomcatTargets={}
            #setup logging
            self.log = logging.getLogger('f14.mission number 1')
            for switch in self.game.switches:
                if switch.name[0:5] in ('upper','lower'):
                    self.add_switch_handler(name=switch.name, event_type='active' ,delay=0.01, handler=self.targetTOMCAT)
                    self.tomcatTargets[switch.name]=False



        def mode_started(self):
            self.log.info("kill 1 starting")
            self.game.utilities.display_text(txt="Start 1",time=3)
            self.game.utilities.set_player_stats('mission_in_progress','kill1')
            self.game.utilities.set_player_stats('kill1',1)
            self.game.update_lamps()
            for target in self.tomcatTargets:
                self.tomcatTargets[target]=False
            self.game.utilities.arduino_write_alpha(display=2,text='Time')
            self.game.utilities.arduino_write_number(display=0,number=1000)
            self.game.utilities.arduino_start_count(display=0,direction=1,limit=200,ticks=8)
            


        def mode_stopped(self):
            for x in self.tomcatTargets:
                self.tomcatTargets[x]=False
            self.game.utilities.set_player_stats('kill1',2)
            self.game.utilities.set_player_stats('mission_in_progress','None')
            self.log.info("mode finishing")


        def update_lamps(self):
            for target in self.tomcatTargets:
                if self.tomcatTargets[target] == False:
                    self.game.lamps[target].schedule(schedule=0xFFF0FFF0)
                else:
                    self.game.lamps[target].enable()

        def targetTOMCAT(self,sw):
            self.tomcatTargets[sw.name]=True
            self.game.sound.play('tomcat')
            #if sw.name[0:5]=="upper":
            #    otherside="lower"+sw.name[5:]
            #else:
            #    otherside="upper"+sw.name[5:]
            #self.tomcatTargets[otherside]=True
            self.game.utilities.score(1000)
            if sum([i for i in self.tomcatTargets.values()])==12: # all targets lit
                self.game.modes.remove(self)
                self.game.utilities.display_text(txt="1 complete",time=3)
            else:
                self.game.utilities.flickerOn(sw.name)
                self.game.utilities.display_text(txt="TOMCAT",time=3)
                #self.game.effects.flickerOn(othersi
            return procgame.game.SwitchStop


            