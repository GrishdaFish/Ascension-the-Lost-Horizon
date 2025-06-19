import tcod as libtcod
from gEngine.utilities.user_interface import menu


class Item:
    # an item that can be picked up and used.
    def __init__(self, spell=None, equipment=None, ammo=None, book=None):
        self.owner = None
        self.value = 0
        self.spell = spell
        self.stackable = False
        self.book = book
        self.qty = 1
        if self.spell:
            self.use_function = self.spell.cast
            self.stackable = True
        self.equipment = equipment
        if self.equipment:
            self.use_function = self.equipment.equip
        self.ammo = ammo
        self.level = 0


    def pick_up(self, inventory, game=None):
        if not self.owner.misc:
            # get stackable items first
            for item in inventory:
                if item.item:
                    if item.item.check_stackable() and item.name == self.owner.name:
                        item.item.stack(self.qty)
                        if game:
                            if self.owner in game.objects:
                                game.objects.remove(self.owner)
                            msg = menu.color_text('You picked up a ', libtcod.yellow)
                            msg += menu.color_text(self.owner.name, self.owner.color)
                            msg += menu.color_text('!', libtcod.yellow)
                            game.message.message(msg, 0)
                        return
            # don't pick up if inventory is full
            if len(inventory) >= 26:
                msg = menu.color_text('Your inventory is full, cannot pick up ', libtcod.yellow)
                msg += menu.color_text(self.owner.name, self.owner.color)
                msg += menu.color_text('.', libtcod.yellow)
                game.message.message(msg, 0)
            else:  # otherwise pick up the item
                inventory.append(self.owner)
                if game:
                    if self.owner in game.objects:
                        game.objects.remove(self.owner)
                    msg = menu.color_text('You picked up a ', libtcod.yellow)
                    msg += menu.color_text(self.owner.name, self.owner.color)
                    msg += menu.color_text('!', libtcod.yellow)
                    game.message.message(msg, 0)

    def check_stackable(self):
        return self.stackable

    def stack(self, qty):
        self.qty += qty

    def drop(self, inventory, owner, mes=True):
        # add to the map and remove from the owners inventory.
        # also, place it at the owners coordinates
        self.owner.objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = owner.x
        self.owner.y = owner.y
        # only display a message if the player dropped it, or if its special
        if mes:
            msg = menu.color_text('%s dropped a ' % owner.name.capitalize(), libtcod.yellow)
            msg += menu.color_text(self.owner.name, self.owner.color)
            msg += menu.color_text('.', libtcod.yellow)
            self.owner.message.message(msg, 0)

    def use(self, inventory, creature, game, player=True):
        # just call the "use_function" if it is defined
        if player:
            if self.level:
                if game.player.fighter.max_consumable_level < self.level:
                    mes = game.gEngine.color_text(self.owner.name, self.owner.color)
                    game.message.message("Your class is unable to use the " + mes)
                    return
            if self.use_function is None:
                game.message.message('The ' + self.owner.name + ' cannot be used.')
            else:
                if not self.equipment:
                    if self.use_function(creature, game.player, game=game) != 'cancelled':
                        if self.check_stackable():
                            if self.qty > 1:
                                self.qty -= 1
                            else:# destroy after use, unless it was cancelled for some reason
                                inventory.remove(self.owner)
                        else:
                            inventory.remove(self.owner)
                else:  ##equip
                    self.use_function(creature, game=game, owner=self.owner)
        else:  ##so mobs can use items
            self.use_function(creature, game=game)


class Equipment:
    def __init__(self, min_power=0, max_power=0, crit_bonus=0, defense=0,
                 type='', subtype=None, location='', best_defense_type='', worst_defense_type='',
                 handed=0, dual_wield=None, damage_type='', threat_level=0,
                 allowed_materials=0, bonus=0, penalty=0, description='', accuracy=0, damage=None,
                 fuel=0, color=None, intensity=0.0):
        self.min_power = min_power                      # TODO this is never used
        self.max_power = max_power                      # TODO this is never used
        self.crit_bonus = crit_bonus                    # TODO this is never used
        self.defense = defense
        self.type = type
        self.subtype = subtype
        self.location = location
        self.best_defense_type = best_defense_type      # TODO this is never used
        self.worst_defense_type = worst_defense_type    # TODO this is never used
        self.handed = handed
        self.dual_wield = dual_wield                    # TODO this is obsolete now
        self.damage_type = damage_type              # TODO this is obsolete, but used heavily throughout
        self.threat_level = threat_level
        self.allowed_materials = allowed_materials
        self.bonus = bonus
        self.penalty = penalty
        self.description = description
        self.accuracy = accuracy
        self.damage = damage
        self.torch = None
        self.fuel = fuel
        self.max_fuel = fuel
        self.torch_color = color
        self.torch_intensity = intensity
        self.mat = None

        self.on_hit_effect = None
        self.effects = []

    """def calc_damage(self):
        total_damage = 0
        if self.damage is not None:
            num_dice = self.damage[0]  # num dice
            sides = self.damage[1]  # num faces
            multiplier = self.damage[2]  # multiplier
            bonus = self.damage[3]  # bonus damages
            for i in range(num_dice):
                total_damage += libtcod.random_get_int(0, 1, sides)
            total_damage = (total_damage * multiplier) + bonus  # + effect_damage
        print(str(total_damage))
        return total_damage"""
    def on_hit(self, min=0, max=0, range=0, radius=0, targets=None, target=None, player=None, game=None, effect_color=(1,1,1)):
        self.on_hit_effect(min, max, range, radius, targets, target, player, game, effect_color)

    ########################################################  equip is handled by equipped panel now
    def equip(self, target, game=None, owner=None, slot=0):  # TODO REFACTOR unnecessary arguments? this isn't marriage - find calls before deleting
        if owner is not None:
            target.fighter.gear.quip_it(owner)

    def un_equip(self, target, item):
        if item is not None:
            target.fighter.gear.unquip_it(item)


class Ammo:
    def __init__(self, weapon_type=None, max_stack=10, dmg_multiplier=1.0, col=[1, 1, 1]):
        self.weapon_type = weapon_type
        self.max_stack = int(max_stack)
        self.damage_multiplier = dmg_multiplier
        self.color = col
