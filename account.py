import ast

class Account:
    def __init__(self, name, id, email, favourites: list, settings: dict, state='main'):
        self.__name = name
        self.__id = id
        self.__email = email
        self.__favourites = favourites
        self.__settings = settings
        self.__current_state = state

    def get_name(self):
        return self.__name

    def get_id(self):
        return self.__id

    def get_email(self):
        return self.__email

    def get_favourites(self):
        return self.__favourites

    def get_settings(self):
        return self.__settings

    def get_current_state(self):
        return self.__current_state

    def set_current_state(self, state):
        self.__current_state = state

    def add_favourite(self, fav):
        self.__favourites.append(fav)

    def remove_favourite(self, fav):
        self.__favourites.remove(fav)

    def update_settings(self, country, category, language):
        self.__settings['country'] = country
        self.__settings['category'] = category
        self.__settings['language'] = language

    def update_settings(self, new_settings):
        self.__settings = new_settings

    # returns account's favourites in json format (stored as strings in DB)
    def get_json_favourites(self):
        json_format_array = []
        for fav in self.__favourites:
            json_format_array.append(ast.literal_eval(fav))
        return json_format_array
