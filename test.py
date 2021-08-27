from dispycord import ext


class Client(ext.Client):
	
	async def on_ready(self):
		
		print("Bot Ready!!")
		
client = Client()
client.run("ODQ5MTIxNDEyNjE4MjU2NDE3.YLWj8A.NTD0n0YaotYNZCNx3lgb4srrDq0")