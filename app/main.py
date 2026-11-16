"""Async console entrypoint for the support-ticket co-pilot."""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
import uuid

from app.agent import initialize_agent
from app.config import settings
from app.logging_config import configure_logging
from app.message import Message

logger = logging.getLogger(__name__)


async def read_console_line(prompt: str, stop_event: asyncio.Event) -> str | None:
    """Read one line while allowing a shutdown signal to interrupt the read."""
    print(prompt, end="", flush=True)
    loop = asyncio.get_running_loop()

    if not hasattr(loop, "add_reader"):
        line_task = asyncio.create_task(asyncio.to_thread(input))
        stop_task = asyncio.create_task(stop_event.wait())
        done, pending = await asyncio.wait(
            {line_task, stop_task}, return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
        if stop_task in done:
            return None
        return line_task.result()

    line_future: asyncio.Future[str] = loop.create_future()

    def on_stdin_ready() -> None:
        if not line_future.done():
            line_future.set_result(sys.stdin.readline().rstrip("\n"))

    loop.add_reader(sys.stdin.fileno(), on_stdin_ready)
    stop_task = asyncio.create_task(stop_event.wait())
    try:
        done, pending = await asyncio.wait(
            {line_future, stop_task}, return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()
        if stop_task in done:
            return None
        return line_future.result()
    finally:
        loop.remove_reader(sys.stdin.fileno())


async def console_loop() -> None:
    """Run an async console session with caller-owned message history."""
    agent = initialize_agent(settings)
    chat_id = f"console-{uuid.uuid4().hex[:8]}"
    user_id = "console-user"
    messages: list[Message] = []
    print("Support-ticket co-pilot ready. Type 'exit' or 'quit' to stop.")
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def request_shutdown() -> None:
        logger.info("shutdown signal received")
        stop_event.set()

    for signum in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(signum, request_shutdown)
        except (NotImplementedError, RuntimeError):
            pass
    try:
        while True:
            text = await read_console_line("\nCustomer: ", stop_event)
            if text is None or text == "":
                logger.info("console shutdown requested")
                return
            if text.strip().lower() in {"exit", "quit"}:
                return
            client_message: Message = {
                "chat_id": chat_id,
                "user_id": user_id,
                "message_id": f"message-{len(messages) + 1}",
                "actor": "user",
                "text": text,
            }
            messages.append(client_message)
            messages[:] = messages[-settings.recent_history_limit:]
            output = await agent(messages)
            print("\nAgent draft:")
            for section in output:
                print(f"\n{section['title']}\n{section['text']}")
    except asyncio.CancelledError:
        logger.info("console task cancelled")
        raise
    finally:
        for signum in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.remove_signal_handler(signum)
            except (NotImplementedError, RuntimeError):
                pass
        logger.info("console loop stopped")


def main() -> None:
    configure_logging()
    try:
        asyncio.run(console_loop())
    except KeyboardInterrupt:
        logger.info("shutdown requested")
    finally:
        logger.info("support-ticket co-pilot shut down cleanly")


if __name__ == "__main__":
    main()
