import logging
import time
from collections.abc import AsyncIterator, Callable
from typing import Any

import grpc
import grpc_interceptor.exceptions as grpc_exceptions
from grpc_interceptor.server import AsyncServerInterceptor


class AsyncAccessLoggerInterceptor(AsyncServerInterceptor):
    def __init__(self, logger: logging.Logger = logging.getLogger("grpc.access")):
        self.logger = logger

    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.aio.ServicerContext,
        method_name: str,
    ):
        metadata = dict(context.invocation_metadata())
        if "rpc-id" not in metadata:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "rpc-id is not set")

        rpc_id = metadata["rpc-id"]
        start_time = time.perf_counter() * 1000
        try:
            response_or_iterator = method(request_or_iterator, context)
            if hasattr(response_or_iterator, "__aiter__"):
                return self._intercept_streaming(
                    response_or_iterator, context, start_time, method_name
                )
            return await response_or_iterator
        finally:
            endtime = time.perf_counter() * 1000
            elapsed_time = endtime - start_time
            status_code = (
                grpc.StatusCode(context.code())
                if context.code()
                else grpc.StatusCode.OK
            )
            self.logger.info(
                f'{context.peer()} - {rpc_id} - "{method_name}" {status_code.value[0]} {status_code.name} "{context.details()}" {elapsed_time:.2f}ms'
            )

    async def _intercept_streaming(self, iterator, context: grpc.aio.ServicerContext):
        try:
            async for r in iterator:
                yield r
        except grpc_exceptions.GrpcException as e:
            await context.abort(e.status_code, e.details)


class AsyncExceptionToStatusInterceptor(AsyncServerInterceptor):
    async def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        context: grpc.aio.ServicerContext,
        method_name: str,
    ) -> Any:
        try:
            response_or_iterator = method(request_or_iterator, context)
            if hasattr(response_or_iterator, "__aiter__"):
                return self._intercept_streaming(response_or_iterator, context)
            return await response_or_iterator
        except Exception as e:
            await self.handle_exception(e, context)

    async def handle_exception(self, e: Exception, context: grpc.aio.ServicerContext):
        if isinstance(e, grpc_exceptions.GrpcException):
            await context.abort(e.status_code, e.details)
        else:
            await context.abort(grpc.StatusCode.INTERNAL, repr(e))

    async def _intercept_streaming(
        self, iterator: AsyncIterator, context: grpc.aio.ServicerContext
    ):
        try:
            async for r in iterator:
                yield r
        except Exception as e:
            await self.handle_exception(e, context)
