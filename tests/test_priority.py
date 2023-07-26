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

import torch
import unittest
from unittest.mock import MagicMock, patch
from openminers.base.priority import record_request_timestamps, default_priority


class PriorityTestCase(unittest.TestCase):
    def test_record_request_timestamps(self):
        hotkey_address = "hotkey1"
        len_request_timestamps = 20

        mock_self = MagicMock()
        mock_self.config.miner.priority.len_request_timestamps = len_request_timestamps
        mock_self.request_timestamps = {}

        mock_forward_call = MagicMock()
        mock_forward_call.src_hotkey = hotkey_address

        times = []
        for i in range(1, 21):
            mock_forward_call.start_time = i
            times.append(i)
            request_timestamps = record_request_timestamps(mock_self, mock_forward_call)
            assert (
                request_timestamps[hotkey_address]
                == [0] * (len_request_timestamps - i) + times
            )
            assert len(request_timestamps[hotkey_address]) == len_request_timestamps

    def test_default_priority(self):
        hotkey_address = "hotkey1"
        stake = 1
        default_priority_value = 100
        time_stake_multiplicate = 2

        mock_self = MagicMock()
        mock_self.metagraph.hotkeys = [hotkey_address]
        mock_self.metagraph.S = [torch.tensor(stake)]
        mock_self.config.miner.priority.time_stake_multiplicate = (
            time_stake_multiplicate
        )
        mock_self.config.miner.priority.default = default_priority_value

        mock_forward_call = MagicMock()
        mock_forward_call.src_hotkey = hotkey_address

        # return default when request timestamp is empty
        mock_self.request_timestamps = {}
        priority = default_priority(mock_self, mock_forward_call)
        assert priority == default_priority_value

        # return priority when request timestamp is not empty
        mock_self.request_timestamps = {hotkey_address: [0] * 10}
        for minute_passed in range(1, 20):
            with patch("time.time", MagicMock(return_value=minute_passed * 60)):
                priority = default_priority(mock_self, mock_forward_call)
                assert (
                    priority == max(minute_passed / time_stake_multiplicate, 1) * stake
                )
