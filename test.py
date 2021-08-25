from dispycord import ext


class Client(ext.Client):
	
	async def on_ready(self):
		...
		
		
client = Client()
client.run("token")