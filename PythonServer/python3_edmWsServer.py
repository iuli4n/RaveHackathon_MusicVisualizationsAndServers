# requires Python3 and aioconsole library
# runs a WebSocket server where there's a local variable being broadcast to all clients
#
# Other python websocket examples: https://www.piesocket.com/blog/python-websocket

import sys
import functools
import asyncio
import aioconsole
import time
import websockets

import pyaudio
import numpy as np
from scipy.io import wavfile
import time
import sys
import wave




### WEBSOCKETS
#
# TODOS:
#   -!! slow clients will get flooded. need a js-level PING mechanism (the websocket ping doesn't work properly because it's lower level)

# how much time between sending updates to each client 
UPDATEDELAY = 0.1

# tracks all clients connected to the webserver
wsclients = []

# coroutine that prints the server status every few seconds
async def ws_serverStatusLoop():
    while True:
        print("Server status")
        print("\t Current value: ",reply)
        print("\t Active clients: ", len(wsclients))
        
        for client in wsclients:
            pong_waiter = await client.ping()
            await pong_waiter
            
            print("\t\t"+str(client.remote_address) + " PING: "+ str(client.latency))
        
        await asyncio.sleep(1)

# coroutine that runs for each client
async def wsclient_handler(websocket, path):

    print ("WS Client connected: "+str(websocket.remote_address)+"   "+str(websocket.id))
    wsclients.append(websocket)

    # if data is received...
    #data = await websocket.recv()
    #reply = f"Data recieved as:  {data}!"

    while True:

        try:
            # send the current value of 'reply'
            await websocket.send(str(reply))
            await asyncio.sleep(UPDATEDELAY)
            
        except websockets.ConnectionClosed:
            print("WS Client disconnected "+str(websocket.remote_address)+"   "+str(websocket.id))
            wsclients.remove(websocket)
            break
        

def ws_startServer():
    # start server
    start_server = websockets.serve(wsclient_handler, "localhost", 8000)
    asyncio.get_event_loop().run_until_complete(start_server)
    print ("Server running. Waiting for clients...")






######################### AUDIO


FORMAT = pyaudio.paInt16 # We use 16bit format per sample
CHANNELS = 1
RATE = 44100
CHUNK = 2048 # bytes of data red from a buffer
RECORD_SECONDS = 0.1
WAVE_OUTPUT_FILENAME = "file.wav"

# use a Blackman window
window = np.blackman(CHUNK)


audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True)#,
                    #frames_per_buffer=CHUNK)
                 

# Open the connection and start streaming the data
stream.start_stream()


def plot_data_OLD(in_data):
    # NOTE: CHUNK was 1024
    
    # get and convert the data to float
    audio_data = np.fromstring(in_data, np.int16)
    # Fast Fourier Transform, 10*log10(abs) is to scale it to dB
    # and make sure it's not imaginary
    dfft = 10.*np.log10(abs(np.fft.rfft(audio_data)))

    print(len(dfft),"   ",dfft[500])


def plot_data(in_data):
    waveData = wave.struct.unpack("%dh"%(CHUNK), in_data)
    npArrayData = np.array(waveData)
    indata = npArrayData*window
    fftData=np.abs(np.fft.rfft(indata))
    fftTime=np.fft.rfftfreq(CHUNK, 1./RATE)
    which = fftData[1:].argmax() + 1
    
    print(round(fftData[124]))
    
    global reply
    reply = round(fftData[124])


### BACKGROUND PROCESSING
ANALYSISDELAY = 0.01

# this is the variable sent to all connected clients
global reply
reply = 0

# coroutine that just increments reply every 1 sec
async def incrementor():
	global reply
	while True:
		#reply = reply + 1
		
		plot_data(stream.read(CHUNK))
		
		await asyncio.sleep(ANALYSISDELAY)








### MAIN EXECUTION

# run incremental task
asyncio.get_event_loop().create_task(incrementor())

# start server
ws_startServer()
asyncio.get_event_loop().create_task(ws_serverStatusLoop())


# wait for keypress

async def waitkey():
    line = await aioconsole.ainput('Press CTRL+C or ENTER to quit.\n')
    print("*** QUITTING, BUT THIS MAY RAISE ERRORS ****")

loop = asyncio.get_event_loop()
loop.run_until_complete(waitkey())
loop.close()


# Close up shop (currently not used because KeyboardInterrupt
# is the only way to close)
stream.stop_stream()
stream.close()

audio.terminate()
