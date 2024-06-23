from typing import Optional
from llama_cpp import Llama
from .base_llm import BaseLLM


class LocalLLMManager(BaseLLM):
    def __init__(self, filepath: str, n_gpu_layers: int = -1, system_message: Optional[str] = None,
                 n_ctx: int = 512, temperature: float = 1.0, token_trim: float = 0.9,
                 verbose: bool = False, history_file: Optional[str] = None) -> None:
        """
        Initializes the local LLM class.

        :param filepath: The path to the LLM model file (.gguf)
        :param n_gpu_layers: How many layers we can offload to the GPU. Set to -1 for all.
        :param system_message: The initial system message provided to the LLM.
        :param n_ctx: Size of the context window. Defaults to 512. Should be changed to match your implementation.
        :param temperature: Adjusts the level of creativity the LLM gives in its responses. (0.0-1.0 inclusive)
        :param token_trim: Sets the point of how full the context window should be until we start trimming old messages.
        :param verbose: Sets whether we print helpful debug messages to the console.
        :param history_file: Conversation JSON file to import if applicable.
        """
        # Initialize Llama CPP for a Local LLM
        self._llm = Llama(model_path=filepath, n_ctx=n_ctx, n_gpu_layers=n_gpu_layers, verbose=False)

        super().__init__(system_message, n_ctx, temperature, token_trim, verbose, history_file)

    def ask(self, msg: str) -> tuple[str, dict[str, int]]:
        """
        Asks the LLM a question. The response is then returned.

        :param msg: The question to ask the LLM.
        :return: The LLM's response in the following format (response, token_usage_info).
        """
        # Validate input message and perform message trimming if we have too many tokens
        self._prep_ask(msg)

        # Get a response
        completion = self._llm.create_chat_completion(messages=self._messages, temperature=self._temperature)

        # Append the response to the message history
        self._messages.append(completion["choices"][0]["message"])

        return completion["choices"][0]["message"]["content"], completion["usage"]

    def get_token_count(self) -> int:
        """
        Gets the current token count in the message history.
        """
        return self._llm.create_chat_completion(messages=self._messages, max_tokens=0)["usage"]["prompt_tokens"]

    def get_token_msg(self, msg: str, role: str = "user") -> int:
        """
        Gets the token count of a provided message.
        """
        temp_message = [{"role": role, "content": msg}]
        return self._llm.create_chat_completion(messages=temp_message, max_tokens=0)["usage"]["prompt_tokens"]


if __name__ == "__main__":
    """
    Testing
    """
    llm_file = "meta-llama-3-8b-instruct-q5_k_m.gguf"
    history_file = "test_llm_manager_history.json"
    continuation = False
    question_to_ask = "Who is the president of the United States and can you tell me a bit about them?"
    system_message = "You are a helpful assistant who answers questions. You must keep your responses within 2 short paragraphs."

    print("TESTS FOR LLM MANAGER...\n")

    if not continuation:
        print("Initializing LlamaCPPManager named my_llm.")
        my_llm = LocalLLMManager(llm_file, verbose=True, system_message=system_message)
    else:
        print("Initializing LlamaCPPManager with conversation history from the file, test_llm_manager_history.json")
        my_llm = LocalLLMManager(llm_file,
                                 history_file=history_file,
                                 verbose=True)

    print(f"Asking the LLM a question. {question_to_ask}")
    llm_response = my_llm.ask(question_to_ask)

    print(f"Token Information: {llm_response[1]}")
    print(f"Here is what we got!\n{llm_response[0]}")

    print("Saving the chat history into a JSON file.")
    my_llm.save_history("test_llm_manager_history.json")

    print("Finished!")
