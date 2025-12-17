"""Test script to verify conversation persistence works correctly."""

import json
import os
from pathlib import Path
from src.aicli.ollama_client import ConversationManager

def test_persistence():
    """Test that conversation history is persisted to file."""

    # Use a test file instead of the real one
    test_file = Path.home() / ".aicli_test_conversation.json"

    # Clean up any existing test file
    if test_file.exists():
        test_file.unlink()

    print("Step 1: Creating first ConversationManager instance...")
    # Create first instance with some messages
    conv1 = ConversationManager(
        system_prompt="Test system prompt",
        history_file=str(test_file)
    )

    # Add some messages
    conv1.add_user_message("Hello, can you help me?")
    conv1.add_assistant_message("Of course! How can I assist you?", [])
    conv1.add_user_message("I need help with my code")

    print(f"✓ Added 3 messages (plus system prompt)")
    print(f"✓ Total messages in memory: {len(conv1.get_messages())}")

    # Verify file was created
    assert test_file.exists(), "History file was not created!"
    print(f"✓ History file created at {test_file}")

    # Read and display file contents
    with open(test_file, 'r') as f:
        saved_data = json.load(f)
    print(f"✓ File contains {len(saved_data)} messages")

    print("\nStep 2: Creating second ConversationManager instance...")
    # Create second instance - should load from file
    conv2 = ConversationManager(
        system_prompt="Test system prompt",
        history_file=str(test_file)
    )

    messages = conv2.get_messages()
    print(f"✓ Loaded {len(messages)} messages from file")

    # Verify messages match
    assert len(messages) == len(conv1.get_messages()), \
        f"Message count mismatch! Expected {len(conv1.get_messages())}, got {len(messages)}"

    # Check specific messages
    user_messages = [m for m in messages if m['role'] == 'user']
    assert len(user_messages) == 2, f"Expected 2 user messages, got {len(user_messages)}"
    assert user_messages[0]['content'] == "Hello, can you help me?"
    assert user_messages[1]['content'] == "I need help with my code"

    print("✓ All messages loaded correctly!")

    print("\nStep 3: Testing clear functionality...")
    conv2.clear()
    messages_after_clear = conv2.get_messages()
    print(f"✓ After clear: {len(messages_after_clear)} messages (should be 1 - system prompt)")
    assert len(messages_after_clear) == 1
    assert messages_after_clear[0]['role'] == 'system'

    # Verify clear was persisted
    conv3 = ConversationManager(
        system_prompt="Test system prompt",
        history_file=str(test_file)
    )
    assert len(conv3.get_messages()) == 1, "Clear was not persisted!"
    print("✓ Clear operation was persisted correctly!")

    # Cleanup
    print(f"\nCleaning up test file...")
    test_file.unlink()
    print("✓ Test file removed")

    print("\n" + "="*50)
    print("🎉 All tests passed! Persistence is working correctly!")
    print("="*50)

if __name__ == "__main__":
    test_persistence()
