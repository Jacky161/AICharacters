from openai import OpenAI
from typing import Optional
from base_llm import BaseLLM


class RemoteLLMManager(BaseLLM):
    def __init__(self, model: str, api_key: str, api_url: Optional[str] = None, system_message: Optional[str] = None,
                 n_ctx: Optional[int] = None, temperature: float = 1.0, token_trim: float = 0.9,
                 verbose: bool = False, history_file: Optional[str] = None) -> None:
        """
        Initializes the remote LLM class that connects to an OpenAI compatible API.

        :param model: The name of the model to use from the API.
        :param api_key: The key required to use the API.
        :param api_url: The url path to the API. If left blank, defaults to OpenAI's api.
        :param system_message: The initial system message provided to the LLM.
        :param n_ctx: Size of the context window. Defaults to 512. Should be changed to match your implementation.
        :param temperature: Adjusts the level of creativity the LLM gives in its responses. (0.0-1.0 inclusive)
        :param token_trim: Sets the point of how full the context window should be until we start trimming old messages.
        :param verbose: Sets whether we print helpful debug messages to the console.
        :param history_file: Conversation JSON file to import if applicable.
        """
        # Connect to the API
        self._llm = OpenAI(api_key=api_key, base_url=api_url)
        self._model = model

        # RemoteLLMManager should almost certainly have n_ctx set
        if n_ctx is None:
            print("[WARNING] n_ctx should be set for RemoteLLMManager. Proceeding with default of 512.")
            n_ctx = 512

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
        completion = self._llm.chat.completions.create(messages=self._messages,
                                                       model=self._model, temperature=self._temperature).to_dict()

        # Append the response to the message history
        self._messages.append(completion["choices"][0]["message"])

        return completion["choices"][0]["message"]["content"], completion["usage"]

    def get_token_count(self) -> int:
        """
        Gets the current token count in the message history.
        """
        return self._llm.chat.completions.create(messages=self._messages,
                                                 model=self._model, max_tokens=0).to_dict()["usage"]["prompt_tokens"]

    def get_token_msg(self, msg: str, role: str = "user") -> int:
        """
        Gets the token count of a provided message.
        """
        temp_message = [{"role": role, "content": msg}]
        return self._llm.chat.completions.create(messages=temp_message,
                                                 model=self._model, max_tokens=0).to_dict()["usage"]["prompt_tokens"]


if __name__ == "__main__":
    """
    Testing
    """
    llm_model = "meta-llama-3-8b-instruct-q5_k_m.gguf"
    api_url = "http://127.0.0.1:8080"
    api_key = "ABC"
    history_file = "test_llm_manager_history.json"
    continuation = False
    question_to_ask = "Who is the president of the United States and can you tell me a bit about them?"
    system_message = "You are a helpful assistant who answers questions. You must keep your responses within 2 short paragraphs."

    print("TESTS FOR LLM MANAGER...\n")

    if not continuation:
        print("Initializing LlamaCPPManager named my_llm.")
        my_llm = RemoteLLMManager(llm_model, "ABC", api_url, system_message=system_message, verbose=True, n_ctx=2048)
    else:
        print("Initializing LlamaCPPManager with conversation history from the file, test_llm_manager_history.json")
        my_llm = RemoteLLMManager(llm_model, "ABC", api_url, verbose=True, history_file=history_file, n_ctx=2048)

    print(f"Asking the LLM a question. {question_to_ask}")
    llm_response = my_llm.ask(question_to_ask)

    print(f"Token Information: {llm_response[1]}")
    print(f"Here is what we got!\n{llm_response[0]}")

    print("Saving the chat history into a JSON file.")
    my_llm.save_history("test_llm_manager_history.json")

    print("Finished!")
