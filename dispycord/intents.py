from typing import final, List

__all__ = (
	"Intent",
)


@final
class Intent:
	
	intent_list: List[str] = [
		'GUILDS',
		'GUILD_MEMBERS',
		'GUILD_BANS',
		'GUILD_EMOJIS',
		'GUILD_INTEGRATIONS',
		'GUILD_WEBHOOKS',
		'GUILD_INVITES',
		'GUILD_VOICE_STATES',
		'GUILD_PRESENCES',
		'GUILD_MESSAGES',
		'GUILD_MESSAGE_REACTIONS',
		'GUILD_MESSAGE_TYPING',
		'DIRECT_MESSAGES',
		'DIRECT_MESSAGE_REACTIONS',
		'DIRECT_MESSAGE_TYPING'
	]
	
	@classmethod
	def all(cls) -> int:
		""" Using all intent. ( not recommended. ) """
		return 32767
	
	@classmethod
	def default(cls) -> int:
		""" Default Intent """
		return 513
		
	@classmethod
	def get(cls, **intent) -> int:
		""" User defined intent """
		return (
			sum(
				[
					1 << cls.intent_list.index(i)
					if val in cls.intent_list else 0
					for i, val in intent.items()
				]
			)
		)