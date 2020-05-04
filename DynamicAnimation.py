import pyglet
import time
# Useful methods
screen_width = pyglet.window.get_platform().get_default_display().get_default_screen().width
screen_height = pyglet.window.get_platform().get_default_display().get_default_screen().height

def centeredSequence(img):
    for frame in img:
        frame.anchor_x = int(frame.width/2)
        frame.anchor_y = int(frame.height/2)


# Experimenting with image grids
image = pyglet.image.load("assets/rolling.png")
image_seq = pyglet.image.ImageGrid(image, 1, 4)  # An image grid with 1 row and 8 columns
centeredSequence(image_seq)
# ^The above splits the image, in a single row, into 8 equal segments; providing "frames"
texture_seq = pyglet.image.TextureGrid(image_seq)  # This creates a texture based off of the ImageGrid (is faster)
centeredSequence(texture_seq)
sprite = pyglet.sprite.Sprite(texture_seq.get_animation(period=1/12, loop=True), x=int(screen_width/2), y=int(screen_height/2))
# Below code renders the window in a loop (looped by window.event)
window = pyglet.window.Window(fullscreen=True)
@window.event
def on_draw():
    window.clear()
    sprite.draw()

pyglet.app.run()
while True:
    for frame in texture_seq:
        sprite.image = frame
        time.sleep(.5)

