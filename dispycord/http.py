import aiohttp
from typing import Union, Optional

__all__ = (
	"HTTP",
)

base_url = 'https://discord.com/api/v9'


class HTTP:
    def __init__(self, *args, **kwargs):
        
        self._client = args[0]
        self._client_session = aiohttp.ClientSession()
        self._token = kwargs.get('token')
        self._authorization = {'Authorization': f'Bot {self._token}'}
        
    async def Route(
        self,
        data: dict,
        endpoint: str,
        method: str
    ) -> None:
        """
        Send data to Discord HTTP
        
        Parameter
        ---------
        :data: data payload to send
        
        :endpoint: HTTP endpoint
        
        :method:	either post, delete, put, patch or get
        mostly of methods are not implemented yet.
        
        """
        url = f"{base_url}/{endpoint}"
        
        if (met := method.lower()) == 'get':
            return await self.client_session.get(url)
            
        elif met == 'post':
            data = await self.client_session.post(
                url,
                json=data,
                headers=self._authorization
            )
        
        if (status := str(data.status))[0] != '2': # type: ignore
            print(f"something went wrong: {status}")
        
    @property
    def token(self):
        return self._token
        
    @property
    def client_session(self):
        return self._client_session