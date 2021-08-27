import asyncio
import json
from aiohttp import ClientWebSocketResponse
from typing import Dict, Union, TYPE_CHECKING, Optional

if TYPE_CHECKING:
	from . import ext

__all__ = ("Gateway",)

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
WSS = "wss://gateway.discord.gg/?v=8&encoding=json"


class Gateway:
	def __init__(self, *args):
		self._client: ext.Client = args[0]
		self._ws: Optional[ClientWebSocketResponse] = None
		
		self._interval: Union[int, float] = 41.25
		self._reconnect: bool = True
	
	async def connect(self) -> None:
		
		async with (
			self._client.http.client_session.ws_connect(WSS)
		) as ws:
			self._ws = ws
			
			while True:
				
				if isinstance((message := await ws.receive()).data, int):
					print("Got integer code.")
					exit(1)
					
				await self.handle_payload(
					json.loads(message.data)
				)
				
	async def identify(self) -> None:
		
		await self._ws.send_json(
			{
				"op": IDENTIFY,
				"d": {
					"token": self._client.http.token,
					"intents": 513,
					"properties": {
						"$os": "linux",
						"$browser": "dispycord",
						"$device": "dispycord"
					}
				}
			}
		)
		
		self._reconnect = False
		
	async def heartbeat(self) -> None:
		
		while True:
			
			await asyncio.sleep(
				4
				if self._reconnect
				else self._interval
			)
			
			await self._ws.send_json(
				{
					"op": HEARTBEAT,
					"d": None
				}
			)
		
	async def handle_payload(
		self,
		data: Dict[str, Union[str, int]]
	) -> None:
		
		if (op := data['op']) == HELLO:
			self._client.loop.create_task(
				self.heartbeat()
			)
			
		elif op == ACK and self._reconnect:
			self._client.loop.create_task(
				self.identify()
			)
			
		elif op == DISPATCH:
			
			ev = getattr(self._client, "on_"+data['t'].lower(), None)
			
			if ev is None:
				return None
			
			if not asyncio.iscoroutinefunction(ev):
				raise TypeError(
					f"'{ev.__name__}' must be coroutine function."
				)
				
			self._client.loop.create_task(ev())