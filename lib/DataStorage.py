import socket
import threading
import time
from utils.SDNNode import SDNNode

class DataStorage(SDNNode):

    storage_location = r'C:\Restricted\study\DataScience\TCD\Scalable computing\Project3\GITHUBNew\sc-p3\lib\DataStorage.txt'

    def __init__(self, node_id, host, port):
        self.node_id = node_id
        self.host = host
        self.port = int(port)
         


    def storing_data(self):
        while True:
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.bind((self.host, self.port))
            soc.listen(1)
            connection, client_address = soc.accept()
            data = SDNNode.decrypt_message(connection.recv(1024),SDNNode.private_key,SDNNode.private_iv) #Manu
            print(data)
            with open(DataStorage.storage_location, 'a', encoding='utf-8') as f:
                f.write(data)
            connection.close()
            soc.close()

            


    def start(self):
        threading.Thread(target=self.storing_data).start()
        
