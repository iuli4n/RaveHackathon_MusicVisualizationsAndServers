# requires Python3 and aioconsole library
# This runs a WebSocket server where there's a local variable being broadcast to all clients
# This doesn't talk to Arduino.
#
# Other python websocket examples: https://www.piesocket.com/blog/python-websocket

import sys
import functools
import asyncio
import aioconsole
import time
import websockets

import sys
import os

import pygame as pg
import pygame.midi

MIDIVERBOSE = False
WSPORT = 31337
WSBROADCASTDELAY = 0.05  # note, only sends when not different than before


# this is the variable sent to all connected clients
reply = 0

# coroutine that just increments reply every 1 sec
async def incrementor():
    global reply
    while True:
        reply = str(int(reply) + 1)
        await asyncio.sleep(1)


# coroutine that runs after each client connects
async def wsclient_handler(websocket, path):

    print ("A client connected");

    # if data is received...
    #data = await websocket.recv()
    #reply = f"Data recieved as:  {data}!"

    while True:
        global reply;
        lastReply = reply
        # send the current value of 'reply'
        reply = str(M1)+","+str(M2)+","+str(M3)
        #print(reply)
        if (lastReply != reply):
            await websocket.send(reply)
        await asyncio.sleep(WSBROADCASTDELAY)





######## MIDI


M1 = 0;
M2 = 0;
M3 = 0;

async def midi_input_main(device_id=None):

    global M1;
    global M2;
    global M3;
    
    pg.init()
    pg.fastevent.init()
    event_get = pg.fastevent.get
    event_post = pg.fastevent.post

    print("here");

    pygame.midi.init()

    print("initialized midi, printing")

    
    
    input_id = pygame.midi.get_default_input_id()
    
    print("using input_id :%s:" % input_id)
    i = pygame.midi.Input(input_id)

    #pg.display.set_mode((1, 1))

    going = True
    while going:
        await asyncio.sleep(0.1);

        events = event_get()
        for e in events:
            if e.type in [pg.QUIT]:
                going = False
            if e.type in [pg.KEYDOWN]:
                going = False
            if e.type in [pygame.midi.MIDIIN]:
                print(e)

        if i.poll():
            midi_events = i.read(100)
            
            # convert them into pygame events.
            midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

            for m_e in midi_evs:
                #event_post(m_e)
                
                if (MIDIVERBOSE): print(m_e)
                
                if (m_e.status == 176):
                
                    if (m_e.data1 == 0):  M1 = m_e.data2;
                    if (m_e.data1 == 1):  M2 = m_e.data2;
                    if (m_e.data1 == 2):  M3 = m_e.data2;
                    
                    #if (m_e.data1 == 16): M1 = m_e.data2;
                    #if (m_e.data1 == 17): M2 = m_e.data2;
                    #if (m_e.data1 == 18): M3 = m_e.data2;

                
                
            

    del i
    pygame.midi.quit()


#input_main()


















### MAIN 

# run incremental task
asyncio.get_event_loop().create_task(incrementor())

# start server
start_server = websockets.serve(wsclient_handler, "localhost", WSPORT)
asyncio.get_event_loop().run_until_complete(start_server)
print ("Server running. Waiting for clients...")

# wait for keypress

async def waitkey():
    line = await aioconsole.ainput('Press CTRL+C or ENTER to quit.')
    print("*** THIS MAY RAISE ERRORS ****")

loop = asyncio.get_event_loop()

asyncio.get_event_loop().create_task(midi_input_main())

loop.run_until_complete(waitkey())
loop.close()
