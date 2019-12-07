
# manages effects that are active
class ConditionManager:

    def __init__(self):
        self.conditions = []

    def add_condition(self, condition):
        self.conditions.append(condition)

    def remove_condition(self, condition):
        for cond in self.conditions:
            if cond == condition:
                self.conditions.remove(condition)

    def update_conditions(self):
        if len(self.conditions) == 1:
            if self.conditions[0].dead:
                self.conditons.pop(0)
        else:
            for condition in range(len(self.conditions) - 1, 0, -1):
                if self.conditions[condition].dead:
                    self.conditions.pop(condition)

        for condition in self.conditions:
            if not condition.dead:
                condition.update()

    def get_conditions(self):
        return self.conditions


class Condition:
    """
        Conditions are lasting status effects that need to be tracked over multiple turns

    """
    def __init__(self, target, effect):
        self.dead = False
        self.target = target        # Target actor, effected by condition
        self.effect = effect        # instance of effect
        if self.effect.duration:    # will either be a number or None
           pass
           #TODO fix time based to ticker based
            #self.start_time = time.time()
            #self.end_duration = self.time_now + self.effect.duration
        #else:
            #self.start_time = self.effect.duration
            #self.end_duration = self.start_time

    def update(self):
        if not self.dead:
            self.effect.do_effect(); #TODO not an actual function
        #if self.end_duration:
            #if self.time_now > self.end_duration:
                #self.dead = True