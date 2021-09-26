from ursina import *
from ursina.prefabs.sprite import Sprite

from crew import Crew
from equipment import Bed

class Spaceship(Entity):

    def __init__(self):
        super().__init__()
        self.active = None
        self.rooms = {}
        self.crew = {}
        self.equipment = {}

        self.fuel = 100.0
    
    def make_room(self, name, x=0, y=0, rotation=0):
        offset = len(self.rooms) * 5.4
        parent = Entity(x=x-offset, y=y, rotation_z=rotation)
        front_airlock = Entity(parent=parent, model='quad', color=color.gray, collider="box", x=2.6, scale_x=.2, scale_y=1.5)
        body = Entity(parent=parent, model='quad', color=color.white, collider="box", x=0, scale_x=5, scale_y=2)
        mid = Entity(parent=parent, model='quad', color=color.red, collider="box", x=-5, scale_x=.2, scale_y=1.5)
        rear = Entity(parent=parent, model='quad', color=color.blue, collider="box", x=-2.6, scale_x=.2, scale_y=1.5)
        far_rear = Entity(parent=parent, model='quad', color=color.red, collider="box", x=-5, scale_x=.2, scale_y=1.5)
        self.rooms[name] = parent

    def make_active(self, name):
        self.active = self.crew[name]
        self.active.active = True
        for c in self.crew.values():
            if c is not self.active:
                c.active = False

    def add_crew(self, name, x=0, y=0):
        self.crew[name] = Crew(name, ship=self, x=x, y=y)

    def add_bed(self, name, x=0, y=0):
        self.equipment[name] = Bed(name, ship=self, x=x, y=y)

    def update(self):

        self.fuel -= 1.0 * time.dt
