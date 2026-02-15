# infrastructure/outbox/poller.py

import asyncio
import logging

from infrastructure.outbox.dispatcher import OutboxDispatcher


logger = logging.getLogger(__name__)


class OutboxPoller:

    def __init__(
        self,
        dispatcher: OutboxDispatcher,
        interval_seconds: float = 1.0,
    ):
        self._dispatcher = dispatcher
        self._interval = interval_seconds
        self._running = False

    async def run(self):

        logger.info("Outbox poller started")

        self._running = True

        while self._running:

            try:

                processed = await self._dispatcher.dispatch_batch()

                if processed == 0:
                    await asyncio.sleep(self._interval)

            except Exception:
                logger.exception("Outbox poller failure")
                await asyncio.sleep(self._interval)

    def stop(self):
        self._running = False