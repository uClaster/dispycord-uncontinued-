'''
MIT License

Copyright (c) 2021 uClaster

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import asyncio
import json
import logging
import time
from typing import TYPE_CHECKING, Union, Optional

import aiohttp

from .errors import error

if TYPE_CHECKING:
    from . import ext

DISPATCH = 0
HEARTBEAT = 1
IDENTIFY = 2
PRESENCE_UPDATE = 3
VOICE_STATE_UPDATE = 4
RESUME = 6
RECONNECT = 7
REQUEST_GUILD_MEMBERS = 8
INVALID_SESSION = 9
HELLO = 10
ACK = 11
WSS = "wss://gateway.discord.gg/?v=9&encoding=json"

log = logging.getLogger(__name__)

__all__ = (
    'AutoSharded',
    'Shard',
    'GatewayRateLimitter',
)


class GatewayRateLimitter:
    ''' WebSocket ratelimit. '''
    def __init__(
        self,
        *,
        per_minute: int = 110,
        per_second: int = 2
    ):
        '''
        ..Gateway Ratelimit::
            Client are allowed to send 120 gateway commands per minute
            or average 2 command per second.
            
        Parameter
        ----------
        :per_minute: command can be sent per minute
        :per_second: command can be sent per second
        
        Attributes
        -----------
        :remain_per_minute:
        :remain_per_second:
        '''
        self.per_minute = per_minute
        self.per_second = per_second
        
        self.remain_per_minute = self.per_minute
        self.remain_per_second = self.per_second
        
        self.minute_future_tick = self.get_current() + 60
        self.second_future_tick = self.minute_future_tick - 60
        
    async def tick(self) -> None:
        ''' Ratelimit ticker '''
        if self.remain_per_minute <= 0 or self.remain_per_second <= 0:
            
            log.warning('Gateway ratelimit.')
            
            await asyncio.sleep(
                self.minute_future_tick - self.get_current()
                if self.remain_per_minute <= 0
                else 1
            )
            
        if (t := self.get_current()) >= self.minute_future_tick:
            self.remain_per_minute = self.per_minute
            
        if t >= self.second_future_tick:
            self.remain_per_second = self.per_second
        
        self.remain_per_minute -= 1
        self.remain_per_second -= 1
        
    def get_current(self) -> int:
        return int(time.time())


class Shard:
    
    def __init__(
        self,
        client: Union['ext.Bot', 'ext.Client'],
        shard_id: int
    ):
        
        self._client = client
        
        self.pacemaker: Optional[asyncio.Task] = None
        self.shard_id = shard_id
        self.num_shards = self._client.num_shards
        self._ratelimitter = GatewayRateLimitter()
        
        self._ws = None
        self._acked: bool = False
        self._interval: Union[int, float] = 41.25
        self._reconnect: bool = False
        
        self._sequence: Optional[int] = None
        self._session_id: Optional[str] = None
        
    def shard_log(self, message: str = 'No content.', logtype: str = 'debug'):
        getattr(log, logtype)(f'Shard {self.shard_id}: {message}')
        
    async def spawn_ws(self) -> None:
        ''' Method call for spawning shard '''
        async with self._client.http.client_session.ws_connect(WSS) as ws:
            self._ws = ws
            
            self.shard_log('Connected to gateway', 'debug')
            
            while True:
                
                if isinstance((message := await ws.receive()).data, int):
                    
                    await self.handle_disconnect(
                        message.data,
                        message.extra
                    )
                    break
            
                if message.data is None:
                    await self.handle_disconnect(
                            message.data,
                            message.extra
                        )
                    break
            
                data = json.loads(message.data)
                op, event, self.seq, d = data['op'], data['t'], data['s'], data['d']
                
                if op == HELLO:
                    
                    self.shard_log('Recieved HELLO', 'debug')
                    self.pacemaker = self._client.loop.create_task(
                        self.start_heartbeat()
                    )
                    
                elif op == ACK:
                    self.shard_log('Recieved ACK', 'debug')
                    await self.identify()
                    
                elif op == INVALID_SESSION:
                    self.shard_log('Stopped working', 'warning')
                    self.pacemaker.cancel()
                    self._ws.close(code=1002)
                    
                elif op == DISPATCH:
                    
                    if event == 'READY':
                        self._session_id = d['session_id']
                        
        if not self._acked:
            exit(1)
            
        if self._ws.closed and self._reconnect:
            await self.spawn_ws()
            
    async def identify(self) -> None:
        '''
        ..identify::
            Used to trigger the initial handshake with the gateway.
            
        Result
        -------
        on success: Your bot will appear online and ready for accepting requests
        on disconnect: resuming if possible.
        '''
        if self._reconnect:
            await self.resume()
            return
        
        if self._acked:
            return
        
        await self.send_as_json({
            'op': IDENTIFY,
            'd': {
                'token': self._client.http.token,
                'intents': self._client.intent,
                'properties': {
                    '$os': 'linux',
                    '$browser': 'dispycord',
                    '$device': 'dispycord'
                },
                'shard': [self.shard_id, self.num_shards]
            }
        })
        
        self._acked = True
        
        self.shard_log('Connected to Discord and recieved READY state')
    
    async def start_heartbeat(self) -> None:
        ''' Start heartbeat. '''
        while True:
            
            await asyncio.sleep(
                4
                if self._acked is False
                else self._interval
            )
            
            await self.send_as_json(
                {
                    'op': HEARTBEAT,
                    'd': None
                }
            )
            
    async def send_as_json(self, data: dict):
        '''
        Same as self._ws.send_json(dict) but with ratelimit ticker
        
        Parameter
        ----------
        :data: takes a dict to parse to JSON.
        '''
        await self._ratelimitter.tick()
        
        await self._ws.send_json(data)
        
    async def resume(self):
        self.shard_log('Shard sending resume request', 'debug')
        self._ws.send_json({
            'op': RESUME,
            'd': {
                'token': self._client.http.token,
                'session_id': self._session_id,
                'seq': self._sequence
            }
        })
        self._reconnect = False
        
    async def handle_disconnect(self, message=None, extra=None) -> None:
        self.shard_log('Recieved a close signal.', 'warning')
        self.pacemaker.cancel()
        
        if (code := str(message)) in error.keys():
            raise error[code](extra)
        self._reconnect = True
        
    async def next_shard(self) -> None:
        ''' Calling for next shard '''
        try:
            await self._client._lock_sentinel.release()
        except Exception:
            ...
            
            
class AutoSharded:
    
    def __init__(self):
        
        self.num_shards = 1 # Default 2:: not necessary for now.
        self.shards: dict = {}
        
        self._lock_sentinel = asyncio.Lock()
        
    async def new_shard(self) -> None:
        ''' Creating new shard object '''
        for shard in range(self.num_shards):
            
            sharder = Shard(
                self,
                shard
            )
            
            log.debug('Spawning shard %s', shard)
            
            self.shards['shard' + str(shard)] = sharder
            
            async with self._lock_sentinel:
                
                self.loop.create_task(
                    sharder.spawn_ws()
                )
                
                await self._lock_sentinel.acquire()
                
            await asyncio.sleep(1)