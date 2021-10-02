from ursina import *
import glob
from collections import OrderedDict
from ursina.prefabs.sprite import Sprite

from crew import Crew
from equipment import Equipment


class Room(Entity):

    def __init__(self, name, ship, length=5.0, y=0, rotation=0, parent=None):

        super().__init__(x=0, y=y)

        self.name = name
        self.ship = ship
        self.crew = {}
        self.equipment = {}

        if parent is not None:
            self.parent = parent
            print(f"{name} setting parent to {self.parent}")
            self.x = 0.0
        else:
            # first room
            if len(self.ship.rooms) == 0:
                self.parent = self.ship
                self.x = 0.0
            else:
                if self.ship.rooms[-1].mid.rotation_z != 0.0:
                    self.parent = self.ship.rooms[-1]
                    self.x = 3.0 # width of centrifuge (2.0) + origin to one size aka width/2 (1.0)
                else:
                    self.parent = self.ship.rooms[-1]
                    self.x = length

        self.label = Text(name.replace("_", " ").upper(), scale=5, z=-0.1, color=color.white, origin = (0.0, 0.0), rotation_z=rotation, parent=self)
        # self.top = Entity(parent=self, model='quad', color=color.gray, collider="box", x=2.6, scale_x=.2, scale_y=1.5)
        self.mid = Entity(parent=self, model='quad', color=color.white, collider="box", x=0, scale_x=length, scale_y=2, rotation_z=rotation)
        # self.bottom = Entity(parent=self, model='quad', color=color.red, collider="box", x=-2.6, scale_x=.2, scale_y=1.5)

        if self.mid.rotation_z != 0.0:
            self.x = 3.0 # width of centrifuge (2.0) + origin to one size aka width/2 (1.0)

        if glob.glob(f"assets/{name}.*"):
            self.mid.texture = f"assets/{name}"

        self.ship.rooms.append(self)

    def add_crew(self, name, x=0, y=0):
        return Crew(name, ship=self.ship, room=self, x=x, y=y)

    def add_bed(self, name, x=0, y=0):
        bed = Equipment(name, texture="assets/bed", ship=self.ship, room=self, x=x, y=y)
        bed.post_walk = [Wait(2.5), Func(bed.set_crew_attr, "tiredness", 0.0)]
        return bed
    
    def add_chair(self, name, x=0, y=0):
        return Equipment(name, texture="assets/chair", ship=self.ship, room=self, x=x, y=y)

class Spaceship(Entity):

    def __init__(self):
        super().__init__()
        self.x -= 20
        self.active = None
        self.warning_state = False
        self.shaking = None
        self.rooms = []
        self.crew = OrderedDict()
        self.equipment = OrderedDict()

        # siren from https://mixkit.co/free-sound-effects/siren/
        self.siren = Audio("assets/warning", loop=True, autoplay=False)
        self.siren.volume = 0.5
        self.alarms = []

        # ship statistics
        self.mission_duration = 1.0
        self.oxygen = 100.0
        self.fuel = 100.0
        self.food = 100.0
        self.damage = 0.0
        self.radiation = 5.0
    
    def make_room(self, name, length=5.0, y=0, rotation=0, parent=None):
        return Room(name, self, length, y, rotation, parent=parent)

    def make_active(self, name):
        self.active = self.crew[name]
        self.active.active = True
        for c in self.crew.values():
            if c is not self.active:
                c.active = False

    def sound_warning(self, state):

        if self.warning_state == state:
            return

        if state:
            self.siren.play()

            for room in self.rooms:
                self.alarms.append(room.mid.blink(color.red, loop=True, duration=.5))
        else:
            self.siren.fade_out(duration=1)
            
            # pause all alarms
            for alarm in self.alarms:
                alarm.pause()
            
            # reset alarms
            self.alarms = []

            # set colour back on mid section
            for room in self.rooms:
                room.mid.color = color.white

        self.warning_state = state

    def update(self):

        self.mission_duration += (1.0/60.0) * time.dt
        self.fuel -= 0.1 * time.dt
