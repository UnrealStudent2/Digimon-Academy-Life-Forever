init python:
    def DoMove(action, user, move, targets, alreadypretext="", alreadyposttext="", repeating=False, parentalbond=False, invoketest=False):
        global BattlefieldEffects
        global UsingMove
        global MoveUser
        global ActiveMove
        global ActionLog
        global ItemText
        global AutoLose

        if (user not in Battlers()):
            action.ChangeSuccess(False)
            return

        if (not MoveValid(user, move)):
            action.ChangeSuccess(False)
            if (not invoketest):
                renpy.say(None, "{} can't use {}!".format(user.GetNickname(), move.Name))
            return

        moveboosts = []
        for fvl in user.GetForeverals():
            if (lookupforeveraldata(fvl, FVLMacros.FVLType) == ForeveralTypes.MoveBoost):
                for newmove in lookupforeveraldata(fvl, FVLMacros.FVLTypeData):
                    moveboosts.append(newmove)

        UsingMove = True
        MoveUser = user
        renpy.show_screen("battleui")
        name = move.Name
        ActiveMove = name
        type = move.Type
        pretext = alreadypretext
        posttext = alreadyposttext
        abortmove = False
        username = user.GetNickname()
        repeat = repeating
        critstage = 0
        healthgain = 0
        power = 0
        fixeddamage = -1
        recoil = 0
        iscrit = False
        sheerforcebonus = False
        subtractpp = True
        atebonus = False#from pixilate, aerilate, stuff like that
        contact = MakesContact(move)

        if (user.HasAbility("Long Reach")):
            contact = False

        if (user.HasStatus("electrified")):
            type = "Electric"
        if (user.HasStatus("ionized") and type == "Normal"):
            type = "Electric"
        
        if (type == "Normal" and user.HasAbility("Pixilate")):
            type = "Fairy"
            atebonus = True

        user.ClearStatus("bound to destiny")

        if (user.HasStatus("flinching")):
            posttext += "{} flinched!".format(username)
            abortmove = True
        elif (user.HasStatus("frozen")):
            if (random.random() > .2 
                and move.Name not in ["Flame Wheel", "Sacred Fire", "Flare Blitz", "Fusion Flare", "Scald", "Steam Eruption", "Burn Up", "Pyro Ball", "Scorching Sands", "Matcha Gotcha"]
                and not (move.Name == "Fillet Away" and "Fillet Away" in moveboosts)):
                pretext += "{} is frozen!".format(username)
                abortmove = True
            else:
                pretext += "{} thawed out!".format(username)
                user.ClearStatus("frozen")
        elif (user.GetStatusCount("asleep") > 0 and name not in ["Snore", "Sleep Talk"]):
            pretext = "{} is fast asleep...".format(username)
            abortmove = True
        elif (user.HasStatus("asleep") and user.GetStatusCount("asleep") <= 0):
            user.ClearStatus("asleep")
            pretext = "{} woke up!".format(username, move.Name)
        elif (user.HasStatus("paralyzed") and random.random() <= .25):
            posttext += "{} is paralyzed, so it can't move!".format(username)
            abortmove = True
        elif (user.HasStatus("infatuated") and random.random() <= .5):
            posttext += "{} is infatuated, and cannot move!".format(username)
            abortmove = True
        elif (user.HasStatus("confused") and user.GetStatusCount("confused") <= 0):
            user.ClearStatus("confused")
            pretext = "{} snapped out of confusion!".format(username, move.Name)
        elif (user.GetStatusCount("confused") > 0):
            pretext = "{} is confused! ".format(username)
            if (random.random() <= .33):
                    posttext += "{} hurt itself in its confusion!".format(username)
                    if (not user.HasStatus("busted disguise") and user.HasAbility("Disguise")):
                        user.AdjustHealth(-user.GetStat(Stats.Health) / 8.0)
                        user.ApplyStatus("busted disguise")
                        posttext += "{}'s disguise was busted!".format(user.GetNickname())
                    else:
                        DoDamage(user, hurtself, user)
                    abortmove = True
        elif (user.HasStatus("taunted") and move.Category == "Status"):
            posttext += "{} is too angry to use {}!".format(username, move.Name)
            abortmove = True
        elif (user.HasStatus("encored") and move != GetLastMove(ActionLog, user)):
            posttext += "{} is swayed into an encore!".format(username)
            abortmove = True
        elif (IsExplosion(name) and AbilityOnField("Damp")):
            posttext += "It's too damp for explosions!"
            abortmove = True
        elif (move.PP == 0):
            posttext += "{} tried to use {}, but there's no PP left for that move!".format(username, move.Name)
            abortmove = True

        if (name not in ["Endure", "Protect", "Wide Guard", "Detect", "Enshroud", "Deathless", "Splinter Shield", "Spiky Shield", "Quick Guard", "Silk Trap", "Baneful Bunker", "Obstruct"]):
            user.ClearStatus(".protections")
        if (name != "Fury Cutter"):
            user.ClearStatus(".furycutter")
        
        if (abortmove):
            action.ChangeSuccess(False)
            if (not invoketest):
                renpy.say(None, pretext + " " + posttext)
            UsingMove = False
            MoveUser = None
            ActiveMove = None
            return

        if (move.Name in moveboosts):
            pretext += "{}'s wishes coalesced! ".format(username)

        pretext += "{} used {}!".format(username, move.Name)


        if (StatusOnFoes(user, "snatching") != None and IsSnatchable(name)):
            user = StatusOnFoes(user, "snatching")
            targets = [user]
            pretext += "The move was snatched by {}!".format(user.GetNickname())
            user.ClearStatus("snatching")

        if (len(targets) == 1 and StatusInBattlers("the standout")):
            for mon in Battlers():
                if (mon.HasStatus("the standout") and mon in GetTargets(user, GetMoveRange(move)) and mon not in GetBattlers(user)):
                    targets = [mon]

        if (GetMoveRange(move) in [Range.All, Range.AllAlliesAndSelf]):
            targets = [user]
        elif (GetMoveRange(move) == Range.AllFoes):
            targets = [targets[0]]

        bouncingmon = None
        for mon in targets:
            if (user != mon and move.Category == "Status" and GetMoveRange(move) not in [Range.All, Range.Self] and (mon.HasAbility("Magic Bounce") or mon.HasStatus("coated in magic"))):
                posttext += "The move was bounced back!"
                bouncingmon = mon
        if (bouncingmon != None):
            user = bouncingmon
            targets = GetTargets(bouncingmon, GetMoveRange(move))

        if (name == "Magnitude"):
            magnitude = random.random()
            if (magnitude < .05):
                posttext += "Magnitude 4!"
                power = 10
            elif (magnitude < .15):
                posttext += "Magnitude 5!"
                power = 30
            elif (magnitude < .35):
                posttext += "Magnitude 6!"
                power = 50
            elif (magnitude < .65):
                posttext += "Magnitude 7!"
                power = 70
            elif (magnitude < .85):
                posttext += "Magnitude 8!"
                power = 90
            elif (magnitude < .95):
                posttext += "Magnitude 9!"
                power = 110
            else:
                posttext += "Magnitude 10!!!"
                power = 150

        sideeffects = []
        posteffects = []

        for i, target in enumerate(targets):
            sideeffects = []
            posteffects = []
            
            doDamage = (False if move.Category == "Status" else True)

            if (user.GetStatusCount("biding") >= 3):
                if (user.GetStatusCount(".bidingdamage") != 0):
                    fixeddamage = user.GetStatusCount(".bidingdamage")[0] * 2.0
                    doDamage = True
                    subtractpp = True
                    target = user.GetStatusCount(".bidingdamage")[1]
                    if (target not in GetBattlers(user, True)):
                        target = random.choice(GetBattlers(user, True))
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)

            checkaccuracy = ((isinstance(move.Accuracy, float) or isinstance(move.Accuracy, int)) 
                and not (user.HasAbility("No Guard") or target.HasAbility("No Guard"))
                and not (move.Name in ["Thunder", "Hurricane"] and WeatherIs("rainy"))
                and not (move.Name == "Blizzard" and (WeatherIs("snowy") or WeatherIs("hail")))
                and not (user.HasStatus(".mindreading") and target.HasStatus("mind read"))
                and not (user.HasStatus(".lockingon") and target.HasStatus("locked on")))

            trueaccuracy = 1.0
            baseaccuracy = move.Accuracy

            if (move.Name in ["Hurricane", "Thunder"] and WeatherIs("sunny")):
                baseaccuracy = 0.5

            if (type in ["Electric", "Water"] and GetMoveRange(move) in [Range.Adjacent, Range.AdjacentFoe, Range.Any, Range.AnyOrSelf, Range.AdjacentAlly, Range.AdjacentAllyOrSelf]):
                for pkmn in Battlers(True):
                    if (pkmn != user):
                        if (type == "Electric" and pkmn.HasAbility("Lightning Rod")
                            or type == "Water" and pkmn.HasAbility("Storm Drain")):
                            target = pkmn
                            checkaccuracy = False
                            break

            if (target not in target.GetTrainer().GetLead()):
                try:
                    newtarget = target.GetTrainer().GetLead()[action.GetTargetSlots()[i]]
                    action.GetTargets()[action.GetTargets().index(target)] = newtarget
                    target = newtarget
                except:
                    target == None

            if (target == None):
                for trainer in Trainers:
                    for othermon in trainer.GetLead():
                        if (othermon in GetTargets(user, GetMoveRange(move), GetMoveRange(move) in [Range.Adjacent, Range.Any, Range.AnyOrSelf])):
                            target = othermon

            if (name in ["Thrash", "Outrage"]):
                target = random.choice(GetTargets(user, Range.AdjacentFoe))

            if (target == None or target != None and target.GetHealthPercentage() <= 0):
                action.ChangeSuccess(False)
                if (not invoketest):
                    renpy.say(None, "{} tried to use {}, but there is no target!".format(username, name))
                UsingMove = False
                MoveUser = None
                ActiveMove = None
                return
            
            if (targets[:i + 1].count(target) > 1):
                continue

            targetstring = " It targets " + target.GetNickname() + "!"
            if (GetMoveRange(move) in [Range.All, Range.AllAdjacent, Range.AllAdjacentFoes, Range.AllFoes, Range.AllAllies, Range.Self, Range.AllAlliesAndSelf]
                or (GetMoveRange(move) == Range.AdjacentAlly and len(GetTargets(user, Range.AdjacentAlly)) == 0)
                or len(GetTargets(user, GetMoveRange(move))) < 2
                or name in ["Dive", "Fly", "Bounce", "Dig", "Shadow Force", "Phantom Force"] and not (user.HasStatus("dug in") or user.HasStatus("airborne") or user.HasStatus("diving") or user.HasStatus("ethereal"))):
                targetstring = ""

            pretext += targetstring

            breaksemiinvul = (name in ["Gust", "Hurricane", "Smack Down", "Sky Uppercut", "Thousand Arrows", "Thunder", "Twister", "Whirlwind"] and target.HasStatus("airborne")
            or name in ["Earthquake", "Fissure", "Magnitude"] and target.HasStatus("dug in")
            or name in ["Whirlpool", "Surf"] and target.HasStatus("diving")
            or name == "Toxic" and user.HasType("Poison")
            or target.HasAbility("No Guard")
            or user.HasAbility("No Guard"))

            ignoresemiinvul = breaksemiinvul

            if (name in ["Stomp", "Body Slam", "Dragon Rush", "Steamroller", "Heat Crash", "Heavy Slam", "Flying Press", "Malicious Moonsault"] and target.HasStatus(".minimized") 
            or name == "Dig" and not user.HasStatus("dug in")
            or name in ["Fly", "Bounce"] and not user.HasStatus("airborne")
            or name == "Dive" and not user.HasStatus("diving")
            or name == "Phantom Force" and not user.HasStatus("ethereal")
            or name == "Toxic" and user.HasType("Poison")
            or name in ["Toxic Spikes", "Spikes", "Stealth Rocks", "Sticky Web"]
            or breaksemiinvul
            or (repeat and (name != "Triple Kick" or MultihitMax != None and user.HasAbility("Skill Link")))):
                ignoresemiinvul = True
                checkaccuracy = False

            if (move.Name in ["Feint", "Phantom Force"]):
                if (target.HasStatus("protected") or EffectOnOwnField(target, "wide guard") or EffectOnOwnField(target, "quick guard")):
                    target.ClearStatus("protected")
                    if ("wide guard" in GetFieldEffects(target)):
                        del GetFieldEffects(target)["wide guard"]
                    if ("quick guard" in GetFieldEffects(target)):
                        del GetFieldEffects(target)["quick guard"]
                    checkaccuracy = False

            if (checkaccuracy):
                accuracybuffs = user.GetStatChanges(Stats.Accuracy)
                evasionbuffs = target.GetStatChanges(Stats.Evasion)
                if (target.HasStatus("confused") and target.HasAbility("Tangled Feet")):
                    evasionbuffs += 3
                if (evasionbuffs > 0 and (target.HasStatus("miraculously seen") or target.HasStatus("foreseen") or target.HasStatus("sniffed out") or user.HasAbility("Keen Eye") 
                or (evasionbuffs != 0 and (user.HasAbility("Unaware") or move.Name in ["Chip Away", "Darkest Lariat"])))):
                    evasionbuffs = 0
                if (accuracybuffs != 0 and target.HasAbility("Unaware")):
                    accuracybuffs = 0
                accuracymodifier = accuracybuffs - evasionbuffs
                if (accuracymodifier > 0):
                    accuracymodifier = min(6, accuracymodifier)
                    accuracymodifier = (accuracymodifier + 3) / 3.0
                elif (accuracymodifier < 0):
                    accuracymodifier = max(-6, accuracymodifier)
                    accuracymodifier = 3.0 / (-accuracymodifier + 3)
                elif (accuracymodifier == 0):
                    accuracymodifier = 1

                if (move.Category == "Status" and target.HasAbility("Wonder Skin")):
                    baseaccuracy = 0.5
                elif ((WeatherIs("sandstorm") and target.HasAbility("Sand Veil"))
                    or (WeatherIs("hail") and target.HasAbility("Snow Cloak"))):
                    accuracymodifier *= 0.8

                if (move.Category == "Physical" and user.HasAbility("Hustle")):
                    accuracymodifier *= 0.8
                elif (user.HasAbility("Compound Eyes")):
                    accuracymodifier *= 1.3

                if (BattlefieldExists("Gravity")):
                    accuracymodifier *= 5.0/3.0

                trueaccuracy = baseaccuracy * accuracymodifier

                if (WeatherIs("blinding fog")):
                    if (trueaccuracy < 1):
                        trueaccuracy = 0

            if ((target.HasStatus("poisoned") or target.HasStatus("badly poisoned")) and user.HasAbility("Merciless")):
                iscrit = True

            if (type == "Fire" and target.HasAbility("Thermal Exchange")):
                posttext += target.ChangeStats(Stats.Attack, 1, target)

            if (((((GetMoveRange(move) in [Range.Adjacent, Range.AdjacentFoe, Range.AllAdjacent, Range.AllAdjacentFoes, Range.AllFoes, Range.Any, Range.AnyOrSelf] or name in ["Thrash", "Outrage"]) and target.HasStatus("protected"))
                and not (target.HasStatus(".silked") and move.Category == "Status")
                and not (target.HasStatus(".obstructing") and move.Category == "Status"))
            or (GetMoveRange(move) in [Range.All, Range.AllAdjacent, Range.AllFoes, Range.AllAdjacentFoes] and EffectOnOwnField(target, "wide guard"))
            or (action.GetPriority() > 0 and EffectOnOwnField(target, "quick guard")))
            and name not in ["Tearful Look", "Hyper Drill", "Bestow"]
            and not (name in ["Fly", "Bounce"] and not user.HasStatus("airborne")
                    or name == "Dig" and not user.HasStatus("dug in")
                    or name == "Dive" and not user.HasStatus("diving")
                    or name in ["Shadow Force", "Phantom Force"] and not user.HasStatus("ethereal"))):  
                repeat = False                  
                doDamage = False
                posttext += "But {} was protected!".format(target.GetNickname())
                if (name in ["Jump Kick", "High Jump Kick"]):
                    user.AdjustHealth(-user.GetStat(Stats.Health) / 2.0)
                    posttext += "{} kept going and crashed!".format(username)
                if (target.HasStatus(".enshrouded") and not contact):
                    posttext += target.ChangeStats(Stats.Evasion, 1, user)
                    target.ClearStatus(".enshrouded")
                elif (target.HasStatus(".splintering") and contact):
                    posttext += ApplyEffect(target, "stealthy rocks", 1, True)
                    target.ClearStatus(".splintering")
                elif (target.HasStatus(".spiky") and contact):
                    user.AdjustHealth(-user.GetStat(Stats.Health) / 8.0)
                elif (target.HasStatus(".silked") and contact):
                    posttext += user.ChangeStats(Stats.Speed, -1, target)
                elif (target.HasStatus(".baneful") and contact):
                    posttext += user.ApplyStatus("poisoned")
                elif (target.HasStatus(".obstructing") and contact):
                    posttext += user.ChangeStats(Stats.Defense, -2, target)
            elif ((checkaccuracy and random.random() > trueaccuracy) or (target.HasStatus("dug in") or target.HasStatus("airborne") or target.HasStatus("ethereal") or target.HasStatus("diving")) and not breaksemiinvul and not ignoresemiinvul):
                doDamage = False
                posttext += "But it missed {}!".format(target.GetNickname())
                repeat = False
                MultihitMax = None
                MultihitCount = None
                if (name in ["Jump Kick", "High Jump Kick"]):
                    user.AdjustHealth(-user.GetStat(Stats.Health) / 2.0)
                    posttext += "{} kept going and crashed!".format(username)
                action.ChangeSuccess(False)
            elif (target.HasType("Dark") and user.HasStatus("pranking") and target != user and move.Category == "Status"):
                doDamage = False
                pretext += "It had no effect on {}...".format(target.GetNickname())
            elif (type == "Electric" and user != target and target.HasAbility("Volt Absorb")):
                doDamage = False
                target.AdjustHealth(target.GetStat(Stats.Health) / 4.0)
            elif (type == "Water" and user != target and (name != "Dive" or user.HasStatus("diving")) and (target.HasAbility("Water Absorb") or target.HasAbility("Dry Skin"))):
                doDamage = False
                target.AdjustHealth(target.GetStat(Stats.Health) / 4.0)
            elif (type == "Grass" and user != target and target.HasAbility("Sap Sipper")):
                doDamage = False
                posttext += target.ChangeStats(Stats.Attack, 1, user)
            elif (type == "Electric" and user != target and target.HasAbility("Lightning Rod") 
                or type == "Water" and user != target and target.HasAbility("Storm Drain")):
                doDamage = False
                posttext += target.ChangeStats(Stats.SpecialAttack, 1, user)
            elif ((type == "Fire" or name == "Will-O-Wisp") and user != target and target.HasAbility("Flash Fire")):
                doDamage = False
                posttext += target.ApplyStatus("aflame")
            elif (IsSoundMove(move.Name) and user != target and target.HasAbility("Soundproof")):
                doDamage = False
                posttext += "{} is soundproof!".format(target.GetNickname())
            elif ((("Spore" in move.Name or ("Powder" in move.Name and move.Name != "Powder Snow")) or move.Name == "Leech Seed") and target.HasType("Grass")):
                doDamage = False
                posttext += "But it failed to affect {}...".format(target.GetNickname())
            elif ((("Spore" in move.Name or ("Powder" in move.Name and move.Name != "Powder Snow")) and target.HasAbility("Overcoat"))):
                doDamage = False
                posttext += "But it failed to affect {}...".format(target.GetNickname())
            elif (user.GetTrainerType() == target.GetTrainerType() and GetMoveRange(move) not in [Range.Self, Range.AllAlliesAndSelf, Range.AllAllies, Range.AdjacentAlly, Range.AdjacentAllyOrSelf] and target.HasAbility("Telepathy")):                    
                doDamage = False
                posttext += "{} used telepathy to dodge the ally's attack!".format(target.GetNickname())
            #cancellation of move effects above here
            #move effects under here
            elif (name == "Splash"):
                posttext += "But nothing happened...".format(username)
            elif (name in ["Absorb", "Mega Drain", "Giga Drain", "Leech Life", "Dream Eater", "Parabolic Charge", "Horn Leech"]):
                healthgain += 0.5
                if (name == "Dream Eater" and not target.HasStatus("asleep")):
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
                    doDamage = False
            elif (name == "Draining Kiss"):
                healthgain += 0.75
            elif (name in ["Tail Whip", "Leer"]):
                posttext += target.ChangeStats(Stats.Defense, -1, user)
            elif (name in ["Rock Smash", "Razor Shell", "Crush Claw"]):
                sideeffects.append(SideEffect(user, target, Stats.Defense, -1, 0.5))
            elif (name in ["Iron Tail"]):
                sideeffects.append(SideEffect(user, target, Stats.Defense, -1, 0.3))
            elif (name == "Flame Charge"):
                sideeffects.append(SideEffect(user, user, Stats.Speed, 1))
            elif (name == "Crunch"):
                sideeffects.append(SideEffect(user, target, Stats.Defense, -1, 0.2))
            elif (name == "Rock Tomb"):
                sideeffects.append(SideEffect(user, target, Stats.Speed, -1))
            elif (name in ["Flamethrower", "Ember", "Flame Wheel", "Heat Wave", "Fire Blast"]):
                sideeffects.append(SideEffect(user, target, "burned", chance=0.1))
            elif (name in ["Lava Plume"]):
                sideeffects.append(SideEffect(user, target, "burned", chance=0.3))
            elif (name in ["Bug Buzz", "Psychic", "Acid", "Earth Power", "Flash Cannon", "Energy Ball"]):
                sideeffects.append(SideEffect(user, target, Stats.SpecialDefense, -1, chance=0.1))
            elif (name == "Shadow Ball"):
                sideeffects.append(SideEffect(user, target, Stats.SpecialDefense, -1, chance=0.2))
            elif (name == "Quiver Dance"):
                posttext += user.ChangeStats(Stats.SpecialAttack, 1, user)
                posttext += user.ChangeStats(Stats.SpecialDefense, 1, user)
                posttext += user.ChangeStats(Stats.Speed, 1, user)
            elif (name == "Venom Drench"):
                if (target.HasStatus("poisoned") or target.HasStatus("badly poisoned")):
                    posttext += target.ChangeStats(Stats.Attack, -1, user)
                    posttext += target.ChangeStats(Stats.SpecialAttack, -1, user)
                    posttext += target.ChangeStats(Stats.Speed, -1, user)
            elif (name == "Hurricane"):
                if (target.HasStatus("airborne")):
                    power *= 2
                sideeffects.append(SideEffect(user, target, "confused", random.randint(2, 5), chance=0.3))
            elif (name == "Inferno"):
                sideeffects.append(SideEffect(user, target, "burned"))
            elif (name in ["Gust", "Twister"]):
                if (target.HasStatus("airborne")):
                    power *= 2
            elif (name == "Defense Curl"):
                user.ApplyStatus(".curling")
                posttext += user.ChangeStats(Stats.Defense, 1, user)
            elif (name == "Echoed Voice"):
                global UsedEchoedVoice
                UsedEchoedVoice = True
                if (BattlefieldExists("Echoed Voice")):
                    power = BattlefieldEffects["Echoed Voice"]
            elif (name in ["Trick", "Switcheroo"]):
                useritem = user.GetItem()
                targetitem = target.GetItem()
                if ((useritem == None and targetitem == None) or target.HasStatus("substitute") or target.HasAbility("Sticky Hold")):
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
                else:
                    posttext += "{}".format(target.GiveItem(useritem, True))
                    posttext += "{}".format(user.GiveItem(targetitem, True))
            elif (name in ["Play Nice", "Growl", "Baby-Doll Eyes"]):
                posttext += target.ChangeStats(Stats.Attack, -1, user)
            elif (name == "Noble Roar"):
                posttext += target.ChangeStats(Stats.Attack, -1, user)
                posttext += target.ChangeStats(Stats.SpecialAttack, -1, user)
            elif (name in ["Lunge", "Breaking Swipe"]):
                sideeffects.append(SideEffect(user, target, Stats.Attack, -1))
            elif (name in ["Mystical Fire", "Snarl"]):
                sideeffects.append(SideEffect(user, target, Stats.SpecialAttack, -1))
            elif (name == "Tickle"):
                posttext += target.ChangeStats(Stats.Attack, -1, user)
                posttext += target.ChangeStats(Stats.Defense, -1, user)
            elif (name == "Thunder Shock"):
                sideeffects.append(SideEffect(user, target, "paralyzed", chance=0.1))
            elif (name in ["Play Rough", "Aurora Beam"]):
                sideeffects.append(SideEffect(user, target, Stats.Attack, -1, chance=0.1))
            elif (name == "Breaking Swipe"):
                sideeffects.append(SideEffect(user, target, Stats.Attack, -1))
            elif (name == "Copycat"):
                move.PP -= 1
                lastmove = GetLastMove(ActionLog, ignorepp=True, ignoremoves=["Copycat"])
                if (lastmove == None):
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
                else:
                    newtargets = GetTargets(user, GetMoveRange(lastmove), True)
                    if (GetMoveRange(lastmove) in [Range.Adjacent, Range.AdjacentAlly, Range.AdjacentAllyOrSelf, Range.AdjacentFoe, Range.Any, Range.AnyOrSelf, Range.Self, Range.All]):
                        newtargets = [random.choice(newtargets)]
                    DoMove(action, user, copy.deepcopy(lastmove), newtargets, alreadypretext=pretext + " {} copied {}! ".format(username, lastmove.Name))
                    ActionLog.append(Action(0, user.GetStat(Stats.Speed), ActionTypes.Move, user.GetTrainer(), user, GetMove(lastmove.Name), GetTrainers(newtargets), newtargets, Turn))
                    return
            elif (name in ["Bullet Seed", "Arm Thrust", "Pin Missile", "Double Slap", "Fury Swipes", "Fury Attack", "Water Shuriken", "Bone Rush", "Spike Cannon", "Comet Punch", "Rock Blast", "Scale Shot"]):
                global MultihitCount
                global MultihitMax
                repeat = True
                if (MultihitCount == None):
                    randval = random.random()
                    if (randval <= 0.35):
                        MultihitCount = 1
                    elif (randval <= 0.7):
                        MultihitCount = 2
                    elif (randval <= 0.85):
                        MultihitCount = 3
                    else:
                        MultihitCount = 4
                    if (user.HasAbility("Skill Link")):
                        MultihitCount = 4
                    MultihitMax = MultihitCount
                posttext += "Hit {} time(s)!".format(MultihitMax - MultihitCount + 1)
                if (MultihitCount != 0):
                    MultihitCount -= 1
                else:
                    if (name == "Scale Shot"):
                        posttext += user.ChangeStats(Stats.Defense, -1, user)
                        posttext += user.ChangeStats(Stats.Speed, 1, user)
                    repeat = False
                    MultihitMax = None
                    MultihitCount = None
            elif (name in ["Double Kick", "Bonemerang", "Dual Chop", "Double Hit", "Twineedle"]):
                global MultihitCount
                global MultihitMax
                repeat = True
                if (name == "Twineedle"):
                    sideeffects.append(SideEffect(user, target, "poisoned", chance=0.2))
                if (MultihitCount == None):
                    MultihitCount = 1
                    MultihitMax = MultihitCount
                posttext += "Hit {} time(s)!".format(MultihitMax - MultihitCount + 1)
                if (MultihitCount != 0):
                    MultihitCount -= 1
                else:
                    repeat = False
                    MultihitMax = None
                    MultihitCount = None
            elif (name in ["Constrict", "Bubble Beam"]):
                sideeffects.append(SideEffect(user, target, Stats.Speed, -1, chance=0.1))
            elif (name == "Rage"):
                posttext += user.ApplyStatus("raging")
            elif (name in ["Confusion", "Psybeam", "Signal Beam"]):
                sideeffects.append(SideEffect(user, target, "confused", random.randint(2, 5), chance=0.1))
            elif (name in ["Water Pulse", "Rock Climb", "Dizzy Punch"]):
                sideeffects.append(SideEffect(user, target, "confused", random.randint(2, 5), chance=0.2))
            elif (name == "Dynamic Punch"):
                sideeffects.append(SideEffect(user, target, "confused", random.randint(2, 5)))
            elif (name in ["Sharpen", "Meditate"]):
                posttext += user.ChangeStats(Stats.Attack, 1, user)
            elif (name == "Howl"):
                for mon in GetBattlers(user):
                    if (not mon.HasAbility("Soundproof")):
                        posttext += mon.ChangeStats(Stats.Attack, 1, user)
            elif (name == "Power-Up Punch"):
                sideeffects.append(SideEffect(user, user, Stats.Attack))
            elif (name == "Swords Dance"):
                posttext += user.ChangeStats(Stats.Attack, 2, user)
            elif (name in ["Poison Sting", "Poison Jab", "Sludge", "Gunk Shot"]):
                sideeffects.append(SideEffect(user, target, "poisoned", chance=0.3))
            elif (name == "Sandstorm"):
                posttext += ApplyWeather("sandstorm", 5)
            elif (name in ["Rain Dance", "Healing Spring"]):
                posttext += ApplyWeather("rainy", 5)
                if (name == "Healing Spring"):
                    user.ApplyStatus("aqua ring")
            elif (name == "Hail"):
                posttext += ApplyWeather("hail", 5)
            elif (name == "Sunny Day"):
                posttext += ApplyWeather("sunny", 5)
            elif (name == "Last Resort"):
                if (not LastResortWorks(ActionLog, user)):
                    doDamage = False
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Spite"):
                lastmove = GetLastMove(ActionLog, target)
                reduction = (min(4, lastmove.PP) if lastmove != None else 0)
                if (lastmove == None or reduction == 0 or lastmove.Name == "Struggle" or target.GetMoveByName(lastmove.Name) == None):
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
                else:
                    if ("Spite" in moveboosts):
                        target.GetMoveByName(lastmove.Name).PP = 0
                        move.PP = 0
                        posttext += "{}'s {}'s PP was reduced to 0!".format(target.GetNickname(), lastmove.Name) 
                    else:
                        target.GetMoveByName(lastmove.Name).PP -= reduction
                        posttext += "{}'s {}'s PP was reduced by {}!".format(target.GetNickname(), lastmove.Name, reduction) 
            elif (name == "Double Team"):
                posttext += user.ChangeStats(Stats.Evasion, 1, user)
            elif (name == "Struggle"):
                move.PP = 99
                user.AdjustHealth(user.GetStat(Stats.Health) * -1.0/4.0, directdamage=True)
                posttext += "{} took recoil damage!".format(username)
            elif (name == "Minimize"):
                user.ApplyStatus(".minimized")
                posttext += user.ChangeStats(Stats.Evasion, 2, user)
            elif (name == "Sticky Web"):
                posttext += ApplyEffect(user, "sticky web", 1, True)
            elif (name == "Toxic Spikes"):
                if ("toxic spikes" in GetFieldEffects(target).keys()):
                    if (GetFieldEffects(target)["toxic spikes"] == 2):
                        posttext += "But it failed!"
                    elif (GetFieldEffects(target)["toxic spikes"] == 1):
                        del GetFieldEffects(target)["toxic spikes"]
                        posttext += ApplyEffect(user, "toxic spikes", 2, True)
                else:
                    posttext += ApplyEffect(user, "toxic spikes", 1, True)
            elif (name == "Spikes"):
                if ("spikes" in GetFieldEffects(target).keys()):
                    if (GetFieldEffects(target)["spikes"] == 3):
                        posttext += "But it failed!"
                    else:
                        spikescount = GetFieldEffects(target)["spikes"]
                        del GetFieldEffects(target)["spikes"]
                        posttext += ApplyEffect(user, "spikes", spikescount + 1, True)
                else:
                    posttext += ApplyEffect(user, "spikes", 1, True)
            elif (name in ["String Shot", "Cotton Spore"]):
                posttext += target.ChangeStats(Stats.Speed, -2, user)
            elif (name in ["Sand Attack", "Smokescreen"]):
                posttext += target.ChangeStats(Stats.Accuracy, -1, user)
            elif (name == "Growth"):
                posttext += user.ChangeStats(Stats.Attack, 1, user)
                posttext += user.ChangeStats(Stats.SpecialAttack, 1, user)
            elif (name == "Harden" or name == "Withdraw"):
                posttext += user.ChangeStats(Stats.Defense, 1, user)
            elif (name == "Wrap"):
                sideeffects.append(SideEffect(user, target, ".wrappedby", user))
                sideeffects.append(SideEffect(user, target, "wrapped", random.randint(4, 5)))
            elif (name == "Fire Spin"):
                sideeffects.append(SideEffect(user, target, ".firespunby", user))
                sideeffects.append(SideEffect(user, target, "firespun", random.randint(4, 5)))
            elif (name == "Whirlpool"):
                if (target.HasStatus("diving")):
                    power *= 2
                sideeffects.append(SideEffect(user, target, ".whirlpooledby", user))
                sideeffects.append(SideEffect(user, target, "whirlpooled", random.randint(4, 5)))
            elif (name == "Sand Tomb"):
                sideeffects.append(SideEffect(user, target, ".entombedby", user))
                sideeffects.append(SideEffect(user, target, "entombed", random.randint(4, 5)))
            elif (name == "Leech Seed"):
                posttext += target.ApplyStatus("seeded", (Battlers().index(user), user), user)
            elif (name == "Mud Sport"):
                posttext += ApplyBattlefieldEffects("Mud Sport", 5)
            elif (name == "Water Sport"):
                posttext += ApplyBattlefieldEffects("Water Sport", 5)
            elif (name in ["Razor Leaf", "Night Slash", "Slash", "Drill Run", "Air Cutter", "Shadow Claw", "Aqua Cutter", "Stone Edge", "Psycho Cut", "Cross Chop", "Leaf Blade", "Karate Chop"]):
                critstage += 1
            elif (name in ["Heart Stamp", "Iron Head", "Astonish", "Bite", "Headbutt", "Stomp", "Rock Slide", "Air Slash", "Zing Zap", "Rolling Kick", "Needle Arm", "Icicle Crash"]):
                sideeffects.append(SideEffect(user, target, "flinching", chance=0.3))
            elif (name in ["Fake Out", "Legacy", "First Impression"]):
                if (Turn == 1 or (Turn - user.GetTurnSwitchedIn() <= 1)):
                    if (name == "Fake Out"):
                        sideeffects.append(SideEffect(user, target, "flinching"))
                    elif (not (target.HasType("Fairy") and target.HasAbility("Own Tempo") or target.HasAbility("Oblivious") or target.HasAbility("Inner Focus") or target.HasAbility("Scrappy"))):
                        target.ApplyStatus("flinching", 1, user)
                        posttext += target.ApplyStatus("paralyzed", 1, user)
                else:
                    posttext += "But it failed!"
                    doDamage = False
                    action.ChangeSuccess(False)
            elif (name in ["Leaf Storm", "Draco Meteor"]):
                posteffects.append(SideEffect(user, user, Stats.SpecialAttack, -2))
            elif (name == "Hammer Arm"):
                posteffects.append(SideEffect(user, user, Stats.Speed, -1))
            elif (name == "Superpower"):
                posteffects.append(SideEffect(user, user, Stats.Attack, -1))
                posteffects.append(SideEffect(user, user, Stats.Defense, -1))
            elif (name in ["Close Combat", "Headlong Rush"]):
                posteffects.append(SideEffect(user, user, Stats.Defense, -1))
                posteffects.append(SideEffect(user, user, Stats.SpecialDefense, -1))
            elif (name == "Bubble"):
                sideeffects.append(SideEffect(user, target, Stats.Speed, -1, chance=0.1))
            elif (name in ["Supersonic", "Confuse Ray", "Sweet Kiss", "Teeter Dance"]):
                posttext += target.ApplyStatus("confused", random.randint(2, 5), user)
            elif (name == "Swagger"):
                posttext += target.ApplyStatus("confused", random.randint(2, 5), user)
                posttext += target.ChangeStats(Stats.Attack, 2, user)
            elif (name == "Flatter"):
                posttext += target.ApplyStatus("confused", random.randint(2, 5), user)
                posttext += target.ChangeStats(Stats.SpecialAttack, 2, user)
            elif (name in ["Misty Terrain", "Electric Terrain", "Grassy Terrain", "Gravity"]):
                posttext += ApplyBattlefieldEffects(name, 5)
            elif (name in ["Flail", "Reversal"]):
                percent = user.GetHealth() / user.GetStat(Stats.Health)
                if (percent >= .6875):
                    power = 20
                elif (percent <= .6875 and percent > .3542):
                    power = 40
                elif (percent <= .3542 and percent > .2083):
                    power = 80
                elif (percent <= .2083 and percent > .1042):
                    power = 100
                elif (percent <= .1042 and percent > .0417):
                    power = 150
                else:
                    power = 200
            elif (name == "Mud-Slap"):
                sideeffects.append(SideEffect(user, target, Stats.Accuracy, -1))
            elif (name in ["Leaf Tornado", "Octazooka"]):
                sideeffects.append(SideEffect(user, target, Stats.Accuracy, -1, 0.5))
            elif (name in ["Mud Bomb", "Mirror Shot", "Muddy Water"]):
                sideeffects.append(SideEffect(user, target, Stats.Accuracy, -1, 0.3))
            elif (name == "Bind"):
                sideeffects.append(SideEffect(user, target, ".boundby", user))
                sideeffects.append(SideEffect(user, target, "bound", random.randint(4, 5)))
            elif (name == "Clamp"):
                sideeffects.append(SideEffect(user, target, ".clampedby", user))
                sideeffects.append(SideEffect(user, target, "clamped", random.randint(4, 5)))
            elif (name == "Infestation"):
                sideeffects.append(SideEffect(user, target, ".infestedby", user))
                sideeffects.append(SideEffect(user, target, "infested", random.randint(4, 5)))
            elif (name == "ERROR"):
                posttext += "This move should not show up. If it does, let me know."
            elif (name == "Charge"):
                posttext += user.ChangeStats(Stats.SpecialDefense, 1, user)
                posttext += user.ApplyStatus("charged")
            elif (name == "Energize"):
                posttext += user.ChangeStats(Stats.SpecialAttack, 1, user)
                posttext += user.ChangeStats(Stats.Attack, 1, user)
                posttext += user.ApplyStatus("charged")
            elif (name in ["Covet", "Thief"]):
                useritem = user.GetItem()
                targetitem = target.GetItem()
                if (useritem == None and targetitem != None and not target.HasAbility("Sticky Hold")):
                    posttext += target.TakeItem()
                    posttext += user.GiveItem(targetitem)
            elif (name in ["Guillotine", "Fissure", "Horn Drill", "Sheer Cold"]):
                accuracy = user.GetLevel() - target.GetLevel() + 30
                if (user.HasStatus(".lockingon") and target.HasStatus("locked on") 
                    or user.HasStatus(".mindreading") and target.HasStatus("mind read")
                    or user.HasAbility("No Guard") 
                    or target.HasAbility("No Guard")):
                    accuracy = 100
                if (target.HasAbility("Sturdy")
                    or target.HasType("Ice") and name == "Sheer Cold"
                    or accuracy < 30
                    or random.randint(1, 100) > accuracy 
                    or (name == "Fissure" and not IsGrounded(target))
                    or (name in ["Guillotine", "Horn Drill"] and target.HasType("Ghost"))):
                    posttext += "But it failed!"
                    doDamage = False
                    action.ChangeSuccess(False)
                else:
                    posttext += "It's a one-hit KO!"
                    fixeddamage = 999
            elif (name == "Taunt"):
                posttext += target.ApplyStatus("taunted", 4, user)
            elif (name == "Heal Block"):
                posttext += target.ApplyStatus("unhealthy", 4, user)
            elif (name in ["Discharge", "Body Slam", "Spark", "Dragon Breath"]):
                sideeffects.append(SideEffect(user, target, "paralyzed", chance=0.3))
            elif (name == "Rollout"):
                user.ApplyStatus(".usedrollout")
                if (user.HasStatus("rollout")):
                    count = user.GetStatusCount("rollout")
                    power = 30 * pow(2, count)
                    if (count == 4):
                        user.ClearStatus("rollout")
                    else:
                        user.ApplyStatus("rollout", count + 1, overwrite=True)
                else:
                    user.ApplyStatus("rollout")
            elif (name == "Ice Ball"):
                user.ApplyStatus(".usediceball")
                if (user.HasStatus("ice ball")):
                    count = user.GetStatusCount("ice ball")
                    power = 30 * pow(2, count)
                    if (count == 4):
                        user.ClearStatus("ice ball")
                    else:
                        user.ApplyStatus("ice ball", count + 1, overwrite=True)
                else:
                    user.ApplyStatus("ice ball")
            elif (name in ["Icy Wind", "Electroweb", "Mud Shot", "Low Sweep"]):
                sideeffects.append(SideEffect(user, target, Stats.Speed, -1))
            elif (name in ["Wood Hammer", "Brave Bird", "Double-Edge", "Flare Blitz"]):
                recoil += 1.0/3.0
                if (name == "Flare Blitz"):
                    sideeffects.append(SideEffect(user, target, "burned", chance=0.1))
            elif (name in ["Take Down", "Submission", "Wild Charge"]):
                recoil += 1.0/4.0
            elif (name == "Head Smash"):
                recoil += 1.0/2.0
            elif (name == "Encore"):
                if (GetLastMove(ActionLog, target) != None):
                    posttext += target.ApplyStatus("encored", 4, user)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Smog"):
                sideeffects.append(SideEffect(user, target, "poisoned", chance=0.4))
            elif (name in ["Twister", "Zen Headbutt", "Dark Pulse", "Dragon Rush"]):
                sideeffects.append(SideEffect(user, target, "flinching", chance=0.2))
            elif (name in ["Hyper Fang", "Bone Club", "Extrasensory"]):
                sideeffects.append(SideEffect(user, target, "flinching", chance=0.1))
            elif (name == "Bide"):
                subtractpp = False
                doDamage = False
                if (user.GetStatusCount("biding") == 0):
                    subtractpp = True
                    posttext += "{} is storing energy!".format(username)
                    user.ApplyStatus("biding")
                elif (user.GetStatusCount("biding") >= 3):
                    if (user.GetStatusCount(".bidingdamage") != 0):
                        fixeddamage = user.GetStatusCount(".bidingdamage")[0] * 2.0
                        doDamage = True
                        posttext += "{} unleashed energy!".format(username)
                        target = user.GetStatusCount(".bidingdamage")[1]
                        if (target not in GetBattlers(user, True)):
                            target = random.choice(GetBattlers(user, True))
                            if (target == None):
                                posttext += "But it failed!"
                                action.ChangeSuccess(False)
                    user.ClearStatus("biding")
            elif (name == "Foresight"):
                posttext += target.ApplyStatus("foreseen", applier=user)
            elif (name == "Rapid Spin"):
                sideeffects.append(SideEffect(user, user, Stats.Speed))
            elif (name == "Focus Energy"):
                posttext += user.ApplyStatus("focused")
            elif (name == "Miracle Eye"):
                posttext += target.ApplyStatus("miraculously seen", applier=user)
            elif (name == "Incinerate"):
                if (IsBerry(target.GetItem())):
                    posttext += target.GiveItem(None, True)
            elif (name == "Psywave"):
                fixeddamage = max(1, math.floor(user.GetLevel() * (random.randint(0, 100) + 50)/100.0))
            elif (name == "Dragon Rage"):
                fixeddamage = 40
            elif (name == "Sonic Boom"):
                fixeddamage = 20
            elif (name in ["Powder Snow", "Ice Beam"]):
                sideeffects.append(SideEffect(user, target, "frozen", chance=0.1))
            elif (name == "Slow Freeze"):
                posttext += target.ApplyStatus("frozen", 1, user)
            elif (name == "Hone Claws"):
                posttext += user.ChangeStats(Stats.Attack, 1, user)
                posttext += user.ChangeStats(Stats.Accuracy, 1, user)
            elif (name == "Odor Sleuth"):
                posttext += target.ApplyStatus("sniffed out", applier=user)
            elif (name in ["Endure", "Protect", "Wide Guard", "Detect", "Enshroud", "Deathless", "Splinter Shield", "Spiky Shield", "Quick Guard", "Silk Trap", "Baneful Bunker", "Obstruct"]):
                protectioncount = user.GetStatusCount(".protections")
                successrate = 1.0 / max((user.GetStatusCount(".protections") * 3), 1)
                if (successrate >= random.random() or name in ["Wide Guard", "Quick Guard"]):
                    if (name in "Endure"):
                        posttext += user.ApplyStatus("enduring")
                    elif (name == "Deathless"):
                        posttext += user.ApplyStatus("deathless")
                    elif (name in ["Protect", "Detect", "Splinter Shield", "Enshroud", "Silk Trap", "Obstruct", "Spiky Shield", "Baneful Bunker"]):
                        if (name == "Enshroud"):
                            user.ApplyStatus(".enshrouded")
                        elif (name == "Splinter Shield"):
                            user.ApplyStatus(".splintering")
                        elif (name == "Silk Trap"):
                            user.ApplyStatus(".silked")
                        elif (name == "Baneful Bunker"):
                            user.ApplyStatus(".baneful")
                        elif (name == "Spiky Shield"):
                            user.ApplyStatus(".spiky")
                        elif (name == "Obstruct"):
                            user.ApplyStatus(".obstructing")
                        posttext += user.ApplyStatus("protected")
                    elif (name == "Wide Guard"):
                        posttext += ApplyEffect(user, "wide guard", 1, False)
                    elif (name == "Wide Guard"):
                        posttext += ApplyEffect(user, "quick guard", 1, False)

                    user.ApplyStatus(".protections", protectioncount + 1, user, True)
                else: 
                    posttext += "But it failed!"
                    user.ClearStatus(".protections")
                    action.ChangeSuccess(False)
            elif (name == "Fury Cutter"):
                cutcount = user.GetStatusCount(".furycutter")
                power = 40 * pow(2, cutcount)
                user.ApplyStatus(".furycutter", cutcount + 1, user, True)
            elif (name in ["Thunder Wave", "Stun Spore", "Glare", "Zap Cannon"]):
                if (target.HasType("Ground") and name == "Thunder Wave"):
                    posttext += "It had no effect..."
                else:
                    posttext += target.ApplyStatus("paralyzed", applier=user)
            elif (name == "Lick"):
                sideeffects.append(SideEffect(user, target, "paralyzed", chance=0.3))
            elif (name in ["Hypnosis", "Sleep Powder", "Spore", "Sing", "Grass Whistle", "Lovely Kiss"]):
                posttext += target.ApplyStatus("asleep", random.randint(2, 4), user)
            elif (name in ["Will-O-Wisp", "Steady Flame"]):
                posttext += target.ApplyStatus("burned", 1, user)
            elif (name in ["Poison Powder", "Poison Gas"]):
                posttext += target.ApplyStatus("poisoned", applier=user)
            elif (name in ["Whirlwind", "Roar"]):
                if (WildBattle):
                    Fled = True
                else:
                    targettrainer = target.GetTrainer()
                    newlist = []
                    for mon in targettrainer.GetTeam():
                        if (mon.Health >= 1 and mon != target and mon not in Battlers()):
                            newlist.append(mon)
                    if (len(newlist) == 0 or target.HasStatus("ingrained")):
                        posttext += "But it failed!"
                        action.ChangeSuccess(False)
                    else:
                        randpkmn = random.choice(newlist)
                        trainer = target.GetTrainer()
                        team = trainer.GetTeam()
                        trainer.ShiftTeam(team.index(target), team.index(randpkmn), True)
                        posttext += "{} was forced out!".format(randpkmn.GetNickname())
                        SwitchInEffects(randpkmn)
            elif (name == "Disable"):
                lastmove = GetLastMove(ActionLog, target)
                if (lastmove != None):
                    posttext += target.ApplyStatus("disabled", 4, user)
                    target.ApplyStatus(".disabling", lastmove.Name)
                elif (name == "Disable"):
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Disabling Poke"):
                lastmove = GetLastMove(ActionLog, target)
                if (lastmove != None):
                    sideeffects.append(SideEffect(user, target, "disabled", 4))
                    sideeffects.append(SideEffect(user, target, ".disabling", lastmove.Name))
            elif (name == "Counter"):
                countercount = user.GetStatusCount(".countering")
                if (countercount == None or isinstance(countercount, int) or len(countercount) != 2 or countercount[1] not in Battlers()):
                    doDamage = False
                    user.ClearStatus(".countering")
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
                else:
                    target = countercount[1]
                    fixeddamage = math.floor(countercount[0] * 2)
                user.ClearStatus(".countering")
            elif (name == "Liberage"):
                posttext += "{} fights for liberty!".format(user.GetNickname())
                for mon in Battlers():
                    mon.ClearStatus("paralyzed")
                    mon.ClearStatus("disabled")
                    mon.ClearStatus("confused")
                    mon.ClearStatus("asleep")
                    mon.ClearStatus("frozen")
                    mon.ClearStatus("infatuated")
                    mon.ResetStatChanges()
                user.ApplyStatus(".liberating")
            elif (name == "Mirror Coat"):
                countercount = user.GetStatusCount(".mirrorcoat")
                if (countercount == None or isinstance(countercount, int) or len(countercount) != 2 or countercount[1] not in Battlers()):
                    doDamage = False
                    user.ClearStatus(".mirrorcoat")
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
                else:
                    target = countercount[1]
                    fixeddamage = math.floor(countercount[0] * 2)
                user.ClearStatus(".mirrorcoat")
            elif (name == "Sweet Scent"):
                posttext += target.ChangeStats(Stats.Evasion, -2, user)
            elif (name in ["Night Shade", "Seismic Toss"]):
                fixeddamage = user.GetLevel()
            elif (name == "Uproar"):
                targets = GetTargets(user, range = Range.AdjacentFoe)
                if (targets == []):
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
                else:
                    target = random.choice(targets)
                    if (user.HasStatus("uproaring")):
                        posttext += "{} continues the Uproar!".format(username)
                    else:
                        posttext += "{} started an Uproar!".format(username)
                        user.ApplyStatus("uproaring", 3)
                        for mon in Battlers():
                            clearstatus = mon.ClearStatus("asleep")
                            posttext += ("" if clearstatus == None else clearstatus)
            elif (name == "Bulldoze"):
                sideeffects.append(SideEffect(user, target, Stats.Speed, -1))
            elif (name == "Metal Claw"):
                sideeffects.append(SideEffect(user, user, Stats.Attack, 1, 0.1))
            elif (name == "Charge Beam"):
                sideeffects.append(SideEffect(user, user, Stats.SpecialAttack, 1, 0.7))
            elif (name == "Fiery Dance"):
                sideeffects.append(SideEffect(user, user, Stats.SpecialAttack, 1, 0.5))
            elif (name == "Steel Wing"):
                if ("Steel Wing" in moveboosts):
                    power = 90
                    randomval = random.random()
                    sideeffects.append(SideEffect(user, user, Stats.Defense, 1, 0.3, randomval=randomval))
                    sideeffects.append(SideEffect(user, user, Stats.SpecialDefense, 1, 0.3, randomval=randomval))
                else:
                    sideeffects.append(SideEffect(user, user, Stats.Defense, 1, 0.1))
            elif (name == "Refresh"):
                user.ClearStatus("burned")
                user.ClearStatus("badly poisoned")
                user.ClearStatus("poisoned")
                user.ClearStatus("paralyzed")
                posttext += "{} became refreshed!".format(username)
            elif (name == "Clear Mind"):
                target.ClearStatus("burned")
                target.ClearStatus("badly poisoned")
                target.ClearStatus("poisoned")
                target.ClearStatus("paralyzed")
                target.ClearStatus("asleep")
                target.ClearStatus("frozen")
                target.ClearStatus("confused")
                target.ClearStatus("perishing")
                target.ClearStatus("infatuated")
                target.ResetStatChanges()
                posttext += "{}'s mind was cleared!".format(target.GetNickname())
            elif (name == "Electro Ball"):
                percent = target.GetStat(Stats.Speed) / user.GetStat(Stats.Speed)
                if (percent > 1):
                    power = 40
                elif (percent > .5):
                    power = 60
                elif (percent > .3333):
                    power = 80
                elif (percent > .25):
                    power = 120
                else:
                    power = 150
            elif (name == "Mist"):
                posttext += ApplyEffect(user, "mist", 5, False)
            elif (name == "Clear Smog"):
                target.ResetStatChanges()
            elif (name == "Haze"):
                for mon in Battlers():
                    mon.ResetStatChanges()
            elif (name == "Sludge Wave"):
                sideeffects.append(SideEffect(user, target, "poisoned", chance=0.1))
            elif (name in ["Poison Tail", "Cross Poison"]):
                critstage += 1
                sideeffects.append(SideEffect(user, target, "poisoned", chance=0.1))
                if (name == "Poison Tail" and name in moveboosts):
                    power = 65
                    if (target.HasType("Normal")):
                        power *= 2
                    if ("toxic spikes" in GetFieldEffects(target).keys()):
                        if (GetFieldEffects(target)["toxic spikes"] == 1):
                            del GetFieldEffects(target)["toxic spikes"]
                            posttext += ApplyEffect(user, "toxic spikes", 2, True)
                    else:
                        posttext += ApplyEffect(user, "toxic spikes", 1, True)
            elif (name == "Teleport"):
                usertrainer = user.GetTrainer()
                newlist = []
                for mon in usertrainer.GetTeam():
                    if (mon.Health >= 1 and mon not in Battlers()):
                        newlist.append(mon)
                if (len(newlist) == 0):
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
                elif (user in FriendlyBattlers()):
                    renpy.say(None, "Pick a Pokémon to switch in.")
                    switchCommand = renpy.call_screen('switch', user.GetTrainer(), True)
                    newPokemon = user.GetTrainer().GetTeam()[switchCommand]
                    if (newPokemon.GetHealth() == 0):
                        renpy.say(None, "{} has fainted, and cannot fight!".format(newPokemon.GetNickname()))
                        DoMove(action, user, move, [user])
                        return
                    elif (newPokemon in Battlers()):
                        renpy.show_screen("battleui")
                        renpy.say(None, "{} is already in battle!".format(newPokemon.GetNickname()))
                        DoMove(action, user, move, [user])
                        return
                    team = usertrainer.GetTeam()
                    usertrainer.ShiftTeam(team.index(user), switchCommand, True)
                    posttext += "{} teleported out, and {} switched in!".format(user.GetNickname(), newPokemon.GetNickname())
                    SwitchInEffects(newPokemon)
                else:
                    newPokemon = random.choice(newlist)
                    team = usertrainer.GetTeam()
                    usertrainer.ShiftTeam(team.index(user), team.index(newPokemon), True)
                    posttext += "{} teleported out, and {} switched in!".format(user.GetNickname(), newPokemon.GetNickname())
                    SwitchInEffects(newPokemon)
            elif (name in ["U-turn", "Flip Turn", "Parting Shot"]):
                usertrainer = user.GetTrainer()
                newlist = []
                for mon in usertrainer.GetTeam():
                    if (mon.Health >= 1 and mon not in Battlers()):
                        newlist.append(mon)
                if (len(newlist) != 0):
                    if (name == "Parting Shot"):
                        posttext += target.ChangeStats(Stats.Attack, -1, user)
                        posttext += target.ChangeStats(Stats.SpecialAttack, -1, user)
                    renpy.say(None, "Pick a Pokémon to switch in.")
                    switchCommand = renpy.call_screen('switch', user.GetTrainer(), True)
                    newPokemon = user.GetTrainer().GetTeam()[switchCommand]
                    if (newPokemon.GetHealth() == 0):
                        renpy.say(None, "{} has fainted, and cannot fight!".format(newPokemon.GetNickname()))
                        DoMove(action, user, move, [user])
                        return
                    elif (newPokemon in Battlers()):
                        renpy.show_screen("battleui")
                        renpy.say(None, "{} is already in battle!".format(newPokemon.GetNickname()))
                        DoMove(action, user, move, [user])
                        return
                    team = usertrainer.GetTeam()
                    usertrainer.ShiftTeam(team.index(user), switchCommand, True)
                    posttext += "{} switched out, and {} switched in!".format(user.GetNickname(), newPokemon.GetNickname())
                    SwitchInEffects(newPokemon)
            elif (name == "Curse"):
                if (not user.HasType("Ghost")):
                    posttext += user.ChangeStats(Stats.Attack, 1, user)
                    posttext += user.ChangeStats(Stats.Defense, 1, user)
                    posttext += user.ChangeStats(Stats.Speed, -1, user)
                else:
                    targets = GetTargets(user, Range.Any, True)
                    if (targets == []):
                        posttext += "But it failed!"
                        action.ChangeSuccess(False)
                    else:
                        target = random.choice(targets)
                        user.AdjustHealth(-user.GetStat(Stats.Health) * 0.5)
                        posttext += target.ApplyStatus("cursed")
            elif (name == "Screech"):
                posttext += target.ChangeStats(Stats.Defense, -2, user)
            elif (name == "Eerie Impulse"):
                posttext += target.ChangeStats(Stats.SpecialAttack, -2, user)
            elif (name in ["Charm", "Feather Dance"]):
                posttext += target.ChangeStats(Stats.Attack, -2, user)
            elif (name == "Scary Face"):
                posttext += target.ChangeStats(Stats.Speed, -2, user)
            elif (name in ["Metal Sound", "Fake Tears"]):
                posttext += target.ChangeStats(Stats.SpecialDefense, -2, user)
            elif (name == "Amnesia"):
                posttext += user.ChangeStats(Stats.SpecialDefense, 2, user)
            elif (name == "Acid Spray"):
                sideeffects.append(SideEffect(user, target, Stats.SpecialDefense, -2))
            elif (name in ["Iron Defense", "Acid Armor"]):
                posttext += user.ChangeStats(Stats.Defense, 2)
            elif (name in ["Barrier", "Cotton Guard"]):
                posttext += user.ChangeStats(Stats.Defense, 3)
            elif (name == "Torment"):
                posttext += target.ApplyStatus("tormented")
            elif (name == "Lucky Chant"):
                posttext += ApplyEffect(user, "lucky", 5, False)
            elif (name in ["Struggle Bug", "Spirit Break"]):
                sideeffects.append(SideEffect(user, target, Stats.SpecialAttack, -1))
            elif (name == "Helping Hand"):
                if (len(GetBattlers(user)) == 1):
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
                else:
                    helpcount = target.GetStatusCount("helped")                
                    posttext += target.ApplyStatus("helped", helpcount + 1, user, True)
            elif (name == "Yawn"):
                posttext += target.ApplyStatus("drowsy", 2)
            elif (name in ["Rest", "Chrysalize"]):
                user.ApplyStatus("asleep", 3, user, True)
                if (user.HasStatus("asleep") and user.GetHealthPercentage() < 1.0):
                    user.ClearStatus("everything", True)
                    posttext += user.ApplyStatus("asleep", 3, user)
                    user.AdjustHealth(999)
                    if (name == "Chrysalize"):
                        posttext += user.ChangeStats(Stats.Defense, 1, user)
                        posttext += user.ChangeStats(Stats.SpecialDefense, 1, user)
                else:
                    user.ClearStatus("asleep")
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Facade"):
                for affliction in normalstatuses:
                    if (user.HasStatus(affliction)):
                        power = move.Power * 2
            elif (name in ["Agility", "Rock Polish"]):
                posttext += user.ChangeStats(Stats.Speed, 2, user)
            elif (name == "Autotomize"):
                posttext += user.ChangeStats(Stats.Speed, 2, user)
                posttext += user.ApplyStatus("nimble", user.GetStatusCount("nimble") + 1, user, overwrite=True)
            elif (name == "Wing It"):
                posttext += username + " is flying free!"
                user.ApplyStatus(".moody", 1, user)
            elif (name == "Heal Pulse"):
                if (target.GetHealthPercentage() < 1):
                    target.AdjustHealth(target.GetStat(Stats.Health) / 2.0)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Floral Healing"):
                if (target.GetHealthPercentage() < 1 and not target.HasStatus("substitute")):
                    if (BattlefieldExists("Grassy Terrain")):
                        target.AdjustHealth(target.GetStat(Stats.Health) / 3.0 * 2.0)
                    else:
                        target.AdjustHealth(target.GetStat(Stats.Health) / 2.0)
                    if ("Floral Healing" in moveboosts):
                        if (BattlefieldExists("Grassy Terrain")):
                            user.AdjustHealth(target.GetStat(Stats.Health) / 3.0 * 2.0)
                        else:
                            user.AdjustHealth(target.GetStat(Stats.Health) / 2.0)
                        target.ClearStatus("burned")
                        target.ClearStatus("badly poisoned")
                        target.ClearStatus("poisoned")
                        target.ClearStatus("paralyzed")
                        target.ClearStatus("asleep")
                        target.ClearStatus("frozen")
                        user.ClearStatus("burned")
                        user.ClearStatus("badly poisoned")
                        user.ClearStatus("poisoned")
                        user.ClearStatus("paralyzed")
                        user.ClearStatus("asleep")
                        user.ClearStatus("frozen")
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Light Screen"):
                posttext += ApplyEffect(user, "light screen", 5, False)
            elif (name == "Reflect"):
                posttext += ApplyEffect(user, "reflect", 5, False)
            elif (name == "Aurora Veil"):
                if (WeatherIs("hail") or WeatherIs("snowy")):
                    posttext += ApplyEffect(user, "aurora veil", 5, False)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Trick-or-Treat"):
                if (not target.HasType("Ghost")):
                    target.ClearStatus("forest curse")
                    posttext += target.ApplyStatus("trick-or-treating")
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Forest's Curse"):
                if (not target.HasType("Grass")):
                    target.ClearStatus("trick-or-treating")
                    posttext += target.ApplyStatus("forest curse")
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Metallize"):
                posttext += target.ApplyStatus("metallic")
            elif (name == "Nuzzle"):
                sideeffects.append(SideEffect(user, target, "paralyzed"))
            elif (name == "Flame Burst"):
                targetpos = GetBattlers(target).index(target)
                for i, mon in enumerate(GetBattlers(target)):
                    if (abs(i - targetpos) == 1):
                        mon.AdjustHealth(-mon.GetStat(Stats.Health) / 16.0)
            elif (name == "Camouflage"):
                user.ApplyStatus("camouflaged", GetCamoType())
            elif (name == "Gyro Ball"):
                power = min(150, 25 * target.GetStat(Stats.Speed, triggerAbilities = False) / max(1, user.GetStat(Stats.Speed, triggerAbilities = False)) + 1)
            elif (name == "Wake-Up Slap"):
                if (not target.HasStatus("substitute")):
                    if (target.HasStatus("asleep")):
                        power = move.Power * 2.0
                        target.ClearStatus("asleep")
            elif (name == "Smelling Salts"):
                if (not target.HasStatus("substitute")):
                    if (target.HasStatus("paralyzed")):
                        power = move.Power * 2.0
                        target.ClearStatus("paralyzed")
            elif (name == "Hex"):
                if (target.HasStatus("asleep") or target.HasStatus("burned") or target.HasStatus("frozen") or target.HasStatus("poisoned") or target.HasStatus("badly poisoned")):
                    power = move.Power * 2.0
            elif (name == "Worry Seed"):
                posttext += target.ApplyStatus("worried", 1, user)
            elif (name in ["Ancient Power", "Silver Wind", "Ominous Wind"]):
                rand = random.random()
                sideeffects.append(SideEffect(user, user, Stats.Attack, 1, 0.1, rand))
                sideeffects.append(SideEffect(user, user, Stats.Defense, 1, 0.1, rand))
                sideeffects.append(SideEffect(user, user, Stats.SpecialAttack, 1, 0.1, rand))
                sideeffects.append(SideEffect(user, user, Stats.SpecialDefense, 1, 0.1, rand))
                sideeffects.append(SideEffect(user, user, Stats.Speed, 1, 0.1, rand))
            elif (name == "Tailwind"):
                ApplyEffect(user, "tailwind", 4, False)
            elif (name in ["Synthesis", "Moonlight", "Morning Sun"]):
                if (CurrentWeather == None):
                    user.AdjustHealth(user.GetStat(Stats.Health) / 2.0)
                elif (WeatherIs("sunny")):
                    user.AdjustHealth(user.GetStat(Stats.Health) * 2.0 / 3.0)
                else:
                    user.AdjustHealth(user.GetStat(Stats.Health) / 4.0)
            elif (name == "Shore Up"):
                if (WeatherIs("sandstorm")):
                    user.AdjustHealth(user.GetStat(Stats.Health) * 2.0 / 3.0)
                else:
                    user.AdjustHealth(user.GetStat(Stats.Health) / 2.0)
            elif (name == "Fire Fang"):
                sideeffects.append(SideEffect(user, target, "flinching", 1, 0.1))
                sideeffects.append(SideEffect(user, target, "burned", 1, 0.1))
            elif (name == "Thunder Fang"):
                sideeffects.append(SideEffect(user, target, "flinching", 1, 0.1))
                sideeffects.append(SideEffect(user, target, "paralyzed", 1, 0.1))
            elif (name == "Ice Fang"):
                sideeffects.append(SideEffect(user, target, "flinching", 1, 0.1))
                sideeffects.append(SideEffect(user, target, "frozen", 1, 0.1))
            elif (name == "Blizzard"):
                sideeffects.append(SideEffect(user, target, "frozen", 1, 0.1))
            elif (name == "Poison Fang"):
                sideeffects.append(SideEffect(user, target, "badly poisoned", 1, 0.5))
            elif (name == "Fire Punch"):
                sideeffects.append(SideEffect(user, target, "burned", 1, 0.1))
            elif (name == "Ice Punch"):
                sideeffects.append(SideEffect(user, target, "frozen", 1, 0.1))
            elif (name == "Thunder Punch"):
                sideeffects.append(SideEffect(user, target, "paralyzed", 1, 0.1))
            elif (name == "Thunder"):
                sideeffects.append(SideEffect(user, target, "paralyzed", 1, 0.3))
            elif (name == "Toxic"):
                posttext += target.ApplyStatus("badly poisoned", 1, user)
            elif (name == "Bad Breath"):
                haspoisonalready = target.HasStatus("badly poisoned")
                hasparalysisalready = target.HasStatus("paralyzed")
                finaltext = ""
                finaltext = target.ApplyStatus("badly poisoned", 1, user)
                if (not target.HasStatus("badly poisoned") or haspoisonalready or hasparalysisalready):
                    finaltext = target.ApplyStatus("paralyzed", 1, user)
                    if (not target.HasStatus("paralyzed") or hasparalysisalready):
                        finaltext = target.ApplyStatus("confused", random.randint(2, 5), user)
                posttext += finaltext
            elif (name == "Safeguard"):
                ApplyEffect(user, "safeguard", 5, False)
            elif (name == "Stealth Rock"):
                ApplyEffect(user, "stealthy rocks", 1, True)
            elif (name == "Endeavor"):
                if (target.GetHealth() > user.GetHealth()):
                    fixeddamage = target.GetHealth() - user.GetHealth()
            elif (name == "Force Palm"):
                sideeffects.append(SideEffect(user, target, "paralyzed", 1, .3))
            elif (name == "Hidden Power"):
                type = typeints[math.ceil(user.GetPersonality() * 17)]
            elif (name == "Aqua Ring"):
                user.ApplyStatus("aqua ring")
            elif (name == "Assurance"):
                if (target.GetDamagedThisTurn()):
                    power = move.Power * 2.0
            elif (name == "Dig"):
                if (not user.HasStatus("dug in")):
                    doDamage = False
                    user.ApplyStatus("dug in", 2, overwrite=True)
                else:
                    subtractpp = False
                    user.ClearStatus("dug in")
            elif (name in ["Fly", "Bounce"]):
                if (not user.HasStatus("airborne")):
                    doDamage = False
                    user.ApplyStatus("airborne", 2, overwrite=True)
                else:
                    subtractpp = False
                    user.ClearStatus("airborne")
            elif (name == "Dive"):
                if (not (user.HasStatus("gulping") or user.HasStatus("gorging")) and user.HasAbility("Gulp Missile")):
                    if (user.GetHealthPercentage() > 0.5):
                        posttext += user.ApplyStatus("gulping")
                    else:
                        posttext += user.ApplyStatus("gorging")
                if (not user.HasStatus("diving")):
                    doDamage = False
                    user.ApplyStatus("diving", 2, overwrite=True)
                else:
                    subtractpp = False
                    user.ClearStatus("diving")
            elif (name == "Phantom Force"):
                if (not user.HasStatus("ethereal")):
                    doDamage = False
                    user.ApplyStatus("ethereal", 2, overwrite=True)
                else:
                    subtractpp = False
                    user.ClearStatus("ethereal")
            elif (name == "Surf"):
                if (not (user.HasStatus("gulping") or user.HasStatus("gorging")) and user.HasAbility("Gulp Missile")):
                    if (user.GetHealthPercentage() > 0.5):
                        posttext += user.ApplyStatus("gulping")
                    else:
                        posttext += user.ApplyStatus("gorging")
            elif (name == "Work Up"):
                posttext += user.ChangeStats(Stats.Attack, 1)
                posttext += user.ChangeStats(Stats.SpecialAttack, 1)
            elif (name == "Calm Mind"):
                posttext += user.ChangeStats(Stats.SpecialAttack, 1)
                posttext += user.ChangeStats(Stats.SpecialDefense, 1)
            elif (name == "Bulk Up"):
                posttext += user.ChangeStats(Stats.Attack, 1)
                posttext += user.ChangeStats(Stats.Defense, 1)
            elif (name == "Coil"):
                posttext += user.ChangeStats(Stats.Attack, 1)
                posttext += user.ChangeStats(Stats.Defense, 1)
                posttext += user.ChangeStats(Stats.Accuracy, 1)
            elif (name == "Cosmic Power"):
                posttext += user.ChangeStats(Stats.Defense, 1)
                posttext += user.ChangeStats(Stats.SpecialDefense, 1)
            elif (name == "Stockpile"):
                posttext += user.ChangeStats(Stats.Defense, 1)
                posttext += user.ChangeStats(Stats.SpecialDefense, 1)
                user.ApplyStatus("stockpiled", min(user.GetStatusCount("stockpiled") + 1, 3), overwrite=True)
            elif (name == "Spit Up"):
                stockcount = user.GetStatusCount("stockpiled")
                if (stockcount != 0):
                    power = stockcount * 100
                    posttext += user.ChangeStats(Stats.Defense, -stockcount)
                    posttext += user.ChangeStats(Stats.SpecialDefense, -stockcount)
                    user.ClearStatus("stockpiled")
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Swallow"):
                stockcount = user.GetStatusCount("stockpiled")
                if (stockcount != 0):
                    if (stockcount == 1):
                        user.AdjustHealth(target.GetStat(Stats.Health) / 4.0)
                    elif (stockcount == 2):
                        user.AdjustHealth(target.GetStat(Stats.Health) / 2.0)
                    elif (stockcount == 3):
                        user.AdjustHealth(target.GetStat(Stats.Health))
                    posttext += user.ChangeStats(Stats.Defense, -stockcount)
                    posttext += user.ChangeStats(Stats.SpecialDefense, -stockcount)
                    user.ClearStatus("stockpiled")
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Dragon Dance"):
                posttext += user.ChangeStats(Stats.Attack, 1)
                posttext += user.ChangeStats(Stats.Speed, 1)
            elif (name == "Shift Gear"):
                posttext += user.ChangeStats(Stats.Attack, 1)
                posttext += user.ChangeStats(Stats.Speed, 2)
            elif (name == "Nasty Plot"):
                posttext += user.ChangeStats(Stats.SpecialAttack, 2)
            elif (name == "Venoshock"):
                if (target.HasStatus("poisoned") or target.HasStatus("badly poisoned")):
                    power = move.Power * 2.0
            elif (name in ["Low Kick", "Grass Knot"]):
                foeweight = target.GetWeight()
                if (foeweight < 10):
                    power = 20
                elif (foeweight < 25):
                    power = 40
                elif (foeweight < 50):
                    power = 60
                elif (foeweight < 100):
                    power = 80
                elif (foeweight < 200):
                    power = 100
                else:
                    power = 120
            elif (name == "Brine"):
                if (target.GetHealthPercentage() <= 0.5):
                    power = move.Power * 2.0
            elif (name == "Wish"):
                if (not EffectOnOwnField(user, "wishing star")):
                    ApplyEffect(user, "wishing star", [2, GetBattlers(user).index(user), user.GetStat(Stats.Health) / 2.0], False)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Mimic"):
                lastmove = GetLastMove(ActionLog, target)
                if (not user.HasStatus("mimicking") and lastmove != None):
                    user.ApplyStatus("mimicking", GetMove(lastmove.Name))
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Attract"):
                if (user.GetGender() == Genders.Male and target.GetGender() == Genders.Female or user.GetGender() == Genders.Female and target.GetGender() == Genders.Male):
                    posttext += target.ApplyStatus("infatuated", user, user)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Captivate"):
                if (user.GetGender() == Genders.Male and target.GetGender() == Genders.Female or user.GetGender() == Genders.Female and target.GetGender() == Genders.Male):
                    posttext += target.ChangeStats(Stats.SpecialAttack, -2, user)
            elif (name == "Ardent Gaze"):
                posttext += target.ApplyStatus("infatuated", user, user)
            elif (name == "Payback"):
                if (PaybackDoubles(user, target)):
                    power = move.Power * 2.0
            elif (name == "Round"):
                if (RoundDoubles(user)):
                    power = move.Power * 2.0
            elif (name == "Smack Down"):
                posttext += target.ApplyStatus("smacked down", 1, user)
            elif (name in ["Ingrain", "Bark Up"]):
                posttext += user.ApplyStatus("ingrained")
                if (name == "Bark Up"):
                    posttext += user.ChangeStats(Stats.Defense, 1)
                    posttext += user.ChangeStats(Stats.SpecialDefense, 1)
            elif (name == "Mean Look"):
                posttext += target.ApplyStatus("menaced", user, user)
            elif (name == "Block"):
                posttext += target.ApplyStatus("blocked", 1, user)
            elif (name == "Spider Web"):
                posttext += target.ApplyStatus("webbed", 1, user)
            elif (name == "Flower Shield"):
                for mon in Battlers(True):
                    if (mon.HasType("Grass")):
                        posttext += mon.ChangeStats(Stats.Defense, 1, user)
            elif (name == "Rototiller"):
                for mon in Battlers(True):
                    if (mon.HasType("Grass") and IsGrounded(mon)):
                        posttext += mon.ChangeStats(Stats.Attack, 1, user)
                        posttext += mon.ChangeStats(Stats.SpecialAttack, 1, user)
            elif (name == "Magnetic Flux"):
                for mon in Battlers(True):
                    if (mon.HasAbility("Plus", triggersplash = False) or mon.HasAbility("Minus", triggersplash = False)):
                        posttext += mon.ChangeStats(Stats.Defense, 1, user)
                        posttext += mon.ChangeStats(Stats.SpecialDefense, 1, user)
            elif (name in ["Milk Drink", "Recover", "Soft-Boiled", "Slack Off"]):
                user.AdjustHealth(target.GetStat(Stats.Health) / 2.0)
            elif (name == "Life Dew"):
                for mon in GetBattlers(user):
                    if (mon.HasAbility("Storm Drain")):#water absorb and dry skin have the same effect as Life Dew, in practice
                        posttext += mon.ChangeStats(Stats.SpecialAttack, 1, user)
                    else:
                        mon.AdjustHealth(mon.GetStat(Stats.Health) / 4.0)
            elif (name == "Roost"):
                user.AdjustHealth(target.GetStat(Stats.Health) / 2.0)
                user.ApplyStatus("roosted")
            elif (name == "Burial Ground"):
                posttext += ApplyBattlefieldEffects("Burial Ground", 5)
            elif (name == "Simple World"):
                posttext += ApplyBattlefieldEffects("Simple World", 5)
            elif (name == "Magnitude"):
                if (target.HasStatus("dug in")):
                    power *= 2
            elif (name == "Acupressure"):
                canraise = []
                for i in range(Stats.Attack, Stats.Evasion + 1):
                    statmod = target.GetStatChanges(i)
                    if (statmod != 6):
                        canraise.append(i)
                raising = None if len(canraise) == 0 else random.choice(canraise)
                if (raising != None):
                    posttext += target.ChangeStats(raising, 2, user)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Tearful Look"):
                posttext += target.ChangeStats(Stats.Attack, -1, user)
                posttext += target.ChangeStats(Stats.SpecialAttack, -1, user)
            elif (name in ["Explosion", "Self-Destruct"]):
                user.AdjustHealth(0, absolute=True)
            elif (name == "Pain Split"):
                newhealth = math.floor((user.GetHealth() + target.GetHealth()) / 2.0)
                user.AdjustHealth(newhealth, absolute=True)
                target.AdjustHealth(newhealth, absolute=True)
            elif (name in ["Power Trip", "Stored Power"]):
                power = 20 + user.GetTotalStatChanges() * 20
            elif (name == "Electrify"):
                posttext += target.ApplyStatus("electrified", 1, user)
            elif (name == "Ion Deluge"):
                for mon in Battlers():
                    mon.ApplyStatus("ionized", 1, user)
            elif (name == "Power Swap"):
                (userattackchange, userspattackchange) = user.GetStatChanges(Stats.Attack), user.GetStatChanges(Stats.SpecialAttack)
                (targetattackchange, targetspattackchange) = target.GetStatChanges(Stats.Attack), target.GetStatChanges(Stats.SpecialAttack)
                user.StatChanges[Stats.Attack], user.StatChanges[Stats.SpecialAttack] = targetattackchange, targetspattackchange
                target.StatChanges[Stats.Attack], target.StatChanges[Stats.SpecialAttack] = userattackchange, userspattackchange
            elif (name == "Guard Swap"):
                (userdefensechange, userspdefensechange) = user.GetStatChanges(Stats.Defense), user.GetStatChanges(Stats.SpecialDefense)
                (targetdefensechange, targetspdefensechange) = target.GetStatChanges(Stats.Defense), target.GetStatChanges(Stats.SpecialDefense)
                user.StatChanges[Stats.Defense], user.StatChanges[Stats.SpecialDefense] = targetdefensechange, targetspdefensechange
                target.StatChanges[Stats.Defense], target.StatChanges[Stats.SpecialDefense] = userdefensechange, userspdefensechange
            elif (name == "Embargo"):
                posttext += target.ApplyStatus("embargoed", 5, user)
            elif (name == "Weather Ball"):
                if (CurrentWeather != None):
                    power *= 2.0
                    if (WeatherIs("sunny")):
                        type = "Fire"
                    elif (WeatherIs("rainy")):
                        type = "Water"
                    elif (WeatherIs("sandstorm")):
                        type = "Rock"
                    elif (WeatherIs("hail")):
                        type = "Ice"
            elif (name in ["Brick Break", "Psychic Fangs"]):
                if (EffectOnOwnField(target, "reflect")):
                    del GetFieldEffects(target)["reflect"]
                if (EffectOnOwnField(target, "light screen")):
                    del GetFieldEffects(target)["light screen"]
                if (EffectOnOwnField(target, "aurora veil")):
                    del GetFieldEffects(target)["aurora veil"]
            elif (name == "Healing Wish"):
                ApplyEffect(user, "healing wish", GetBattlers(user).index(user), False)
                user.AdjustHealth(0, absolute=True)
            elif (name == "Future Sight"):
                if (alreadypretext != "The vision came true!"):
                    doDamage = False
                    ApplyEffect(target, "future sight", (Turn, GetBattlers(target).index(target), user), False)
            elif (name == "Laser Focus"):
                posttext += user.ApplyStatus("laser focused", 2, user)
            elif (name == "Mirror Move"):
                move.PP -= 1
                lastmove = GetLastMove(ActionLog, target=user, ignorepp=True)
                if (lastmove == None):
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
                else:
                    newtargets = [target]
                    if (GetMoveRange(lastmove) not in [Range.Adjacent, Range.AdjacentAlly, Range.AdjacentAllyOrSelf, Range.AdjacentFoe, Range.Any, Range.AnyOrSelf, Range.Self, Range.All]):
                        newtargets = GetTargets(user, GetMoveRange(lastmove))
                    DoMove(action, user, copy.deepcopy(lastmove), newtargets, alreadypretext=pretext + " {} mirrored {}! ".format(username, lastmove.Name))
                    return
            elif (name == "Destiny Bond"):
                if (dawnbattle):
                    posttext += "Your destiny diverges from Altaria, and cannot be bound!"
                else:
                    user.ApplyStatus("bound to destiny")
            elif (name == "Sky Attack"):
                if (not user.HasStatus("cloaked in light")):
                    doDamage = False
                    posttext += user.ApplyStatus("cloaked in light")
                else:
                    critstage += 1
                    sideeffects.append(SideEffect(user, target, "flinching", chance=0.3))
                    user.ClearStatus("cloaked in light")
            elif (name == "Solar Beam"):
                if (not (user.HasStatus("charging light") or WeatherIs("sunny"))):
                    doDamage = False
                    posttext += user.ApplyStatus("charging light")
                else:
                    user.ClearStatus("charging light")
            elif (name == "Skull Bash"):
                if (not (user.HasStatus("hardheaded"))):
                    doDamage = False
                    posttext += user.ChangeStats(Stats.Defense, 1, user)
                    posttext += user.ApplyStatus("hardheaded")
                else:
                    user.ClearStatus("hardheaded")
            elif (name == "Razor Wind"):
                if (not user.HasStatus("whipping up winds")):
                    doDamage = False
                    posttext += user.ApplyStatus("whipping up winds")
                else:
                    critstage += 1
                    user.ClearStatus("whipping up winds")
            elif (name == "Tri Attack"):
                ailment = "burned"
                randnum = random.random()
                if (randnum < 1.0/3.0):
                    ailment = "paralyzed"
                elif (randnum < 2.0 /3.0):
                    ailment = "frozen"
                sideeffects.append(SideEffect(user, target, ailment, chance=0.2))
            elif (name == "Earthquake"):
                if (target.HasStatus("dug in")):
                    power *= 2
            elif (name == "Surf"):
                if (target.HasStatus("diving")):
                    power *= 2
            elif (name == "Moonblast"):
                sideeffects.append(SideEffect(user, target, Stats.SpecialAttack, -2, chance=0.3))
            elif (name == "Magnet Rise"):
                user.ApplyStatus("levitating", count=5)
            elif (name == "Perish Song"):
                if (dawnbattle):
                    posttext += "The Altaria's angelic cry drowns out the Perish Song!"
                else:
                    for mon in Battlers():
                        mon.ApplyStatus("perishing", count=4, applier=user)
            elif (name == "Sucker Punch"):
                validmove = False
                for oppaction in CurrentActions[CurrentActions.index(action):]:
                    if (oppaction.GetActionType() == ActionTypes.Move and oppaction.GetUser() == target and oppaction.GetMove().Category in ["Physical", "Special"]):
                        validmove = True
                if (not validmove):
                    doDamage = False
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name in ["Water Spout", "Eruption"]):
                power = user.GetHealthPercentage() * 150.0 
            elif (name == "Petal Dance"):
                target = random.choice(GetTargets(user, Range.AdjacentFoe))
                if (not user.HasStatus("petal dancing")):
                    user.ApplyStatus("petal dancing", random.choice([3, 4]))
            elif (name == "Pollen Puff"):
                if (target in GetBattlers(user)):
                    doDamage = False
                    if (target.GetHealthPercentage() < 1):
                        target.AdjustHealth(target.GetStat(Stats.Health) / 2.0)
                    else:
                        posttext += "But it failed!"
                        action.ChangeSuccess(False)
            elif (name == "Aromatherapy"):
                if (mon in FriendlyBattlers()):
                    for trainer in FriendlyTrainers():
                        for target in trainer.GetTeam():
                            target.ClearStatus("burned")
                            target.ClearStatus("badly poisoned")
                            target.ClearStatus("poisoned")
                            target.ClearStatus("paralyzed")
                            target.ClearStatus("asleep")
                            target.ClearStatus("frozen")
                else:
                    for trainer in EnemyTrainers():
                        for target in trainer.GetTeam():
                            target.ClearStatus("burned")
                            target.ClearStatus("badly poisoned")
                            target.ClearStatus("poisoned")
                            target.ClearStatus("paralyzed")
                            target.ClearStatus("asleep")
                            target.ClearStatus("frozen")
            elif (name in ["Rock Wrecker", "Giga Impact", "Hyper Beam", "Frenzy Plant", "Hydro Cannon", "Blast Burn", "Roar of Time"]):
                user.ApplyStatus("recharging", 2)
            elif (name == "Frustration"):
                points = GetSocialPoints()
                power = min(1, (9999 - points) / 9999) * 102
            elif (name == "Return"):
                power = min(1, GetSocialPoints() / 9999) * 102
            elif (name == "Magic Coat"):
                posttext += user.ApplyStatus("coated in magic")
            elif (name == "Triple Kick"):
                global MultihitCount
                global MultihitMax
                repeat = True
                if (MultihitCount == None):
                    power = 10
                    MultihitCount = 2
                    MultihitMax = MultihitCount
                posttext += "Hit {} time(s)!".format(MultihitMax - MultihitCount + 1)
                if (MultihitCount != 0):
                    MultihitCount -= 1
                    power = 30 - MultihitCount * 10
                else:
                    repeat = False
                    MultihitMax = None
                    MultihitCount = None
            elif (name == "Power Trick"):
                posttext += user.ApplyStatus("power tricked")
            elif (name == "Memento"):
                posttext += target.ChangeStats(Stats.Attack, -2, user)
                posttext += target.ChangeStats(Stats.SpecialAttack, -2, user)
                user.AdjustHealth(0, absolute=True)
            elif (name == "Final Gambit"):
                fixeddamage = user.GetHealth()
                user.AdjustHealth(0, absolute=True)
            elif (name == "Substitute"):
                if (user.GetHealthPercentage() > 0.25 and not user.HasStatus("substitute")):
                    user.AdjustHealth(-user.GetStat(Stats.Health) / 4.0)
                    user.ApplyStatus("substitute", user.GetStat(Stats.Health) / 4.0, user)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Belly Drum"):
                if (user.GetHealthPercentage() > 0.5 and user.GetStatChanges(Stats.Attack) < 6):
                    user.AdjustHealth(-user.GetStat(Stats.Health) / 2.0)
                    posttext += user.ChangeStats(Stats.Attack, 99)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Fillet Away"):
                if (user.GetHealthPercentage() > 0.5 and (user.GetStatChanges(Stats.Attack) < 6 or user.GetStatChanges(Stats.SpecialAttack) < 6 or user.GetStatChanges(Stats.Speed) < 6)):
                    user.AdjustHealth(-user.GetStat(Stats.Health) / 2.0)
                    posttext += user.ChangeStats(Stats.Attack, 2)
                    posttext += user.ChangeStats(Stats.SpecialAttack, 2)
                    posttext += user.ChangeStats(Stats.Speed, 2)
                    if ("Fillet Away" in moveboosts):
                        user.ClearStatus("burned")
                        user.ClearStatus("badly poisoned")
                        user.ClearStatus("poisoned")
                        user.ClearStatus("paralyzed")
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "No Retreat"):
                if (CanSwitch(user, False)):
                    if ("No Retreat" in moveboosts):
                        for mon in GetBattlers(user):
                            mon.ChangeStats(Stats.Attack, 1)
                            mon.ChangeStats(Stats.Defense, 1)
                            mon.ChangeStats(Stats.SpecialAttack, 1)
                            mon.ChangeStats(Stats.SpecialDefense, 1)
                            mon.ChangeStats(Stats.Speed, 1)
                            mon.ApplyStatus("no retreat")
                        posttext += "{} leads the charge that will not retreat!".format(user.GetNickname())
                    else:
                        posttext += user.ChangeStats(Stats.Attack, 1)
                        posttext += user.ChangeStats(Stats.Defense, 1)
                        posttext += user.ChangeStats(Stats.SpecialAttack, 1)
                        posttext += user.ChangeStats(Stats.SpecialDefense, 1)
                        posttext += user.ChangeStats(Stats.Speed, 1)
                        user.ApplyStatus("no retreat")
                        posttext += "{} will not retreat!".format(user.GetNickname())
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Mind Reader"):
                posttext += target.ApplyStatus("mind read", 2, user)
                user.ApplyStatus(".mindreading", 2)
            elif (name == "Lock-On"):
                posttext += target.ApplyStatus("locked on", 2, user)
                user.ApplyStatus(".lockingon", 2)
            elif (name == "Retaliate"):
                avenging = False
                for mon in user.GetTrainer().GetTeam():
                    if (mon.GetFaintedTurn() in [Turn, Turn - 1]):
                        avenging  = True
                if (avenging):
                    power *= 2
                    posttext += "{} avenges the fallen!".format(username)
            elif (name == "Shell Smash"):
                posttext += user.ChangeStats(Stats.Attack, 2)
                posttext += user.ChangeStats(Stats.Defense, -1)
                posttext += user.ChangeStats(Stats.SpecialAttack, 2)
                posttext += user.ChangeStats(Stats.SpecialDefense, -1)
                posttext += user.ChangeStats(Stats.Speed, 2)
            elif (name in ["Follow Me", "Rage Powder"]):
                posttext += user.ApplyStatus("the standout")
            elif (name == "Secret Power"):
                if (GetCamoType() in ["Normal", "Electric"]):
                    sideeffects.append(SideEffect(user, target, "paralyzed", chance=0.3))
                elif (GetCamoType() in ["Rock", "Steel"]):
                    sideeffects.append(SideEffect(user, target, "flinching", chance=0.3))
                elif (GetCamoType() in ["Ground", "Dark"]):
                    sideeffects.append(SideEffect(user, target, Stats.Accuracy, -1, chance=0.3))
                elif (GetCamoType() in ["Water", "Fighting"]):
                    sideeffects.append(SideEffect(user, target, Stats.Attack, -1, chance=0.3))
                elif (GetCamoType() in ["Ice"]):
                    sideeffects.append(SideEffect(user, target, "freezing", chance=0.3))
                elif (GetCamoType() in ["Fire"]):
                    sideeffects.append(SideEffect(user, target, "burned", chance=0.3))
                elif (GetCamoType() in ["Ghost", "Dragon"]):
                    sideeffects.append(SideEffect(user, target, Stats.Defense, -1, chance=0.3))
                elif (GetCamoType() in ["Grass", "Bug"]):
                    sideeffects.append(SideEffect(user, target, "asleep", chance=0.3))
                elif (GetCamoType() in ["Fairy", "Poison"]):
                    sideeffects.append(SideEffect(user, target, Stats.SpecialAttack, -1, chance=0.3))
                elif (GetCamoType() in ["Psychic", "Flying"]):
                    sideeffects.append(SideEffect(user, target, Stats.Speed, -1, chance=0.3))
            elif (name == "Psych Up"):
                user.StatChanges = copy.copy(target.StatChanges)
                if (target.HasStatus("focused")):
                    posttext += user.ApplyStatus("focused")
            elif (name == "Entrained"):
                if (not (IsSpecialAbility(user.GetAbility()) or IsSpecialAbility(target.GetAbility()))):
                    target.ApplyStatus(".tracing", user.GetAbility(), user)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Skill Swap"):
                myability = user.GetAbility()
                theirability = target.GetAbility()
                if (not (IsSpecialAbility(myability) or IsSpecialAbility(theirability))):
                    user.ApplyStatus(".tracing", theirability, user)
                    target.ApplyStatus(".tracing", myability, user)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Metronome"):
                move.PP -= 1
                lastmove = GetMove(random.choice(movesin))
                while (lastmove.Name in ["Stone Cold Stunner", "Liberage", "ERROR"]):
                    lastmove = GetMove(random.choice(movesin))
                newtargets = GetTargets(user, GetMoveRange(lastmove), True)
                if (GetMoveRange(lastmove) in [Range.Adjacent, Range.AdjacentAlly, Range.AdjacentAllyOrSelf, Range.AdjacentFoe, Range.Any, Range.AnyOrSelf, Range.Self, Range.All]):
                    newtargets = [random.choice(newtargets)]
                DoMove(action, user, copy.deepcopy(lastmove), newtargets, alreadypretext=pretext)
                ActionLog.append(Action(0, user.GetStat(Stats.Speed), ActionTypes.Move, user.GetTrainer(), user, GetMove(lastmove.Name), GetTrainers(newtargets), newtargets, Turn))
                return
            elif (name == "Gastro Acid"):
                target.ApplyStatus(".tracing", "Suppressed", user)
            elif (name == "Defog"):
                posttext += target.ChangeStats(Stats.Evasion, -1, user)
                removeeffects = ["sticky web", "toxic spikes", "stealthy rocks", "spikes"]
                effectdel = []
                for cleareffect in FriendlyEffects.keys():
                    if (cleareffect in removeeffects):
                        effectdel.append(cleareffect)
                for clearingeffect in effectdel:
                    del FriendlyEffects[clearingeffect]
                if (len(effectdel) > 0):
                    posttext += "Cleared own field!"
                removeeffects += ["light screen", "reflect", "safeguard", "mist", "aurora veil"]
                effectdel = []
                for cleareffect in EnemyEffects.keys():
                    if (cleareffect in removeeffects):
                        effectdel.append(cleareffect)
                for clearingeffect in effectdel:
                    del EnemyEffects[clearingeffect]
                if (len(effectdel) > 0):
                    posttext += "Cleared foe's field!"
            elif (name == "Imprison"):
                user.ApplyStatus("imprisoning")
            elif (name == "Focus Punch"):
                if (user.GetDamagedThisTurn() == Turn):
                    doDamage = False
                    subtractpp = False
                    posttext += "{} lost its focus!".format(username)
            elif (name == "Beat Up"):
                global MultihitCount
                global MultihitMax
                repeat = True
                if (MultihitCount == None):
                    MultihitCount = len(user.GetTrainer().GetUnfaintedTeam()) - 1
                    MultihitMax = MultihitCount
                beatupper = user.GetTrainer().GetUnfaintedTeam()[MultihitCount]
                posttext += "{} joined the fray!".format(beatupper.GetNickname())
                power = beatupper.GetStat(Stats.Attack) / 10 + 5
                if (MultihitCount != 0):
                    MultihitCount -= 1
                else:
                    repeat = False
                    MultihitMax = None
                    MultihitCount = None
            elif (name == "Acrobatics"):
                if (user.GetItem() == None):
                    power *= 2
            elif (name == "Thrash"):
                if (target == None):
                    doDamage = False
                    action.ChangeSuccess(False)
                    posttext += "But it failed!"
                if (not user.HasStatus("thrashing")):
                    user.ApplyStatus("thrashing", random.randint(2, 3), user)
            elif (name == "Outrage"):
                if (target == None):
                    doDamage = False
                    action.ChangeSuccess(False)
                    posttext += "But it failed!"
                if (not user.HasStatus("outraged")):
                    user.ApplyStatus("outraged", random.randint(2, 3), user)
            elif (name == "Super Fang"):
                fixeddamage = math.floor(target.GetHealth() / 2.0)
            elif (name == "Anchor Shot"):
                posttext += target.ApplyStatus("anchored", user, user)
                if ("Anchor Shot" in moveboosts):
                    power = 90
                    sideeffects.append(SideEffect(user, target, Stats.Attack, -1))
                    sideeffects.append(SideEffect(user, target, Stats.Speed, -1))
            elif (name == "Spirit Shackle"):
                posttext += target.ApplyStatus("shackled", user, user)
            elif (name == "After You"):
                for newaction in CurrentActions:
                    if (newaction.GetUser() == target and newaction.GetActionType() == ActionTypes.Move):
                        newaction.SetPerformed()
                        DoMove(newaction, target, newaction.GetMove(), newaction.GetTargets(), alreadypretext=pretext)
                        return
                posttext += "But it failed!"
                action.ChangeSuccess(False)
            elif (name == "Baton Pass"):
                usertrainer = user.GetTrainer()
                newlist = []
                for mon in usertrainer.GetTeam():
                    if (mon.Health >= 1 and mon not in Battlers()):
                        newlist.append(mon)
                if (len(newlist) == 0):
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
                else:
                    statchanges = copy.copy(user.GetAllStatChanges())
                    statuslist = ["confused", "focused", ".mindreading", ".lockingon", ".tracing", "blocked", "webbed", "seeded", "cursed", "substitute", "ingrained", "power tricked", "heal blocked", "embargoed", "perishing", "levitating", "aqua ring"]
                    newstatus = {}
                    for status in user.GetStatusKeys():
                        newstatus[status] = user.Status[status]                      
                    renpy.say(None, "Pick a Pokémon to switch in.")
                    switchCommand = renpy.call_screen('switch', user.GetTrainer(), True)
                    newPokemon = user.GetTrainer().GetTeam()[switchCommand]
                    if (newPokemon.GetHealth() == 0):
                        renpy.say(None, "{} has fainted, and cannot fight!".format(newPokemon.GetNickname()))
                        DoMove(action, user, move, [user])
                        return
                    elif (newPokemon in Battlers()):
                        renpy.show_screen("battleui")
                        renpy.say(None, "{} is already in battle!".format(newPokemon.GetNickname()))
                        DoMove(action, user, move, [user])
                        return
                    team = usertrainer.GetTeam()
                    usertrainer.ShiftTeam(team.index(user), switchCommand, True)
                    posttext += "{} passed the baton to {}!".format(user.GetNickname(), newPokemon.GetNickname())
                    SwitchInEffects(newPokemon)
                    for status, count in newstatus.items():
                        newPokemon.ApplyStatus(status, count)
                    for statchange, count in statchanges.items():
                        newPokemon.ChangeStats(statchange, count)
            elif (name == "Shed Tail"):
                usertrainer = user.GetTrainer()
                newlist = []
                for mon in usertrainer.GetTeam():
                    if (mon.Health >= 1 and mon not in Battlers()):
                        newlist.append(mon)
                if (user.GetHealthPercentage() > 0.5 and not user.HasStatus("substitute") and len(newlist) > 0):
                    user.AdjustHealth(-user.GetStat(Stats.Health) / 2.0)
                    user.ApplyStatus("substitute", user.GetStat(Stats.Health) / 4.0, user)
                    statuscount = user.GetStatusCount("substitute")
                    renpy.say(None, "Pick a Pokémon to switch in.")
                    switchCommand = renpy.call_screen('switch', user.GetTrainer(), True)
                    newPokemon = user.GetTrainer().GetTeam()[switchCommand]
                    if (newPokemon.GetHealth() == 0):
                        renpy.say(None, "{} has fainted, and cannot fight!".format(newPokemon.GetNickname()))
                        DoMove(action, user, move, [user])
                        return
                    elif (newPokemon in Battlers()):
                        renpy.show_screen("battleui")
                        renpy.say(None, "{} is already in battle!".format(newPokemon.GetNickname()))
                        DoMove(action, user, move, [user])
                        return
                    team = usertrainer.GetTeam()
                    usertrainer.ShiftTeam(team.index(user), switchCommand, True)
                    posttext += "{} put up a substitute for {}!".format(user.GetNickname(), newPokemon.GetNickname())
                    SwitchInEffects(newPokemon)
                    newPokemon.ApplyStatus("substitute", statuscount)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Snatch"):
                user.ApplyStatus("snatching")
            elif (name == "Assist"):
                move.PP -= 1
                moveslist = []
                for othermon in user.GetTrainer().GetTeam():
                    if (othermon != user):
                        for move in othermon.GetMoveNames():
                            if (AssistCanCall(move)):
                                moveslist.append(GetMove(move))
                if (moveslist == []):
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
                else:
                    newmove = random.choice(moveslist)
                    pretext += "{} called {}!".format(user.GetNickname(), newmove.Name)
                    newtargets = GetTargets(user, GetMoveRange(newmove), True)
                    if (GetMoveRange(newmove) not in [Range.AllFoes, Range.AllAlliesAndSelf, Range.AllAllies, Range.AllAdjacentFoes, Range.AllAdjacent, Range.All]):
                        newtargets = [random.choice(newtargets)]
                    DoMove(action, user, newmove, newtargets, pretext, posttext, False)
                    ActionLog.append(Action(0, user.GetStat(Stats.Speed), ActionTypes.Move, user.GetTrainer(), user, GetMove(newmove.Name), GetTrainers(newtargets), newtargets, Turn))
                    return
            elif (name in ["Revenge", "Avalanche"]):
                if (user.GetDamagedThisTurn() == Turn):
                    power *= 2
            elif (name == "Punishment"):
                power = 60
                for statchange, value in target.GetAllStatChanges().items():
                    if (value > 0):
                        power += 20 * value
                power = min(200, power)
            elif (name == "Snore"):
                if (user.HasStatus("asleep")):
                    sideeffects.append(SideEffect(user, target, "flinching", chance=0.3))
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name in ["Bug Bite", "Pluck"]):
                if (IsBerry(target.GetItem()) and not target.HasAbility("Sticky Hold")):
                    posttext += target.TakeItem()
                    UseItem(user, False, True, True)
            elif (name == "Natural Gift"):
                if (IsBerry(user.GetItem())):
                    type, power = NaturalGiftData(user.GetItem())
                    user.MarkItemUsed()
                else:
                    doDamage = False
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Recycle"):
                if (user.GetItem() == None):
                    for itemaction, item, turn in reversed(user.GetItemHistory()):
                        if (itemaction == "Used"):
                            posttext += user.GiveItem(item)
                            break
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Knock Off"):
                if (not target.HasAbility("Sticky Hold")):
                    msg = target.TakeItem()
                    if ("lost its" in msg):
                        power *= 1.5
                        posttext += msg
            elif (name == "Bestow"):
                if (target.GetItem() == None and user.GetItem() != None and not target.HasStatus("substitute")):
                    ownitem = user.GetItem()
                    posttext += user.TakeItem()
                    posttext += target.GiveItem(ownitem)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Belch"):
                consumedberry = False
                for itemaction, item, turn in reversed(user.GetItemHistory()):
                    if (itemaction == "Used" and IsBerry(item)):
                        consumedberry = True
                        break
                if (not consumedberry):
                    doDamage = False
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Discard"):
                if (user.GetItem() != None):
                    posttext += "{} discarded its item!".format(username)
                    user.MarkItemUsed()
                    posttext += user.ChangeStats(Stats.Speed, 2)
                    posttext += user.ChangeStats(Stats.Evasion, 2)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Throat Chop"):
                sideeffects.append(SideEffect(user, target, "gasping", 3))
            elif (name == "Wring Out"):
                power = max(1, target.GetHealth() / target.GetStat(Health) * 120)
            elif (name == "Stomping Tantrum"):
                lastmove = GetLastMove(ActionLog, user, returnaction=True)
                if (lastmove != None):
                    if (not lastmove.GetSuccess()):
                        power *= 2.0
            elif (name == "Sleep Talk"):
                notallowed = ["Assist", "Belch", "Beak Blast", "Bide", "Bounce", "Copycat", "Dig", "Dive", "Dynamax Cannon", "Freeze Shock", "Fly", "Focus Punch", "Geomancy", "Ice Burn", "Me First", "Metronome", "Mirror Move", "Mimic", "Phantom Force", "Razor Wind", "Shadow Force", "Shell Trap", "Sketch", "Skull Bash", "Sky Attack", "Sky Drop", "Solar Blade", "Solar Beam", "Struggle", "Uproar"]

                possiblemoves = user.GetMoveNames()
                for notmove in notallowed:
                    if notmove in possiblemoves:
                        possiblemoves.remove(notmove)

                if (not user.HasStatus("sleeping") or possiblemoves == []):
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
                else:
                    newmove = GetMove(random.choice(possiblemoves))
                    pretext += "{} called {}!".format(user.GetNickname(), newmove.Name)
                    newtargets = GetTargets(user, GetMoveRange(newmove), True)
                    if (GetMoveRange(newmove) not in [Range.AllFoes, Range.AllAlliesAndSelf, Range.AllAllies, Range.AllAdjacentFoes, Range.AllAdjacent, Range.All]):
                        newtargets = [random.choice(newtargets)]
                    DoMove(action, user, newmove, newtargets, pretext, posttext, False)
                    ActionLog.append(Action(0, user.GetStat(Stats.Speed), ActionTypes.Move, user.GetTrainer(), user, GetMove(newmove.Name), GetTrainers(newtargets), newtargets, Turn))
                    return
            elif (name == "Grudge"):
                posttext += user.ApplyStatus("begrudging")
            elif (name == "Ally Switch"):
                usertrainer = user.GetTrainer()
                newlist = []
                if (user in FriendlyBattlers() and len(FriendlyBattlers()) > 1 or user in EnemyBattlers() and len(EnemyBattlers()) > 1):
                    if (user in FriendlyBattlers()):
                        for othermon in FriendlyBattlers():
                            if (othermon != user):
                                usertrainer.ShiftTeam(team.index(user), team.index(othermon), positionswitch=True)
                    else:
                        for othermon in EnemyBattlers():
                            if (othermon != user):
                                usertrainer.ShiftTeam(team.index(user), team.index(othermon), positionswitch=True)
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Role Play"):
                if (not IsSpecialAbility(user.GetAbility()) and not IsSpecialAbility(target.GetAbility())):
                    user.ApplyStatus(".tracing", target.GetAbility())
                    posttext += "{} copied the ability {}!".format(user.GetNickname(), target.GetAbility())
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)
            elif (name == "Frost Breath"):
                iscrit = True
            elif (name == "Salt Cure"):
                sideeffects.append(SideEffect(user, target, "salt cured"))
            elif (name in ["Heat Crash", "Heavy Slam"]):
                foeweight = target.GetWeight()
                selfweight = user.GetWeight()
                ratio = foeweight / selfweight
                if (ratio > 0.5):
                    power = 40
                elif (ratio > 0.3335):
                    power = 60
                elif (ratio > .2501):
                    power = 80
                elif (ratio > .2001):
                    power = 100
                else:
                    power = 120
            elif (name == "Stone Cold Stunner"):# the duuuuumbeeeeest thing Iiiiii've eveeeeer doooooone!~
                AutoLose = True
            elif (name == "Rage Fist"):
                if (user.GetId() == pokedexlookupname("Primeape", DexMacros.Id)):
                    if (user.GetStatusCount("annihilating") < 19):
                        user.ApplyStatus("annihilating", user.GetStatusCount("annihilating") + 1, overwrite=True)
                    else:
                        user.Evolve(pokedexlookupname("Annihilape", DexMacros.Id))
                power = min(7, user.TimesHit + 1) * 50
            elif (name == "Psycho Shift"):
                if (user.HasNormalStatus()):
                    target.ApplyStatus(user.GetNormalStatus(), user.GetStatusCount(user.GetNormalStatus()), user)
                    user.ClearStatus(user.GetNormalStatus())
                else:
                    posttext += "But it failed!"
                    action.ChangeSuccess(False)















            ###INSERT NEW MOVES HERE###############################################
            else:
                doDamage = True

            typebonus = GetTypeBonus(name, type, target, user)

            if (typebonus <= 1 and target.HasAbility("Wonder Guard")):
                typebonus = 0

            if (doDamage and math.floor(user.GetId()) == 334 and dawnbattle and len(FriendlyUnfainteds()) == 1):
                movesdodged.append(move.Name)

            if (doDamage and typebonus != 0):
                if (doDamage and not target.HasStatus("busted disguise") and target.HasAbility("Disguise")):
                    doDamage = False
                    target.AdjustHealth(-target.GetStat(Stats.Health) / 8.0)
                    target.ApplyStatus("busted disguise")
                    posttext += "{}'s disguise was busted!".format(target.GetNickname())

                if (len(sideeffects) > 0):
                    sheerforcebonus = True

                recklessbonus = recoil > 0 and user.HasAbility("Reckless")
                if (doDamage):
                    if (fixeddamage == -1):
                        if (user.HasStatus("laser focused")):
                            iscrit = True
                        if (not iscrit):
                            critodds = 0
                            if (user.HasAbility("Super Luck", False)):
                                critstage += 1
                            if (user.HasStatus("focused")):
                                critstage += 2
                            if (critstage == 0):
                                critodds = 1.0/24.0
                            elif (critstage == 1):
                                critodds = 1.0/8.0
                            elif (critstage == 2):
                                critodds = 1.0/2.0
                            elif (critstage >= 3):
                                critodds = 1.0

                            iscrit = random.random() <= critodds

                            if (iscrit and user.HasAbility("Super Luck")):
                                iscrit = True

                        if (iscrit and (target.HasAbility("Shell Armor") or target.HasAbility("Battle Armor"))):
                            iscrit = False

                        if (EffectOnOwnField(target, "lucky")):
                            iscrit = False

                    prehealth = target.GetHealthPercentage()
                    prehealthraw = target.GetHealth()

                    analyticbonus = False
                    if (action in CurrentActions and len(CurrentActions[CurrentActions.index(action):]) == 1):
                        analyticbonus = True
                    if (len(targets) > 1):
                        power *= .75

                    damage = DoDamage(user, move, target, type, iscrit, power, typebonus, fixeddamage, sheerforcebonus, recklessbonus, atebonus, analyticbonus, parentalbond, contact)
                    
                    if (damage > 0 and user.HasAbility("Stench")):
                        sideeffects.append(SideEffect(user, target, "flinching", chance=0.1))
                    if (iscrit):
                        pretext += "It's a critical hit on {}!".format(target.GetNickname())
                        if (target.HasAbility("Anger Point")):
                            pretext += target.ChangeStats(Stats.Attack, 6 - target.GetStatChanges(Stats.Attack), target)
                    if (typebonus > 1 and fixeddamage == -1):
                        PlaySound("supereffective.ogg")
                        pretext += "It's super effective on {}!".format(target.GetNickname())
                    elif (typebonus < 1 and typebonus > 0 and fixeddamage == -1):
                        PlaySound("notveryeffective.ogg")
                        pretext += "It's not very effective on {}...".format(target.GetNickname())
                    elif (typebonus == 1):
                        PlaySound("normaldamage.ogg")
                    if (target.HasStatus("raging") and damage != 0):
                        posttext += "{}'s rage grows!".format(target.GetNickname())
                        posttext += target.ChangeStats(Stats.Attack, 1, target)
                    if (target.HasStatus("biding") and damage != 0):
                        if (target.HasStatus(".bidingdamage")):
                            target.ApplyStatus(".bidingdamage", (target.GetStatusCount(".bidingdamage")[0] + damage, user), overwrite=True)
                        else:
                            target.ApplyStatus(".bidingdamage", (damage, user), overwrite=True)
                    if (healthgain > 0):
                        healthgain = math.ceil(damage * healthgain)
                        user.AdjustHealth(healthgain)
                        posttext += "{} recovered HP!".format(username)
                    if (recoil > 0 and (move.Name == "Struggle" or not user.HasAbility("Rock Head"))):
                        recoil = math.ceil(damage * recoil)
                        if (user.AdjustHealth(-recoil)):
                            posttext += "{} took recoil damage!".format(username)
                    if (target.HasStatus("frozen") and type == "Fire"):
                        posttext += target.ClearStatus("frozen")
                    if (contact and random.random() <= 0.3 and user.HasAbility("Poison Touch")):
                        posttext += target.ApplyStatus("poisoned", 1, user)
                    if (target.GetHealth() <= 0 and (target.HasStatus("enduring") or target.HasStatus("deathless") or (prehealth == 1.0 and target.HasAbility("Sturdy")))):
                        target.AdjustHealth(1, True)
                        if (target.HasStatus("deathless")):
                            target.AdjustHealth(target.GetStat(Stats.Health) / 2.0, True)
                        posttext += "{} endured!".format(target.GetNickname())
                    if (target.GetHealth() <= 0 and math.floor(user.GetId()) == 334 and user.GetLevel() == 68 and target.GetId() == 25 and len(movesdodged) < 5 and target.HasAbility("Freelectric")):
                        if (prehealthraw > 1):
                            target.AdjustHealth(1, True)
                            posttext += "{} toughed it out so you wouldn't feel sad!".format(target.GetNickname())
                        elif (prehealthraw == 1):
                            target.AdjustHealth(0.1, True)
                            posttext += "{} toughed it out and bared a grin!".format(target.GetNickname())
                        elif (prehealthraw == 0.1):
                            target.AdjustHealth(0.01, True)
                            posttext += "{} toughed it out and took a deep breath!".format(target.GetNickname())
                        elif (prehealthraw == 0.01):
                            target.AdjustHealth(0.001, True)
                            posttext += "{} toughed it out and challenges the king!".format(target.GetNickname())
                        elif (prehealthraw == 0.001):
                            target.AdjustHealth(0.001, True)
                            posttext += "{} toughed it out and will never fall!".format(target.GetNickname())
                    if (target.GetHealth() <= 0 and target.HasStatus(".liberating")):
                        target.AdjustHealth(1, True)
                        posttext += "{} is liberated!".format(target.GetNickname())
                    if (target.GetHealth() <= 0 and name in ["False Swipe", "Hold Back"]):
                        target.AdjustHealth(1, True)
                    if (move.Category == "Physical" and target.HasAbility("Weak Armor")):
                        posttext += target.ChangeStats(Stats.Defense, -1, target)
                        posttext += target.ChangeStats(Stats.Speed, 2, target)
                    if (contact and (user.GetGender() == Genders.Male and target.GetGender() == Genders.Female or user.GetGender() == Genders.Female and target.GetGender() == Genders.Male) and random.random() <= 0.3 and target.HasAbility("Cute Charm")):
                        posttext += user.ApplyStatus("infatuated", target, target)
                    if (contact and random.random() <= 0.3 and not (user.HasType("Grass") or user.HasItem("Safety Goggles")) and target.HasAbility("Effect Spore") and not user.HasAbility("Overcoat")):
                        newrand = random.random()
                        if (newrand <= 0.3):
                            user.ApplyStatus("poison", 1, target)
                        elif (newrand <= .6333):
                            user.ApplyStatus("paralyzed", 1, target)
                        else:
                            user.ApplyStatus("asleep", random.randint(2, 4), target)
                    if (contact and target.HasAbility("Iron Barbs")):
                        user.AdjustHealth(-user.GetStat(Stats.Health) / 8.0)
                        posttext += "{} was hurt by the {}!".format(username, target.GetAbility())
                    if (contact and target.HasAbility("Rough Skin")):
                        user.AdjustHealth(-user.GetStat(Stats.Health) / 8.0)
                        posttext += "{} was hurt by the {}!".format(username, target.GetAbility())
                    if ((target.HasStatus("gulping") or target.HasStatus("gorging")) and (target.HasAbility("Gulp Missile") or target.HasForeveral("Cramorant Foreveral"))):
                        user.AdjustHealth(-user.GetStat(Stats.Health) / 4.0)
                        if (target.HasStatus("gulping")):
                            posttext += user.ChangeStats(Stats.Defense, -1, target)
                            target.ClearStatus("gulping")
                        elif (target.HasStatus("gorging")):
                            posttext += user.ApplyStatus("paralyzed", 1, target)
                            target.ClearStatus("gorging")
                    if (name == "Fell Stinger" and target.GetHealthPercentage() <= 0):
                        posttext += user.ChangeStats(Stats.Attack, 3)
                    if (contact and target.GetHealth() == 0 and target.HasAbility("Aftermath") and not AbilityOnField("Damp")):
                        user.AdjustHealth(-user.GetStat(Stats.Health) / 4.0)
                        posttext += "{} was caught in the aftermath!".format(username)
                    if (target.GetHealth() == 0 and target.HasStatus("bound to destiny")):
                        posttext += "{} was bound to destiny!".format(username)
                        user.AdjustHealth(0, absolute=True)
                    if (contact and random.random() <= 0.3 and target.HasAbility("Flame Body")):
                        posttext += user.ApplyStatus("burned")
                    if (contact and random.random() <= 0.3 and target.HasAbility("Poison Point")):
                        posttext += user.ApplyStatus("poisoned")
                    if (contact and random.random() <= 0.3 and target.HasAbility("Static")):
                        posttext += user.ApplyStatus("paralyzed")
                    if (contact and target.HasAbility("Pickpocket")):
                        useritem = user.GetItem()
                        targetitem = target.GetItem()
                        if (useritem != None and targetitem == None and not user.HasAbility("Sticky Hold")):
                            posttext += user.TakeItem()
                            posttext += target.GiveItem(targetitem)
                    if (contact and target.HasItem("Sticky Barb")):
                        if (user.GetItem() == None):
                            posttext += user.GiveItem("Sticky Barb")
                    if (move.Category != "Status" and target.HasAbility("Cursed Body")):
                        posttext += user.ApplyStatus("disabled", 4, user)
                        user.ApplyStatus(".disabling", move.Name)
                    if (type == "Dark" and target.HasAbility("Justified")):
                        posttext += target.ChangeStats(Stats.Attack, 1)
                    if (type in ["Bug", "Dark", "Ghost"] and target.HasAbility("Rattled")):
                        posttext += target.ChangeStats(Stats.Speed, 1)
                    if (target.GetHealthPercentage() < 0.5 and target.HasAbility("Berserk")):
                        posttext += target.ChangeStats(Stats.SpecialAttack, 1)
                    if (target.GetHealthPercentage() == 0.0 and user.HasAbility("Moxie")):
                        posttext += user.ChangeStats(Stats.Attack, 1)
                    if (target.GetHealthPercentage() == 0.0 and target.HasStatus("grudging")):
                        move.PP = 0
                        posttext += "{} bore a grudge!".format(target)
                    if (target.HasStatus(".countering") and move.Category == "Physical"):
                        target.ApplyStatus(".countering", (max(1, math.floor(damage * 2.0)), user), overwrite=True)
                    if (target.HasStatus(".mirrorcoat") and move.Category == "Special"):
                        target.ApplyStatus(".mirrorcoat", (max(1, math.floor(damage * 2.0)), user), overwrite=True)
                    if (move.Category == "Physical" and target.HasAbility("Toxic Debris")):
                        if ("toxic spikes" in GetFieldEffects(user).keys()):
                            if (GetFieldEffects(user)["toxic spikes"] == 1):
                                del GetFieldEffects(user)["toxic spikes"]
                                posttext += ApplyEffect(user, "toxic spikes", 2, False)
                        else:
                            posttext += ApplyEffect(user, "toxic spikes", 1, False)
                    if (name in ["Dragon Tail", "Circle Throw"] and target.GetHealthPercentage() > 0):
                        targettrainer = target.GetTrainer()
                        newlist = []
                        for mon in targettrainer.GetTeam():
                            if (mon.Health >= 1 and mon != target and mon not in Battlers()):
                                newlist.append(mon)
                        if (len(newlist) != 0):
                            randpkmn = random.choice(newlist)
                            trainer = target.GetTrainer()
                            team = trainer.GetTeam()
                            trainer.ShiftTeam(team.index(target), team.index(randpkmn), True)
                            posttext += "{} was forced out!".format(randpkmn.GetNickname())
                            SwitchInEffects(randpkmn)
                    if (prehealth >= 0.5 and target.GetHealthPercentage() < 0.5 and target.GetHealth() > 0 and (target.HasAbility("Wimp Out") or target.HasAbility("Emergency Exit"))):
                        if (target.GetTrainer().GetType() != TrainerType.Enemy):
                            usertrainer = target.GetTrainer()
                            newlist = []
                            for mon in usertrainer.GetTeam():
                                if (mon.Health >= 1 and mon not in Battlers()):
                                    newlist.append(mon)
                            if (len(newlist) != 0):
                                newPokemon = FriendlyBattlers()[0]
                                while (newPokemon in Battlers() or newPokemon.GetHealth() == 0):
                                    renpy.say(None, "Pick a Pokémon to switch in.")
                                    switchCommand = renpy.call_screen('switch', usertrainer, True)
                                    if (switchCommand != "back"):
                                        newPokemon = usertrainer.GetTeam()[switchCommand]
                                        if (newPokemon.GetHealth() == 0):
                                            renpy.show_screen("battleui")
                                            renpy.say(None, "{} has fainted, and cannot fight!".format(newPokemon.GetNickname()))
                                        elif (newPokemon in Battlers()):
                                            renpy.show_screen("battleui")
                                            renpy.say(None, "{} is already in battle!".format(newPokemon.GetNickname()))
                                team = usertrainer.GetTeam()
                                usertrainer.ShiftTeam(team.index(target), switchCommand, True)
                                posttext += "{} retreated, and {} switched in!".format(target.GetNickname(), newPokemon.GetNickname())
                                SwitchInEffects(newPokemon)
                        else:                        
                            targettrainer = target.GetTrainer()
                            newlist = []
                            for mon in targettrainer.GetTeam():
                                if (mon.Health >= 1 and mon != target):
                                    newlist.append(mon)
                            if (len(newlist) != 0):
                                randpkmn = random.choice(newlist)
                                trainer = target.GetTrainer()
                                team = trainer.GetTeam()
                                trainer.ShiftTeam(team.index(target), team.index(randpkmn), True)
                                posttext += "{} retreated, and {} shifted in!".format(target.GetNickname(), randpkmn.GetNickname())
                                SwitchInEffects(randpkmn)
                    if (name == "Rapid Spin"):
                        removeeffects = ["sticky web", "toxic spikes", "stealthy rocks", "spikes"]
                        removestatus = ["wrapped", "bound", "clamped", "infested", "firespun", "whirlpooled", "seeded", "entombed", "ingrained", "anchored", "shackled"]
                        statusdel = []
                        effectdel = []
                        for clearstatus in user.GetStatusKeys():
                            if (clearstatus in removestatus):
                                statusdel.append(clearstatus)
                        for clearingstatus in statusdel:
                            user.ClearStatus(clearingstatus)

                        if (user in FriendlyBattlers()):
                            for cleareffect in FriendlyEffects.keys():
                                if (cleareffect in removeeffects):
                                    effectdel.append(cleareffect)
                            for clearingeffect in effectdel:
                                del FriendlyEffects[clearingeffect]
                        else:
                            for cleareffect in EnemyEffects.keys():
                                if (cleareffect in removeeffects):
                                    effectdel.append(cleareffect)
                            for clearingeffect in effectdel:
                                del EnemyEffects[clearingeffect]
                        if (len(statusdel) + len(effectdel)):
                            posttext += "Cleared entrapments!"

            elif (doDamage and typebonus == 0):
                pretext += "It had no effect on {}...".format(target.GetNickname())
                if (name in ["Jump Kick", "High Jump Kick"]):
                    user.AdjustHealth(-user.GetStat(Stats.Health) / 2.0)
                    posttext += "{} kept going and crashed!".format(username)

            if (doDamage and typebonus != 0):
                for sideeffect in sideeffects:
                    posttext += sideeffect.Apply()

        for posteffect in posteffects:
            posttext += posteffect.Apply()

        if (len(targets) == 1 and not repeating and not repeat and doDamage and not parentalbond and user.HasAbility("Parental Bond")):
            DoMove(action, user, move, targets, pretext + posttext, "", False, True)
            return

        clearimmediately = ["airborne", "dug in", "diving", "ethereal"]
        for status in clearimmediately:
            if (user.GetStatusCount(status) == 1):
                user.ClearStatus(status)

        if (user.HasStatus("thrashing") and not doDamage):
            user.ClearStatus("thrashing")
        if (user.HasStatus("outraged") and not doDamage):
            user.ClearStatus("outraged")

        for fvl in user.GetForeverals():
            if (lookupforeveraldata(fvl, FVLMacros.FVLType) == ForeveralTypes.Training):
                if (fvl == "Tyrogue Everal"):
                    if (IsPunchMove(name)):
                        user.EVs[2] = min(user.EVs[2] + 3, 255)
                        posttext += "{} trained his Defense by punching!".format(user.GetNickname())
                    elif ("Kick" in name):
                        user.EVs[1] = min(user.EVs[1] + 3, 255)
                        posttext += "{} trained his Attack by kicking!".format(user.GetNickname())
                elif (fvl == "Meditite Everal"):
                    pronouns = ("his" if user.GetGender() == Genders.Male else ("her" if user.GetGender() == Genders.Female else "its"))
                    if (type == "Fighting"):
                        user.EVs[1] = min(user.EVs[1] + 3, 255)
                        posttext += "{} trained {} Attack through physical power!".format(user.GetNickname(), pronouns)
                    elif (type == "Psychic"):
                        user.EVs[4] = min(user.EVs[4] + 3, 255)
                        posttext += "{} trained {} Special Defense through mental fortitude!".format(user.GetNickname(), pronouns)
                elif (fvl == "Marill Everal"):
                    pronouns = ("his" if user.GetGender() == Genders.Male else ("her" if user.GetGender() == Genders.Female else "its"))
                    if (move.Category == "Physical"):
                        user.EVs[1] = min(user.EVs[1] + 3, 255)
                        posttext += "{} trained {} Attack through physical power!".format(user.GetNickname(), pronouns)
                    elif (move.Category == "Special"):
                        user.EVs[4] = min(user.EVs[0] + 3, 255)
                        posttext += "{} trained {} HP through special power!".format(user.GetNickname(), pronouns)

        finaltext = FormatText(pretext + posttext + ItemText)
        fontsize = ""
        if (len(finaltext) > 230):
            fontsize = "{size=-8}"

        if (not invoketest):
            renpy.say(None, fontsize + finaltext)
        ItemText = ""

        if (repeat and target.GetHealth() > 0):
            DoMove(action, user, move, [target], "", "", repeat)
        elif (subtractpp):
            move.PP -= 1
            if (AbilityOnOpponentField(user, "Pressure")):
                move.PP -= 1
            if (move.PP <= 0):
                move.PP = 0

        UsingMove = False
        MoveUser = None
        ActiveMove = None

        if (invoketest):
            return (AllyPokemon(), BattlefieldEffects, EnemyPokemon())