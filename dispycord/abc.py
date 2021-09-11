from typing import overload, Optional

from . import http
from .embeds import Embed


class MessageAble:
    '''
    MessageAble model for
    :abc.User:
    :abc.TextChannel:
    '''
    async def send(
        self,
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = False,
        embed: Optional[Embed] = None,
        message_reference: Optional[int] = None
    ) -> None:
        
        raw = {}
        
        raw['tts'] = tts
        
        if content:
            raw['content'] = content
            
        if isinstance(embed, Embed):
            raw['embeds'] = embed.to_dict
            
        if message_reference:
            raw['message_reference'] = message_reference
            
        await self.message._http.Route(
            raw,
            f'/channels/{self.id}/messages',
            'POST'
        )
        
    async def reply(
        self,
        content: Optional[str] = None,
        *,
        tts: Optional[bool] = False,
        embed: Optional[Embed] = None
    ) -> None:
        
        await self.send(
            content,
            tts=tts,
            embed=embed,
            message_reference = {
                'message_id': self.message.id,
                'channel_id': self.id,
                'guild_id': self.guild.id,
            }
        )
        
        
class Guild:
    
    def __init__(self, message: 'Message'):
        
        self.id = message.raw.get('guild_id')
        

class User(MessageAble):
    
    def __init__(self, message: 'Message'):
        
        self.name: str = message.raw['author']['username']
        self.discriminator: str = message.raw['author']['discriminator']
        self.id: int = message.raw['author']['id']
        self.avatar_url = message.raw['author']['avatar']
        
    @property
    def mention(self):
        return f'<@{self.id}>'


class TextChannel(MessageAble):
    
    def __init__(self, message: 'Message'):
        
        self.id: int = message.raw['channel_id']
        self.message = message
        self.guild = Guild(message)
        
    @property
    def mention(self):
        return f'<#{self.id}>'


class Message:
    
    def __init__(self, http: http.HTTP, payload: dict):
        
        self.content: str = payload['content']
        self.id: int = payload['id']
        
        self._http = http
        self.raw = payload
        
        self.channel: TextChannel = TextChannel(self)
        self.author: User = User(self)
        self.guild: Guild = Guild(self)