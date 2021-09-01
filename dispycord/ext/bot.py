import asyncio
from typing import Callable, Any, Union

from .client import Client
from .core import Command


class Bot(Client):
	
	''' A rewrite version of client
	This has all : Client : functionality + more advanced features.
	'''
	
	def __init__(self, **option):
		super().__init__(**option)
		self._commands: list = []
		self._listeners: dict = {}
	
	def command(self, **option):
		''' Command registers.
		Automatically generating slash commands.
		
		Parameter
		-----------
		
		:param option:
		---------------
			| guild_only: book
		'''
		def inner(function: Callable[..., Any]) -> Command:
			
			command = Command(
				function,
				**option
			)
			self._commands.append(command)
			return command
			
		return inner
		
	def event(self, **option):
		'''option param
		An event registering.
		
		:param option.run_once: whether the event should only run once.
		'''
		def inner(function: Callable[..., Any]):
			self.add('listeners', function, option)
			
		return inner
			
	def add(
		self,
		bound: str,
		function: Callable[..., Any],
		opt: dict
	) -> None:
		'''
		Helper to insert callable to :bound:
		
		:param bound: A dict that contains comand or listener.
		:param function: command's or event's function.
		:param opt: command's or event's kwargs.
		'''
		if not asyncio.iscoroutinefunction(function):
			raise TypeError(f"'{function.__name__}' must be coro.")
			
		if (types := getattr(self, bound)) is None:
			raise NameError(f"Couldn't get '{bound}'")
			
		opt['function'] = function
		types[function.__name__] = opt
		
	@property
	def listeners(self):
		return self._listeners
		
	@property
	def commands(self):
		return self._commands