import asyncio
from typing import (
    Callable,
    Any,
    Union,
    List,
    Optional,
    TypeVar,
    Iterator,
)

from .client import Client
from .core import Command, Event


class Bot(Client):
    ''' A rewrite version of client
    This has all : Client : functionality + more advanced features.
    '''
    def __init__(self, **option):
        super().__init__(**option)
        self._commands = []
        self._listeners = {}
        
    def command(
        self,
        *,
        name: str,
        description: str,
        slash_type: int,
        guild: Union[str, int, List[Union[str, int]]] = None
    ):
        ''' Command registers.
        Automatically generating slash commands.
        
        Parameter
        ---------
        :name: command's name
        :description: command's description,
        :slash_type: slash type
        :guild: If guild is not specified it may registered as global command.
        '''
        def inner(function: Callable[..., Any]) -> Command:
            
            command = Command(
                function,
                name=name,
                description=description,
                slash_type=slash_type,
                guild=guild
            )
            self.commands.append(command)
            return command
            
        return inner
        
    def event(
        self,
        *,
        run_once=False
    ) -> None:
        '''
        Event registers.
        
        Parameters
        ----------
        :run_once: whether the event should only run once.
        '''
        def inner(function: Callable[..., Any]):
            func_name = function.__name__
            if not asyncio.iscoroutinefunction(function):
                raise TypeError(f"'{func_name}' must ne coroutine function.")
                
            self.listeners[func_name] = Event(
                function,
                run_once=run_once,
                loop=self.loop
            )
            
        return inner
        
    def _build_command(self) -> None:
        '''
        Request for slash command.
        
        Return
        ------
        None
        '''
        for command in self.commands:
            ...
            
    async def dispatch(self, ev: str, *param) -> Optional[Any]:
        
        if (evd := self.listeners.get(ev, None)) is None or evd.dispatched:
            return None
            
        return evd(*param)
        
    @property
    def commands(self):
        return self._commands
        
    @property
    def listeners(self):
        return self._listeners