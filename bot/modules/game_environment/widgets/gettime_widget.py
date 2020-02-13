from bot import loaded_modules_dict
from os import path, pardir

module_name = path.basename(path.normpath(path.join(path.abspath(__file__), pardir, pardir)))
widget_name = path.basename(path.abspath(__file__))[:-3]


def get_weekday_string(server_days_passed):
    days_of_the_week = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday"
    ]

    current_day_index = int(float(server_days_passed) % 7)
    if 0 <= current_day_index <= 6:
        return days_of_the_week[current_day_index]
    else:
        return "n/a"


def is_currently_bloodmoon(module, day, time):
    active_dataset = module.dom.data.get("module_game_environment", {}).get("active_dataset", None)
    next_bloodmoon_date = (
        module.dom.data
        .get("module_game_environment", {})
        .get(active_dataset, {})
        .get("gamestats", {})
        .get("BloodMoonDay", None)
    )

    if int(next_bloodmoon_date) == int(day) and 22 >= int(time) <= 23:
        return True
    if (int(next_bloodmoon_date) + 1) == int(day) and 0 <= int(time) <= 4:
        return True

    return False


def main_widget(*args, **kwargs):
    module = args[0]
    dispatchers_steamid = kwargs.get("dispatchers_steamid", None)
    active_dataset = module.dom.data.get("module_game_environment", {}).get("active_dataset", None)

    template_frontend = module.templates.get_template('gametime_widget/view_frontend.html')
    gametime = module.dom.data.get("module_game_environment", {}).get(active_dataset, {}).get("last_recorded_gametime", {
        "day": "00",
        "hour": "00",
        "minute": "00",
    })
    gametime["weekday"] = get_weekday_string(gametime["day"])
    gametime["is_bloodmoon"] = is_currently_bloodmoon(module, gametime["day"], gametime["hour"])

    data_to_emit = module.template_render_hook(
        module,
        template=template_frontend,
        last_recorded_gametime=gametime,
    )

    module.webserver.send_data_to_client_hook(
        module,
        payload=data_to_emit,
        data_type="widget_content",
        clients=[dispatchers_steamid],
        target_element={
            "id": "gametime_widget",
            "type": "div",
            "selector": "body > header > div > div"
        }
    )


def update_widget(*args, **kwargs):
    module = args[0]
    updated_values_dict = kwargs.get("updated_values_dict", None)
    original_values_dict = kwargs.get("original_values_dict", None)

    gametime = updated_values_dict.get("last_recorded_gametime", None)
    old_gametime = original_values_dict.get("last_recorded_gametime", None)
    if gametime is None:
        module.trigger_action_hook(module, event_data=["gettime", {}])
        return False

    if gametime == old_gametime:
        pass
        # return

    gametime["weekday"] = get_weekday_string(gametime["day"])
    gametime["is_bloodmoon"] = is_currently_bloodmoon(module, gametime["day"], gametime["hour"])

    template_frontend = module.templates.get_template('gametime_widget/view_frontend.html')
    data_to_emit = module.template_render_hook(
        module,
        template=template_frontend,
        last_recorded_gametime=gametime,
    )

    module.webserver.send_data_to_client_hook(
        module,
        payload=data_to_emit,
        data_type="widget_content",
        clients=module.webserver.connected_clients.keys(),
        target_element={
            "id": "gametime_widget",
            "type": "div",
            "selector": "body > header > div > div"
        }
    )
    return gametime


widget_meta = {
    "description": "displays the in-game time and day",
    "main_widget": main_widget,
    "handlers": {
        "module_game_environment/%map_identifier%/last_recorded_gametime": update_widget
    },
    "enabled": True
}

loaded_modules_dict["module_" + module_name].register_widget(widget_name, widget_meta)
