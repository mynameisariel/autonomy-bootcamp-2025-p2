"""
Heartbeat worker that sends heartbeats periodically.
"""

import os
import pathlib
import time

from pymavlink import mavutil

from utilities.workers import worker_controller
from . import heartbeat_sender
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def heartbeat_sender_worker(
    connection: mavutil.mavfile,
    controller: worker_controller
) -> None:
    """
    Worker process - shows that systems is active and responding. Sends a heartbeat message once per second.

    connection: MAVlink connection
    controller: communication channel between the main process and this worker
    """
    
    # =============================================================================================
    #                          ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
    # =============================================================================================

    # Instantiate logger
    worker_name = pathlib.Path(__file__).stem
    process_id = os.getpid()
    result, local_logger = logger.Logger.create(f"{worker_name}_{process_id}", True)
    if not result:
        print("ERROR: Worker failed to create logger")
        return

    # Get Pylance to stop complaining
    assert local_logger is not None

    local_logger.info("Logger initialized", True)

    # =============================================================================================
    #                          ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
    # =============================================================================================
    # Instantiate class object (heartbeat_sender.HeartbeatSender)

    status, heartbeat_sender_instance = heartbeat_sender.HeartbeatSender.create(connection, local_logger)

    if not status:
        local_logger.error("Failed to create heartbeat sender instance.", True)
        return

    # Main loop: do work.
    while not controller.is_exit_requested():
        # GOAL - send HEARBEAT (0) once per second
        controller.check_pause()
        heartbeat_sender_instance.run()

        time.sleep(1)




# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
