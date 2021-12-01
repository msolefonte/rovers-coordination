import sys
from utils.NetworkVisualizer import NetworkVisualizer


def parse_arguments():
    print('[INFO] Network Visualizer started with args', sys.argv[1:], flush=True)
    node_id, host, port, coordinates_x, coordinates_y, encryption_key = sys.argv[1:]

    sdn_properties = {
        'host': host, 'port': int(port), 'known_peers': []
    }
    physical_properties = {
        'location': {'x': int(coordinates_x), 'y': int(coordinates_y)},
        'radio_range': 2147483647,
        'encryption_key': encryption_key
    }

    return node_id, sdn_properties, physical_properties


def main():
    network_visualizer = NetworkVisualizer(*parse_arguments())
    network_visualizer.start()


main()
