"""
Module runs script for daily count of excessive idling for each Transport.
"""

import asyncio
import logging

from datetime import datetime, timedelta
from dotenv import load_dotenv

from data_fetch.collector import Collector


load_dotenv()

log_fh = logging.FileHandler("scheduled_tasks.log")
_ = logging.basicConfig(
    format="%(asctime)s - %(name)s - %(lineno)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
    filename="scheduled_tasks.log",
)
logger = logging.getLogger()


class Scheduler:
    """Scheduler runs script for daily count of excessive idling for each Transport."""

    async def run(self) -> None:
        """Run the calculation."""

        # Get current day.
        now = datetime.now() - timedelta(days=1)
        ts_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        ts_end = now.replace(hour=23, minute=59, second=59, microsecond=0)

        try:
            # Calculate excessive idling and save to DB.
            logging.info(f"Fetching data for: {ts_start} - {ts_end}")
            rc = Collector(
                int(ts_start.timestamp() * 1000), int(ts_end.timestamp() * 1000)
            )

            rc.make_record()
        except Exception as e:
            logging.exception(f"Exception occured while running scheduler: {e}")
            logging.exception(f"Missing date range: {ts_start} - {ts_end}")

    async def run_idling_schedule(self, hour: int, minute: int, second: int) -> None:
        """Coroutine runs every day at given time.

        Args:
            hour (int): Hour when running script.
            minute (int): Minute when running script.
            second (int): Second when running script.
        """
        while True:
            # Initialize datetime object when script will be executed.
            now = datetime.now()
            target_time = now.replace(
                hour=hour, minute=minute, second=second, microsecond=0
            )

            # If current time is less then start point,
            # sleep as long as it takes till start point.
            # Then run script.
            if now < target_time:
                sleep_duration = (target_time - now).total_seconds()
                logging.info(
                    f"It's too early. Wait for {sleep_duration} seconds to execute the task."
                )
                await asyncio.sleep(sleep_duration)
                await self.run()

            # If current time is greater then start point,
            # sleep as long as it takes till start point of the next day.
            # Then run script.
            elif now >= target_time:
                target_time += timedelta(days=1)

                sleep_duration = (target_time - now).total_seconds()
                logging.info(
                    f"It's done for today. Waiting for {sleep_duration} seconds to execute the task"
                )
                await asyncio.sleep(sleep_duration)
                await self.run()


if __name__ == "__main__":
    scheduler = Scheduler()
    asyncio.run(scheduler.run_idling_schedule(2, 0, 0))
