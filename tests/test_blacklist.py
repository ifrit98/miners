# The MIT License (MIT)
# Copyright © 2023 Yuma Rao

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import time
import json
import hashlib
import unittest
from unittest.mock import MagicMock
from openminers.base.blacklist import is_prompt_in_cache, default_blacklist


class BlacklistTestCase(unittest.TestCase):
    def test_sanitize_cache(self):
        """Test if old entries are removed according to block span"""
        # Arrange
        messages = ["Message from hotkey1"]
        key_to_delete = hashlib.sha256(json.dumps(messages).encode()).hexdigest()

        mock_prompt_cache = {
            key_to_delete: ("hotkey1", 1),
        }
        prompt_cache_block_span = 1
        current_block = 3

        mock_self = MagicMock()
        mock_self.prompt_cache = mock_prompt_cache.copy()
        mock_self.config.miner.blacklist.prompt_cache_block_span = (
            prompt_cache_block_span
        )
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
        """Test if entries are not removed according to block span"""
        # Arrange
        messages = ["Message from hotkey1"]
        prompt_key = hashlib.sha256(json.dumps(messages).encode()).hexdigest()

        mock_prompt_cache = {
            prompt_key: ("hotkey1", 3),
        }
        prompt_cache_block_span = 1
        current_block = 3

        mock_self = MagicMock()
        mock_self.prompt_cache = mock_prompt_cache.copy()
        mock_self.config.miner.blacklist.prompt_cache_block_span = (
            prompt_cache_block_span
        )
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
        """Test if repeated entries are blacklisted"""
        # Arrange
        messages = ["Message from hotkey1"]
        prompt_key = hashlib.sha256(json.dumps(messages).encode()).hexdigest()

        mock_prompt_cache = {
            prompt_key: ("hotkey1", 1),
        }
        prompt_cache_block_span = 1
        current_block = 1

        mock_self = MagicMock()
        mock_self.prompt_cache = mock_prompt_cache.copy()
        mock_self.config.miner.blacklist.prompt_cache_block_span = (
            prompt_cache_block_span
        )
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
        """Test if new entries are not blacklisted and added correctly to cache"""
        # Arrange
        messages = ["New prompt from hotkey1"]
        expected_prompt_key = hashlib.sha256(json.dumps(messages).encode()).hexdigest()

        mock_prompt_cache = {}
        prompt_cache_block_span = 1
        current_block = 1

        mock_self = MagicMock()
        mock_self.prompt_cache = mock_prompt_cache.copy()
        mock_self.config.miner.blacklist.prompt_cache_block_span = (
            prompt_cache_block_span
        )
        mock_self.metagraph.block = current_block

        mock_forward_call = MagicMock()
        mock_forward_call.src_hotkey = "hotkey1"
        mock_forward_call.messages = messages

        # Act
        should_blacklist = is_prompt_in_cache(mock_self, mock_forward_call)

        # Assert
        assert should_blacklist is False
        assert mock_self.prompt_cache[expected_prompt_key] == ("hotkey1", current_block)

    def test_request_timestamps_blacklist(self):
        hotkey_address = "hotkey1"
        min_request_period = 30
        len_request_timestamps = 50

        mock_self = MagicMock()
        mock_self.config.miner.blacklist.whitelist = []
        mock_self.config.miner.blacklist.blacklist = []
        mock_self.config.miner.blacklist.allow_non_registered = False
        mock_self.config.miner.blacklist.force_validator_permit = False
        mock_self.config.miner.blacklist.min_request_period = min_request_period
        mock_self.metagraph.hotkeys = [hotkey_address]
        mock_self.request_timestamps = {
            hotkey_address: [time.time() - (min_request_period * 60 - 1)]
            * len_request_timestamps
        }

        mock_forward_call = MagicMock()
        mock_forward_call.src_hotkey = hotkey_address
        mock_forward_call.messages = "message"

        should_blacklist, blacklist_message = default_blacklist(
            mock_self, mock_forward_call
        )
        assert should_blacklist == True

        # Should not black list when period is longer
        mock_self.request_timestamps = {
            hotkey_address: [time.time() - (min_request_period * 60)]
            * len_request_timestamps
        }
        should_blacklist, blacklist_message = default_blacklist(
            mock_self, mock_forward_call
        )
        assert should_blacklist == False

    def test_request_timestamps_blacklist_empty_dictionary(self):
        hotkey_address = "hotkey1"
        min_request_period = 30

        mock_self = MagicMock()
        mock_self.config.miner.blacklist.whitelist = []
        mock_self.config.miner.blacklist.blacklist = []
        mock_self.config.miner.blacklist.allow_non_registered = False
        mock_self.config.miner.blacklist.force_validator_permit = False
        mock_self.config.miner.blacklist.min_request_period = min_request_period
        mock_self.metagraph.hotkeys = [hotkey_address]
        mock_self.request_timestamps = {}

        mock_forward_call = MagicMock()
        mock_forward_call.src_hotkey = hotkey_address
        mock_forward_call.messages = "message"

        should_blacklist, blacklist_message = default_blacklist(
            mock_self, mock_forward_call
        )
        assert should_blacklist == False


if __name__ == "__main__":
    unittest.main()
