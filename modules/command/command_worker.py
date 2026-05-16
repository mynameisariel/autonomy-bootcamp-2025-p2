"""
Command worker to make decisions based on Telemetry Data.
"""

import os
import pathlib

from pymavlink import mavutil

from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import command
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def command_worker(
    connection: mavutil.mavfile,
    target: command.Position,
    controller: worker_controller.WorkerController, 
    input_queue: queue_proxy_wrapper.QueueProxyWrapper, 
    output_queue: queue_proxy_wrapper.QueueProxyWrapper
) -> None:
    """
    Worker process.

    connection: MAVLink connection
    controller: communication channel between the main process and this worker
    input_queue: queue that recieves Telemetry data
    output_queue: queue that sends outputs to main process
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
    # Instantiate class object (command.Command)
    status, command_instance = command.Command.create(connection, target, local_logger)
    if not status:
        local_logger.error("Failed to create command object.", True)
        return

    # Main loop: do work.
    while not controller.is_exit_requested():
        controller.check_pause()

        telemetry_data = input_queue.queue.get()
        if telemetry_data is None:
            break

        output_string = command_instance.run(telemetry_data)
        if output_string is not None:
            output_queue.queue.put(output_string)

# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
