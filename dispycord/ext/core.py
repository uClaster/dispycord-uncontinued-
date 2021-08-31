import inspect
from typing import Callable, Any, Union, Optional, Literal

F = Callable[..., Any]


class Command:
	
	def __init__(
		self,
		callback: Callable[..., Any],
		**option
	):

		self._callback: F = callback
		self._option = option
		
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
		
	def is_global(self) -> Literal[True, False]:
		""" It is global slash command?
		
		Return
		-------
		True if there's guild keyword in self._option
		else False
		"""
		return (
			True
			if self._option.get('guild', None) is None
			else False
		)
	
	def to_dict(self) -> dict:
		return self._option
		
	@property
	def callback(self) -> Callable[..., Any]:
		return self._callback
		
	@property
	def has_error_handler(self) -> Union[bool, F]:
		return self._error or False