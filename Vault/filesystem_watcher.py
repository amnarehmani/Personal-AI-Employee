"""
File System Watcher for AI Employee

This script monitors the Inbox folder for new files and moves them to Needs_Action
when detected. This is a simple implementation of the watcher pattern described
in the hackathon document.
"""

import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InboxHandler(FileSystemEventHandler):
    """Handles file system events in the Inbox folder"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        logger.info(f"Initialized InboxHandler with vault path: {vault_path}")

    def on_created(self, event):
        """Called when a file is created in the watched directory"""
        if event.is_directory:
            return

        source = Path(event.src_path)
        logger.info(f"New file detected: {source.name}")

        # Move file from Inbox to Needs_Action
        if self.inbox in source.parents:  # Make sure it's actually from inbox
            dest = self.needs_action / source.name
            try:
                # Wait a moment to ensure file is fully written
                time.sleep(1)

                # Move the file to Needs_Action folder
                shutil.move(str(source), str(dest))
                logger.info(f"Moved {source.name} from Inbox to Needs_Action")

                # Create a metadata file with processing instructions
                self.create_processing_metadata(source, dest)

            except Exception as e:
                logger.error(f"Error moving file {source.name}: {e}")

    def on_moved(self, event):
        """Called when a file is moved in the watched directory"""
        if event.is_directory:
            return

        dest = Path(event.dest_path)
        logger.info(f"File moved to: {dest.name}")

    def create_processing_metadata(self, source: Path, dest: Path):
        """Create a metadata file with processing instructions"""
        meta_content = f"""---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size if source.exists() else 0}
received: {datetime.now().isoformat()}
status: pending
---

## Processing Request
File '{source.name}' has been moved to Needs_Action.

## Suggested Actions
- [ ] Review content
- [ ] Determine priority
- [ ] Assign appropriate action
- [ ] Process and move to Done when complete

## Original Location
{source.parent.name}
"""

        # Create a .md file with the same name to provide processing instructions
        meta_path = dest.with_suffix('.md')
        try:
            # Only create metadata if the file doesn't exist already
            if not meta_path.exists():
                with open(meta_path, 'w', encoding='utf-8') as f:
                    f.write(meta_content)
                logger.info(f"Created metadata file: {meta_path.name}")
        except Exception as e:
            logger.error(f"Error creating metadata for {dest.name}: {e}")

def main():
    """Main function to run the file system watcher"""
    vault_path = Path.cwd()  # Current working directory

    # Ensure required directories exist
    (vault_path / 'Inbox').mkdir(exist_ok=True)
    (vault_path / 'Needs_Action').mkdir(exist_ok=True)
    (vault_path / 'Done').mkdir(exist_ok=True)
    (vault_path / 'Plans').mkdir(exist_ok=True)
    (vault_path / 'Pending_Approval').mkdir(exist_ok=True)
    (vault_path / 'Logs').mkdir(exist_ok=True)

    # Create the event handler
    event_handler = InboxHandler(str(vault_path))

    # Create the observer
    observer = Observer()
    observer.schedule(event_handler, str(vault_path / 'Inbox'), recursive=False)

    # Start the observer
    observer.start()
    logger.info("File system watcher started. Monitoring Inbox folder...")
    logger.info("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("File system watcher stopped by user.")

    observer.join()
    logger.info("File system watcher terminated.")

if __name__ == "__main__":
    main()