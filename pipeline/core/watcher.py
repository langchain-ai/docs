"""File watcher implementation.

This module provides file system watching capabilities for the documentation
build pipeline, enabling automatic rebuilds when source files change.
"""

import asyncio
import contextlib
import logging
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from pipeline.core.builder import DocumentationBuilder

logger = logging.getLogger(__name__)


class DocsFileHandler(FileSystemEventHandler):
    """Handles file system events for documentation files.

    This handler processes file system events (creation, modification, deletion)
    and triggers appropriate build actions. It uses a queue-based approach
    for proper async coordination.

    Attributes:
        builder: DocumentationBuilder instance for processing files.
        event_queue: Queue for communicating file events to async processor.
        loop: Event loop for scheduling async tasks.
    """

    def __init__(
        self,
        builder: DocumentationBuilder,
        event_queue: asyncio.Queue[Path | None],
        loop: asyncio.AbstractEventLoop,
    ) -> None:
        """Initialize the file handler.

        Args:
            builder: DocumentationBuilder instance to use for rebuilding files.
            event_queue: Queue for sending file change events to async processor.
            loop: Event loop for scheduling async operations.
        """
        super().__init__()
        self.builder = builder
        self.event_queue = event_queue
        self.loop = loop

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events.

        Processes file modification events and queues rebuilds for
        supported file types.

        Args:
            event: File system event containing the modified file path.
        """
        if event.is_directory:
            return

        if not isinstance(event.src_path, str):
            raise TypeError("Expected event.src_path to be a string")

        src_path = event.src_path

        file_path = Path(src_path)
        if file_path.suffix.lower() in self.builder.copy_extensions:
            logger.info("File changed: %s", file_path)
            # Put file change event in queue for async processing
            self.loop.call_soon_threadsafe(self.event_queue.put_nowait, file_path)

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events.

        Delegates to on_modified since creation and modification
        require the same handling logic.

        Args:
            event: File system event containing the created file path.
        """
        self.on_modified(event)

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events.

        Removes the corresponding file from the build directory
        when a source file is deleted.

        Args:
            event: File system event containing the deleted file path.
        """
        if event.is_directory:
            return

        if not isinstance(event.src_path, str):
            raise TypeError("Expected event.src_path to be a string")

        file_path = Path(event.src_path)

        relative_path = file_path.relative_to(self.builder.src_dir)
        output_path = self.builder.build_dir / relative_path

        if output_path.exists():
            output_path.unlink()
            logger.info("Deleted: %s", relative_path)


class FileWatcher:
    """Watches for file changes and triggers rebuilds.

    This class coordinates file system watching with the documentation
    builder to provide automatic rebuilds during development using
    proper async task management.

    Attributes:
        src_dir: Path to the source directory to watch.
        build_dir: Path to the build directory for output.
        builder: DocumentationBuilder instance for processing files.
        observer: Watchdog observer for file system events.
        handler: Event handler for processing file changes.
        event_queue: Queue for coordinating file change events.
        pending_files: Set of files that have pending rebuilds.
        rebuild_task: Current async task for rebuilding (for cancellation).
    """

    def __init__(self, src_dir: Path, build_dir: Path) -> None:
        """Initialize the file watcher.

        Args:
            src_dir: Path to the source directory to watch for changes.
            build_dir: Path to the build directory for output files.
        """
        self.src_dir = src_dir
        self.build_dir = build_dir
        self.builder = DocumentationBuilder(src_dir, build_dir)
        self.observer = Observer()
        self.event_queue: asyncio.Queue[Path | None] = asyncio.Queue()
        self.pending_files: set[Path] = set()
        self.rebuild_task: asyncio.Task[None] | None = None

        # Handler will be created in start() when we have the event loop
        self.handler: DocsFileHandler | None = None

    async def start(self) -> None:
        """Start watching for file changes.

        Begins monitoring the source directory for file system events
        and runs indefinitely until interrupted. Uses proper async
        task coordination for file processing.

        Raises:
            KeyboardInterrupt: When the user interrupts the process.
        """
        # Get current event loop
        loop = asyncio.get_running_loop()

        # Create handler with event loop reference
        self.handler = DocsFileHandler(self.builder, self.event_queue, loop)

        # Schedule observer
        self.observer.schedule(self.handler, str(self.src_dir), recursive=True)
        self.observer.start()

        try:
            # Start event processor task
            processor_task = asyncio.create_task(self._process_events())

            # Wait indefinitely
            await processor_task

        except asyncio.CancelledError:
            # Cancel any pending rebuild task
            if self.rebuild_task:
                self.rebuild_task.cancel()
            raise
        finally:
            self.observer.stop()
            self.observer.join()

    async def _process_events(self) -> None:
        """Process file change events from the queue.

        This method runs continuously, processing file change events
        and managing debounced rebuilds.
        """
        while True:
            try:
                # Wait for file change events
                file_path = await self.event_queue.get()

                if file_path is None:
                    # Shutdown signal
                    break

                # Add to pending files
                self.pending_files.add(file_path)

                # Schedule/reschedule rebuild with debouncing
                if self.rebuild_task:
                    self.rebuild_task.cancel()

                self.rebuild_task = asyncio.create_task(self._rebuild_after_delay())

            except asyncio.CancelledError:
                break

    async def _rebuild_after_delay(self) -> None:
        """Rebuild files after a short delay to batch changes.

        Waits for a debounce period, then rebuilds all pending files
        to avoid excessive rebuilds during rapid file changes.
        """
        try:
            await asyncio.sleep(0.5)  # Debounce delay

            if self.pending_files:
                files_to_build = list(self.pending_files)
                self.pending_files.clear()

                logger.info("Rebuilding %d files...", len(files_to_build))
                self.builder.build_files(files_to_build)

        except asyncio.CancelledError:
            # Task was cancelled, just return
            pass

    async def shutdown(self) -> None:
        """Gracefully shutdown the file watcher.

        Sends a shutdown signal to the event processor and cancels
        any pending rebuild tasks.
        """
        # Signal shutdown to event processor
        await self.event_queue.put(None)

        # Cancel any pending rebuild task
        if self.rebuild_task:
            self.rebuild_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.rebuild_task
