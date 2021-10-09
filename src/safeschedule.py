import datetime
from logging import Logger

from schedule import Scheduler


class SafeScheduler(Scheduler):
    def __init__(self, logger: Logger = None):
        self.logger = logger
        super().__init__()

    def _run_job(self, job):
        try:
            super()._run_job(job)
        except Exception as e:
            if self.logger is not None:
                self.logger.error(e)
            self.cancel_job(job)
