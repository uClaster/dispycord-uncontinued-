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
WSS = "wss://gateway.discord.gg/?v=9&encoding=json"


class Gateway:
	def __init__(self, *args, **options):
		self._client: Union[ext.Bot, ext.Client] = args[0]
		self._ws: Optional[ClientWebSocketResponse] = None # type: ignore
		
		self._interval: Union[int, float] = 41.25
		self._acked: bool = False
		self._resuming: bool = False
		
		self._intents: int = options.get("intent", Intent.default())
		
		self._session_id: Optional[str] = None
		self._seq: Optional[int] = None
	
	async def connect(self) -> None:
		"""
		Listen for gateway messages.
		| Messages category are depends on bot's intents.
		"""
		async with self._client.http.client_session.ws_connect(WSS) as ws:
			self._ws = ws
			
			while True:
				
				if (message := await ws.receive()).type in (WSMsgType.CLOSE, WSMsgType.CLOSED,):
					await self.emit_closing(
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
			exit(1)
			
		await self.connect()
		
	async def identify(self) -> None:
		"""
		If this section is accepted, your bot will on ready state.
		Additional information:
		
		| token: your bot's token
		| intents: bot's intents. default is 513.
		| browser: Library's name
		| device: Library's name
		"""
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
		"""
		Start heartbeat.
		| this way is to maintain connection between client and server
		"""
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
		"""
		An expected call when your bot's got disconnected.
		| Not Tested |
		"""
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
			
	async def emit_closing(
		self,
		**data
	) -> None:
		"""
		Showing's the websockets closing reason.
		| check whether resume is possible.
		"""
		if (code := data.get('code')) in error.keys():
			raise error[code](data.get("extra"))
			
		if data.get('extra') is None:
			
			await self._ws.close(code=1002)
			self._resuming = True
		
	async def handle_payload(
		self,
		data: Dict[str, Union[str, int]]
	) -> None:
		
		""" Handle messages payload """
		
		if isinstance(s := data['s'], int):
			self._seq = s
		
		if (op := data['op']) == HELLO:
			self._client.loop.create_task(
				self.heartbeat()
			)
			
		elif op == ACK:
			
			if self._resuming:
				await self.resume()
				
			if self._acked:
				return
			
			self._client.loop.create_task(
				self.identify()
			)
			
		elif op == RECONNECT:
			...
			
		elif op == DISPATCH:
			print("dispatch")
			if (t := data['t'].lower()) == 'ready': # type: ignore
				
				self._session_id = data['d']['session_id'] # type: ignore
				self._client.data = data['d']['user'] # type: ignore
				
				for command in self._client.commands: # type: ignore
					
					slash_option: dict = command.to_dict()
					
					endpoint: str = f'/applications/{self._client.id}/commands'
					
					if not command.is_global():
						guild = slash_option.pop('guild')
						endpoint = f'/applications/{self._client.id}/guilds/{guild}/commands'
					
					await self._client.http.Route(
						slash_option,
						endpoint,
						'POST'
					)
				
			if (ev := self._client.listeners.get('on_'+t, None)) is not None: # type: ignore
				self._client.loop.create_task(ev['function']())