import dispycord
from dispycord import ext

bot = ext.Bot(
	intent=dispycord.Intent.get(
		GUILDS=True,
		GUILD_MESSAGES=True
	)
)


@bot.command(
	guild=849122408043380747,
	name='choose',
	description='ban people',
	type=1
)
async def ban_slash():
	...


@bot.event(run_once=True)
async def on_ready():
	print(f"Logging in as: {bot}")
	print(f"Commands: {bot.commands}\nListeners: {bot.listeners}")
	
bot.run("ODQ5MTIxNDEyNjE4MjU2NDE3.YLWj8A.NTD0n0YaotYNZCNx3lgb4srrDq0")