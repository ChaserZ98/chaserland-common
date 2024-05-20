import asyncio
import signal
from abc import ABC, abstractmethod
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from typing import Self

import grpc

from chaserland_common.grpc.logger import logger
from chaserland_common.ref import Ref


class AbstractContext(AbstractAsyncContextManager, ABC):
    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError


class Server:
    def __init__(
        self,
        address: str,
        graceful_shutdown_timeout: int = 5,
        lifespan: Callable[[Self], AbstractAsyncContextManager[AbstractContext]] = None,
        interceptors: list[grpc.ServerInterceptor] = None,
        loop: asyncio.AbstractEventLoop = None,
    ):
        self.interceptors = interceptors
        self.address = address
        self.graceful_shutdown_timeout = graceful_shutdown_timeout
        self.lifespan = lifespan
        self.context_ref: Ref[AbstractContext] = Ref()
        self.servicers = []

        self.loop = loop or asyncio.get_event_loop()

    def add_servicer(self, register_func: Callable, servicer):
        self.servicers.append((register_func, servicer))

    def set_lifespan(
        self, lifespan: Callable[[Self], AbstractAsyncContextManager[AbstractContext]]
    ):
        self.lifespan = lifespan

    def run(self):
        try:
            self.loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt raised.")
            self.loop.run_until_complete(self.graceful_shutdown())
        finally:
            self.loop.close()

    def signal_handler(self, sig, frame):
        logger.info(f"Signal {signal.Signals(sig).name} received.")
        raise KeyboardInterrupt

    async def graceful_shutdown(self):
        logger.info(
            f"Starting graceful shutdown... Allowing {self.graceful_shutdown_timeout} seconds for ongoing calls to finish"
        )
        await self.server.stop(self.graceful_shutdown_timeout)

    async def start(self):
        logger.info(f"Creating server on {self.address}...")
        self.server = grpc.aio.server(interceptors=self.interceptors)
        self.server.add_insecure_port(self.address)

        logger.info("Setting up signal handlers...")
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        for register_func, servicer in self.servicers:
            logger.info(f"Adding servicer {servicer.__class__.__name__}...")
            register_func(servicer, self.server)

        async with self.lifespan(self) as context:
            self.context_ref.current = context
            await self.server.start()
            await self.server.wait_for_termination()
            self.context_ref.current = None
