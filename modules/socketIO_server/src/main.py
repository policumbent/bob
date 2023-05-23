import socketio
from aiohttp import web
import json

sio = socketio.AsyncServer(async_mode='aiohttp', 
        cors_allowed_origins="*", 
        cookie=False)
app = web.Application()
sio.attach(app)

curr_data = {
                "heartrate" : 0.0,
                "power" : 0.0,
                "cadence" : 0.0,
                "distance" : 0.0,
                "speed" : 0.0,
                "time" : 0.0,
                "gear" : 0.0
            }

class SocketIO():

    def __init__(self, host, port):
        web.run_app(app, host=host, port=port)
        
    @sio.event
    async def connect(sid, environ):
        print(f'Connected: {sid}')

    @sio.event
    async def disconnect(sid):
        print(f'Disconnected: {sid}')

    @sio.on('new data')
    async def new_data(sid, data):
        data = json.loads(data)
        curr_data[data["topic"]] = data["payload"]
        print(curr_data)
        await sio.emit('update data', json.dumps(curr_data), skip_sid=sid)


if __name__ == '__main__':
    SocketIO('localhost', '1337')