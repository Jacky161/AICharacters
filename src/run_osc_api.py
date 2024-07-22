import uvicorn
import threading
import csv
from fastapi import FastAPI, Response, status, Body, HTTPException
from onscreencharacter import OnScreenCharacter
from queue import Queue
from typing import Annotated

app = FastAPI()


@app.post("/api/{osc}/chat", status_code=status.HTTP_202_ACCEPTED)
def api_chat(osc: str, message: Annotated[str, Body()], response: Response) -> dict[str, int]:
    if osc not in app.state.characters:
        raise HTTPException(status_code=404, detail=f"OSC {osc} does not exist.")

    # Add message to the queue to be processed
    app.state.chat_queue.put((osc, message))
    return {"Queue Position": app.state.chat_queue.qsize()}


@app.put("/api/{osc}/messages", status_code=status.HTTP_204_NO_CONTENT)
def api_replace_messages(osc: str, messages: list[dict[str, str]] | None = None) -> None:
    """
    Replaces the message history of a certain onscreen character with a new history
    """
    app.state.characters[osc].set_message_history(messages)


@app.put("/api/{osc}/sysmsg", status_code=status.HTTP_200_OK)
def api_replace_system_message(osc: str, system_message: Annotated[str | None, Body()] = None) -> dict[str, int]:
    """
    Replaces the system message of a certain onscreen character, returning the number of tokens present in the new msg.
    """
    tokens = app.state.characters[osc].set_system_message(system_message)
    return {"System Message Tokens": tokens}


@app.get("/api/{osc}/messages")
def api_get_messages(osc: str) -> list[dict[str, str]]:
    """
    Gets the message history of a certain onscreen character.
    """
    return app.state.characters[osc].get_message_history()


@app.get("/api/characters")
def api_get_characters() -> list[str]:
    """
    Gets names of all characters that can be used through the API.
    """
    return list(app.state.characters.keys())


@app.get("/api/queue")
def api_get_queue() -> int:
    """
    Returns the length of the processing queue
    """
    return app.state.chat_queue.qsize()


def init_app_state():
    app.state.characters = {}
    app.state.chat_queue = Queue(maxsize=0)  # Infinite queue size

    # Initialize worker thread
    app.state.worker = threading.Thread(target=talk_char, args=(app.state.chat_queue,), daemon=True)
    app.state.worker.start()

    # Read each character from the csv file
    with open("characters.csv") as char_csv:
        csv_reader = csv.reader(char_csv, delimiter=",")

        line_no = 0
        for row in csv_reader:
            if line_no == 0:
                assert row == ["character_name", "scene_name", "source_name"]
            else:
                app.state.characters[row[0]] = OnScreenCharacter(row[1], row[2])

            line_no += 1


def talk_char(q: Queue):
    # Worker thread to process messages in the queue
    while True:
        char_info = q.get()
        app.state.characters[char_info[0]].talk(char_info[1])
        q.task_done()


if __name__ == "__main__":
    init_app_state()
    uvicorn.run(app, host="localhost", port=8000)
