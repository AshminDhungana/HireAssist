import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable


@dataclass
class Task:
    id: str
    task_type: str
    payload: Dict[str, Any]
    status: str = "queued"  # queued | running | completed | failed
    attempts: int = 0
    error: Optional[str] = None
    created_at: float = field(default_factory=lambda: time.time())
    updated_at: float = field(default_factory=lambda: time.time())


class InProcessTaskQueue:
    def __init__(self) -> None:
        self.queue: asyncio.Queue[Task] = asyncio.Queue()
        self.tasks: Dict[str, Task] = {}
        self.handlers: Dict[str, Callable[[Dict[str, Any]], asyncio.Future]] = {}
        self._worker_task: Optional[asyncio.Task] = None
        self.max_attempts = 5

    def register_handler(self, task_type: str, handler: Callable[[Dict[str, Any]], Any]) -> None:
        async def _async_wrapper(payload: Dict[str, Any]):
            result = handler(payload)
            if asyncio.iscoroutine(result):
                return await result
            return result
        self.handlers[task_type] = _async_wrapper  # type: ignore

    async def start(self) -> None:
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._worker_loop())

    async def stop(self) -> None:
        if self._worker_task:
            self._worker_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._worker_task

    def enqueue(self, task_type: str, payload: Dict[str, Any]) -> str:
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, task_type=task_type, payload=payload)
        self.tasks[task_id] = task
        self.queue.put_nowait(task)
        return task_id

    def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        t = self.tasks.get(task_id)
        if not t:
            return None
        return {
            "id": t.id,
            "type": t.task_type,
            "status": t.status,
            "attempts": t.attempts,
            "error": t.error,
            "created_at": t.created_at,
            "updated_at": t.updated_at,
        }

    async def _worker_loop(self) -> None:
        while True:
            task: Task = await self.queue.get()
            handler = self.handlers.get(task.task_type)
            if not handler:
                task.status = "failed"
                task.error = f"No handler for {task.task_type}"
                task.updated_at = time.time()
                continue
            backoff = 1.0
            while task.attempts < self.max_attempts:
                task.status = "running"
                task.attempts += 1
                task.updated_at = time.time()
                try:
                    await handler(task.payload)
                    task.status = "completed"
                    task.updated_at = time.time()
                    break
                except Exception as e:
                    task.error = str(e)
                    task.status = "failed"
                    task.updated_at = time.time()
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, 30)
            self.queue.task_done()


task_queue = InProcessTaskQueue()


