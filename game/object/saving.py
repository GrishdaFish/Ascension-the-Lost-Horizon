__author__ = 'GrishdaFish'
import os
import sys
import pickle
from cryptography.fernet import Fernet

class SaveGame:
    def __init__(self, game: any, gEngine: any, save_location: str, save_key: str = None)->None:
        """
        Class that handles creating and dumping a save file to disk
        :param game: the main game instance
        :param gEngine: the gEngine instance
        :param save_location: the location of the save file
        :param save_key: the decryption key. If None, pulls the key from a file
        """
        self.game = game
        self.gEngine = gEngine
        self.save_location = save_location
        self.key_location = os.path.join(os.path.abspath('.'), 'sav_key.key')
        self.save_key = save_key
        if not self.save_key:
            self.load_save_key()

        # List should be populated with a dict of "Object.Name":dict[Object_data:value]
        self.save_object: list[dict[str, any]] = []

    def load_save_key(self)->None:
        """
        Loads the decryption key from a file
        :return: Nothing
        """
        try:
            with open(self.key_location,"rb") as file:
                self.save_key = file.read()
        except FileNotFoundError:
            self.save_key = Fernet.generate_key()
            with open(self.key_location, "wb") as file:
                file.write(self.save_key)
        print(self.save_key)

    def parse_object(self, object_to_parse: any=None, save_ob: dict=None)->any:
        """
        Parses a game.object.Object to a dict to be saved to file
        :param object_to_parse: Object class
        :param save_ob: dict file to append this object to
        :return: Completed save_ob dict
        """
        if not object_to_parse:
            return
        if not save_ob:
            save_ob = {}
        save_ob["name"] = object_to_parse.name
        save_ob["is_player"] = object_to_parse.is_player
        save_ob["x_pos"] = object_to_parse.x
        save_ob["y_pos"] = object_to_parse.y
        r, g, b = object_to_parse.color
        save_ob["color"] = (r,g,b)

        if object_to_parse.fighter:
            save_ob = self.parse_fighter(object_to_parse.fighter, save_ob)
        elif object_to_parse.item:
            save_ob = self.parse_item(object_to_parse.item, save_ob)
        elif object_to_parse.misc:
            save_ob = self.parse_misc(object_to_parse.misc, save_ob)
        elif object_to_parse.torch:
            save_ob = self.parse_torch(object_to_parse.torch, save_ob)

        return save_ob

    def parse_fighter(self, object_to_parse: any=None, save_ob: dict=None)->any:
        if not object_to_parse:
            return
        if not save_ob:
            save_ob = {}
        save_ob["stat_panel"] = object_to_parse.stat.get_all_base_stats()
        gear = object_to_parse.gear.gimmie_da_quips()
        gear_list = []
        for item in gear:
            if item:
                gear_list.append(self.parse_object(item))
        save_ob["equipment"] = gear_list
        save_ob["money"] = object_to_parse.money
        save_ob["level"] = object_to_parse.level
        save_ob["current_xp"] = object_to_parse.current_xp
        save_ob["xp_to_next_level"] = object_to_parse.xp_to_next_level
        item_list = []
        for item in object_to_parse.inventory:
            item_list.append(self.parse_object(item))
        save_ob["inventory"] = item_list
        save_ob["max_hp"] = object_to_parse.max_hp
        save_ob["hp"] = object_to_parse.hp
        save_ob["max_stamina"] = object_to_parse.max_stamina
        save_ob["stamina"] = object_to_parse.stamina
        save_ob["stamina_regen-speed"] = object_to_parse.stamina_regen_speed
        save_ob["max_consumable_level"] = object_to_parse.max_consumable_level

        return save_ob

    def parse_item(self, object_to_parse: any=None, save_ob: dict=None)->any:
        if not object_to_parse:
            return
        if not save_ob:
            save_ob = {}
        save_ob["value"] = object_to_parse.value
        if object_to_parse.spell:
            save_ob["spell_component"] = self.parse_spell(object_to_parse.spell)
            save_ob["stackable"] = object_to_parse.stackable
            save_ob["qty"] = object_to_parse.qty
        elif object_to_parse.equipment:
            save_ob["equipment"] = self.parse_equipment(object_to_parse.equipment)

        return save_ob

    def parse_spell(self, object_to_parse: any=None, save_ob: dict=None)->any:
        if not object_to_parse:
            return
        if not save_ob:
            save_ob = {}
        #save_ob["spell_name"] = object_to_parse.name
        save_ob["min"] = object_to_parse.min
        save_ob["max"] = object_to_parse.max
        save_ob["radius"] = object_to_parse.radius
        save_ob["targets"] = object_to_parse.targets
        save_ob["type"] = object_to_parse.type
        save_ob["range"] = object_to_parse.range
        #save_ob["effect_per_level"] = object_to_parse.effect_per_level
        save_ob["additional_effect"] = object_to_parse.addition_effects
        #save_ob["additional_effect_magnitude"] = object_to_parse.additional_effect_magnitude
        #save_ob["magnitude_per_level"] = object_to_parse.magnitude_per_level
        save_ob["spell_fx"] = object_to_parse.spell_effects
        return save_ob

    def parse_equipment(self, object_to_parse: any=None, save_ob: dict=None)->any:
        if not object_to_parse:
            return
        if not save_ob:
            save_ob = {}
        if object_to_parse.torch:
            save_ob["fuel"] = object_to_parse.fuel
            save_ob["max_fuel"] = object_to_parse.max_fuel
            r, g, b = object_to_parse.torch_color
            save_ob["torch_color"] = (r, g, b)
            save_ob["torch_intensity"] = object_to_parse.torch_intensity
        else:
            save_ob["defense"] = object_to_parse.defense
            save_ob["type"] = object_to_parse.type
            save_ob["subtype"] = object_to_parse.subtype
            save_ob["location"] = object_to_parse.location
            save_ob["damage_type"] = object_to_parse.damage_type
            save_ob["bonus"] = object_to_parse.bonus
            save_ob["penalty"] = object_to_parse.penalty
            save_ob["description"] = object_to_parse.description
            save_ob["accuracy"] = object_to_parse.accuracy
            save_ob["damage"] = object_to_parse.damage
            save_ob["mat"] = object_to_parse.mat

        return save_ob

    def parse_torch(self, object_to_parse: any=None, save_ob: dict=None)->any:
        if not object_to_parse:
            return
        if not save_ob:
            save_ob = {}

        return save_ob

    def parse_misc(self, object_to_parse: any=None, save_ob: dict=None)->any:
        if not object_to_parse:
            return
        if not save_ob:
            save_ob = {}

    def parse_map(self, object_to_parse: any=None, save_ob: dict=None)->any:
        if not object_to_parse:
            return
        if not save_ob:
            save_ob = {}

    def dump_to_disc(self, save_ob):
        if save_ob:
            fernet = Fernet(self.save_key)
            with open(self.save_location, 'wb') as file:
                pickle.dump(save_ob, file)
            with open(self.save_location, 'rb') as file:
                save_ob = fernet.encrypt(file.read())
            with open(self.save_location,'wb') as file:
                file.write(save_ob)
            #with open(self.save_location, 'rb') as file:
            #    save_ob = fernet.decrypt(file.read())
            #    loaded_data = pickle.loads(save_ob)
            #    print(loaded_data)


    def save_game(self, save_ob: dict=None):
        if not save_ob:
            pass
        else:
            self.dump_to_disc(save_ob)


    def load_game(self, save_location: str = None)->any:
        try:
            if not save_location:
                with open(self.save_location,"rb") as file:
                    save_file = file.read()
            else:
                with open(save_location,"rb") as file:
                    save_file = file.read()
        except FileNotFoundError:
            if not save_location:
                s = self.save_location
            else:
                s = save_location
            self.gEngine.engine_error_popup("File Not Found", "Save file [%s] not found" %str(s), True )