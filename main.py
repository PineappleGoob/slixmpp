from slixmpp import ClientXMPP
import logging
import asyncio
import slixmpp
from getpass import getpass
from argparse import ArgumentParser
import discord

class BOot(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password) 
        
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

    def message(self, msg):
        print(msg['body'])
        if msg['type'] in ('normal', 'chat'):
            if msg['body'] == '[This message is OMEMO encrypted]':
               msg.reply('Please turn off Omemo (or possibly other) encryptions because I cant see em :(').send()
               print('sent')
            else:
               print('wasnt it')



         #   msg.reply("Thanks for sending:\n%s" % msg['body']).send()





if __name__ == '__main__':
    # Setup the command line arguments.
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
                        format='%(levelname)-8s %(message)s')
    xmpp = BOot (args.jid, args.password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0199') # Ping
    xmpp.connect()
    asyncio.get_event_loop().run_forever()
    sendmsg = input('msg to send:')