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
from typing import TYPE_CHECKING, Union

import aiohttp

if TYPE_CHECKING:
	from . import ext

__all__ = (
	'AutoSharded',
	'Shard',
)

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


class Shard:
	
	def __init__(
		self,
		client: Union['ext.Bot', 'ext.Client'],
		shard_id: int
	):
		
		self._client = client
		
		self.shard_id = shard_id
		self.num_shards = self._client.num_shards
		
		self._ws = None
		self._acked: bool = False
		self._interval: Union[int, float] = 41.25
		
	def logging(self, message: str) -> None:
		print(f"Shard {self.shard_id}: {message}")
		
	async def identify(self) -> None:
		
		if self._acked:
			return
		
		self.logging("IDENTIFYING")
		
		await self._ws.send_json({
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
		await self.next_shard()
		
	async def spawn_ws(self) -> None:
		
		self.logging("Attempt to connect.")
		
		async with self._client.http.client_session.ws_connect(WSS) as ws:
			self._ws = ws
			
			while True:
				
				if (message := await ws.receive()).extra is None:
					break
				
				if (op := json.loads(message.data)['op']) == HELLO:
					
					self._client.loop.create_task(
						self.start_heartbeat()
					)
					
				elif op == ACK:
					
					await self.identify()
					
				elif op == INVALID_SESSION:
					self.logging("Failed to identify.")
	
	async def start_heartbeat(self) -> None:
		
		while True:
			
			await asyncio.sleep(
				4
				if self._acked is False
				else self._interval
			)
			
			self.logging("heartbeating")
			
			await self._ws.send_json(
				{
					'op': HEARTBEAT,
					'd': None
				}
			)
			
	async def next_shard(self) -> None:
		''' Calling for next shard '''
		try:
			await self._client._lock.release()
		except:
			...
		
		
class AutoSharded:
	
	def __init__(self):
		
		self.num_shards = 2
		self.shards: dict = {}
	
	async def new_shard(self) -> None:
		''' Creating new shard object '''
		for shard in range(self.num_shards):
			
			sharder = Shard(
				self,
				shard
			)
			
			self.shards['shard' + str(shard)] = sharder
			
			async with self._lock:
				
				self.loop.create_task(
					sharder.spawn_ws()
				)
				
				await self._lock.acquire()
				
			await asyncio.sleep(1)