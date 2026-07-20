import pytest
import os
import shutil
from app.memory.store_semantic import SemanticMemoryStore

@pytest.fixture
def semantic_store():
    # Use a temporary directory for tests
    test_dir = "./test_chroma_db"
    store = SemanticMemoryStore(persist_directory=test_dir)
    yield store
    # Cleanup
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir, ignore_errors=True)

def test_semantic_memory_store(semantic_store):
    # Store a turn
    turn_id = "test_turn_1"
    content = "I really love playing tennis on the weekends."
    semantic_store.store_turn(turn_id, content, metadata={"role": "user"})
    
    # Store another unrelated turn
    semantic_store.store_turn("test_turn_2", "My favorite color is blue.", metadata={"role": "user"})
    
    # Query for related concepts
    results = semantic_store.query_memory("What sports do I like?", n_results=1)
    
    assert len(results) == 1
    assert "tennis" in results[0]
