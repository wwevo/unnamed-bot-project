from modules.module import Module
from modules import loaded_modules_dict
from time import time


class Environment(Module):
    templates = object

    def __init__(self):
        setattr(self, "default_options", {
            "module_name": self.get_module_identifier()[7:]
        })

        setattr(self, "required_modules", [
            "module_dom",
            "module_telnet",
            "module_webserver"
        ])
        Module.__init__(self)

    @staticmethod
    def get_module_identifier():
        return "module_environment"

    def on_socket_connect(self, steamid):
        Module.on_socket_connect(self, steamid)
        self.update_status_widget()

    def on_socket_disconnect(self, steamid):
        Module.on_socket_disconnect(self, steamid)
        self.update_status_widget()

    # region Standard module stuff
    def setup(self, options=dict):
        Module.setup(self, options)
        self.run_observer_interval = 1
    # endregion

    def update_status_widget(self):
        self.dom.upsert({
            self.get_module_identifier(): {
                "webserver_logged_in_users": self.webserver.connected_clients
            }
        })

        template_frontend = self.templates.get_template('server_status_widget_frontend.html')
        data_to_emit = template_frontend.render(
            webserver_logged_in_users=self.dom.data.get(self.get_module_identifier()).get("webserver_logged_in_users"),
            server_is_online=self.dom.data.get("module_telnet").get("server_is_online"),
            last_recorded_gametime=self.dom.data.get(self.get_module_identifier()).get("last_recorded_gametime"),
            shutdown_in_seconds=self.dom.data.get(self.get_module_identifier()).get("shutdown_in_seconds", None)
        )

        self.webserver.send_data_to_client(
            event_data=data_to_emit,
            data_type="widget_content",
            clients=self.webserver.connected_clients.keys(),
            target_element="widget_environment_data"
        )

    def run(self):
        next_cycle = 0
        while not self.stopped.wait(next_cycle):
            profile_start = time()
            self.last_execution_time = time() - profile_start
            next_cycle = self.run_observer_interval - self.last_execution_time


loaded_modules_dict[Environment().get_module_identifier()] = Environment()