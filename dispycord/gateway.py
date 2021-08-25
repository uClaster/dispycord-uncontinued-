import aiohttp
import asyncio
import json 
from typing import Dict, Union, TYPE_CHECKING 

if TYPE_CHECKING:
	from . import ext

__all__ = ("Gateway",)

wss = "wss://gateway.discord.gg/?v=8&encoding=json"


class Gateway:
	
	def __init__(self, *args):
		self._client: ext.Client = args[0]
	
	async def connect(self) -> None:
		
		async with (
			self._client.http.client_session.ws_connect(wss)
		) as ws:
			
			while True:
				message = await ws.receive()
				await self.handle_payload(
					json.loads(message.data)
				)
				
	async def handle_payload(
		self,
		data: Dict[str, Union[str, int]]
	) -> None:
		
		print(data)