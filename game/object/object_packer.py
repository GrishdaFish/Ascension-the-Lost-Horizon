### usage:
#   prick = PickleRiiick(self.gEngine, [player or mob])
#
#   # Save to server:
#   prick.pack_fighter()
#   prick.pack_fighter_gear()
#   prick.save_fighter_package()
#
#   # restore from server
#   prick.get_fighter_package()
#   prick.unpack_fighter()
#   prick.unpack_fighter_gear()

class PickleRiiick: # burp
    """ Pickle Rick wil protect your saved data from all things fallout resistant: rats, roaches, and russians """
    def __init__(self, gEngine, fighter=None):  # setting default none so we can pass different objects
        self.purpose = "pass butter"  # oh. my. god.
        # this stores the network compatible data structure:  {'request': request_type, 'data': json.dumps(data)}
        self.payload = {}
        #  passed for network calls
        self.gEngine = gEngine
        #  the fighter to package
        self.fighter = fighter
        self.fighter_package = None
        #  add additional objects you'd like to pack individually below and add defaults to constructor

    def clear_payload(self):
        """ Clears the payload in case you are reusing the same Pickle*buurp*Riiick """
        self.payload = {}

    def save_fighter_package(self):
        self.gEngine.network_send_package("store_fighter", {"pickled_fighter": self.payload})

    def get_fighter_package(self):
        self.fighter_package = self.gEngine.network_send_package("get_fighter", None)

    def pack_fighter(self):
        """ packs up the stats you will need to setup a new fighter and stat_panel """
        # handle perks later
        if self.fighter:
            self.payload.update({"stats": self.fighter.stat.get_all_base_stats(),
                                 "fighter_info": self.fighter.get_attribute_package(),
                                 "level": self.fighter.level,
                                 "threat": self.fighter.threat,
                                 "name": self.name})

    def pack_fighter_gear(self):
        """ packs up the equipped gear on a passed fighter """
        if self.fighter:
            gear = self.fighter.gear.gimmie_da_quips()
            eq_slots = self.fighter.gear.gimmie_da_slots_all()
            for g, slot in zip(gear, eq_slots):
                if g:
                    omfg = g.item.equipment
                    omfg_fx = []
                    for fx in omfg.effects:
                        if fx:
                            omfg_fx.append(fx.get_effect_package())
                    gear_package = [omfg.type, g.name, omfg.mat]  # , omfg_fx]
                else:
                    gear_package = [0]
                self.payload.update({slot: gear_package})

    def unpack_fighter(self):
        """ called after get_fighter_package() to set the received stats """
        if self.fighter_package:
            payload = self.fighter_package['data']['pickled_fighter']
            self.fighter.stat.set_all_base_stats(payload['stats'])
            self.fighter.set_attributes_from_package(payload['fighter_info'])
            self.fighter.level = int(payload['level'])
            # threat should actually get calculated back once equipment and stats are in, right?
            # self.fighter.threat = payload['threat']
            self.name = payload['name']
        else:
            print("You forgot to get the fighter package")

    def unpack_fighter_gear(self):
        """ called after get_fighter_package() to rebuild and equip the received gear """
        if self.fighter_package:
            payload = self.fighter_package['data']['pickled_fighter']
            # [[omfg.type, g.name, omfg.mat, omfg_fx], ...]
            eq_slots = self.fighter.gear.gimmie_da_slots_all()
            for slot in eq_slots:
                # TODO INVESTIGATE!! this currently gets a little whacky when rebuilding gear
                if payload[slot] != '0':
                    payload[slot][1] = payload[slot][1].strip(payload[slot][2] + " ")

                    eq = self.game.build_objects.build_equipment(self.game, 0, 0, payload[slot][0], payload[slot][1], payload[slot][2])
                    # eq.item.effects = None
                    # for fx in slot[3]:
                    #     new_effect = Effect(eq.item, effect=fx[0])
                    #     new_effect.set_from_effect_package(fx)
                    #     eq.item.effects.append(new_effect)
                    self.fighter.gear.quip_it(eq)
            # handle inventory
            # handle perks
        else:
            print("You forgot to get the fighter package")
