import json
import hashlib
import unittest
from unittest.mock import MagicMock
from openminers.base.blacklist import is_prompt_in_cache

class BlacklistTestCase(unittest.TestCase):
    def test_sanitize_cache(self):
        """ Test if old entries are removed according to block span """
        # Arrange
        messages =  ["Message from hotkey1"]
        key_to_delete =  hashlib.sha256(json.dumps(messages).encode()).hexdigest()

        mock_prompt_cache = {
            key_to_delete: ('hotkey1', 1),
        }
        prompt_cache_block_span = 1
        current_block = 3

        mock_self = MagicMock()
        mock_self.prompt_cache = mock_prompt_cache.copy()
        mock_self.config.miner.blacklist.prompt_cache_block_span = prompt_cache_block_span
        mock_self.metagraph.block = current_block

        mock_forward_call = MagicMock()
        mock_forward_call.src_hotkey = "hotkey1"
        mock_forward_call.messages = messages

        # Act
        should_blacklist = is_prompt_in_cache(mock_self, mock_forward_call)

        # Assert
        assert should_blacklist is True
        assert len(mock_self.prompt_cache) == len(mock_prompt_cache) - 1

    def test_sanitize_cache_no_entries_removed(self):
        """ Test if entries are not removed according to block span """
        # Arrange
        messages = ["Message from hotkey1"]
        prompt_key = hashlib.sha256(json.dumps(messages).encode()).hexdigest()

        mock_prompt_cache = {
            prompt_key: ('hotkey1', 3),
        }
        prompt_cache_block_span = 1
        current_block = 3

        mock_self = MagicMock()
        mock_self.prompt_cache = mock_prompt_cache.copy()
        mock_self.config.miner.blacklist.prompt_cache_block_span = prompt_cache_block_span
        mock_self.metagraph.block = current_block

        mock_forward_call = MagicMock()
        mock_forward_call.src_hotkey = "hotkey1"
        mock_forward_call.messages = messages

        # Act
        should_blacklist = is_prompt_in_cache(mock_self, mock_forward_call)

        # Assert
        assert should_blacklist is True
        assert len(mock_self.prompt_cache) == len(mock_prompt_cache)


    def test_existing_prompt_in_cache(self):
        """ Test if repeated entries are blacklisted"""
        # Arrange
        messages = ["Message from hotkey1"]
        prompt_key = hashlib.sha256(json.dumps(messages).encode()).hexdigest()

        mock_prompt_cache = {
            prompt_key: ('hotkey1', 1),
        }
        prompt_cache_block_span = 1
        current_block = 1

        mock_self = MagicMock()
        mock_self.prompt_cache = mock_prompt_cache.copy()
        mock_self.config.miner.blacklist.prompt_cache_block_span = prompt_cache_block_span
        mock_self.metagraph.block = current_block

        mock_forward_call = MagicMock()
        mock_forward_call.src_hotkey = "hotkey1"
        mock_forward_call.messages = messages

        # Act
        should_blacklist = is_prompt_in_cache(mock_self, mock_forward_call)

        # Assert
        assert should_blacklist is True
        assert mock_self.prompt_cache == mock_prompt_cache


    def test_new_prompt_not_in_cache(self):
        """ Test if new entries are not blacklisted and added correctly to cache """
        # Arrange
        messages = ["New prompt from hotkey1"]
        expected_prompt_key = hashlib.sha256(json.dumps(messages).encode()).hexdigest()

        mock_prompt_cache = {}
        prompt_cache_block_span = 1
        current_block = 1

        mock_self = MagicMock()
        mock_self.prompt_cache = mock_prompt_cache.copy()
        mock_self.config.miner.blacklist.prompt_cache_block_span = prompt_cache_block_span
        mock_self.metagraph.block = current_block

        mock_forward_call = MagicMock()
        mock_forward_call.src_hotkey = "hotkey1"
        mock_forward_call.messages = messages

        # Act
        should_blacklist = is_prompt_in_cache(mock_self, mock_forward_call)

        # Assert
        assert should_blacklist is False
        assert mock_self.prompt_cache[expected_prompt_key] == ('hotkey1', current_block)



if __name__ == '__main__':
    unittest.main()
