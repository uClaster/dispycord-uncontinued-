import asyncio
from typing import Optional

from .. import HTTP
from .. import AutoSharded
from ..intents import Intent

__all__ = ("Client",)


class Client(AutoSharded):
    
    """ Discord Client """
    
    def __init__(self, *, intent: int = 513):
        super().__init__()
        
        self.intent = intent
        
        self._loop = asyncio.get_event_loop()
        self._http: Optional[HTTP] = None
        
        self.user: Optional[dict] = None
    
    def run(self, token: str) -> None:
        """
        Invoking gateway to do connect mechanism.
        
        :param token: Bot's token.
        """
        self._http = HTTP(self, token=token)
        
        self._loop.run_until_complete(
            self.new_shard()
        )
        self._loop.run_forever()
        
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
        return self.user['username']
        
    @property
    def id(self):
        return self.user['id']
        
    @property
    def discriminator(self):
        return self.user['discriminator']