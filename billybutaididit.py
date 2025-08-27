import asyncio
import logging
from slixmpp import ClientXMPP
import discord

logging.basicConfig(level=logging.INFO)

DISCORD_TOKEN = 'MTQxMDA0MTE2NzQ5MTM2NzEzMg.GUSxC6.f5GSQUT3ZNLvVbcV5scshVBw_qdNb4Fma3dCrw'
XMPP_JID = 'pinedev@yax.im'
XMPP_PASS = 'Amir3132'

# Discord client
intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)

@discord_client.event
async def on_ready():
    print(f'Discord logged in as {discord_client.user}')

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return
    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

# Slixmpp client
class BOot(ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

    async def message(self, msg):
        print(msg['body'])
        if msg['type'] in ('normal', 'chat'):
            await asyncio.sleep(0)  # placeholder for async work

async def main():
    xmpp = BOot(XMPP_JID, XMPP_PASS)
    xmpp.register_plugin('xep_0030')  # Service Discovery
    xmpp.register_plugin('xep_0199')  # Ping

    # Connect slixmpp
    await xmpp.connect()
    # Run both Discord and XMPP concurrently
    await asyncio.gather(
        discord_client.start(DISCORD_TOKEN),
        xmpp.process(forever=True)
    )

asyncio.run(main())
