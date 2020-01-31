import copy

class Perk:
    """ Perk base class provides all the necessary global features, at minimum you must override activate """
    def __init__(self, owner, weapon_type, branch, height, max_level, trigger):
        self.owner = owner
        self.weapon_type = weapon_type
        self.branch = branch
        self.height = height
        self.level = 0
        self.max_level = max_level
        self.description = None
        #
        self.trigger = trigger
        self.is_active = False  # active effects, not just active skills (but also active skills :D)
        self.is_locked_out = False  # for top path lockout tracking

    def set_description(self, description):
        """ rather than having a big stupid ass string for every constructor we can use this to pass each skill its
            description from another source (dict, toml, etc.) en mass, ex post-facto,
            this should also be where unified output formatting (flavor country) is done """
        self.description = description

    def level_up(self):
        """ simply checks for max level and increases """
        if self.max_level > self.level:
            self.level += 1
            self.apply_level_up()
            return True
        return False

    def lockout_skill(self):
        """ locks out an upper tree skill """
        self.is_locked_out = True

    def apply_level_up(self):
        """ override to generate unique level up procedure """
        pass

    def activate(self):
        """ override to generate an activate procedure """
        pass

    def deactivate(self):
        """ override to deactivate """
        pass

    def update(self, stuff):
        """ under consideration for active skill duration tracking """
        pass


class GreatHammerKillSplash(Perk):
    def apply_level_up(self):
        # bonus stuff += some value
        pass

    def activate(self):
        # do that thing you do
        pass

    def deactivate(self):
        # is this an active skill?
        pass


class BabyTownFrolics(Perk):
    def __init__(self, owner, weapon_type, branch, height, max_level, trigger):
        super().__init__(owner, weapon_type, branch, height, max_level, trigger)
        self.amount = 100
        self.stat_effected = "Strength"
        super().set_description("Gonna make you strong pussy!")

    def apply_level_up(self):
        self.deactivate()
        self.amount += 100
        self.activate()

    def activate(self):
        self.is_active = True
        current = self.owner.fighter.stat.get_stat_base(self.stat_effected)
        new_amount = current + self.amount
        self.owner.fighter.stat.set_stat_base(self.stat_effected, new_amount)

    def deactivate(self):
        self.is_active = False
        current = self.owner.fighter.stat.get_stat_base(self.stat_effected)
        new_amount = current - self.amount
        self.owner.fighter.stat.set_stat_base(self.stat_effected, new_amount)


class PerkTree:
    """ Everyone gets a PerkTree """
    def __init__(self, owner):
        self.owner = owner

        self.perk_tree = {"great hammer": (BabyTownFrolics(self.owner, "great hammer", "offensive", 1, 200, "passive"),
                                           GreatHammerKillSplash(self.owner, "great hammer", "offensive", 1, 10, "on_hit"),
                                           ),
                          "long sword": (BabyTownFrolics(self.owner, "long sword", "offensive", 1, 5, "passive"),
                                         ),
                          # add more weapon types here
                          }
        # always make sure you didn't fuck up the perk tree!
        self.make_sure_we_didnt_fuck_up_the_perk_tree()

        self.perk_trees_maxed = 0
        self.total_perk_trees = len(list(self.perk_tree.keys()))
        self.total_perkpoints_spent = 0  # per tree basis?


        # tracks the players consecutive action triggers
        self.consecutive_triggers = {
            "blocks": 0,
            "parries": 0,
            "dodges": 0,
            "hits_taken": 0,
            "hits_landed": 0,
            "crits": 0,
            "kills_last_turn": 0,
        }

    def update_trigger_counts(self, action, kills=0):
        """ handles updating self.consecutive_triggers """
        if action == "block":
            self.consecutive_triggers['blocks'] += 1
            self.consecutive_triggers['parries'] = 0
            self.consecutive_triggers['dodges'] = 0
            self.consecutive_triggers['hits_taken'] = 0
        if action == "parry":
            self.consecutive_triggers['blocks'] = 0
            self.consecutive_triggers['parries'] += 1
            self.consecutive_triggers['dodges'] = 0
            self.consecutive_triggers['hits_taken'] = 0
        if action == "dodge":
            self.consecutive_triggers['blocks'] = 0
            self.consecutive_triggers['parries'] = 0
            self.consecutive_triggers['dodges'] += 1
            self.consecutive_triggers['hits_taken'] = 0
        if action == "hit_taken":
            self.consecutive_triggers['blocks'] = 0
            self.consecutive_triggers['parries'] = 0
            self.consecutive_triggers['dodges'] = 0
            self.consecutive_triggers['hits_taken'] += 1
        if action == "crit":
            pass
        if action == "attack_landed":
            pass

    def destroy_perk_tree(self):
        """ destroy reference to all perk objects on fighter death """
        self.perk_tree = None

    def get_all_perks_by_weapon(self, weapon):
        """ get all the skills for a weapon by passing in its associated name """
        return list(self.perk_tree[weapon].values())

    def get_perk_by_trigger_type(self, weapon, trig_type):
        """ get array of skills for a particular weapon with the passed trigger type """
        perks = []
        for perk in list(self.perk_tree[weapon].values()):
            if perk.trigger == trig_type:
                perks.append(perk)
        if perks:
            return perks

    def is_owned(self, perk):
        """ checks for a perk level of 1 or higher """
        for perk in list(self.perk_tree[perk.weapon_type].values()):
            if perk == perk:
                if perk.level > 0:
                    return True
        return False

    def activate_perk(self, perk):
        """ turn on active perk and apply it's effect """
        if not perk.is_active:  # TODO, im sure we will need to check for cool-down and available MP etc.
            perk.activate()

    def is_active(self, perk):
        """ checks if a perk is in use """
        return perk.is_active

    def level_up_perk(self, perk):
        """ makes sure you have sp + req. met and levels the perk, logging the point spent and checks for max tree """
        if self.owner.fighter.unused_skill_points > 0 and not perk.is_locked_out \
        and self.check_prerequisite_in_branch(perk) and self.check_prerequisite_in_tree(perk):
            if perk.level_up():
                self.total_perkpoints_spent += 1
                self.owner.fighter.unused_skill_points -= 1
                # we will track which trees are maxed for achievement, need to store this somewhere
                self.check_for_max_tree(perk.weapon_type)
                if perk.branch == "path_a":
                    self.lockout_path(perk.weapon_type, "path_b")
                if perk.branch == "path_b":
                    self.lockout_path(perk.weapon_type, "path_a")
            return True
        return False

    def check_prerequisite_in_branch(self, perk):
        """ checks the tree by branch and height to make sure all prior skills have been learned """
        if perk.level > 0:  # already has pre-req met obviously
            return True
        else:
            for pre_req in list(self.perk_tree[perk.weapon_type].values()):
                if pre_req.branch == perk.branch and pre_req.height < perk.height:
                    if pre_req.level == 0:
                        return False
            return True

    def check_prerequisite_in_tree(self, perk):
        """ checks the tree to ensure path conditions are met """
        if perk.branch == "offensive" or perk.branch == "defensive" or perk.branch == "utility":
            # I actually want the tree to require start with crit and other util before offense or def selection
            # so this will get a little add on here
            return True
        if perk.branch == "left_center":
            # check for offense and util fully activated
            if self.is_fully_activated_branch(perk.weapon_type, "offensive") and \
            self.is_fully_activated_branch(perk.weapon_type, "utility"):
                return True
        if perk.branch == "right_center":
            # check for defense and util fully activated
            if self.is_fully_activated_branch(perk.weapon_type, "defensive") and \
            self.is_fully_activated_branch(perk.weapon_type, "utility"):
                return True
        if perk.branch == "center":
            # check for left_center and right_center fully activated
            if self.is_fully_activated_branch(perk.weapon_type, "left_center") and \
            self.is_fully_activated_branch(perk.weapon_type, "right_center"):
                return True
        if perk.branch == "path_a":
            # check for center activated and no path_b activated
            if self.is_fully_activated_branch(perk.weapon_type, "center") and \
            not self.is_activated_branch(perk.weapon_type, "path_b"):
                return True
        if perk.branch == "path_b":
            # check for center activated and no path_a activated
            if self.is_fully_activated_branch(perk.weapon_type, "center") and \
            not self.is_activated_branch(perk.weapon_type, "path_a"):
                return True
        return False

    def is_activated_branch(self, weapon_type, branch):
        """ checks to ensure ANY skills in a branch have been activated """
        for perks in list(self.perk_tree[weapon_type].values()):
            if perks.branch == branch and perks.level > 0:
                return True
        return False

    def is_fully_activated_branch(self, weapon_type, branch):
        """ checks to ensure ALL skills in a branch have been activated """
        for perks in list(self.perk_tree[weapon_type].values()):
            if perks.branch == branch and perks.level == 0:
                return False
        return True

    def is_maxed_tree(self, weapon_type):
        """ if all skills in tree are activated and max level, you win a cookie! """
        for perks in list(self.perk_tree[weapon_type].values()):
            if perks.level != perks.max_level:
                return False
        return True

    def lockout_path(self, weapon_type, path):
        """ if upper path a is selected perma-lock all path b skills and vice versa,
            pass the path you want to lock out """
        for perk in list(self.perk_tree[weapon_type].values()):
            if perk.branch == path:
                perk.lockout_skill()

    def make_sure_we_didnt_fuck_up_the_perk_tree(self):
        pass
        # # TODO: This is all defined to identify failures in the perk tree when its fully set up, which its not
        # # the tree map is used make sure we don't fuck up initializing branches/heights
        # self.perk_tree_map = {"offensive": [1, 1, 2, 3],
        #                       "utility": [1, 1, 2, 3],
        #                       "defensive": [1, 1, 2, 3],
        #                       "left_center": [1],
        #                       "right_center": [1],
        #                       "center": [1],
        #                       "path_a": [1, 2, 3, 3, 4],
        #                       "path_b": [1, 2, 3, 3, 4]
        #                      }
        # self.init_map = copy.deepcopy(self.perk_tree_map)  # copy the tree map structure
        # for branch in list(self.init_map):
        #     self.init_map[branch] = []      # clear out the copy
        #
        # for weapon in list(self.perk_tree):  # we have to check each weapon tree
        #     for perk in list(self.perk_tree[weapon]):
        #         self.init_map[perk.branch].append(perk.height)  # build a map from our weapon tree
        #     for branch in list(self.init_map):
        #         self.init_map[branch].sort()
        #     if self.init_map != self.perk_tree_map:
        #         print("You fucked up on one of the " + weapon + " perks. Check " + self.owner.name + "'s perk tree.")
        #     for branch in list(self.init_map):
        #         self.init_map[branch] = []
