from llama_cpp import Llama
import json
from llmexceptions import *
from typing import Optional


class LlamaCPPManager:
    """
    Class for working with LlamaCPP in a more friendly manner and easy to use manner.
    """

    def __init__(self, filepath: str, system_message: Optional[str] = None,
                 n_ctx: int = 512, temperature: float = 1.0, token_trim: float = 0.9,
                 verbose: bool = False, history_file: Optional[str] = None) -> None:
        """
        Initializes the LLM Manager with the repository defined from hugging face.

        :param filepath: LLM Model file to load (GGUF).
        :param n_ctx: Size of the context window in tokens.
        :param temperature: Adjusts the level of creativity the LLM gives in its responses. Higher is more creative.
        :param history_file: Conversation JSON file to import if applicable.
        """
        self._llm = Llama(model_path=filepath, n_ctx=n_ctx, n_gpu_layers=-1, verbose=False)
        self._messages = []
        self._temperature = temperature
        self._n_ctx = n_ctx
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
            self._log(f"Loaded system message, {system_message}")

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
        valid_roles = ["system", "user", "assistant"]
        if role not in valid_roles:
            raise NonValidRole(f"Role must be one of {valid_roles}, not {role}")

        # Add the message to the history
        new_message = {"role": role, "content": content}
        self._messages.append(new_message)

    def ask(self, msg: str) -> tuple[str, dict[str, int]]:
        """
        Asks the LLM a question. The response is then returned.

        :param msg: The question to ask the LLM.
        :return: The LLM's response in the following format (response, token_usage_info).
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
        
        while fill_amount > self._token_trim:
            if self._messages[0]["role"] != "system":
                self._messages.pop(0)
            else:
                self._messages.pop(1)

            cur_token = self.get_token_count()
            fill_amount = self.get_token_count() / self._n_ctx

            self._log(f"Popped a message! Token count is now {cur_token}. "
                      f"Context Fill % is {fill_amount * 100:.2f}%.")

        # Get a response
        completion = self._llm.create_chat_completion(messages=self._messages, temperature=self._temperature)

        # Append the response to the message history
        self._messages.append(completion["choices"][0]["message"])

        return completion["choices"][0]["message"]["content"], completion["usage"]

    def save_history(self, filepath: str) -> None:
        """
        Saves the conversation history with the LLM into a JSON file.
        :param filepath: The path to where to save the history
        """
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(self._messages, file, ensure_ascii=False, indent=4)

    def get_token_count(self) -> int:
        """
        Gets the current token count in the message history.
        """
        return self._llm.create_chat_completion(messages=self._messages, max_tokens=0)["usage"]["prompt_tokens"]

    def get_token_msg(self, msg: str, role: str = "user") -> int:
        """
        Gets the token count of a provided message.
        """
        temp_messages = [{"role": role, "content": msg}]
        return self._llm.create_chat_completion(messages=temp_messages, max_tokens=0)["usage"]["prompt_tokens"]
    
    def _log(self, *args) -> None:
        if self._verbose:
            print("[LCPPMgr]", *args)


if __name__ == "__main__":
    """
    Testing
    """
    llm_file = "Meta-Llama-3-8B-Instruct.Q6_K.gguf"
    history_file = "test_llm_manager_history.json"
    continuation = False
    question_to_ask = "Who is the president of the United States and can you tell me a bit about them?"
    system_message = "You are a helpful assistant who answers questions. You must keep your responses within 2 short paragraphs."

    print("TESTS FOR LLM MANAGER...\n")

    if not continuation:
        print("Initializing LlamaCPPManager named my_llm.")
        my_llm = LlamaCPPManager(llm_file, verbose=True, system_message=system_message)
    else:
        print("Initializing LlamaCPPManager with conversation history from the file, test_llm_manager_history.json")
        my_llm = LlamaCPPManager(llm_file,
                                 history_file=history_file,
                                 verbose=True)

    print(f"Asking the LLM a question. {question_to_ask}")
    llm_response = my_llm.ask(question_to_ask)

    print(f"Token Information: {llm_response[1]}")
    print(f"Here is what we got!\n{llm_response[0]}")

    print("Saving the chat history into a JSON file.")
    my_llm.save_history("test_llm_manager_history.json")

    print("Finished!")
