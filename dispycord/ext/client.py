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
		
		self.data: Optional[dict] = None
	
	def run(self, token: str) -> None:
		"""
		Invoking gateway to do connect mechanism.
		
		:param token: Bot's token.
		"""
		self._gateway = Gateway(self)
		self._http = HTTP(self, token=token)
		
		self._loop.run_until_complete(
			self._gateway.connect()
		)
		
	def __repr__(self):
		return self.name + '#' + self.discriminator
		
	@property
	def loop(self):
		return self._loop
		
	@property
	def http(self):
		return self._http
		
	@property
	def name(self):
		return self.data['username']
		
	@property
	def id(self):
		return self.data['id']
		
	@property
	def discriminator(self):
		return self.data['discriminator']