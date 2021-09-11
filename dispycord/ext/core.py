import inspect
from typing import (
    Callable,
    Any,
    Union,
    Optional,
    Literal,
    List,
    )

F = Callable[..., Any]


class Command:
    
    def __init__(
        self,
        callback: Callable[..., Any],
        *,
        name: str,
        description: str,
        slash_type: int,
        guild: Optional[Union[int, List[int]]] = None
    ):

        self._callback: F = callback
        
        self.name: str = name
        self.description: str = description
        self.type: int = slash_type
        self.guild: Optional[Union[int, List[int]]] = guild
        
        self._error: Optional[F] = None
        
    def error(
        self,
        error_func: Callable[..., Any]
    ) -> None:
        """
        An error handler when slash returning error signal.
        | Not Implemented |
        """
        if not inspect.iscoroutinefunction(error_func):
            return
        
        self._error = error_func
        
    def is_global(self) -> bool:
        """ It is global slash command?
        
        Return
        -------
        True if guild is not Nonetype.
        else False
        """
        return True if self.guild is None else False
    
    def to_dict(self) -> dict:
        ...
        
    @property
    def callback(self) -> Callable[..., Any]:
        return self._callback
        
    @property
    def has_error_handler(self) -> Union[bool, F]:
        return self._error or False
        
        
class Event:
    
    def __init__(
        self,
        function: F,
        *,
        run_once: bool = False,
        loop
    ):
        self._function = function
        self.run_once = run_once
        self._dispatched = False
        
        self._loop = loop
        
    def __call__(self, *param) -> Any:
        if self.run_once:
            self._dispatched = True
        return self._loop.create_task(
            self._function(*param)
        )
        
    @property
    def dispatched(self) -> bool:
        return self._dispatched