import sys
from utils.NetworkVisualizer import NetworkVisualizer


def main():
    print('[INFO] Rover started with args', sys.argv[1:], flush=True)
    node_id, host, port, coordinates_x, coordinates_y, encryption_key = sys.argv[1:]

    network_visualizer = NetworkVisualizer(node_id, host, int(port), coordinates_x, coordinates_y, encryption_key)
    network_visualizer.start()


main()
