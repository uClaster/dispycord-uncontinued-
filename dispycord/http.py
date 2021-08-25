import aiohttp
from typing import Union

__all__ = ("HTTP",)


class HTTP:
	
	def __init__(self, *args, **kwargs):
		
		self._client = args[0]
		self._client_session = aiohttp.ClientSession()
		self._token = kwargs.get('token')
		
	def Route(self) -> Union[dict, str]:
		
		return {}
		
	@property
	def token(self):
		return self._token
		
	@property
	def client_session(self):
		return self._client_session