import os
import dotenv
import time
from typing import Optional

from gtts import gTTS
from src.llm import RemoteLLMManager
from audiomanager import AudioManager
from obsmanager import OBSWSManager


class OnScreenCharacter:
    def __init__(self, scene_name: str, source_name: str):
        self._scene_name = scene_name
        self._source_name = source_name

        dotenv.load_dotenv(dotenv.find_dotenv())

        # Variables to connect to LLM API
        llm_model: str = str(os.getenv("AI_LLM_MODEL"))
        api_key: str = str(os.getenv("AI_API_KEY"))
        api_url: str = str(os.getenv("AI_API_URL"))
        system_message: Optional[str] = os.getenv("AI_SYSTEM_MESSAGE")
        self.verbose: bool = bool(os.getenv("AI_VERBOSE"))
        n_ctx: int = int(os.getenv("AI_n_ctx"))

        # Variables to connect to OBS WS
        obs_host: str = str(os.getenv("OBSWS_HOST"))
        obs_port: int = int(os.getenv("OBSWS_PORT"))
        obs_password: str = str(os.getenv("OBSWS_PASSWORD"))

        self._llm: RemoteLLMManager = RemoteLLMManager(llm_model, api_key, api_url,
                                                       system_message=system_message, verbose=self.verbose, n_ctx=n_ctx)
        self._audio = AudioManager(self.verbose)
        self._obs = OBSWSManager(obs_host, obs_port, obs_password)

    def talk(self, msg: str):
        # Ask the LLM
        response = self._llm.ask(msg)

        # Print out its response
        self._log(f"Got this response: {response[0]}")
        self._log(f"Token Information: {response[1]}")

        file_name = f"tts_temp_{time.time()}.mp3"
        try:
            # Create text to speech reading out the response
            tts = gTTS(response[0], lang="en")
            tts.save(file_name)
        except Exception as e:
            print(f"[CharacterMgr] Ran into an error while generating TTS: {e}")
            print(f"[CharacterMgr] Please manually generate audio file named recover.mp3 and press enter to continue.")

            file_name = "recover.mp3"
            input()

        # Show character in OBS and play audio
        self._obs.set_source_visibility(self._scene_name, self._source_name, True)
        self._audio.play(file_name)
        self._obs.set_source_visibility(self._scene_name, self._source_name, False)

    def _log(self, *args):
        if self.verbose:
            print("[CharacterMgr]", *args)


if __name__ == "__main__":
    # Testing OnScreenCharacter
    my_char = OnScreenCharacter("Websockets Testing", "Steve - AICharacter")
    my_char.talk("Who are you")
