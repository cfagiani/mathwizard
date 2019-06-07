# screen width
WIDTH = 1500
# screen height
HEIGHT = 1000
# max frames per second
FPS = 25

# directory for game resources
RESOURCE_DIR = "resources"

# delay after key is held down until we repeate
KEY_REPEAT_DELAY = 100
# interval for repeated keys
KEY_REPEAT_INTERVAL = 30

# number of horizontal 'positions' into which the game board is divided
MAX_POS = 150
# number of correct answers per level
SCORE_PER_LEVEL = 10
# maximum value for the target
MAX_TARGET = 25
# max number of equations that are live at once
MAX_CONCURRENT = WIDTH // 300
# max number of pixels down an equation will move
MAX_STEP = HEIGHT // 300
# max number of frames an equation will wait before starting to descend
MAX_DELAY = FPS * 4
# frames until we repeat the movement for a held joystick button
JOYSTICK_REPEAT = 40 // (1000 / FPS)
# frames after the 'level complete' is displayed until we show the 'press any key' message
WON_MSG_TICKS = FPS * 3
# frames until the 'press any key' message is displayed on the title screen
TITLE_TICKS = FPS * 4
# frames after blowing up the last correct equation until the level win message is displayed
WIN_DELAY = FPS
# number of 'positions' wide a zap is
ZAP_WIDTH = 4
INCORRECT_ANSWER_RATIO = 3
