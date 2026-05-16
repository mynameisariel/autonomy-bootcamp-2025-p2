"""
Heartbeat receiving logic.
"""

from pymavlink import mavutil

from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatReceiver:
    """
    HeartbeatReceiver class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ):
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """
        try:
            return True, cls(cls.__private_key, connection, local_logger)
        except Exception as e:
            local_logger.error(f"Failed to create HeartbeatSender: {e}", True)
            return False, None

    def __init__(self, key: object, connection: mavutil.mavfile, local_logger: logger) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"

        # Do any intializiation here
        self.connection = connection
        self.logger = local_logger

        self.connected = False
        self.missed_heartbeats = 0

    def run(
        self,
    ):
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """
        try:
            msg = self.connection.recv_match(type="HEARTBEAT", blocking=True, timeout=1)
        except Exception as e:
            self.logger.error(f"Failed to receive heartbeat: {e}", True)
            self.missed_heartbeats += 1
            if self.missed_heartbeats >= 5:
                self.connected = False
            return self.connected

        if msg:
            self.logger.info("Heartbeat received", True)
            self.missed_heartbeats = 0
            self.connected = True
        else:
            self.missed_heartbeats += 1
            self.logger.warning("Missed a heartbeat", True)
            if self.missed_heartbeats >= 5:
                self.connected = False

        return self.connected


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
