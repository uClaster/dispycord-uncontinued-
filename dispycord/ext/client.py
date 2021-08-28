import asyncio
from typing import Optional

from .. import Gateway
from .. import HTTP

__all__ = ("Client",)


class Client:
	
	""" Discord Client """
	
	def __init__(self, **kwargs):
		
		self._loop: asyncio.Loop = asyncio.get_event_loop()
		self._lock: asyncio.Lock = asyncio.Lock
		self._gateway: Optional[Gateway] = None
		self._http: Optional[HTTP] = None
	
	def run(self, token: str) -> None:
		"""
		If succeed, your bot will on ready state.
		
		:param token: Bot's token.
		"""
		self._gateway = Gateway(self)
		self._http = HTTP(self, token=token)
		
		self._loop.run_until_complete(
			self._gateway.connect()
		)
		
	@property
	def loop(self):
		return self._loop
		
	@property
	def http(self):
		return self._http