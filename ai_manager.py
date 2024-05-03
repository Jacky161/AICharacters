from ollama import Client as OllamaClient
import atexit
import time
import json
from exceptions import *


class AIManager:
    def __init__(self, model_name: str, model_file: str = None,
                 history_file: str = None, endpoint: str = "http://localhost:11434") -> None:
        """
        Initializes the AI Manager with the model defined in the file and name given.
        If a model file is not provided, initialize a standard llama3 model.

        :param model_name: The name of the model to create.
        :param model_file: The filepath to the modelfile (ollama format).
        :param endpoint: The URL where ollama is listening.
        """
        self._ai = OllamaClient(host=endpoint)
        self._model_name = model_name
        self._messages = []
        self._messages_time = []

        # Read the modelfile if it exists
        if model_file is not None:
            with open(model_file, "r", encoding="utf-8") as file:
                model = file.read()
        else:
            model = "FROM llama3"

        # Import conversation history if it exists
        if history_file is not None:
            with open(history_file, "r", encoding="utf-8") as file:
                self._messages = json.load(file)

        # Create our model with the modelfile
        self._ai.create(model=model_name, modelfile=model)

        # Register deletion when program exits
        atexit.register(self._on_exit)

        # Record creation time
        self._creation_time = time.time()

    def add_message(self, role: str, msg: str) -> None:
        """
        Adds a new message to the conversation history of the AI.
        :param role: Who the message was spoken by - (system, user, assistant)
        :param msg: The message to be added.
        """
        valid_roles = ["system", "user", "assistant"]
        if role not in valid_roles:
            raise NonValidRole(f"Role must be one of {valid_roles}, not {role}")

        # Add the message to the history
        new_message = {"role": role, "content": msg}
        self._messages.append(new_message)
        self._messages_time.append(time.time())

    def ask(self, msg: str) -> tuple:
        """
        Asks the AI a question. The response is then returned.
        :param msg: The question to ask the AI.
        :return: The AI's response in the following format (response, num_tokens_in_response).
        """
        # Add the message to the history and ask the AI to generate a response
        self.add_message("user", msg)
        response = self._ai.chat(model=self._model_name, messages=self._messages)

        # Append the response to the message history
        self.add_message("assistant", response["message"]["content"])

        return response["message"]["content"], response["eval_count"]

    def save_history(self, filepath: str) -> None:
        """
        Saves the conversation history with the AI into a JSON file.
        :param filepath: The path to where to save the history
        """
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(self._messages, file, ensure_ascii=False, indent=4)

    def _on_exit(self):
        """
        Cleanup function for when the program exists.
        """
        # print(f"Self destructing the model {self._model_name}...")
        self._ai.delete(self._model_name)


if __name__ == "__main__":
    """
    Test Cases
    """
    continuation = False
    question_to_ask = "Who is the current president of the United States? Can you tell me a bit about them?"

    print("TESTS FOR AI MANAGER...\n")

    if not continuation:
        print("Initializing an AIManager named my_ai.")
        my_ai = AIManager("my_ai")
    else:
        print("Initializing an AIManager named my_ai with conversation history from the file, test_ai_manager_history.json")
        my_ai = AIManager("my_ai", history_file="test_ai_manager_history.json")

    print(f"Asking the AI a question. {question_to_ask}")
    ai_response = my_ai.ask(question_to_ask)

    print(f"Response has {ai_response[1]} tokens!")
    print(f"Here is what we got!\n{ai_response[0]}")

    print("Saving the chat history into a JSON file.")
    my_ai.save_history("test_ai_manager_history.json")

    print("Finished. my_ai should now self destruct before exiting.")
