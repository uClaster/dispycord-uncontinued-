import asyncio
import json
from aiohttp import ClientWebSocketResponse, WSMsgType
from typing import Dict, Union, TYPE_CHECKING, Optional

from .intents import Intent
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
WSS = "wss://gateway.discord.gg/?v=8&encoding=json"


class Gateway:
	def __init__(self, *args, **options):
		self._client: ext.Client = args[0]
		self._ws: Optional[ClientWebSocketResponse] = None
		
		self._interval: Union[int, float] = 41.25
		self._acked: bool = False
		self._resuming: bool = False
		
		self._intents: int = options.get("intent", Intent.default())
		
		self._session_id: str = ''
		self._seq: Optional[int] = None
	
	async def connect(self) -> None:
		
		async with (
			self._client.http.client_session.ws_connect(WSS)
		) as ws:
			self._ws = ws
			
			while True:
				
				if (message := await ws.receive()).type in (WSMsgType.CLOSE, WSMsgType.CLOSED,):
					await self.handle_disconnect(
						code=str(message.data),
						extra=message.extra
					)
				
				try:
					await self.handle_payload(
						json.loads(message.data)
					)
				except TypeError:
					break
				
		if not self._acked:
			await self._client.loop.close()
			exit(1)
			
		await self.connect()
		
	async def identify(self) -> None:
		
		if self._acked:
			return None
		
		await self._ws.send_json(
			{
				"op": IDENTIFY,
				"d": {
					"token": self._client.http.token,
					"intents": self._intents,
					"properties": {
						"$os": "linux",
						"$browser": "dispycord",
						"$device": "dispycord"
					}
				}
			}
		)
		
		self._acked = True
		
	async def heartbeat(self) -> None:
		
		while True:
			
			await asyncio.sleep(
				self._interval
				if self._acked
				else 4
			)
			
			await self._ws.send_json(
				{
					"op": HEARTBEAT,
					"d": None
				}
			)
			
	async def resume(self) -> None:
		
		await self._ws.send_json(
			{
				"op": RESUME,
				"d": {
					"token": self._client.http.token,
					"session_id": self._session_id,
					"seq": self._seq
				}
			}
		)
		
		self._resuming = False
			
	async def handle_disconnect(
		self,
		**data
	) -> None:
		
		if (code := data.get('code')) in error.keys():
			raise error[code](data.get("extra"))
			
		if (extra := data.get('extra')) is None:
			
			await self._ws.close(code=1002)
			self._resuming = True
		
	async def handle_payload(
		self,
		data: Dict[str, Union[str, int]]
	) -> None:
		
		if isinstance(s := data['s'], int):
			self._seq = s
		
		if (op := data['op']) == HELLO:
			self._client.loop.create_task(
				self.heartbeat()
			)
			
		elif op == ACK:
			
			if self._resuming:
				await self.resume()
			
			self._client.loop.create_task(
				self.identify()
			)
			
		elif op == DISPATCH:
			
			if data['d'].get('session_id', None) is not None:
				self._session_id = data['d']['session_id']
			
			ev = getattr(self._client, "on_" + data['t'].lower(), None)
			
			if ev is None:
				return None
			
			if not asyncio.iscoroutinefunction(ev):
				raise TypeError(
					f"'{ev.__name__}' must be coroutine function."
				)
				
			self._client.loop.create_task(ev())
			
		elif op == RECONNECT:
			
			print("Bot reconnected after resumed.")