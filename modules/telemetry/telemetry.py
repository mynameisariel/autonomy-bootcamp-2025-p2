"""
Telemetry gathering logic.
"""

import time

from pymavlink import mavutil

from ..common.modules.logger import logger


class TelemetryData:  # pylint: disable=too-many-instance-attributes
    """
    Python struct to represent Telemtry Data. Contains the most recent attitude and position reading.
    """

    def __init__(
        self,
        time_since_boot: int | None = None,  # ms
        x: float | None = None,  # m
        y: float | None = None,  # m
        z: float | None = None,  # m
        x_velocity: float | None = None,  # m/s
        y_velocity: float | None = None,  # m/s
        z_velocity: float | None = None,  # m/s
        roll: float | None = None,  # rad
        pitch: float | None = None,  # rad
        yaw: float | None = None,  # rad
        roll_speed: float | None = None,  # rad/s
        pitch_speed: float | None = None,  # rad/s
        yaw_speed: float | None = None,  # rad/s
    ) -> None:
        self.time_since_boot = time_since_boot
        self.x = x
        self.y = y
        self.z = z
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity
        self.z_velocity = z_velocity
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.roll_speed = roll_speed
        self.pitch_speed = pitch_speed
        self.yaw_speed = yaw_speed

    def __str__(self) -> str:
        return f"""{{
            time_since_boot: {self.time_since_boot},
            x: {self.x},
            y: {self.y},
            z: {self.z},
            x_velocity: {self.x_velocity},
            y_velocity: {self.y_velocity},
            z_velocity: {self.z_velocity},
            roll: {self.roll},
            pitch: {self.pitch},
            yaw: {self.yaw},
            roll_speed: {self.roll_speed},
            pitch_speed: {self.pitch_speed},
            yaw_speed: {self.yaw_speed}
        }}"""


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Telemetry:
    """
    Telemetry class to read position and attitude (orientation).
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ):
        """
        Falliable create (instantiation) method to create a Telemetry object.
        """
        # Create a Telemetry object
        try:
            return True, cls(cls.__private_key, connection, local_logger)
        except Exception as e:
            local_logger.error(f"Failed to create Telemetry object: {e}", True)
            return False, None

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> None:
        assert key is Telemetry.__private_key, "Use create() method"

        # Do any intializiation here
        self.connection = connection
        self.logger = local_logger

    def run(
        self,
    ):
        """
        Receive LOCAL_POSITION_NED and ATTITUDE messages from the drone,
        combining them together to form a single TelemetryData object.
        """
        # Read MAVLink message LOCAL_POSITION_NED (32)
        local_position_ned_msg = self.connection.recv_match(
            type="LOCAL_POSITION_NED", blocking=False, timeout=1
        )
        # Read MAVLink message ATTITUDE (30)
        attitude_msg = self.connection.recv_match(type="ATTITUDE", blocking=False, timeout=1)
        time.sleep(1)
        # Return the most recent of both, and use the most recent message's timestamp
        if local_position_ned_msg and attitude_msg:
            time_since_boot = max(attitude_msg.time_boot_ms, local_position_ned_msg.time_boot_ms)

            telemetry_data = TelemetryData(
                time_since_boot=time_since_boot,
                x=local_position_ned_msg.x,
                y=local_position_ned_msg.y,
                z=local_position_ned_msg.z,
                x_velocity=local_position_ned_msg.vx,
                y_velocity=local_position_ned_msg.vy,
                z_velocity=local_position_ned_msg.vz,
                roll=attitude_msg.roll,
                pitch=attitude_msg.pitch,
                yaw=attitude_msg.yaw,
                roll_speed=attitude_msg.rollspeed,
                pitch_speed=attitude_msg.pitchspeed,
                yaw_speed=attitude_msg.yawspeed,
            )
            self.logger.info("Telemetry data received successfully", True)
            return True, telemetry_data
        self.logger.error("Error receiving local_position_ned_msg or atitude+msg", True)
        return False, None


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
