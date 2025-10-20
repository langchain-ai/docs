"""File watcher implementation.

This module provides file system watching capabilities for the documentation
build pipeline, enabling automatic rebuilds when source files change.
"""

import asyncio
import contextlib
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
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

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if a file should be ignored by the watcher.

        Ignores temporary files, backup files, and other non-source files.

        Args:
            file_path: Path to the file to check.

        Returns:
            True if the file should be ignored, False otherwise.
        """
        file_name = file_path.name

        # Ignore backup files created by editors
        if file_name.endswith(("~", ".bak", ".orig")):
            return True

        # Ignore other kinds of temporary files
        return bool(
            file_name.startswith(".") and file_name.endswith((".tmp", ".temp", ".swp"))
        )

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
            msg = "Expected event.src_path to be a string"
            raise TypeError(msg)

        src_path = event.src_path

        file_path = Path(src_path)

        # Skip ignored files
        if self._should_ignore_file(file_path):
            return

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
            msg = "Expected event.src_path to be a string"
            raise TypeError(msg)

        file_path = Path(event.src_path)

        # Skip ignored files
        if self._should_ignore_file(file_path):
            return

        relative_path = file_path.relative_to(self.builder.src_dir.absolute())
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
            await asyncio.sleep(0.2)  # Reduced debounce delay for faster response

            if self.pending_files:
                files_to_build = list(self.pending_files)
                self.pending_files.clear()

                # Build files with progress indication
                await self._build_files_async(files_to_build)

        except asyncio.CancelledError:
            # Task was cancelled, just return
            pass

    async def _build_files_async(self, files_to_build: list[Path]) -> None:
        """Build files asynchronously with progress indication.

        Args:
            files_to_build: List of source files that need to be built.
        """
        file_count = len(files_to_build)

        if file_count == 1:
            # For single file, build directly with simple message
            file_path = files_to_build[0]
            relative_path = file_path.absolute().relative_to(self.src_dir.absolute())
            logger.info("🔄 Rebuilding %s...", relative_path)

            # Run build in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=1) as executor:
                await loop.run_in_executor(executor, self.builder.build_file, file_path)

            logger.info("✅ Rebuilt %s", relative_path)

        else:
            # For multiple files, show progress bar
            logger.info("🔄 Rebuilding %d files...", file_count)

            completed = 0

            def build_single_file(file_path: Path) -> bool:
                """Build a single file and return success status."""
                try:
                    self.builder.build_file(file_path)
                except Exception:
                    logger.exception("Failed to build file %s", file_path)
                    return False
                else:
                    return True

            # Use thread pool for concurrent building
            loop = asyncio.get_event_loop()
            max_workers = min(4, file_count)  # Limit concurrent builds

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all build tasks
                futures = [
                    loop.run_in_executor(executor, build_single_file, file_path)
                    for file_path in files_to_build
                ]

                # Process results as they complete with progress updates
                for future in asyncio.as_completed(futures):
                    await future
                    completed += 1

                    # Show progress to stderr (allowed for user feedback)
                    progress = int(
                        (completed / file_count) * 20
                    )  # 20 char progress bar
                    bar = "█" * progress + "░" * (20 - progress)
                    percent = int((completed / file_count) * 100)
                    sys.stderr.write(
                        f"\r🔨 [{bar}] {percent}% ({completed}/{file_count})"
                    )
                    sys.stderr.flush()

                sys.stderr.write("\n")  # New line after progress bar
                sys.stderr.flush()

            logger.info("✅ Rebuilt %d files", file_count)

        # Touch built files to trigger hot reload
        await self._touch_built_files(files_to_build)

    async def _touch_built_files(self, source_files: list[Path]) -> None:
        """Touch built files to ensure mint dev detects changes.

        Args:
            source_files: List of source files that were built.
        """

        def touch_files_for_source(source_file: Path) -> int:
            """Touch all built files for a source file. Returns count touched."""
            try:
                current_time = time.time()
                touched_count = 0
                relative_path = source_file.absolute().relative_to(
                    self.src_dir.absolute()
                )

                # Handle different content types based on the updated build_file logic
                if relative_path.parts[0] == "oss":
                    # OSS content is versioned - check Python and JavaScript versions
                    # Skip if it's a shared file (images, JS, CSS) - those go to root
                    if self.builder.is_shared_file(source_file):
                        built_file = self.build_dir / relative_path
                        if built_file.suffix.lower() == ".md":
                            built_file = built_file.with_suffix(".mdx")
                        if built_file.exists():
                            os.utime(built_file, (current_time, current_time))
                            touched_count += 1
                    else:
                        # Remove 'oss/' prefix and add version-specific paths
                        sub_path = Path(*relative_path.parts[1:])

                        for version in ["python", "javascript"]:
                            built_file = self.build_dir / "oss" / version / sub_path

                            # Handle .md -> .mdx conversion
                            if built_file.suffix.lower() == ".md":
                                built_file = built_file.with_suffix(".mdx")

                            # Touch the file if it exists
                            if built_file.exists():
                                os.utime(built_file, (current_time, current_time))
                                touched_count += 1

                elif relative_path.parts[0] in {"labs", "langsmith"}:
                    # Unversioned content
                    built_file = self.build_dir / relative_path

                    # Handle .md -> .mdx conversion
                    if built_file.suffix.lower() == ".md":
                        built_file = built_file.with_suffix(".mdx")

                    # Touch the file if it exists
                    if built_file.exists():
                        os.utime(built_file, (current_time, current_time))
                        touched_count += 1

                elif self.builder.is_shared_file(source_file):
                    # Shared files (images, docs.json, JS/CSS) - go to build root
                    built_file = self.build_dir / relative_path
                    if built_file.exists():
                        os.utime(built_file, (current_time, current_time))
                        touched_count += 1

                else:
                    # Root-level files
                    built_file = self.build_dir / relative_path

                    # Handle .md -> .mdx conversion
                    if built_file.suffix.lower() == ".md":
                        built_file = built_file.with_suffix(".mdx")

                    # Touch the file if it exists
                    if built_file.exists():
                        os.utime(built_file, (current_time, current_time))
                        touched_count += 1

            except Exception:
                logger.exception("Failed to touch built files for %s", source_file)
                return 0
            else:
                return touched_count

        try:
            # Touch files concurrently for better performance
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [
                    loop.run_in_executor(executor, touch_files_for_source, source_file)
                    for source_file in source_files
                ]

                results = await asyncio.gather(*futures)
                total_touched = sum(results)

            logger.debug("Touched %d built files to trigger hot reload", total_touched)

        except Exception:
            logger.exception("Failed to touch built files for hot reload")

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
