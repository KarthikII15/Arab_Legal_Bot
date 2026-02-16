"""
Test suite for chat persistence functionality (Issue 1)
Tests that new chats are created, saved, and appear in history
"""

import pytest
import json
import time
import os
from datetime import datetime
from chat_storage import ChatStorage
from pathlib import Path

class TestChatPersistence:
    """Test chat history persistence functionality"""
    
    @pytest.fixture
    def storage(self):
        """Create test storage instance with temporary database"""
        test_db_path = "test_chat_history.db"
        storage = ChatStorage(db_path=test_db_path)
        yield storage
        # Cleanup
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    
    def test_new_chat_saves_to_database(self, storage):
        """
        Test Issue 1: New chat is saved to the database
        Verify: Chat created → saved to database → can be retrieved
        """
        # Create new conversation
        conv_id = "test_conv_001"
        title = "تحليل قضية تجارية"
        preview = "نزاع حول عقد توريد"
        messages = [
            {
                "id": "msg_001",
                "role": "user",
                "content": "تحليل قضيتي",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "msg_002",
                "role": "assistant",
                "content": "سيتم تحليل القضية",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        # Save conversation
        print(f"\n[TEST] Saving conversation {conv_id}")
        success = storage.save_conversation(conv_id, title, preview, messages, None)
        
        assert success, "Failed to save conversation"
        print(f"[TEST] ✓ Conversation saved successfully")
        
        # Retrieve and verify
        print(f"[TEST] Retrieving conversation {conv_id}")
        retrieved = storage.get_conversation(conv_id)
        
        assert retrieved is not None, "Conversation not found after save"
        assert retrieved['id'] == conv_id, "Conversation ID mismatch"
        assert retrieved['title'] == title, "Title mismatch"
        assert len(retrieved['messages']) == len(messages), "Message count mismatch"
        print(f"[TEST] ✓ Conversation retrieved and verified")
    
    def test_new_chat_appears_in_history_list(self, storage):
        """
        Test Issue 1: New chat appears in chat history list
        Verify: Create chat → appears in get_all_conversations()
        """
        # Create multiple conversations
        conversations = [
            {
                "id": "conv_001",
                "title": "قضية 1",
                "preview": "نزاع تجاري",
                "messages": [{"role": "user", "content": "الرسالة 1"}]
            },
            {
                "id": "conv_002",
                "title": "قضية 2",
                "preview": "نزاع عمل",
                "messages": [{"role": "user", "content": "الرسالة 2"}]
            },
            {
                "id": "conv_003",
                "title": "قضية 3",
                "preview": "نزاع إداري",
                "messages": [{"role": "user", "content": "الرسالة 3"}]
            }
        ]
        
        # Save all conversations
        print(f"\n[TEST] Saving {len(conversations)} conversations")
        for conv in conversations:
            success = storage.save_conversation(
                conv['id'], conv['title'], conv['preview'], conv['messages'], None
            )
            assert success, f"Failed to save {conv['id']}"
            print(f"[TEST] ✓ Saved {conv['id']}")
        
        # Get conversation list
        print(f"[TEST] Retrieving conversation list")
        conv_list = storage.get_all_conversations(limit=50)
        
        assert len(conv_list) >= len(conversations), "Not all conversations in list"
        print(f"[TEST] ✓ Retrieved {len(conv_list)} conversations")
        
        # Verify each conversation is in the list
        retrieved_ids = [c['id'] for c in conv_list]
        for conv in conversations:
            assert conv['id'] in retrieved_ids, f"{conv['id']} not found in history list"
            print(f"[TEST] ✓ {conv['id']} found in history")
    
    def test_chat_persists_after_database_reload(self, storage):
        """
        Test Issue 1: Chat persists after application reload
        Verify: Create chat → reload DB → chat still exists
        """
        db_path = storage.db_path
        conv_id = "persistent_chat_001"
        title = "محادثة دائمة"
        messages = [{"role": "user", "content": "هذه الرسالة يجب أن تستمر"}]
        
        # Save conversation
        print(f"\n[TEST] Saving conversation to persist: {conv_id}")
        success = storage.save_conversation(conv_id, title, "preview", messages, None)
        assert success, "Failed to save conversation for persistence test"
        print(f"[TEST] ✓ Conversation saved")
        
        # Create new storage instance (simulates app reload)
        print(f"[TEST] Creating new storage instance (simulating app reload)")
        storage2 = ChatStorage(db_path=db_path)
        
        # Reload conversation
        retrieved = storage2.get_conversation(conv_id)
        
        assert retrieved is not None, "Conversation not found after reload"
        assert retrieved['title'] == title, "Title lost after reload"
        assert retrieved['messages'][0]['content'] == messages[0]['content'], "Message content lost"
        print(f"[TEST] ✓ Conversation persisted across reload")
    
    def test_update_existing_chat(self, storage):
        """
        Test: Updating an existing chat (ON CONFLICT UPDATE)
        Verify: Save with same ID → overwrites previous data
        """
        conv_id = "test_update_001"
        
        # Save initial version
        print(f"\n[TEST] Saving initial version of {conv_id}")
        msg1 = [{"role": "user", "content": "First message"}]
        success = storage.save_conversation(conv_id, "Initial Title", "Initial preview", msg1, None)
        assert success, "Failed to save initial version"
        print(f"[TEST] ✓ Initial version saved")
        
        # Update with new version
        print(f"[TEST] Updating {conv_id} with new content")
        msg2 = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "Response"},
            {"role": "user", "content": "Second message"}
        ]
        success = storage.save_conversation(conv_id, "Updated Title", "Updated preview", msg2, None)
        assert success, "Failed to update conversation"
        print(f"[TEST] ✓ Updated version saved")
        
        # Verify update
        retrieved = storage.get_conversation(conv_id)
        
        assert retrieved['title'] == "Updated Title", "Title not updated"
        assert len(retrieved['messages']) == 3, "Messages not updated"
        assert retrieved['messages'][-1]['content'] == "Second message", "New message not added"
        print(f"[TEST] ✓ Update verified - conversation has {len(retrieved['messages'])} messages")
    
    def test_concurrent_chat_creation(self, storage):
        """
        Test: Multiple chats created rapidly (stress test)
        Verify: All chats saved successfully and appear in history
        """
        num_chats = 10
        conv_ids = []
        
        print(f"\n[TEST] Creating {num_chats} conversations rapidly")
        
        # Create multiple conversations quickly
        for i in range(num_chats):
            conv_id = f"test_concurrent_{i:03d}"
            conv_ids.append(conv_id)
            
            success = storage.save_conversation(
                conv_id,
                f"Chat {i}",
                f"Preview {i}",
                [{"role": "user", "content": f"Message {i}"}],
                None
            )
            
            assert success, f"Failed to save {conv_id}"
            if (i + 1) % 3 == 0:
                print(f"[TEST] ✓ Saved {i + 1}/{num_chats} conversations")
        
        # Get all conversations
        print(f"[TEST] Retrieving all conversations")
        conv_list = storage.get_all_conversations()
        
        # Verify all created conversations are in the list
        retrieved_ids = [c['id'] for c in conv_list]
        for conv_id in conv_ids:
            assert conv_id in retrieved_ids, f"{conv_id} not in history list"
        
        print(f"[TEST] ✓ All {num_chats} conversations found in history")
    
    def test_chat_with_analysis_data(self, storage):
        """
        Test: Chat with analysis data (classification, etc.) is saved correctly
        Verify: Analysis object properly serialized and deserialized
        """
        conv_id = "test_analysis_001"
        messages = [{"role": "user", "content": "قضية تجارية"}]
        analysis = {
            "classification": {
                "name_ar": "نزاع تجاري",
                "name_en": "Commercial Dispute",
                "confidence": 0.95,
                "category": "commercial"
            },
            "legal_principles": ["قانون الالتزامات", "قانون العقود"],
            "recommendations": ["طلب تسوية", "المحاكمة"]
        }
        
        print(f"\n[TEST] Saving conversation with analysis data: {conv_id}")
        success = storage.save_conversation(conv_id, "قضية بتحليل", "نزاع", messages, analysis)
        
        assert success, "Failed to save conversation with analysis"
        print(f"[TEST] ✓ Conversation with analysis saved")
        
        # Retrieve and verify
        retrieved = storage.get_conversation(conv_id)
        
        assert retrieved['analysis'] is not None, "Analysis data lost"
        assert retrieved['analysis']['classification']['confidence'] == 0.95, "Confidence value corrupted"
        assert len(retrieved['analysis']['legal_principles']) == 2, "Legal principles lost"
        print(f"[TEST] ✓ Analysis data verified - classification confidence: {retrieved['analysis']['classification']['confidence']}")
    
    def test_arabic_text_preservation(self, storage):
        """
        Test: Arabic text in conversations is preserved correctly
        Verify: UTF-8 encoding works + no character corruption
        """
        conv_id = "test_arabic_001"
        arabic_title = "تحليل قضية الطلاق والحضانة"
        arabic_preview = "نزاع على حقوق الحضانة بين الزوجين"
        arabic_messages = [
            {
                "role": "user",
                "content": "أريد تحليل قضيتي المتعلقة بالطلاق والحضانة"
            },
            {
                "role": "assistant",
                "content": "سأقوم بتحليل قضيتك المتعلقة بالطلاق والحضانة حسب القانون الشرعي والمحلي"
            }
        ]
        
        print(f"\n[TEST] Saving conversation with Arabic text: {conv_id}")
        success = storage.save_conversation(conv_id, arabic_title, arabic_preview, arabic_messages, None)
        
        assert success, "Failed to save Arabic text"
        print(f"[TEST] ✓ Arabic text saved")
        
        # Retrieve and verify encoding
        retrieved = storage.get_conversation(conv_id)
        
        assert retrieved['title'] == arabic_title, "Arabic title corrupted"
        assert retrieved['preview'] == arabic_preview, "Arabic preview corrupted"
        assert retrieved['messages'][0]['content'] == arabic_messages[0]['content'], "Arabic message content corrupted"
        print(f"[TEST] ✓ Arabic text preserved correctly")
    
    def test_large_conversation_history(self, storage):
        """
        Test: Conversation with many messages handles correctly
        Verify: Large message arrays don't cause issues
        """
        conv_id = "test_large_001"
        num_messages = 100
        
        # Create large message array
        print(f"\n[TEST] Creating conversation with {num_messages} messages: {conv_id}")
        messages = []
        for i in range(num_messages):
            messages.append({
                "id": f"msg_{i:03d}",
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Message {i}: " + ("صالح " * 20),  # Large text
                "timestamp": datetime.now().isoformat()
            })
        
        # Save
        success = storage.save_conversation(conv_id, "Large Conversation", "100 messages", messages, None)
        assert success, "Failed to save large conversation"
        print(f"[TEST] ✓ Saved conversation with {num_messages} messages")
        
        # Retrieve
        retrieved = storage.get_conversation(conv_id)
        
        assert len(retrieved['messages']) == num_messages, "Message count mismatch"
        assert retrieved['messages'][-1]['content'].startswith("Message 99"), "Last message incorrect"
        print(f"[TEST] ✓ Retrieved conversation with all {num_messages} messages intact")
    
    def test_database_integrity(self, storage):
        """
        Test: Database file integrity and accessibility
        Verify: Database file exists and is valid
        """
        print(f"\n[TEST] Checking database integrity")
        
        # Save a conversation first
        storage.save_conversation("test_integrity_001", "Test", "Test", [], None)
        
        # Check file exists
        db_path = storage.db_path
        assert os.path.exists(db_path), "Database file does not exist"
        print(f"[TEST] ✓ Database file exists: {db_path}")
        
        # Check file size is reasonable
        file_size = os.path.getsize(db_path)
        assert file_size > 0, "Database file is empty"
        print(f"[TEST] ✓ Database file size: {file_size} bytes")
        
        # Try to open multiple connections simultaneously
        conn1 = storage._get_conn()
        conn2 = storage._get_conn()
        
        assert conn1 is not None, "Failed to create first connection"
        assert conn2 is not None, "Failed to create second connection"
        
        conn1.close()
        conn2.close()
        print(f"[TEST] ✓ Multiple database connections work")


# Run tests manually
if __name__ == "__main__":
    print("=" * 60)
    print("Chat Persistence Tests (Issue 1)")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "-s"])
