import time
import picokeypad

keypad = picokeypad.PicoKeypad()
keypad.set_brightness(1.0)


lit = 0

colour_index = 0

NUM_PADS = keypad.get_num_pads()





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

for coord in gridToColors.keys():
    if(gridToColors[coord] != (0, 0, 0)):
        initialGridState[coord] = True
        gridState[coord] = True
    else:
        initialGridState[coord] = None
        gridState[coord] = None


dimPercentage = .05

NUM_PADS = keypad.get_num_pads()

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

# The colour to set the keys when pressed, yellow.

isAsleep = False
# Attach handler functions to all of the keys

def press_handler(keyPressed):
    #sleep key pressed
    if keyPressed == 15:
        global isAsleep
        if(isAsleep == True):
            wakeKeypad()
            isAsleep = False
        else:
            sleepKeypad()
            isAsleep = True
    #reset key pressed
    elif keyPressed == 11:
        for key in range(NUM_PADS):
            if(initialGridState[keyNumToGrid[key]]):
                color =  gridToColors[keyNumToGrid[key]]
                keypad.illuminate(key, *color)
                gridState[keyNumToGrid[key]] = True
            else:
                keypad.illuminate(key, 0,0,0)

    #any of the other keys pressed
    else:
        if(gridState[keyNumToGrid[keyPressed]] != None):
            dimAmount = dimPercentage if gridState[keyNumToGrid[keyPressed]] else 1.0
            color =  map(lambda color:  int(float(color) * dimAmount), gridToColors[keyNumToGrid[keyPressed]])
            keypad.illuminate(keyPressed, *color)
            gridState[keyNumToGrid[keyPressed]] = not gridState[keyNumToGrid[keyPressed]]
    
last_buttons = 0

wakeKeypad()

while True:
    current_buttons = keypad.get_button_states()
    if last_buttons != current_buttons:
        changed_buttons = current_buttons ^ last_buttons
        pressed_buttons = current_buttons & changed_buttons
        released_buttons =  last_buttons & changed_buttons
        last_buttons = current_buttons
        
        print()
        
        pressed_buttons_indices = []
        index = 0
        while pressed_buttons:
            if(pressed_buttons & 0x01):
                pressed_buttons_indices.append(index)
            pressed_buttons = pressed_buttons >> 1
            index = index + 1
            
        for button in pressed_buttons_indices:
            press_handler(button)
        
        keypad.update()
        time.sleep(.1)
