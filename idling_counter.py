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

    async def run(self):
        now = datetime.now() - timedelta(days=1)
        ts_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        ts_end = now.replace(hour=23, minute=59, second=59, microsecond=0)

        try:
            logging.info(f"Fetching data for: {ts_start} - {ts_end}")
            rc = Collector(
                int(ts_start.timestamp() * 1000), int(ts_end.timestamp() * 1000)
            )

            rc.make_record()
        except Exception as e:
            logging.exception(f"Exception occured while running scheduler: {e}")
            logging.exception(f"Missing date range: {ts_start} - {ts_end}")

    async def run_idling_schedule(self, hour: int, minute: int, second: int):
        while True:
            now = datetime.now()
            target_time = now.replace(
                hour=hour, minute=minute, second=second, microsecond=0
            )
            if now < target_time:
                sleep_duration = (target_time - now).total_seconds()
                logging.info(
                    f"It's too early. Wait for {sleep_duration} seconds to execute the task."
                )
                await asyncio.sleep(sleep_duration)
                await self.run()

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
