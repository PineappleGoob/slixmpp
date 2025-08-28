# This example requires the 'message_content' intent.
from slixmpp import ClientXMPP
import logging
import asyncio
import slixmpp
from getpass import getpass
from argparse import ArgumentParser
import queue
import discord
import threading
from threading import Lock
import xmpp
import time
import json
#discord setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

with open('config.json','r') as f:
	configs = json.load(f)


# event from xmpp to discord
tevent = asyncio.Event()
#event from discord to xmpp
devent = threading.Event()

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
    print(message.content)
    with list_lock:
        global dshared_list
        #puts message in da queue
        dshared_list.append(message.content)
        print(dshared_list)
    devent.set()
    print('event set')

#manages sending the queued xmpp messages to da discord
async def messagemachine():
        print('waiting for event')
        await tevent.wait()
        channel = client.get_channel(1065988089769631796)
        global xshared_list
        messagetosend = xshared_list[0]
        xshared_list = xshared_list[1:]
        tevent.clear()
        await channel.send(messagetosend)	
        await messagemachine()	



#xmpp class
class BOot(slixmpp.ClientXMPP):
    #initalization
    def __init__(self, jid, password):
        super().__init__(jid, password) 
        
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)


    #on start xmpp
    async def start(self, event):
        print('started and connected to xmpp')
        await self.messagemachine()
        self.send_presence()
        await self.get_roster()

    async def messagemachine(self):
        print('waiting for event x')
        #jid = xmpp.protocol.JID(configs['XmppUser'])
        #connection = xmpp.Client(server=jid.getDomain(), debug=True)
        #connection.connect()
        #connection.auth(user=jid.getNode(), password=configs['XmppPass'], resource=jid.getResource())

        devent.wait()
        devent.clear()
        global dshared_list
        print('huzzahsdfd')
        msgs = dshared_list[0]
        print('sending')
		slixmpp.ClientXMPP.send_message(mto=configs['Recipient'], body=msgs)
        #connection.send(xmpp.protocol.Message(to=configs['Recipient'], body=msgs))
        await self.messagemachine()




    #on message
    async def message(self, msg):
        #prints message
        #print(msg['body'])
        #locks
        with list_lock:
            #puts message in da queue
            xshared_list.append(msg['body'])
            print(xshared_list)
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
	xmpp = BOot (configs['XmppUser'], configs['XmppPass']) #jid, password
	xmpp.register_plugin('xep_0030') # Service Discovery
	xmpp.register_plugin('xep_0199') # Ping
	xmpp.connect()
	# 3. Use the correct loop object to run the Slixmpp processing loop.
	loop.run_forever()

if __name__ == '__main__':

        
     #discord starting   
    def discordthing(): 
        client.run(configs['BotToken'])
        
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
		
		

