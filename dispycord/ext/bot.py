import asyncio
from typing import Callable, Any, Union

from .client import Client
from .core import Command


class Bot(Client):
	
	""" A rewrite version of client
	This has all : Client : functionality + more advanced features.
	"""
	
	def __init__(self, **option):
		super().__init__(**option)
		self._commands: dict = {}
		self._listeners: dict = {}
	
	def command(self, **option):
		"""option param
		
		:param option.slash_command:
		
			If this is set to True, the command will be slash command.
				Else it will be normal command with message invoking.
				
				Note: You should use slash command instead of with message command
						As Discord expect us to migrate to slash command per 2022 and
						You will have to enabled message privileged intent afterall.
		"""
		def inner(function: Callable[..., Any]):
			self.add('_commands', function, option)
			
		return inner
		
	def event(self, **option):
		"""option param
		An event registering.
		
		:param option.run_once: whether the event should only run once.
		"""
		def inner(function: Callable[..., Any]):
			self.add('_listeners', function, option)
			
		return inner
			
	def add(
		self,
		bound: str,
		function: Callable[..., Any],
		opt: dict
	) -> None:
		"""
		Helper to insert data to :bound:
		
		:param bound: A dict that contains command or listener.
		:param function: command's or event's function.
		:param opt: command's or event's kwargs.
		"""
		if not asyncio.iscoroutinefunction(function):
			raise TypeError(f"'{function.__name__}' must be coro.")
			
		if (types := getattr(self, bound)) is None:
			raise NameError(f"Couldn't get '{bound}'")
			
		opt['function'] = function
		types[function.__name__] = opt
			
	@property
	def commands(self):
		return self._commands
		
	@property
	def listeners(self):
		return self._listeners