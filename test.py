import asyncio
import logging

import dispycord
from dispycord import ext

#logging.basicConfig(level=logging.DEBUG)

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
	slash_type=1
)
async def ban_slash():
	...


@bot.event(run_once=True)
async def on_ready():
	print(f"Logging in as: {bot}")
	
	
@bot.event(run_once=False)	
async def on_message_create(message):
    
    if message.author.id == bot.id:
        return
    
    if (cmd := message.content.lower().split())[0] == '!remind':
        secs = cmd[1]
        
        emby = dispycord.Embed(
            title='Reminder',
            description=f'Waiting for {secs} seconds.'
        )
        
        emby.set_footer(
            text=message.author.name,
            icon_url=message.author.avatar_url
        )
        
        await message.channel.send(embed=emby)
        
        await asyncio.sleep(int(secs))
        
        await message.channel.send(f"Wake up! {message.author.mention}")
	
bot.run("ODQ5MTIxNDEyNjE4MjU2NDE3.YLWj8A.NTD0n0YaotYNZCNx3lgb4srrDq0")