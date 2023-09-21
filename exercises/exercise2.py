from emulators.Device import Device
from emulators.Medium import Medium
from emulators.MessageStub import MessageStub


class RipMessage(MessageStub):
    def __init__(self, sender: int, destination: int, table):
        super().__init__(sender, destination)
        self.table = table

    def __str__(self):
        return f'RipMessage: {self.source} -> {self.destination} : {self.table}'

class RoutableMessage(MessageStub):
    def __init__(self, sender: int, destination: int, first_node: int, last_node: int, content):
        super().__init__(sender, destination)
        self.content = content
        self.first_node = first_node
        self.last_node = last_node

    def __str__(self):
        return f'RoutableMessage: {self.source} -> {self.destination} : {self.content}'




class RipCommunication(Device):

    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)

        if self.index() == (self.number_of_devices()-1):
            self.neighbors = [0, self.index()-1]
        elif self.index() == 0:
            self.neighbors = [self.index()+1, self.number_of_devices()-1]
        else:
            self.neighbors = [self.index()+1, self.index()-1]

        self.routing_table = dict()

    def run(self):
        for neigh in self.neighbors:
            self.routing_table[neigh] = (neigh, 1)
        self.routing_table[self.index()] = (self.index(), 0)
        for neigh in self.neighbors:
            self.medium().send(RipMessage(self.index(), neigh, self.routing_table))
        #print(self.routing_table)

        while True:
            ingoing = self.medium().receive()
            if ingoing is None:
                # this call is only used for synchronous networks
                self.medium().wait_for_next_round()
                continue

            if type(ingoing) is RipMessage:
                print(f"Device {self.index()}: Got new table from {ingoing.source}")
                returned_table = self.merge_tables(ingoing.source, ingoing.table)
                if returned_table is not None:
                    self.routing_table = returned_table
                    for neigh in self.neighbors:
                        self.medium().send(RipMessage(self.index(), neigh, self.routing_table))

            if type(ingoing) is RoutableMessage:
                print(f"Device {self.index()}: Routing from {ingoing.first_node} to {ingoing.last_node} via #{self.index()}: [#{ingoing.content}]")
                if ingoing.last_node is self.index():
                    print(f"\tDevice {self.index()}: delivered message from {ingoing.first_node} to {ingoing.last_node}: {ingoing.content}")
                    continue
                if self.routing_table[ingoing.last_node] is not None:
                    (next_hop, distance) = self.routing_table[ingoing.last_node]
                    self.medium().send(RoutableMessage(self.index(), next_hop, ingoing.first_node, ingoing.last_node, ingoing.content))
                    continue
                print(f"\tDevice {self.index()}:  DROP Unknown route #{ingoing.first_node} to #{ingoing.last_node} via #{self.index}, message #{ingoing.content}")

            # this call is only used for synchronous networks
            self.medium().wait_for_next_round()
            
            if len(self.routing_table) >= self.number_of_devices():
                return True
            

    def merge_tables(self, src, table):
        updated = False

        for destination, (next_hop, distance) in table.items():
            # Skip routes to itself
            if destination == self.index():
                continue
            
            # If destination is not in routing table we add it
            if destination not in self.routing_table:
                self.routing_table[destination] = (src, distance + 1)
                updated = True
            else:
                # Compare metrics for those that are in the routing table
                current_next_hop, current_distance = self.routing_table[destination]

                # Apply the rip update rules
                if src == current_next_hop:
                    # Route through the same next hop, update if metric changes
                    if distance + 1 != current_distance:
                        self.routing_table[destination] = (src, distance + 1)
                        updated = True
                elif distance + 1 < current_distance:
                    # Better route found, update the table
                    self.routing_table[destination] = (src, distance + 1)
                    updated = True
        if updated:
            return self.routing_table
        else:
            return None

    def print_result(self):
        print(f'\tDevice {self.index()} has routing table: {self.routing_table}')