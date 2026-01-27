"""
Audit Logging System (Production Grade).
Uses an asyncio Queue and background worker to prevent blocking the main execution path.
Includes log rotation to prevent unbounded growth.
"""
import asyncio
import json
import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import structlog
import aiofiles

from secureshell.models import ExecutionResult

logger = structlog.get_logger()

class AuditLogger:
    """
    Async audit logger with background worker and log rotation.
    """
    def __init__(
        self, 
        log_path: str = "secureshell_audit.jsonl", 
        queue_size: int = 1000,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB default
        backup_count: int = 5
    ):
        self.log_path = Path(log_path)
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=queue_size)
        self._worker_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()

    async def start(self):
        """Start the background logging worker."""
        if not self._worker_task:
            self._worker_task = asyncio.create_task(self._process_queue())

    async def stop(self):
        """Stop the worker and flush the queue."""
        if self._worker_task:
            # Signal stop
            self._stop_event.set()
            # Wait for queue to drain
            await self._queue.join()
            # Cancel worker
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

    async def log_execution(
        self,
        command: str,
        reasoning: str,
        context: Dict[str, Any],
        result: ExecutionResult
    ):
        """
        Submit a log entry to the queue. Non-blocking unless queue is full.
        """
        if not self._worker_task:
            # Auto-start if not started (though explicit start is better)
            await self.start()
            
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "command": command,
            "reasoning": reasoning,
            "context": context,
            "result": result.model_dump(mode="json"),
        }
        
        try:
            # put_nowait raises QueueFull if full.
            # In production, we might want to drop logs or block?
            # Dropping is safer for app stability, blocking ensures audit integrity.
            # We'll block with a short timeout to apply backpressure if system is overwhelmed.
            await asyncio.wait_for(self._queue.put(entry), timeout=0.5)
        except asyncio.TimeoutError:
            logger.error("audit_queue_full_dropped_msg", command=command)
        except Exception as e:
            logger.error("audit_enqueue_failed", error=str(e))

    async def _process_queue(self):
        """Background worker to write logs to disk."""
        while not self._stop_event.is_set():
            try:
                # Wait for batch of messages or timeout
                entries = []
                
                # Fetch first item (blocking)
                try:
                    first = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                    entries.append(first)
                except asyncio.TimeoutError:
                    continue # Check stop event
                
                # Try to fetch more immediately (batching)
                while not self._queue.empty() and len(entries) < 50:
                    entries.append(self._queue.get_nowait())
                
                # Bulk write
                await self._write_batch(entries)
                
                # Mark done
                for _ in entries:
                    self._queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("audit_worker_error", error=str(e))
                # Don't crash the worker

    async def _write_batch(self, entries: list):
        """Write batch of entries with rotation check."""
        try:
            # Check if rotation needed
            await self._rotate_if_needed()
            
            async with aiofiles.open(self.log_path, mode='a') as f:
                lines = [json.dumps(e) + "\n" for e in entries]
                await f.writelines(lines)
        except Exception as e:
            logger.error("audit_file_write_failed", error=str(e))
    
    async def _rotate_if_needed(self):
        """Rotate log file if it exceeds max size."""
        try:
            if not self.log_path.exists():
                return
            
            file_size = self.log_path.stat().st_size
            
            if file_size >= self.max_bytes:
                logger.info("audit_log_rotation", size=file_size, max=self.max_bytes)
                
                # Rotate existing backups
                for i in range(self.backup_count - 1, 0, -1):
                    old_file = Path(f"{self.log_path}.{i}")
                    new_file = Path(f"{self.log_path}.{i + 1}")
                    
                    if old_file.exists():
                        if new_file.exists():
                            new_file.unlink()  # Remove oldest if at limit
                        old_file.rename(new_file)
                
                # Move current to .1
                backup_file = Path(f"{self.log_path}.1")
                if backup_file.exists():
                    backup_file.unlink()
                self.log_path.rename(backup_file)
                
        except Exception as e:
            logger.error("audit_rotation_failed", error=str(e))

