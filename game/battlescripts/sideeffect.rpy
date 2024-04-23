init python:
    class SideEffect:
        def __init__(self, user, target, type, magnitude=1, chance=1, randomval=0):
            self.User = user#the Pokémon object applying this sideeffect
            self.Target = target#the Pokémon object this sideeffect will be applied to.
            self.Type = type#Stats Macro or string with a status
            self.Magnitude = magnitude#int--refers either to the num of statchanges or the number of turns the status is applied for
            self.Chance = chance#float--the chance this sideeffect will be applied. Defaults to true.
            self.RandomVal = randomval#for use when multiple side effects aren't independent

        def GetTargets(self, target):
            return self.Target

        def GetType(self, target):
            return self.Type

        def GetMagnitude(self, target):
            return self.Magnitude

        def GetChance(self, target):
            return self.Chance

        def Apply(self, selfinflicted=False, overwrite=False):
            if (self.User.HasAbility("Serene Grace")):
                self.Chance *= 2.0
            if ((self.RandomVal if self.RandomVal != 0 else random.random()) <= self.Chance and not self.Target.HasAbility("Shield Dust") and not self.User.HasAbility("Sheer Force")):
                if (isinstance(self.Type, str)):
                    return self.Target.ApplyStatus(self.Type, self.Magnitude, self.User, overwrite)
                else:
                    return self.Target.ChangeStats(self.Type, self.Magnitude, self.User)
            return ""