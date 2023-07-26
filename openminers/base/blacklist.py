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
import wandb
import hashlib
import bittensor as bt
from typing import Union, Tuple, Callable


def is_prompt_in_cache(self, forward_call: "bt.TextPromptingForwardCall") -> bool:
    # Hashes prompt
    # Note: Could be improved using a similarity check
    prompt = json.dumps(list(forward_call.messages))
    prompt_key = hashlib.sha256(prompt.encode()).hexdigest()
    current_block = self.metagraph.block

    should_blacklist: bool
    # Check if prompt is in cache, if not add it
    if prompt_key in self.prompt_cache:
        should_blacklist = True
    else:
        caller_hotkey = forward_call.src_hotkey
        self.prompt_cache[prompt_key] = (caller_hotkey, current_block)
        should_blacklist = False

    # Sanitize cache by removing old entries according to block span
    keys_to_remove = []
    for key, (_, block) in self.prompt_cache.items():
        if block + self.config.miner.blacklist.prompt_cache_block_span < current_block:
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del self.prompt_cache[key]

    return should_blacklist


def default_blacklist(
    self, forward_call: "bt.TextPromptingForwardCall"
) -> Union[Tuple[bool, str], bool]:
    # Check if the key is white listed.
    if forward_call.src_hotkey in self.config.miner.blacklist.whitelist:
        return False, "whitelisted hotkey"

    # Check if the key is black listed.
    if forward_call.src_hotkey in self.config.miner.blacklist.blacklist:
        return True, "blacklisted hotkey"

    # Check registration if we do not allow non-registered users
    if (
        not self.config.miner.blacklist.allow_non_registered
        and self.metagraph is not None
        and forward_call.src_hotkey not in self.metagraph.hotkeys
    ):
        return True, "hotkey not registered"

    # If the user is registered, it has a UID.
    uid = self.metagraph.hotkeys.index(forward_call.src_hotkey)

    # Check if the key has validator permit
    if (
        self.config.miner.blacklist.force_validator_permit
        and not self.metagraph.validator_permit[uid]
    ):
        return True, "validator permit required"

    if is_prompt_in_cache(self, forward_call):
        return True, "prompt already sent recently"

    # request period
    if forward_call.src_hotkey in self.request_timestamps:
        period = time.time() - self.request_timestamps[forward_call.src_hotkey][0]
        if period < self.config.miner.blacklist.min_request_period * 60:
            return (
                True,
                f"{forward_call.src_hotkey} request frequency exceeded {len(self.request_timestamps[forward_call.src_hotkey])} requests in {self.config.miner.blacklist.min_request_period} minutes.",
            )

    # Otherwise the user is not blacklisted.
    return False, "passed blacklist"


def blacklist(
    self, func: Callable, forward_call: "bt.TextPromptingForwardCall"
) -> Union[Tuple[bool, str], bool]:
    bt.logging.trace("run blacklist function")

    # First check to see if the black list function is overridden by the subclass.
    does_blacklist = None
    reason = None
    try:
        # Run the subclass blacklist function.
        blacklist_result = func(forward_call)

        # Unpack result.
        if hasattr(blacklist_result, "__len__"):
            does_blacklist, reason = blacklist_result
        else:
            does_blacklist = blacklist_result
            reason = "no reason provided"

    except NotImplementedError:
        # The subclass did not override the blacklist function.
        does_blacklist, reason = default_blacklist(self, forward_call)

    except Exception as e:
        # There was an error in their blacklist function.
        bt.logging.error(f"Error in blacklist function: {e}")
        does_blacklist, reason = default_blacklist(self, forward_call)

    finally:
        # If the blacklist function returned None, we use the default blacklist.
        if does_blacklist == None:
            does_blacklist, reason = default_blacklist(self, forward_call)

        # Finally, log and return the blacklist result.
        bt.logging.trace(f"blacklisted: {does_blacklist}, reason: {reason}")
        if does_blacklist and self.config.wandb.on:
            wandb.log(
                {
                    "blacklisted": float(does_blacklist),
                    "return_message": reason,
                    "hotkey": forward_call.src_hotkey,
                }
            )
        return does_blacklist, reason
