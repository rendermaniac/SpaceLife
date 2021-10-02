import glob

from ursina import *
from ursina.prefabs.animation import Animation
from ursina.prefabs.animator import Animator
from ursina.prefabs.health_bar import HealthBar

from util import updateHealthBarColor

class Crew(Entity):

    def __init__(self, name, ship=None, room=None, active=True, x=0, y=0):
        super().__init__(x=x, y=y, always_on_top=True, collider="box")
        self.z = -2
        self.name = name
        self.active = active
        self.ship = ship
        self.room = room

        # add to ship
        if self.ship:
            ship.crew[name] = self

        if self.room:
            room.crew[name] = self
            self.parent = room

        self.speed = 2.0

        # health bar states
        self.stress = 0.0
        self.fatigue = 0.0
        self.bone_density = 100.0
        self.radiation = 0.0

        self.overall_health = HealthBar(x=-0.2, y=0.27, scale_x=0.5, scale_y=0.1, parent=self)
        self.overall_health.show_text = False

        left_images = "assets/left"
        right_images = "assets/right"
        up_images = "assets/up"
        down_images = "assets/down"

        if glob.glob(f"assets/{name}_left*"):
            self.scale = 0.15
            left_images = f"assets/{name}_left"

        if glob.glob(f"assets/{name}_right*"):
            right_images = f"assets/{name}_right"

        if glob.glob(f"assets/{name}_up*"):
            up_images = f"assets/{name}_up"

        if glob.glob(f"assets/{name}_down*"):
            down_images = f"assets/{name}_down"

        self.animator = Animator(   animations = {
                                    "left"  : Animation(left_images, parent=self),
                                    "right" : Animation(right_images, parent=self),
                                    "up"    : Animation(up_images, parent=self),
                                    "down"  : Animation(down_images, parent=self),
                                }
                            )

        self.animation.pause()

    @property
    def animation(self):
        return self.animator.animations[self.animator.state]

    def start_all_animations(self):
        for anim in self.animator.animations.values():
            anim.start()

    def pause_all_animations(self):
        for anim in self.animator.animations.values():
            anim.pause()

    def on_click(self):
        self.ship.make_active(self.name)

    def calculate_health(self):
        return (self.bone_density + (100.0 - self.stress)  + (100.0 - self.fatigue)  + (100.0 - self.radiation)) * 0.25

    def update(self):

        # crew radiation increases with the ship radiation
        if self.room.name != "safe_room":
            self.radiation += 0.01 * self.ship.radiation * time.dt
        
        if self.room.name != "med_bay":
            self.radiation -= 0.01 * time.dt

        if self.room.name == "sleeping":
            self.fatigue -= 0.1 * time.dt
        else:
            self.fatigue += 0.1 * time.dt

        if self.room.name == "gym":
            self.bone_density += 0.1 *time.dt
            self.fatigue += 0.2 * time.dt
        else:
            self.bone_density -= 0.1 * time.dt

        if self.room.name == "cafeteria":
            self.stress -= 0.1 * time.dt
            self.ship.food -= 0.1 * time.daylight

        if self.room.name == "greenhouse":
            #self.mood += 0.1 * time.dt
            self.ship.food += 0.1 * time.dt
            
        health = self.calculate_health()
        if self.overall_health.value != health:
            self.overall_health.value = health

        updateHealthBarColor(self.overall_health, good_level = 80.0, bad_level = 20.0)

    def move_to(self, equipment, post_walk=[]):

        pos_old_room = self.position

        # change space to the same room as the equipment
        if self.parent != equipment.room:
            wp = self.world_position
            self.parent = equipment.room
            self.world_position = wp

        s = Sequence()
        s.append(Func(self.start_all_animations))

        # move in y from current position to centre line
        distance_centre = self.world_position.y - self.ship.world_position.y
        distance_along = equipment.position.x - self.position.x
        distance_across = self.ship.world_position.y + equipment.world_position.y

        duration = abs(distance_centre) / self.speed

        if duration != 0.0:
            if distance_centre > 0:
                s.append(Func(setattr, self.animator, "state", "down"))
            elif distance_centre < 0:
                s.append(Func(setattr, self.animator, "state", "up"))

            s.append(Func(self.animate_y, self.position.y - distance_centre, duration=duration, curve=curve.linear))
            s.append(duration)

        # move x direction along ship
        # note that animate_x moves to this position in local space - it is not a distance
        duration = abs(distance_along) / self.speed
        
        if duration != 0.0:
            if distance_along < 0:
                s.append(Func(setattr, self.animator, "state", "left"))
            elif distance_along > 0:
                s.append(Func(setattr, self.animator, "state", "right"))

            s.append(Func(self.animate_x, equipment.position.x, duration=duration, curve=curve.linear))
            s.append(duration)

        # move in y to position
        # note that animate_y moves to this position in local space - it is not a distance
        duration = abs(distance_across) / self.speed

        if duration != 0.0:
            if distance_across > 0:
                s.append(Func(setattr, self.animator, "state", "up"))
            elif distance_across < 0:
                s.append(Func(setattr, self.animator, "state", "down"))

            s.append(Func(self.animate_y, equipment.position.y, duration=duration, curve=curve.linear))
            s.append(duration)

        s.append(Func(setattr, self.animator, "state", "left"))
        s.append(Func(self.pause_all_animations))

        for pw in post_walk:
            s.append(pw)

        # set new room
        s.append(Func(setattr, self, "room", equipment.room))

        s.start()

if __name__ == "__main__":

    from ursina import *
    app = Ursina()

    camera.orthographic = True
    camera.fov = 10

    Crew("captain")

    app.run()