from autobahn.asyncio.wamp import ApplicationSession
from autobahn.asyncio.wamp import ApplicationRunner
from asyncio import coroutine
import logging

logging.basicConfig(filename='msg_trollbox.log', format='%(asctime)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.DEBUG)

class PoloniexComponent(ApplicationSession):
    def onConnect(self):
        self.join(self.config.realm)

    @coroutine
    def onJoin(self, details):
        def onTrollbox(*args):
            #print("Message received:", args)
            #logging.info('Message received', args)
            #logging.info(args[1:]) # Ignore 'trollboxMessage'
            logging.info(args[3:]) # Ignore 'trollboxMessage', 'messageid', and 'username'

        try:
            yield from self.subscribe(onTrollbox, 'trollbox')
        except Exception as e:
            print("Could not subscribe to topic:", e)

def main():
    runner = ApplicationRunner("wss://api.poloniex.com", "realm1")
    runner.run(PoloniexComponent)

if __name__ == "__main__":
    main()