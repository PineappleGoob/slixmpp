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

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


tevent = threading.Event()
shared_list = []
list_lock = Lock()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await messagemachine()
			#send message 

async def messagemachine():
        print('waiting for event')
        tevent.wait()
        channel = client.get_channel(1065988089769631796)
        global shared_list
        messagetosend = shared_list[0]
        shared_list = shared_list[1:]
        tevent.clear()
        await channel.send(messagetosend)	
        await messagemachine()	


class BOot(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password) 
        
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)

    async def start(self, event):
        print('started and connected to xmpp')
        self.send_presence()
        await self.get_roster()

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        

        channel = client.get_channel(1065988089769631796)
        messagetosend = shared_list[0]
        shared_list = shared_list[1:]
        await channel.send(messagetosend)

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')


    async def message(self, msg):
        print(msg['body'])
        with list_lock:
            shared_list.append(msg['body'])
            print(shared_list)
        tevent.set()
        if msg['type'] in ('normal', 'chat'):
            if msg['body'] == '[This message is OMEMO encrypted]':
               msg.reply('Please turn off Omemo (or possibly other) encryptions because I cant see em :(').send()
               print('sent')
            else:
               self.send_message('dougdoug@xmpp.skydevs.me',msg['body'],mtype='chat')
               #channel = client.get_channel(1065988089769631796)
               #channel.send('a')



         #   msg.reply("Thanks for sending:\n%s" % msg['body']).send()



def xmppthing(): 
	# 1. Create a new event loop for this thread.
	loop = asyncio.new_event_loop()
	# 2. Set the new event loop as the current one for this thread.
	asyncio.set_event_loop(loop)
	xmpp = BOot ('pinedev@yax.im', 'Amir3132') #jid, password
	xmpp.register_plugin('xep_0030') # Service Discovery
	xmpp.register_plugin('xep_0199') # Ping
	xmpp.connect()
	# 3. Use the correct loop object to run the Slixmpp processing loop.
	loop.run_forever()

if __name__ == '__main__':

        
        
    def discordthing(): 
        client.run('MTQxMDA0MTE2NzQ5MTM2NzEzMg.G_I9SK.s8GgS7TUX2Iy7KUPaG9dnNasAyqowqe7i3vYN8')
        
        
    thread1 = threading.Thread(target=discordthing)
    thread2 = threading.Thread(target=xmppthing)
    thread2.start()
    thread1.start()
    thread2.join()
    thread1.join()



    #client.run('MTQxMDA0MTE2NzQ5MTM2NzEzMg.GUSxC6.f5GSQUT3ZNLvVbcV5scshVBw_qdNb4Fma3dCrw')


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
		
		



