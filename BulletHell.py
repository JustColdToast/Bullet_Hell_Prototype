import pyglet
from PIL import Image
import time
# ---------Check what the display size is for the primary screen-----------
screen_width = pyglet.canvas.get_display().get_default_screen().width
screen_height = pyglet.canvas.get_display().get_default_screen().height

# -----------Below is a collection of useful functions as well as important objects----------------

'''----------THE BELOW FUNCTION IS DEPRECIATED IN FAVOR OF OBJECT-BY-OBJECT BASIS TIME-KEEPING
class _CooldownFunc:  # This class is used to make a decorator to prevent simultaneous calling of set functions
    def __init__(self, func, duration):
        self._func = func
        self.duration = duration
        self._start_time = 0

    @property
    def remaining(self):
        return self.duration - (time.time() - self._start_time)

    @remaining.setter
    def remaining(self, value):
        self._start_time = time.time() - (self.duration - value)

    def __call__(self, *args, **kwargs):
        if self.remaining <= 0:
            self.remaining = self.duration
            return self._func(*args, **kwargs)

    def __getattr__(self, attr):
        return self._func.__getattribute__(attr)


def cooldown(duration):  # Cooldown decorator
    def decorator(func):
        return _CooldownFunc(func, duration)
    return decorator
'''


class PhysicsObject:  # Represents a physical object instance associated with a sprite
    def __init__(self, sprite):
        self.sprite = sprite  # Sets the sprite associated with the object
        self.vx, self.vy = 0, 0  # This indicates the "step" of movement in each update; represents velocity

    def update(self, dt):  # dt must be provided as all update methods are called in a batch on a clock
        if (((self.sprite.x - self.sprite.width > screen_width) or (self.sprite.x + self.sprite.width < 0))
            and
                ((self.sprite.y - self.sprite.height > screen_height) or (self.sprite.y + self.sprite.height < 0))):
            self.delete()  # If out of bounds of screen, delete self
        else:  # otherwise, continue movement path
            self.sprite.x += self.vx * dt * 2
            self.sprite.y += self.vy * dt * 2

    def delete(self):  # This function deletes an objects sprite, then removes it from a list of objects
        self.sprite.delete()
        objects.remove(self)


class Player(PhysicsObject):  # Represents a player entity
    def __init__(self, sprite):
        super().__init__(sprite)  # Call the PhysicsObject constructor
        self.lastAbilityCall = time.time()
        self.mouseX = screen_width//2
        self.mouseY = screen_height//2

    def update(self, dt):
        super().update(dt)  # Call the PhysicsObject update
        # dt is multiplied to factor for inconsistencies in frame display times
        if keyState[key.W]:
            if (self.sprite.y + (self.sprite.height / 2) + 100 * dt * 2) < screen_height:
                self.sprite.y += 200 * dt * 2
        elif keyState[key.S]:
            if (self.sprite.y - (self.sprite.height / 2) - 100 * dt * 2) > 0:
                self.sprite.y -= 200 * dt * 2
        if keyState[key.A]:
            if (self.sprite.x - (self.sprite.width / 2) - 100 * dt * 2) > 0:
                self.sprite.x -= 200 * dt * 2
        elif keyState[key.D]:
            if (self.sprite.x + (self.sprite.height / 2) + 100 * dt * 2) < screen_width:
                self.sprite.x += 200 * dt * 2
        if keyState[key.SPACE]:  # Creates bullets when space is pressed
            self.shoot()

    def shoot(self):
        if time.time() >= self.lastAbilityCall + 0.25:  # If 0.5 seconds have passed since the last ability call
            self.lastAbilityCall = time.time()  # Update the last ability call

            bullet = PhysicsObject(pyglet.sprite.Sprite(playerImg, player.sprite.x, player.sprite.y,
                                                        batch=batch))
            '''
            if keyState[key.W]:
                bullet.vy = 500
            elif keyState[key.S]:
                bullet.vy = -500
            if keyState[key.A]:
                bullet.vx = -500
            elif keyState[key.D]:
                bullet.vx = 500
            '''
            # Alternative, mouse-based, firing method
            # Creates a line between two points and adjusts the base speed to accommodate the slope
            slope = (self.mouseX-self.sprite.x, self.mouseY-self.sprite.y)
            print(self.mouseX, self.mouseY)
            print(self.sprite.x, self.sprite.y)
            print("slope:" +str(slope))
            bullet.vy, bullet.vx = 2*slope[1], 2*slope[0]
            objects.append(bullet)  # adds bullet to list of objects


def centre_anchor(img):  # This function centers the anchors on images and animations (directly affects input data)
    if isinstance(img, pyglet.image.AbstractImage):
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
    elif isinstance(img, pyglet.image.Animation):
        for frame in img:
            frame.anchor_x = img.width // 2
            frame.anchor_y = img.height // 2
    elif isinstance(img, pyglet.image.AbstractImageSequence):
        for image in  img:
            image.anchor_x = img.width // 2
            image.anchor_y = img.height // 2
    else:
        print("Data-type centering scheme unaccounted for")


def scale_to_screen(img, factor):  # This function scales images to the size of the screen, returns pyglet.AbstractImage
    # Objects must be scaled to retain the ratio of sizes between all sprites
    print()
    img = img.resize((int(img.size[0]*factor), int(img.size[1]*factor)), Image.ANTIALIAS)
    img_data = img.tobytes()
    return pyglet.image.ImageData(img.size[0], img.size[1], img.mode,
                                  img_data, pitch=-img.size[0]*len(img.mode))


# --------Setup of all primary assets below------------
objects = []  # This represents all physics objects currently present
batch = pyglet.graphics.Batch()  # represents a batch of images
# Setup scale of main character sprite (according to monitor resolution)
# Png scaling requires RGBA, JPG's use RGB (no alpha)
playerImg = scale_to_screen(Image.open("assets/green_circle.png"), 0.375*screen_width/1920)  # Scale player sprite
centre_anchor(playerImg)
player = pyglet.sprite.Sprite(playerImg, screen_width // 2, screen_height//2, batch=batch)
player = Player(player)  # Creates player object
objects.append(player)
# Setup background image (scale)
background = pyglet.sprite.Sprite(scale_to_screen(Image.open("assets/Background.jpg"), screen_width/1920), 0, 0)
# Setup of bullets
bulletTexture = scale_to_screen(Image.open("assets/green_circle.png"), 0.02*screen_width/1920)
# Execution of display window (as well as drawing) below
window = pyglet.window.Window(fullscreen=True)

key = pyglet.window.key
keyState = key.KeyStateHandler()
window.push_handlers(keyState)
window.set_mouse_visible(True)  # Make the mouse visible

# --------------All other functions---------------


@window.event
def on_draw():
    window.clear()
    background.draw()
    player.sprite.draw()
    batch.draw()


def update(dt):  # This function handles cycling through the update functions of all objects on screen
    for item in objects:
        item.update(dt)


@window.event
def on_mouse_motion(x, y, dx, dy):
    # Updates the mouse position for the player character
    player.mouseX, player.mouseY = x, y


pyglet.clock.schedule_interval(update, 1/120)  # Movement is checked 120 times a second (2x 60fps)

pyglet.app.run()
