
import logging
import sqlite3

from pathlib import Path
from langgraph.checkpoint.sqlite import SqliteSaver

logger = logging.getLogger(__name__)


class CheckpointManager:

    def __init__(self):
        self.checkpointer = None
        self.connection = None

        # Project root directory
        self.project_root = Path(__file__).resolve().parents[2]

        # Persistent checkpoint database
        self.database_path = (
            self.project_root / "clinical_checkpoints.sqlite"
        )

    def initialize(self):

        if self.checkpointer is None:

            self.database_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            self.connection = sqlite3.connect(
                str(self.database_path),
                check_same_thread=False
            )

            self.connection.execute(
                "PRAGMA journal_mode=WAL"
            )

            self.checkpointer = SqliteSaver(
                self.connection
            )

            self.checkpointer.setup()

            logger.info(
                "SQLite persistent checkpoint storage initialized: %s",
                self.database_path
            )

        return self.checkpointer

    def get_config(self, thread_id):

        if not thread_id:
            raise ValueError(
                "Thread ID is required."
            )

        return {
            "configurable": {
                "thread_id": str(thread_id)
            }
        }

    def get_checkpointer(self):
        return self.initialize()

    def close(self):

        if self.connection is not None:

            self.connection.close()

            self.connection = None
            self.checkpointer = None

            logger.info(
                "SQLite checkpoint connection closed."
            )


checkpoint_manager = CheckpointManager()
