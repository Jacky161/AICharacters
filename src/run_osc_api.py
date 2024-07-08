import uvicorn
import threading
from fastapi import FastAPI, Response, status
from onscreencharacter import OnScreenCharacter
from queue import Queue


app = FastAPI()


@app.post("/api/{osc}/chat", status_code=status.HTTP_202_ACCEPTED)
def api_chat(osc: str, message: str, response: Response):
    if osc not in app.state.characters:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": f"{osc} is not a valid character."}

    # Add message to the queue to be processed
    app.state.chat_queue.put((osc, message))
    return {"queue position": app.state.chat_queue.qsize()}


def init_app_state():
    # TODO: Use .env or some other config file
    scene_name = "Websockets Testing"

    app.state.characters = {}
    app.state.chat_queue = Queue(maxsize=0)  # Infinite queue size

    # Initialize worker thread
    app.state.worker = threading.Thread(target=talk_char, args=(app.state.chat_queue,), daemon=True)
    app.state.worker.start()

    # Each character has its own OSC class
    # TODO: Use .env or some other config file
    characters = ["Steve", "Herobrine"]
    for character in characters:
        app.state.characters[character] = OnScreenCharacter(scene_name, character + " - AICharacter")


def talk_char(q: Queue):
    # Worker thread to process messages in the queue
    while True:
        char_info = q.get()
        app.state.characters[char_info[0]].talk(char_info[1])
        q.task_done()


if __name__ == "__main__":
    init_app_state()
    uvicorn.run(app, host="localhost", port=8000)
