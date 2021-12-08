class RoverAntenna:
    def __init__(self):
        self.antenna_deployed = False

    def _block_movement(self):
        self.movement_disabled = True
        self.antenna_deployed = True

    def _unblock_movement(self):
        self.movement_disabled = False
        self.antenna_deployed = False

    # TODO Start HTTP Server - When petition received, execute callback
    def deploy_antenna(self, callback):
        print('[INFO] Deploying antenna')
        self._block_movement()
        pass

    # TODO Stop HTTP Server
    def undeploy_antenna(self):
        print('[INFO] Undeploying antenna')
        self._unblock_movement()
        pass
