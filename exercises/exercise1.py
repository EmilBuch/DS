import random

from emulators.Device import Device
from emulators.Medium import Medium
from emulators.MessageStub import MessageStub


class GossipMessage(MessageStub):

    def __init__(self, sender: int, destination: int, secrets):
        super().__init__(sender, destination)
        # we use a set to keep the "secrets" here
        self.secrets = secrets

    def __str__(self):
        return f'{self.source} -> {self.destination} : {self.secrets}'


class Gossip(Device):

    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)
        
        # for this exercise we use the index as the "secret"
        self._secrets = set([index])

    def run(self):
        if self.index() == (self.number_of_devices()-1):
            receiver = 0
        else:
            receiver = self.index() + 1

        message = GossipMessage(self.index(), receiver, self._secrets)
        self.medium().send(message)

        while True:
            ingoing = self.medium().receive()
            if ingoing is None:
                continue

            self._secrets = self._secrets.union(ingoing.secrets)

            if self.index() == (self.number_of_devices()-1):
                receiver = 0
            else:
                receiver = self.index() + 1

            message = GossipMessage(self.index(), receiver, self._secrets)
            self.medium().send(message)

            if len(self._secrets) == self.number_of_devices():
                break
        return

    def print_result(self):
        print(f'\tDevice {self.index()} got secrets: {self._secrets}')
