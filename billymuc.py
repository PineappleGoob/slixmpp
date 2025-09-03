# This example requires the 'message_content' intent.
from slixmpp import ClientXMPP
import logging
import asyncio
from getpass import getpass
from argparse import ArgumentParser
import queue
import discord
from discord import app_commands, SyncWebhook
import threading
from threading import Lock
import xmpp
import slixmpp_omemo
import time
import aiohttp
from discord.ext import commands
import json
import base64
import requests
#discord setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
# event from xmpp to discord
tevent = asyncio.Event()
xmpp_loop = None

#event from discord to xmpp
devent = threading.Event()

with open('config.json', 'r') as file:
    config = json.load(file)
with open('webhook.json', 'r') as file:
    webhooks = json.load(file)

avatar_data = None
#list for xmpp messages to queue up for discord to send
xshared_list = []
list_lock = Lock()

#list for discord messages to queue up for xmpp to send
dshared_list = []
xqueue = asyncio.Queue()

#discord on startup
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await tree.sync()
    asyncio.create_task(messagemachine())
			#send message 

webhookurl = None
@tree.command(name='setup', description='Run this before you do anything. Very important')
async def setup(interaction: discord.Interaction):
    channel = interaction.channel
    global webhookurl
    for mapping in webhooks.get("guildids", []):
        print(interaction.guild_id)
        print(mapping)
        if str(interaction.guild_id) in mapping:
            webhookurl = mapping[str(interaction.guild_id)]
            print(webhookurl)
            break
    if webhookurl:
        webhooksending = SyncWebhook.from_url(webhookurl)
        webhooksending.send('test')
    else:
        webhoook = await channel.create_webhook(name='Sky.Bit')
        webhooks["guildids"].append({str(interaction.guild_id): str(webhoook.url)})
        with open('webhook.json', 'w') as file:
            json.dump(webhooks, file, indent=4)




#manages sending the queued xmpp messages to da discord
import aiohttp
from discord import Webhook

async def messagemachine():
    global xshared_list, webhookurl
    channel = client.get_channel(1065988089769631796)

    async with aiohttp.ClientSession() as session:
        while True:
            if xshared_list:
                messagetosend = xshared_list.pop(0)

                if webhookurl:
                    webhook = Webhook.from_url(webhookurl, session=session)
                    await webhook.send(
                        messagetosend,
                        username='SkydotBit',
                        avatar_url='https://skydevs.me/foxxo.gif'
                    )
                    print('Message sent via async webhook')
                else:
                    await channel.send('Run /setup to make stuff work')

            await asyncio.sleep(0.05)  # yield control to the event loop


#discord to xmpp
@client.event
async def on_message(message):
    if message.author.bot or message.author == client.user:
        return
    
    print(message.content)
    # Push the message to the XMPP queue
    dshared_list.append(message.content)
    print("Message queued for XMPP")
"""""
    #if message is from bot return
    if message.author == client.user:
        return
    if message.author.bot:
        return
    print(message.content)
    with list_lock:
        global dshared_list
        #puts message in da queue
        dshared_list.append(message.content)
        print(dshared_list)
        jid = xmpp.protocol.JID(config['User'])
        connection = xmpp.Client(server=jid.getDomain(), debug=True)
        connection.connect()
        connection.auth(user=jid.getNode(), password=config['Pass'], resource=jid.getResource())
        connection.sendInitPresence()  # essential
        while dshared_list:
            msgs = dshared_list.pop(0)
            connection.send(xmpp.protocol.Message(to=config['Recipient'], body=msgs, typ="chat"))

    #devent.set() temporaryily disable until find better fix here.
    print('event set')
"""
#xmpp class
class BOot(ClientXMPP):
    #initalization
    def __init__(self, jid, password):
        super().__init__(jid, password) 
   
        self.room = 'hasibixo@muc.xmpp.skydevs.me'
        self.nick = 'Discord'     
        self.add_event_handler('session_start', self.start)
        self.add_event_handler("groupchat_message", self.muc_message)

        #self.register_plugin('xep_0384')



    #on start xmpp
    async def start(self, event):
        print('started and connected to xmpp')
        self.send_presence()
        await self.get_roster()
        await self.plugin['xep_0045'].join_muc(self.room, self.nick)
        asyncio.create_task(self.process_discord_queue())
        self.add_event_handler(
            "muc_joined",
            lambda room, **kwargs: self.send_message(
                mto=self.room,
                mbody="I heard that",
                mtype="groupchat"
            )
        )

    def muc_joined(self, room):
        print('maybe sent?')
        if room == self.room:
            self.send_message(
                mto=self.room,
                mbody="I heard that",
                mtype="groupchat"
            )

    def muc_message(self, msg):
        if msg['mucnick'] != self.nick and self.nick in msg['body']:
            self.send_message(mto=msg['from'].bare,
                            mbody="I heard that, %s." % msg['mucnick'],
                            mtype='groupchat')

        
    async def messagemachine(self):
        



        while True:
            print('waiting for event x')
            devent.wait()
            devent.clear()
            global dshared_list
            print('huzzahsdfd')
            msgs = dshared_list.pop(0)
            print('sending')
            print('sent?')
            #await self.messagemachine() 



    async def sendmessager(self, msg):
        print('test')
        self.send_message('jibberbob@conversations.im',msg,mtype='chat')
        


    async def retrieve_avatar(self, jid):
        vcard = await self['xep_0054'].get_vcard(jid=config['Recipient'])

        photo_elem = vcard.xml.find('{vcard-temp}PHOTO')  # correct namespace
        if photo_elem is not None:
            binval = vcard['BINVAL']
            if binval is not None:
                avatar_bytes = binval.text.encode('utf-8')
                with open("avatar.jpg", "wb") as f:
                    import base64
                    f.write(base64.b64decode(avatar_bytes))
        else:
            print("No photo element found")

    async def process_discord_queue(self):
        while True:
            global dshared_list
            if dshared_list:
                with list_lock:  # lock to prevent race conditions
                    msg = dshared_list.pop(0)
                print('sending')
                self.send_message(
                    mto=str(config['Recipient']),
                    mbody=msg,
                    mtype='chat'
                )
                print(f"Sent to XMPP: {msg}")
            await asyncio.sleep(0.05)  # yield to the event loop


    #on message
    async def message(self, msg):
        print('received thy message')
        #prints message
        print(msg)
        print(msg['body'])
        await self.retrieve_avatar(config['Recipient'])

        #decrypted = self['xep_0384'].decrypt_message(msg['body'])
        #print(decrypted)
        #locks
        with list_lock:
            #puts message in da queue
            xshared_list.append(msg['body'])
            tevent.set()
            print(xshared_list)
        print()
        #sets off tevent
        if msg['type'] in ('normal', 'chat'):
            #if encrypted request decryption
            if msg['body'] == '[This message is OMEMO encrypted]':
               msg.reply('Please turn off Omemo (or possibly other) encryptions because I cant see em :(').send()
               print('sent')
            else:
               print('received?')
               #channel = client.get_channel(1065988089769631796)
               #channel.send('a')



         #   msg.reply("Thanks for sending:\n%s" % msg['body']).send()


def xmppthing(): 
    # 1. Create a new event loop for this thread.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(xmpp_loop)
    # 2. Set the new event loop as the current one for this thread.
    asyncio.set_event_loop(loop)
    xmpp = BOot (config['User'], config['Pass']) #jid, password
    xmpp.register_plugin('xep_0030')  # Service Discovery
    xmpp.register_plugin('xep_0199')  # Ping
    xmpp.register_plugin('xep_0045')  # MUC
    xmpp.register_plugin('xep_0084')  # Omemo
    xmpp.register_plugin('xep_0054')  # vCard
    xmpp.register_plugin('xep_0060')
    xmpp.register_plugin('xep_0163')
    xmpp.connect()
    # 3. Use the correct loop object to run the Slixmpp processing loop.
    loop.run_forever()
    loop.call_soon_threadsafe(tevent.set)

if __name__ == '__main__':

        
     #discord starting   
    def discordthing(): 
        client.run(config['token'])
        
     #manages all the threads and shit   
    thread1 = threading.Thread(target=discordthing)
    thread2 = threading.Thread(target=xmppthing)
    thread2.start()
    thread1.start()
    thread2.join()
    thread1.join()


"""    # Setup the command line arguments.
    parser = ArgumentParser(description=BOot.__doc__)

    # Output verbosity options.
    parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                        action="store_const", dest="loglevel",
                        const=logging.ERROR, default=logging.INFO)
    parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                        action="store_const", dest="loglevel",
                        const=logging.DEBUG, default=logging.INFO)

    # JID and password options.
    parser.add_argument("-j", "--jid", dest="jid",
                        help="JID to use")
    parser.add_argument("-p", "--password", dest="password",
                        help="password to use")

    args = parser.parse_args()

    if args.jid is None:
        args.jid = input("Username: ")
    if args.password is None:
        args.password = getpass("Password: ")
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')"""
		
		


