import time
from pynput import keyboard
from multiprocessing import Process, Queue

fetchKeyPress = 10

def on_release(key):
    global fetchKeyPress 
    fetchKeyPress = key
    print(key)
    if key == keyboard.Key.esc:
        fetchKeyPress = 0
        print('escaped!')
        # Stop listener
        return False


def keyboardListener(q):
    global fetchKeyPress
    prevKeyFetch = 10    # Keep track of the previous keyPress
    keyboard.Listener(on_release=on_release).start()
    while (fetchKeyPress):
        print ('Last Key Pressed was ', fetchKeyPress)
        # Fill the Queue only when a new key is pressed
        if (not (fetchKeyPress == prevKeyFetch)):
            q.put(fetchKeyPress)   
        # Update the previous keyPress
        prevKeyFetch = fetchKeyPress
        time.sleep(0.25)
    print('Keybord Listener Terminated!!!')
    q.put('Terminate')


def oneSecondTimer(q):
    runner = True   # Runs the while() loop
    starttime = time.time()
    while (runner):
        print('\ttick')
        if (not q.empty()): 
            qGet = q.get()
            print ('\tQueue Size ', q.qsize())
            print ('\tQueue out ', qGet)
            # Condition to terminate the program
            if (qGet == 'Terminate'):
                # Make runner = False to terminate the While loop
                runner = False
        time.sleep(1.0 - ((time.time() - starttime) % 1.0))
    return False


if __name__ == '__main__':
    q = Queue()
    p1 = Process(target=oneSecondTimer, args=(q,))
    p1.start()
    p2 = Process(target=keyboardListener, args=(q,))
    p2.start()