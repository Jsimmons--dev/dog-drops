import time
import picokeypad

keypad = picokeypad.PicoKeypad()

# got tired of trying to remember the linear button numbers.
# made this map to make it easier to initialize the grid
keyNumToGrid = {
    0: (0, 0),
    1: (0, 1),
    2: (0, 2),
    3: (0, 3),
    4: (1, 0),
    5: (1, 1),
    6: (1, 2),
    7: (1, 3),
    8: (2, 0),
    9: (2, 1),
    10: (2, 2),
    11: (2, 3),
    12: (3, 0),
    13: (3, 1),
    14: (3, 2),
    15: (3, 3)
}

#default state of the grid
gridToColors = {
    (0, 0): (255, 128, 0),
    (0, 1): (255, 128, 0),
    (0, 2): (255, 128, 0),
    (0, 3): (0,  0, 0),
    (1, 0): (51, 255, 255),
    (1, 1): (0,  0, 0),
    (1, 2): (51, 255, 255),
    (1, 3): (0, 0, 0),
    (2, 0): (255, 255, 255),
    (2, 1): (0, 0, 0),
    (2, 2): (255, 255, 255),
    (2, 3): (0, 255, 0),
    (3, 0): (0, 0, 0),
    (3, 1): (0, 0, 0),
    (3, 2): (78, 78, 78),
    (3, 3): (128, 128, 0)

}


initialGridState = {}
gridState = {}

# automatically determine if the key is on or off
for coord in gridToColors.keys():
    if(gridToColors[coord] != (0, 0, 0)):
        initialGridState[coord] = True
        gridState[coord] = True
    else:
        initialGridState[coord] = None
        gridState[coord] = None

# rather than just turn off the keys, dim them to a percentage.
# this lets you know which keys are not used vs are in use and already pressed.
# Thanks for the idea Tanner!
dimPercentage = .05

NUM_PADS = keypad.get_num_pads()

# the bottom right key is a sleep key in case the lights are bothersome when not in a drop session
def sleepKeypad():
    keypad.clear()

def wakeKeypad():
    for key in range(NUM_PADS):
        if(gridState[keyNumToGrid[key]] == True or gridState[keyNumToGrid[key]] == False):
            dimAmount = dimPercentage if gridState[keyNumToGrid[key]] == False else 1.0
            color =  map(lambda color:  int(float(color) * dimAmount), gridToColors[keyNumToGrid[key]])
            keypad.illuminate(key, *color)
        else:
            keypad.illuminate(key, 0,0,0)
    keypad.update()

isAsleep = False

#this handles all key presses
def press_handler(keyPressed):
    #sleep key pressed, bottom right
    if keyPressed == 15:
        global isAsleep
        if(isAsleep == True):
            wakeKeypad()
            isAsleep = False
        else:
            sleepKeypad()
            isAsleep = True
    #reset key pressed, right above the sleep key
    elif keyPressed == 11:
        for key in range(NUM_PADS):
            if(initialGridState[keyNumToGrid[key]]):
                color =  gridToColors[keyNumToGrid[key]]
                keypad.illuminate(key, *color)
                gridState[keyNumToGrid[key]] = True
            else:
                keypad.illuminate(key, 0,0,0)

    #any of the other keys pressed
    # None keys are not in use. The other keys have a True: full brightness, False: dimmed state
    else:
        if(gridState[keyNumToGrid[keyPressed]] != None):
            dimAmount = dimPercentage if gridState[keyNumToGrid[keyPressed]] else 1.0
            color =  map(lambda color:  int(float(color) * dimAmount), gridToColors[keyNumToGrid[keyPressed]])
            keypad.illuminate(keyPressed, *color)
            gridState[keyNumToGrid[keyPressed]] = not gridState[keyNumToGrid[keyPressed]]
    
last_buttons = 0

wakeKeypad()

while True:
    # don't do any work if there weren't any key presses or releases this cycle
    current_buttons = keypad.get_button_states()
    if last_buttons != current_buttons:
        # if there were button state changes, do some binary math to get which ones have changed
        changed_buttons = current_buttons ^ last_buttons
        pressed_buttons = current_buttons & changed_buttons
        released_buttons =  last_buttons & changed_buttons
        last_buttons = current_buttons

        # do some work to convert the binary state results into a usable array of buttons pressed
        pressed_buttons_indices = []
        index = 0
        while pressed_buttons:
            if(pressed_buttons & 0x01):
                pressed_buttons_indices.append(index)
            pressed_buttons = pressed_buttons >> 1
            index = index + 1
            
        for button in pressed_buttons_indices:
            # run the key handler for each button pressed
            press_handler(button)
        
        # no led's change unless you actually call this update to write the data across the pins
        keypad.update()
        # sleep so this doesn't run full bore when I'm actually just pushing 10 buttons a day
        time.sleep(.1)
