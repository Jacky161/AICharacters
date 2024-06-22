import json
import copy
from typing import Optional
from abc import ABC, abstractmethod
from llmexceptions import *


class BaseLLM(ABC):
    """
    Base Abstract Class for interacting with an LLM but is missing an actual LLM implementation.
    """

    def __init__(self, system_message: Optional[str] = None, n_ctx: int = 512,
                 temperature: float = 1.0, token_trim: float = 0.9,
                 verbose: bool = False, history_file: Optional[str] = None) -> None:
        """
        Initializes the base LLM class.

        :param system_message: The initial system message provided to the LLM.
        :param n_ctx: Size of the context window. Defaults to 512. Should be changed to match your implementation.
        :param temperature: Adjusts the level of creativity the LLM gives in its responses. (0.0-1.0 inclusive)
        :param token_trim: Sets the point of how full the context window should be until we start trimming old messages.
        :param verbose: Sets whether we print helpful debug messages to the console.
        :param history_file: Conversation JSON file to import if applicable.
        """
        self._messages = []
        self._n_ctx = n_ctx
        self._temperature = temperature
        self._token_trim = token_trim
        self._verbose = verbose
        self._system_msg_tokens = 0

        # Import conversation history if it exists
        if history_file is not None:
            with open(history_file, "r", encoding="utf-8") as file:
                self._messages = json.load(file)
                self._log(f"Loaded history file, {history_file}")
        elif system_message is not None:  # system_message is ignored if history_file is provided
            self.add_message("system", system_message)
            self._log(f"Loading system message, {system_message}")

        if len(self._messages) > 0:
            # Check if we do have a system message and measure its token length
            if self._messages[0]["role"] == "system":
                self._system_msg_tokens = self.get_token_msg(self._messages[0]["content"], "system")
                self._log(f"Imported system message with {self._system_msg_tokens} tokens.")

    def add_message(self, role: str, content: str) -> None:
        """
        Adds a new message to the conversation history of the LLM.
        :param role: Who the message was spoken by - (system, user, assistant)
        :param content: The message to be added.
        """
        valid_roles = ("system", "user", "assistant")
        if role not in valid_roles:
            raise NonValidRole(f"Role must be one of {valid_roles}, not {role}")

        # Add the message to the history
        new_message = {"role": role, "content": content}
        self._messages.append(new_message)

    def get_message_history(self) -> list[dict[str, str]]:
        """
        Returns a copy of the messages in the conversation history.
        """
        return copy.deepcopy(self._messages)

    def _prep_ask(self, msg: str) -> bool:
        """
        Preps the LLM for a new prompt provided to it. We make sure the message does not have too many tokens
        to process first. Then, we trim messages if needed to stay within the acceptable context fill %.
        """
        # Ensure message itself does not exceed max tokens
        msg_tokens = self.get_token_msg(msg)
        self._log(f"Got a prompt with {msg_tokens} tokens.")

        if msg_tokens + self._system_msg_tokens > self._token_trim * self._n_ctx:
            raise MaxCtxWindow(f"Message {msg} has {msg_tokens} exceeds maximum context window.")

        # Add the message to the history
        self.add_message("user", msg)

        # Check our token usage, trim if percentage used is too high
        cur_token = self.get_token_count()
        fill_amount = self.get_token_count() / self._n_ctx

        self._log(f"Current token count in history is {cur_token}. "
                  f"Context Fill % is {fill_amount * 100:.2f}%.")

        # Keep removing old messages until context fill % is low enough
        while fill_amount > self._token_trim:
            if self._messages[0]["role"] != "system":
                self._messages.pop(0)
            else:
                self._messages.pop(1)

            cur_token = self.get_token_count()
            fill_amount = self.get_token_count() / self._n_ctx

            self._log(f"Popped a message! Token count is now {cur_token}. "
                      f"Context Fill % is {fill_amount * 100:.2f}%.")

        return True

    @abstractmethod
    def ask(self, msg: str) -> tuple[str, dict[str, int]]:
        """
        Asks the LLM a question. The response is then returned.
        Note: Implementation should use _prep_ask method to validate the message.

        :param msg: The question to ask the LLM.
        :return: The LLM's response in the following format (response, token_usage_info).
        """
        raise NotImplementedError("Method ask is not implemented.")

    def save_history(self, filepath: str) -> None:
        """
        Saves the conversation history with the LLM into a JSON file.
        :param filepath: The path to where to save the history
        """
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(self._messages, file, ensure_ascii=False, indent=4)

    @abstractmethod
    def get_token_count(self) -> int:
        """
        Gets the current token count of the message history.
        """
        raise NotImplementedError("Method get_token_count is not implemented.")

    @abstractmethod
    def get_token_msg(self, msg: str, role: str = "user") -> int:
        """
        Gets the token count of a provided message.
        """
        raise NotImplementedError("Method get_token_msg is not implemented.")

    def _log(self, *args) -> None:
        if self._verbose:
            print("[LLMMgr]", *args)
