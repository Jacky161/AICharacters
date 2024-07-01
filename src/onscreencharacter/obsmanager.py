import obsws_python as obs


class OBSWSManager:
    def __init__(self, host: str, port: int, password: str, timeout: int = 3):
        """
        Create the OBS Websockets Manager.

        :param host: The address to connect to.
        :param port: The port to connect to.
        :param password: The password to access websockets with.
        :param timeout: How long to wait in seconds until timing out the connection.
        """
        self._obs = obs.ReqClient(host=host, port=port, password=password, timeout=timeout)

    def get_scene_item_id(self, scene_name: str, source_name: str) -> int:
        """
        Gets the OBS Item ID from the scene and source name. Used as a preliminary step for using other methods that
        typically require the item id.
        """
        response = self._obs.get_scene_item_id(scene_name, source_name)
        return response.scene_item_id

    def set_source_visibility(self, scene_name: str, source_name: str, visible: bool = True) -> None:
        """
        Shows or hides a scene given its scene and source name.
        """

        source_id: int = self.get_scene_item_id(scene_name, source_name)
        self._obs.set_scene_item_enabled(scene_name, source_id, visible)

    def get_source_visibility(self, scene_name: str, source_name: str) -> bool:
        """
        Gets whether a source given its scene and source name is visible or not.
        """
        source_id: int = self.get_scene_item_id(scene_name, source_name)
        return self._obs.get_scene_item_enabled(scene_name, source_id).scene_item_enabled


if __name__ == "__main__":
    test_scene_name = "Websockets Testing"
    test_source_name = "Steve - AICharacter"

    obs_manager = OBSWSManager(host='localhost', port=4455, password='password')
    print("Created the manager.")

    # Show source
    obs_manager.set_source_visibility(test_scene_name, test_source_name, visible=True)
    print("Showed the source.")
    print(f"Source is visible: {obs_manager.get_source_visibility(test_scene_name, test_source_name)}")
    input("Press enter to continue.")

    # Hide source
    obs_manager.set_source_visibility(test_scene_name, test_source_name, visible=False)
    print("Hid the source.")
    print(f"Source is visible: {obs_manager.get_source_visibility(test_scene_name, test_source_name)}")
