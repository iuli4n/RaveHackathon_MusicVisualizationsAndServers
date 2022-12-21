# requires Python3 and some of these libraries
#
# does these:
#    - runs a WebSocket server where there's a local variable being broadcast to all clients
#    - the data is coming from audio analysis
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
from scipy.interpolate import interp1d

#################################################
# MISC - FOR SIMPLIFYING AUDIO
#

MAXSIMPLIFIED = 10
MAXRANGE = 50000
    
def mscale(v):
    
    v = min(v, MAXRANGE)
    x = int(interp1d([0,MAXRANGE],[0,MAXSIMPLIFIED])(v))
    
    return x
    
def stars(x):
    s = ""
    
    for i in range(x):
        s = s+"*"
    for i in range(MAXSIMPLIFIED-x-1):
        s = s+" "
    
    return s
    


##################################################
## WEBSOCKETS
#
# TODOS:
#   -!! slow clients will get flooded. need a js-level PING mechanism (the websocket ping doesn't work properly because it's lower level)

DELAY_CLIENTUPDATES = 0.1   # how much time between sending updates to each client 
DELAY_SERVERSTATUS = 10     # seconds between printing the server status to console

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
        
        await asyncio.sleep(DELAY_SERVERSTATUS)

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
            await asyncio.sleep(DELAY_CLIENTUPDATES)
        
        # when client disconnects..
        except websockets.ConnectionClosed:
            print("WS Client disconnected "+str(websocket.remote_address)+"   "+str(websocket.id))
            wsclients.remove(websocket)
            break
        

def ws_startServer():
    # start server
    start_server = websockets.serve(wsclient_handler, "localhost", 8000)
    asyncio.get_event_loop().run_until_complete(start_server)
    print ("Server running. Waiting for clients...")






######################### AUDIO PROCESSING


FORMAT = pyaudio.paInt16 # We use 16bit format per sample
CHANNELS = 1
RATE = 44100
CHUNK = 1024 # 2048 # bytes of data red from a buffer
RECORD_SECONDS = 0.1 # 0.1
WAVE_OUTPUT_FILENAME = "file.wav"

# use a Blackman window
window = np.blackman(CHUNK)


audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
                 

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
    
    
global ai2
ai2 = 1;

def plot_data(in_data):
    waveData = wave.struct.unpack("%dh"%(CHUNK), in_data)
    npArrayData = np.array(waveData)
    indata = npArrayData*window
    fftData=np.abs(np.fft.rfft(indata))
    fftTime=np.fft.rfftfreq(CHUNK, 1./RATE)
    which = fftData[1:].argmax() + 1
    
    m1 = (round(fftData[ai2]))
    m2 = (round(fftData[70]))
    m3 = (round(fftData[120]))
    
    val1 = mscale(m1)
    val2 = mscale(m2)
    val3 = mscale(m3)
    
    print(ai2,"\t", stars(val1),"\t", stars(val2), "\t", stars(val3))
    
    global reply
    reply = str(val1)+","+str(val2)+","+str(val3)


##################################################


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


##################################################





##################################################
### MAIN EXECUTION

# run incremental task
asyncio.get_event_loop().create_task(incrementor())

# start server
ws_startServer()
asyncio.get_event_loop().create_task(ws_serverStatusLoop())


# wait for keypress

async def waitkey():
    while True:
        line = await aioconsole.ainput('Press CTRL+C or ENTER to quit.\n')
        
        global ai2
        
        if (line == "["):
            ai2 = ai2 - 3
            ai2 = max(ai2, 1)
            
        if (line == "]"):
            ai2 = ai2 + 3
            ai2 = min(ai2, 512)
            
        if (line == "q"):
            return;
    
    print("*** QUITTING, BUT THIS MAY RAISE ERRORS ****")

loop = asyncio.get_event_loop()
loop.run_until_complete(waitkey())
loop.close()


# Close up shop (currently not used because KeyboardInterrupt
# is the only way to close)
stream.stop_stream()
stream.close()

audio.terminate()
