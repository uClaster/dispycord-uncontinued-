import dispycord
from dispycord import ext


class Client(ext.Client):
	
	async def on_ready(self):
		
		print("Bot ready!!")
		
	async def on_message_create(self):
		
		print("enumerating!")
		a = [x for x in range(9999999)]
		print("completed")
		
		
client = Client(
	
	intent=dispycord.Intent.get(
		GUILDS=True,
		GUILD_MESSAGES=True
	)
	
)
	
client.run("ODQ5MTIxNDEyNjE4MjU2NDE3.YLWj8A.NTD0n0YaotYNZCNx3lgb4srrDq0")