"""
Decision-making logic.
"""

import math

from pymavlink import mavutil

from ..common.modules.logger import logger
from ..telemetry import telemetry


class Position:
    """
    3D vector struct.
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Command:  # pylint: disable=too-many-instance-attributes
    """
    Command class to make a decision based on recieved telemetry,
    and send out commands based upon the data.
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        target: Position,
        local_logger: logger.Logger,
    ):
        """
        Falliable create (instantiation) method to create a Command object.
        """
        try:
            return True, cls(cls.__private_key, connection, target, local_logger)
        except Exception as e:
            local_logger.error(f"Failed to create Command object: {e}", True)
            return False, None

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        target: Position,
        local_logger: logger.Logger,
    ) -> None:
        assert key is Command.__private_key, "Use create() method"

        # Do any intializiation here
        self.connection = connection
        self.target = target
        self.logger = local_logger

        self.initial_x = None
        self.initial_y = None
        self.initial_z = None
        self.initial_time = None
        self.cur_time = None

    def run(
        self,
        telemetry_data: telemetry.TelemetryData
    ):
        """
        Make a decision based on received telemetry data.
        """
        if telemetry_data is None:
            self.logger.warning("No telemetry data received", True)
            return False, None
        
        # Log average velocity for this trip so far
        if self.initial_time is None:
            self.initial_x = telemetry_data.x
            self.initial_y = telemetry_data.y
            self.initial_z = telemetry_data.z
            self.initial_time = 0.0
            self.cur_time = 0.5

        else:
            total_time = self.cur_time - self.initial_time
            self.cur_time += 0.5

            delta_vx = telemetry_data.x - self.initial_x
            delta_vy = telemetry_data.y - self.initial_y
            delta_vz = telemetry_data.z - self.initial_z

            avg_vx = delta_vx / total_time
            avg_vy = delta_vy / total_time
            avg_vz = delta_vz / total_time

            self.logger.info(f"Average velocity: ({avg_vx}, {avg_vy}, {avg_vz}) m/s")
        
        # Use COMMAND_LONG (76) message, assume the target_system=1 and target_componenet=0
        # The appropriate commands to use are instructed below

        # Adjust height using the comand MAV_CMD_CONDITION_CHANGE_ALT (113)
        # String to return to main: "CHANGE_ALTITUDE: {amount you changed it by, delta height in meters}"
        
        delta_altitude = self.target.z - telemetry_data.z

        if abs(delta_altitude) > 0.5:
            self.logger.info("Adjust drone altitude.", True)
            self.connection.mav.command_long_send(
                1, 0, mavutil.mavlink.MAV_CMD_CONDITION_CHANGE_ALT, 0, 1, 0, 0, 0, 0, 0, self.target.z,
            )
            return f"CHANGE_ALTITUDE: {delta_altitude}"

        # Adjust direction (yaw) using MAV_CMD_CONDITION_YAW (115). Must use relative angle to current state
        # String to return to main: "CHANGING_YAW: {degree you changed it by in range [-180, 180]}"
        # Positive angle is counter-clockwise as in a right handed system

        target_angle = math.atan2(self.target.y - telemetry_data.y, self.target.x - telemetry_data.x)
        delta_yaw = target_angle - telemetry_data.yaw
        delta_yaw_deg = math.degrees(delta_yaw)

        while delta_yaw_deg > 180:
            delta_yaw_deg -= 360
        while delta_yaw_deg < -180:
            delta_yaw_deg += 360

        if abs(delta_yaw_deg) > 5.0:
            self.logger.info("Adjust drone yaw.", True)
            self.connection.mav.command_long_send(
                1, 0, mavutil.mavlink.MAV_CMD_CONDITION_YAW, 0, delta_yaw_deg, 5, 0, 1, 0, 0, 0,
            )
            return f"CHANGING_YAW: {delta_yaw_deg}"
        
        return None
        


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
