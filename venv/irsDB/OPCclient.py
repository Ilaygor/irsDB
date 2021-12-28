"""this is test class for receiving data from PLC by OPC-UA protocol"""
import sys
from opcua import ua, Client

ACCESS_METOD = 'opc.tcp'
OPCUA_IP = '172.31.1.32'
OPCUA_PORT = '4840'


class OPCUAHandler:
    url = f'{ACCESS_METOD}://{OPCUA_IP}:{OPCUA_PORT}/'
    client = Client(url)

    def connect(self):
        """connect to OPC-UA Server"""
        self.client.connect()

    def get_node_value(self, node):
        """get node and extract variable value"""
        return self.client.get_node(node).get_value()

    def disconnect(self):
        """disconnect to OPC-UA Server"""
        self.client.disconnect()


if __name__ == '__main__':
    # create inst class
    handler = OPCUAHandler()
    # connect to Server
    handler.connect()
    # get and print data
    #print(handler.get_node_value("ns=4;s=|var|BL20-PG-EN-V3.Application.POU.b"))
    # disconnect from Server
    handler.disconnect()