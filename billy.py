# This example requires the 'message_content' intent.
from slixmpp import ClientXMPP
import logging
import asyncio
from getpass import getpass
from argparse import ArgumentParser
import queue
import discord
import threading
from threading import Lock
import xmpp
import slixmpp_omemo
import time
import aiohttp
import base64
#discord setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# event from xmpp to discord
tevent = asyncio.Event()
#event from discord to xmpp
devent = threading.Event()


avatar_data = None
#list for xmpp messages to queue up for discord to send
xshared_list = []
list_lock = Lock()

#list for discord messages to queue up for xmpp to send
dshared_list = []


#discord on startup
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await messagemachine()
			#send message 

#discord to xmpp
@client.event
async def on_message(message):
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
        jid = xmpp.protocol.JID('dougdoug@xmpp.skydevs.me')
        connection = xmpp.Client(server=jid.getDomain(), debug=True)
        connection.connect()
        msgs = dshared_list.pop(0)
        connection.auth(user=jid.getNode(), password='dougdoug', resource=jid.getResource())
        connection.send(xmpp.protocol.Message(to='jibberbob@conversations.im', body=msgs))
    #devent.set() temporaryily disable until find better fix here.
    print('event set')

#manages sending the queued xmpp messages to da discord
async def messagemachine():
        while True:
            print('waiting for event')
            await tevent.wait()
            print('evento activato')
            channel = client.get_channel(1065988089769631796)
            global xshared_list

            messagetosend = xshared_list.pop(0)
            tevent.clear()
            async with aiohttp.ClientSession() as session:
                async with session.get("https://skydevs.me/foxxo.gif") as resp:
                    avatar_bytes = await resp.read()

            webhoook = await channel.create_webhook(name='Sky.Bit', avatar=avatar_bytes)
            await webhoook.send(messagetosend)	
            print('sent')



#xmpp class
class BOot(ClientXMPP):
    #initalization
    def __init__(self, jid, password):
        super().__init__(jid, password) 
        
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', lambda msg: asyncio.create_task(self.message(msg)))
        #self.register_plugin('xep_0384')



    #on start xmpp
    async def start(self, event):
        print('started and connected to xmpp')
        self.send_presence()
        await self.get_roster()

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
        vcard = await self['xep_0054'].get_vcard(jid='sky.bit@xmpp.skydevs.me')

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




    #on message
    async def message(self, msg):
        print('received thy message')
        #prints message
        print(msg)
        print(msg['body'])
        await self.retrieve_avatar('sky.bit@xmpp.skydevs.me')

        #decrypted = self['xep_0384'].decrypt_message(msg['body'])
        #print(decrypted)
        #locks
        with list_lock:
            #puts message in da queue
            xshared_list.append(msg['body'])
            print(xshared_list)
        print()
        #sets off tevent
        tevent.set()
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
	# 2. Set the new event loop as the current one for this thread.
	asyncio.set_event_loop(loop)
	xmpp = BOot ('dougdoug@xmpp.skydevs.me', 'dougdoug') #jid, password
	xmpp.register_plugin('xep_0030') # Service Discovery
	xmpp.register_plugin('xep_0199') # Ping
	xmpp.register_plugin('xep_0084') # omemo :)
	xmpp.register_plugin('xep_0054') # omemo :)
	xmpp.register_plugin('xep_0060') # omemo :)
	xmpp.register_plugin('xep_0163') # omemo :)
	xmpp.connect()
	# 3. Use the correct loop object to run the Slixmpp processing loop.
	loop.run_forever()

if __name__ == '__main__':

        
     #discord starting   
    def discordthing(): 
        client.run('MTQxMDA0MTE2NzQ5MTM2NzEzMg.G_I9SK.s8GgS7TUX2Iy7KUPaG9dnNasAyqowqe7i3vYN8')
        
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
		
		


