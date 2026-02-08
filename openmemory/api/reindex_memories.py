#!/usr/bin/env python3
"""
Script to reindex existing memories from PostgreSQL to Qdrant.

Usage:
    python scripts/reindex_memories.py --user-id heldigard
    python scripts/reindex_memories.py --all  # Reindex for all users

This script:
1. Fetches all memories from PostgreSQL
2. Indexes them in Qdrant for semantic search (embeddings generated internally)
"""

import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Memory, User
from app.utils.memory import get_memory_client
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_user_memories(db: Session, user_id: str):
    """Fetch all memories for a user."""
    user = db.query(User).filter(User.name == user_id).first()
    if not user:
        logger.error(f"User '{user_id}' not found in database")
        return []

    memories = db.query(Memory).filter(
        Memory.user_id == user.id,
        Memory.state != 'deleted'
    ).all()

    logger.info(f"Found {len(memories)} memories for user '{user_id}'")
    return memories


def reindex_memories_for_user(user_id: str, batch_size: int = 10):
    """Reindex all memories for a specific user."""
    logger.info(f"Starting reindex for user: {user_id}")

    # Get memory client
    memory_client = get_memory_client()
    if not memory_client:
        logger.error("Failed to initialize memory client")
        return False

    db = SessionLocal()
    try:
        memories = get_user_memories(db, user_id)

        if not memories:
            logger.warning(f"No memories found for user '{user_id}'")
            return True

        indexed_count = 0
        errors_count = 0

        for i, memory in enumerate(memories):
            try:
                # Add memory content to vector store
                # mem0.add() will generate embeddings internally
                memory_client.add(
                    memory.content,
                    user_id=user_id,
                    metadata={
                        "memory_id": str(memory.id),
                        "source_app": "openmemory",
                        "migrated": True,
                        "created_at": memory.created_at.isoformat() if memory.created_at else None,
                    }
                )

                indexed_count += 1
                logger.info(f"[{i+1}/{len(memories)}] Indexed: {memory.id} - {memory.content[:50]}...")

                # Batch progress log
                if (indexed_count) % batch_size == 0:
                    logger.info(f"Progress: {indexed_count}/{len(memories)} memories indexed")

            except Exception as e:
                errors_count += 1
                logger.error(f"Error indexing memory {memory.id}: {e}")

        logger.info(f"Reindex complete for user '{user_id}': {indexed_count} indexed, {errors_count} errors")
        return errors_count == 0

    finally:
        db.close()


def reindex_all_users():
    """Reindex memories for all users in the database."""
    logger.info("Starting full reindex for all users")

    db = SessionLocal()
    try:
        users = db.query(User).all()
        logger.info(f"Found {len(users)} users")

        if not users:
            logger.warning("No users found in database")
            return True

        success_count = 0
        error_count = 0

        for user in users:
            logger.info(f"\n{'='*50}")
            logger.info(f"Processing user: {user.name}")
            logger.info(f"{'='*50}")

            # Count memories for this user
            memory_count = db.query(Memory).filter(
                Memory.user_id == user.id,
                Memory.state != 'deleted'
            ).count()
            logger.info(f"Memories to index: {memory_count}")

            if memory_count > 0:
                if reindex_memories_for_user(user.name):
                    success_count += 1
                else:
                    error_count += 1
            else:
                logger.info(f"Skipping user '{user.name}' - no memories")
                success_count += 1

        logger.info(f"\n{'='*50}")
        logger.info(f"Full reindex complete: {success_count} users successful, {error_count} users with errors")
        logger.info(f"{'='*50}")

        return error_count == 0

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Reindex memories from PostgreSQL to Qdrant"
    )
    parser.add_argument(
        '--user-id',
        type=str,
        help='Reindex memories for a specific user ID'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Reindex memories for all users'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Batch size for progress logging (default: 10)'
    )

    args = parser.parse_args()

    if not args.user_id and not args.all:
        parser.error("Must specify --user-id or --all")

    if args.user_id:
        success = reindex_memories_for_user(args.user_id, args.batch_size)
    else:
        success = reindex_all_users()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
