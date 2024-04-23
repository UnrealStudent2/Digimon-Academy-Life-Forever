init python:
    def oldmandialog(attributes):
        if (Turn == 0):
            renpy.call_in_new_context("oldmandialog0")

label oldmandialog0:
    hide screen battle
    show screen battleui
    show red:
        xpos 0.1
    show oldman milotic:
        xpos 0.9
    with dis

    red @surprised "Wait, two Pokémon?"

    oldman @surprisedbrow happymouth "What, lad? Weren't you listenin'? This entire round will be double battles!"

    red @sweat happymouth closedbrow "Oops. I've been out of the region for a bit, so I guess I missed the part where they told us that."

    oldman @happybrow happymouth "Eheheh! Looks like I've got the upper hand here, then!"

    red @talkingmouth "Maybe, but I'm still confident in [pika_name]. C'mon, buddy! Let's do this!"

    $ renpy.music.play("Audio/Pokemon/pikachu_angry1.ogg", channel="altcry", loop=None)
    pikachu cocky_2b "Pika! Pika!"

    hide red 
    hide oldman
    show screen battle
    with dis
    return

init python:
    def dawndragonitedialog(attributes):
        if ("BeforeBattle" in attributes and Turn == 0):
            renpy.call_in_new_context("dawndragonitedialog0")
        elif ("PreStep" in attributes and Turn == 1):
            renpy.call_in_new_context("dawndragonitedialog1")
        elif ("AfterMove" in attributes and "Ally" in attributes and Turn == 1):
            renpy.call_in_new_context("dawndragonitedialog2")

label dawndragonitedialog0:
    hide screen battle
    show screen battleui
    show red sadbrow frownmouth:
        xpos 0.1
    show dawn sad:
        xpos 0.9
    with dis

    dawn @sad "So... you're using Lance's Dragonite..."

    red @sad "Look..."

    hide red 
    hide dawn
    show screen battle
    with dis
    return

label dawndragonitedialog1:
    hide screen battle
    show screen battleui
    show red sadbrow frownmouth:
        xpos 0.1
    show dawn sad:
        xpos 0.9
    with dis

    dawn @closedbrow frownmouth "I guess all you really cared about was power, after all."
    dawn @angrybrow sadmouth "Maybe you really are mind-controlling people, huh?"

    red @angry "No!"

    show dawnbreakstheicebg1 
    hide screen battleui
    with Dissolve(3.0)

    dawn angrybrow frownmouth "{w=0.5}.{w=0.5}.{w=0.5}."

    show dawnbreakstheicedawn with Dissolve(3.0)

    dawn "It doesn't matter."

    show dawnbreakstheiceblizzard with Dissolve(3.0)

    dawn "For my entire life, I've been living in a cage. It's cold, and harsh, and I've had to live in it alone. Too weak for a champion, and too powerful for everyone else."
    dawn "But when I tried to get away from all that, and just do my own thing, people said I was wasting my potential."

    pause 1.0

    dawn "Fine. Here's my potential--the {i}true{/i} potential of my partner and I!"

    show dawnbreakstheicedawnlight behind dawnbreakstheiceblizzard with dis

    narrator "Altaria's Altarianite is reacting to Dawn's Mega Chisel!"

    pause 1.0

    $ PlaySound("megaevo.mp3")

    show dawnbreakstheicebg2 behind dawnbreakstheicedawnlight
    show dawnbreakstheicealtarialight behind dawnbreakstheicedawnlight
    with dis

    dawn "Altaria! Break the chains of ice! Eliminate all restrictions, and show the dark of night a new dawn! Mega Evolution!"

    $ EnemyBattlers()[0].ChangeForme(334.1)
    $ EnemyBattlers()[0].ApplyStatus("mega evolved")

    dawn @angrybrow happymouth "Altaria, now's your time! We won't be taken down without a fight--Cotton Guard, now!"

    hide red 
    hide dawn
    hide dawnbreakstheicealtaria
    hide dawnbreakstheicealtarialight
    hide dawnbreakstheicebg1
    hide dawnbreakstheicebg2
    hide dawnbreakstheicedawn
    hide dawnbreakstheicedawnlight
    hide dawnbreakstheiceblizzard
    show screen battle
    with dis
    return

label dawndragonitedialog2:
    hide screen battle
    show screen battleui
    show red surprised:
        xpos 0.1
    show dawn angrybrow happymouth:
        xpos 0.9
    with dis

    red "Wait... that didn't K.O.?"

    dawn @angrybrow happymouth "It sure didn't! We've got them, Altaria! Just make sure that you don't get hit critically, and we've got this!"

    dawn @happy "Altaria, Altaria, you're the one! You've got power, you've got fun! You're the best, you're the star! We're gonna win--and we'll go far!"

    $ ApplyEffect(dawnaltariaobj, "lucky", 999, False)

    narrator "Dawn started a Lucky Chant!"

    redmind @confusedeyebrows playfuleyes frownmouth "That doesn't seem fair."

    hide red 
    hide dawn
    show screen battle
    with dis
    return

init python:
    def dawnpikachudialog(attributes):
        global allowfractions
        allowfractions = True
        if ("BeforeBattle" in attributes and Turn == 0 and "dawnpikachudialog0" not in dialogshown):
            renpy.call_in_new_context("dawnpikachudialog0")
            dialogshown.append("dawnpikachudialog0")
        elif ("AfterMove" in attributes and movesdodged == [] and "Enemy" in attributes and len(FriendlyUnfainteds()) == 1 and "dawnpikachudialog1" not in dialogshown):
            renpy.call_in_new_context("dawnpikachudialog1")
            dialogshown.append("dawnpikachudialog1")
        elif ("AfterMove" in attributes and len(movesdodged) == 1 and "Enemy" in attributes and len(FriendlyUnfainteds()) == 1 and "dawnpikachudialog2" not in dialogshown):
            renpy.call_in_new_context("dawnpikachudialog2")
            dialogshown.append("dawnpikachudialog2")
        elif ("PostTurn" in attributes and len(movesdodged) == 2 and len(FriendlyUnfainteds()) == 1 and "dawnpikachudialog3" not in dialogshown):
            renpy.call_in_new_context("dawnpikachudialog3")
            dialogshown.append("dawnpikachudialog3")
        elif ("PostTurn" in attributes and len(movesdodged) == 3 and len(FriendlyUnfainteds()) == 1 and "dawnpikachudialog4" not in dialogshown):
            renpy.call_in_new_context("dawnpikachudialog4")
            dialogshown.append("dawnpikachudialog4")
        elif ("PostTurn" in attributes and len(movesdodged) == 4 and len(FriendlyUnfainteds()) == 1 and "dawnpikachudialog5" not in dialogshown):
            renpy.call_in_new_context("dawnpikachudialog5")
            dialogshown.append("dawnpikachudialog5")
        elif ("AfterMove" in attributes and "Enemy" in attributes and len(movesdodged) ==  5 and len(FriendlyUnfainteds()) == 1 and "dawnpikachudialog7" not in dialogshown):
            renpy.call_in_new_context("dawnpikachudialog7")
            dialogshown.append("dawnpikachudialog7")
        elif ("PostTurn" in attributes and len(movesdodged) == 6 and len(FriendlyUnfainteds()) == 1 and "dawnpikachudialog8" not in dialogshown):
            renpy.call_in_new_context("dawnpikachudialog8")
            dialogshown.append("dawnpikachudialog8")
        elif ("PostTurn" in attributes and len(movesdodged) == 7 and len(FriendlyUnfainteds()) == 1 and "dawnpikachudialog9" not in dialogshown):
            renpy.call_in_new_context("dawnpikachudialog9")
            dialogshown.append("dawnpikachudialog9")
        elif ("PostTurn" in attributes and len(movesdodged) == 8 and len(FriendlyUnfainteds()) == 1 and "dawnpikachudialog10" not in dialogshown):
            renpy.call_in_new_context("dawnpikachudialog10")
            dialogshown.append("dawnpikachudialog10")
        elif ("AfterMove" in attributes and "Enemy" in attributes and len(movesdodged) == 9 and len(FriendlyUnfainteds()) == 1 and "dawnpikachudialog11" not in dialogshown):
            renpy.call_in_new_context("dawnpikachudialog11")
            dialogshown.append("dawnpikachudialog11")
        elif ("UseItem" in attributes and "Enemy" in attributes and "dawnpikachuitemdialog" not in dialogshown):
            renpy.call_in_new_context("dawnpikachuitemdialog")
            dialogshown.append("dawnpikachuitemdialog")

label dawnpikachuitemdialog:
    hide screen battle
    show screen battleui
    show red:
        xpos 0.1
    show dawn:
        xpos 0.9
    with dis

    red @confused "Dang, you have items...?"

    dawn @surprised "I can't believe I actually have to use them here...!"

    $ ValueChange("Dawn", 3, 0.9, False)

    dawn @happy "I'm really impressed, [first_name]. The only other time I had to use items was..."
    dawn @sadbrow happymouth "Well, I {i}lost{/i} that time."

    red @happy "Heh. I think those kinds of items are a bit out of my budget right now, though..."

    dawn @sadbrow happymouth "Well, um... maybe I should just let you know I have a {i}lot{/i} more..."

    red @sweat closedbrow talking2mouth "Noted."
    redmind @thinking "Mannn... Rich people, am I right?"

    hide red 
    hide dawn
    show screen battle
    with dis
    return

label dawnpikachudialog0:
    hide screen battle
    show screen battleui
    show red:
        xpos 0.1
    show dawn:
        xpos 0.9
    with dis

    dawn @happy "Thank you, [first_name]. I never thought I'd get to have another battle like this."

    red @happy "I can't even imagine what you've gone through, but I can tell you shouldn't have had to go through it. Giving you a fun battle is the least I can do."

    redmind @thinking "Admittedly, there's absolutely no way I'm going to win this, but... at least no-one's giving up. And not having to worry about who 'wins' or 'loses' is freeing."

    pause 1.0

    redmind @sweat closedbrow frownmouth "That being said. A level 68 Altaria? What's she even doing in this school? She could be battling Champions already..."

    hide red 
    hide dawn
    show screen battle
    with dis
    return

label dawnpikachudialog1:
    hide screen battle
    show screen battleui
    show red sadbrow:
        xpos 0.1
    show dawn sadbrow:
        xpos 0.9
    with dis

    dawn @talkingmouth "I guess... I guess this is it, then."

    red @talkingmouth "Eh, I wouldn't rule out [pika_name]. Not yet, anyway."

    dawn @sadbrow talkingmouth "It's nice that you believe in him, but... every odd is kinda stacked against you right now, isn't it?"

    red -sadbrow @happy "Not every odd. I still have [pika_name], and as long as I have him, I have all the odds I need."

    $ renpy.music.play("Audio/Pokemon/pikachu_angry1.ogg", channel="altcry", loop=None)
    pikachu cocky_2b "Pika! Pika!"

    pause 1.0

    dawn @talkingmouth "I... I remember what that was like... to believe so absolutely, and so truly, in my partners, in my friends..."

    pause 1.0

    dawn @sadbrow happymouth "Thank you."

    dawn angry "Altaria, finish this. Dragon Pulse."

    hide red 
    hide dawn
    show screen battle
    with dis
    return

label dawnpikachudialog2:
    hide screen battle
    show screen battleui
    show red surprised:
        xpos 0.1
    show dawn surprised:
        xpos 0.9
    with dis

    dawn "Um...? What was that?"

    red @confused "Beats me. [pika_name]?"

    $ renpy.music.play("Audio/Pokemon/pikachu_angry1.ogg", channel="altcry", loop=None)
    pikachu cocky_2b "Pika! Pika!"

    narrator "{glitch=5.00}...Something's stirring. The whisper of liberation echoes again...{/glitch}"

    hide red 
    hide dawn
    show screen battle
    with dis
    return

label dawnpikachudialog3:
    hide screen battle
    show screen battleui
    show red surprised:
        xpos 0.1
    show dawn surprised:
        xpos 0.9
    with dis

    dawn "Why... {i}how{/i} is your Pikachu still holding on?"

    red @happy "I've got no idea, but let's press this advantage!"

    $ renpy.music.play("Audio/Pokemon/pikachu_angry2.ogg", channel="altcry", loop=None)
    pikachu cocky_2b "Ka... Pikachu!"

    narrator "{glitch=10.00}...Something's approaching. The murmur of liberation gets louder still.{/glitch}"

    hide red 
    hide dawn
    show screen battle
    with dis
    return

label dawnpikachudialog4:
    hide screen battle
    show screen battleui
    show red:
        xpos 0.1
    show dawn surprised:
        xpos 0.9
    with dis

    dawn "Whaaaat is happening?"

    red @happy "A Pokémon battle? This is a real battle, Dawn! Stuff happens, and no-one knows why! When was the last time you were surprised?"

    $ renpy.music.play("Audio/Pokemon/pikachu_angry2.ogg", channel="altcry", loop=None)
    pikachu cocky_2b "Ka... Pikapi!"

    narrator "{glitch=15.00}It's getting closer! The shout of liberation is heard clearly!{/glitch}"

    hide red 
    hide dawn
    show screen battle
    with dis
    return

label dawnpikachudialog5:
    hide screen battle
    show screen battleui
    show red happy:
        xpos 0.1
    show dawn closedbrow frownmouth:
        xpos 0.9
    with dis

    dawn @talkingmouth "I've never seen anything like this before--is this what Cynthia was trying to show me?"

    red @surprised "You've talked to Cynthia?"

    dawn @angrybrow happymouth "I {i}battled{/i} Cynthia! And a Pokémon that battled Cynthia can more than handle a tiny Pikachu! Altaria, use your most powerful Dragon Pulse!"

    $ renpy.music.play("Audio/Pokemon/pikachu_angry3.ogg", channel="altcry", loop=None)
    pikachu cocky_2b "Pikaaaaaaaachu!"

    narrator "{glitch=20.00}It's right nearby! It's gusting hard! The scream of liberation will never be silenced!{/glitch}"

    narrator "{glitch=20.00}A new option has appeared to you...{/glitch}"

    hide red 
    hide dawn
    show screen battle
    with dis
    return

label dawnpikachudialog6:
    $ renpy.music.set_volume(0.0, 5.0)
    hide blank2
    hide screen battleui
    hide screen battle
    show blank2
    show sugimoripikachu:
        xpos 200  
        yanchor 1.0 
        ypos 1.0 
        xzoom -1.0
        pause 5.0
        ease 3.0 xpos 960 xanchor 0.5 yalign 0.5
        pause 2.0
        alpha 0.0
    with Dissolve(5.0)

    pause 3.0

    python:
        pikachuobj.Id = 25.2
        pikachuobj.Nature = Natures.Brave
        pikachuobj.RecalculateStats()
        pikachuobj.Health = pikachuobj.GetStat(Stats.Health)
        renpy.music.queue("audio/music/evolution_cut.mp3", channel="evolution")
        renpy.call_screen("evolution", 25, 25.2, True)
        renpy.music.stop(channel="evolution")
        PlaySound("Get.ogg")
        renpy.music.set_volume(1.0, 3.0)

    play music "audio/music/theme.mp3" fadein 7.0

    hide sugimoripikachu
    hide blank2
    hide screen battleui
    show screen battleui
    with dis

    pause 2.0

    label pickbanner:

    narrator "The banner of liberation flies again!"

    narrator "What color will your banner be?"

    $ renpy.call_screen("liberize")

    if (len(libtypes) == 0):
        narrator "You must pick a banner to fly! Liberation has no room for bystanders!"

        jump pickbanner

    $ types = libtypes[0]
    if (len(libtypes) == 2):
        $ types = libtypes[0] + "/" + libtypes[1]

    narrator "Do you want to raise up the banner of the [types]-type?"

    menu:
        "Let me fight for another cause.":
            jump pickbanner

        "Raise it high!":
            pass

    narrator "It is so."

    pause 1.0

    show red surprised:
        xpos 0.1
    show dawn surprised:
        xpos 0.9
    with dis

    dawn "What the heck is that?! Is that some kind of Pikachu evolution I've never heard of?"

    red "I have no idea... buddy, are you good?"

    $ renpy.music.play("Audio/Pokemon/pikachu_angry3.ogg", channel="altcry", loop=None)

    libpikachu glowing @angryeyes happymouth sparks "Pik... Pika. Pikerachu!"

    red -surprised @happy "Looks like he's still firing on all cylinders!"

    red @talkingmouth "Well, Dawn?"

    dawn @angrybrow happymouth "I-- I have {i}no{/i} idea what's happening! Altaria, another Dragon Pulse!"

    redmind @thinking "...I think I might know why she didn't win against Cynthia. She's kind of a one-track-minded battler, huh?"

    $ renpy.music.play("Audio/Pokemon/pikachu_scared.ogg", channel="altcry", loop=None)

    libpikachu @angry2eyes surprisedmouth "Pik... Pika. Pikerachu!"

    redmind @thinking "He's being brave, but... that's still my [pika_name]. I can tell that he's worried about getting hit again."
    redmind @angrybrow frownmouth "I don't understand this power, but if I want to have any chance of winning, [bluecolor]I need to think about what Dawn is likely to do, and Liberize accordingly.{/color}"
    redmind @closedbrow frownmouth "[bluecolor]Right now, she's planning on using a {i}Dragon Pulse{/i}...{/color}"

    hide red
    hide dawn
    with dis

    return

label dawnpikachudialog7:
    hide screen battle
    show screen battleui
    show red happy:
        xpos 0.1
    show dawn angrybrow happymouth:
        xpos 0.9
    with dis

    dawn @talkingmouth "Pretty sneaky of you, [first_name]! Is this some kind of crazy Terastalization power?"

    red @winkeyes talkingmouth "You wouldn't believe me if I told you what it was."

    pause 1.0

    dawn @surprisedbrow sadmouth "Wait, you have no idea what this is, do you?"

    red @happy "Hah, hah! You caught me! Nope!"

    dawn @happy "Well, that was a clever trick, absorbing my Dragon-type move with your Fairy-type transformation! But can you take an Earthquake?"

    hide red 
    hide dawn
    show screen battle
    with dis
    return

label dawnpikachudialog8:
    hide screen battle
    show screen battleui
    show red happy:
        xpos 0.1
    show dawn happy:
        xpos 0.9
    with dis

    dawn "Oh, you dodged that too... well, how about we show him this next move, Altaria? Maybe we can turn their bad luck into some good luck for us..."

    dawn @angrybrow happymouth "Altaria, use Ominous Wind!"

    red @angrybrow happymouth "[pika_name], we're not out yet!"

    hide red 
    hide dawn
    show screen battle
    with dis
    return

label dawnpikachudialog9:
    hide screen battle
    show screen battleui
    show red happy:
        xpos 0.1
    show dawn happy:
        xpos 0.9
    with dis

    dawn "Hah! Guess you figured that one out, then... well, we're not going to give up yet! We'll make our voices be heard!"

    dawn @angrybrow happymouth "Altaria, Hyper Voice!"

    hide red 
    hide dawn
    show screen battle
    with dis
    return

label dawnpikachudialog10:
    hide screen battle
    show screen battleui
    show red happy:
        xpos 0.1
    show dawn happy:
        xpos 0.9
    with dis

    red @happy "Hm... correct me if I'm wrong, but that's four moves, right? Unless Janine taught you how to use a fifth move, I'm pretty sure that means you can't hit me."
    
    red @sweat talking2mouth "Of course... nothing's immune to the Fairy-type..."

    red @angrybrow happymouth "So does this mean I've finally earned the right to see your Mega Altaria?"

    dawn -happy @sadbrow happymouth "...[first_name], this has been the most fun I've ever had in a battle."

    red -happy @happy "I'm glad. I didn't expect any of {i}this{/i} would happen--but as long as you come out of this happy, then... hey, I'd call that a win."

    show dawnbreakstheicebg1 
    hide screen battleui
    with Dissolve(3.0)

    show dawnbreakstheicedawn with Dissolve(3.0)

    dawn "[first_name]... there's something I want you to understand."

    show dawnbreakstheiceblizzard with Dissolve(3.0)

    dawn "For my entire life, I've been living in a cage. It's cold, and harsh, and I've had to live in it alone. I was too weak to be a champion, but too powerful for everyone else."
    dawn "But when I tried to get away from all that, and just do my own thing, people said I was wasting my potential."

    pause 1.0

    dawn "But you... just now... you saw me for more than my potential. You saw me for who I am. Right now. In this moment."
    dawn "And that... unlike {i}anything{/i} else... made me want to show you my potential."
    dawn "So here's my potential, [first_name]. My true power. The {i}true{/i} potential of my partner and I!"

    show dawnbreakstheicedawnlight behind dawnbreakstheiceblizzard with dis

    narrator "Altaria's Altarianite is reacting to Dawn's Mega Chisel!"

    pause 1.0

    $ PlaySound("megaevo.mp3")

    show dawnbreakstheicebg2 behind dawnbreakstheicedawnlight
    show dawnbreakstheicealtarialight behind dawnbreakstheicedawnlight
    with dis

    dawn "Altaria! Break the chains of ice! Eliminate all restrictions, and show the dark of night a new dawn! Mega Evolution!"

    $ EnemyBattlers()[0].ChangeForme(334.1)
    $ EnemyBattlers()[0].ApplyStatus("mega evolved")

    dawn angrybrow talking2mouth "Altaria, now's your time! Sing the ultimate song--use your true, full-power Hyper Voice!"

    red angrybrow talking2mouth "[pika_name]! I believe in you! I 100%% know you can win this! So attack, with everything you've got!"

    $ PlaySound("finalsmash.mp3")

    libpikachu @angry2eyes happymouth sparks "Pikera.... CHUUUUUU!"

    $ pikachuobj.LearnNewMove([(1, "Liberage")])

    hide dawnbreakstheicealtaria
    hide dawnbreakstheicealtarialight
    hide dawnbreakstheicebg1
    hide dawnbreakstheicebg2
    hide dawnbreakstheicedawn
    hide dawnbreakstheicedawnlight
    hide dawnbreakstheiceblizzard
    show screen battle
    with dis
    return

label dawnpikachudialog11:
    $ renpy.music.set_volume(0.0, 5.0)
    hide blank2
    hide screen battleui
    show blank2
    show liberationpikachu:
        xpos 200  
        yanchor 1.0 
        ypos 1.0 
        xzoom -1.0
        pause 2.0
        ease 2.0 ypos 0.7
    show liberationpikachutail:
        xpos 200  
        yanchor 1.0 
        ypos 1.0 
        xzoom -1.0
        matrixcolor TintMatrix(GetLiberaColor())
        pause 2.0
        ease 2.0 ypos 0.7
    show liberationpikachucollar:
        xpos 200  
        yanchor 1.0 
        ypos 1.0 
        xzoom -1.0
        matrixcolor TintMatrix(GetLiberaColor(False))
        pause 2.0
        ease 2.0 ypos 0.7
    show megaaltaria:
        xpos 1720
        xanchor 1.0  
        yanchor 1.0 
        ypos 1.0
        pause 2.0
        ease 2.0 ypos 0.7
    with Dissolve(5.0)

    pause 3.0

    show liberationpikachu:
        ease 3.0 xpos 100
        ease 0.3 xpos 960

    show liberationpikachutail:
        ease 3.0 xpos 100
        ease 0.3 xpos 960

    show liberationpikachucollar:
        ease 3.0 xpos 100
        ease 0.3 xpos 960

    show megaaltaria:
        ease 3.0 xpos 1820
        ease 0.3 xpos 960

    stop music fadeout 1.5

    pause 3.0

    show blank with spinfaderapid

    pause 3.0

    lisia @surprised "{cps=*0.3}It's... {/cps}{cps=*0.2}it's...!"
    lisia @surprised "{cps=*0.05}It's a d{w=1.0}{nw}"

    $ EnemyBattlers()[0].Health = 0
    show screen battleui
    hide blank
    hide blank2
    hide liberationpikachu
    hide liberationpikachucollar
    hide liberationpikachutail
    hide megaaltaria

    extend @happy "{/cps}efeat for Dawn!"

    lisia @surprised "Surprising absolutely everybody, [first_name] [last_name] is the winner!"

    return

init python:
    def possessedwilldialog(attributes):
        currentscene = None
        if (Turn == 1):
            currentscene = "possessedwilldialog0"
        elif (Turn == 2):
            currentscene = "possessedwilldialog1"
        elif (Turn == 3):
            currentscene = "possessedwilldialog2"

        if (currentscene != None and currentscene not in seencutscenes):
            seencutscenes.append(currentscene)
            renpy.call_in_new_context(currentscene)

label possessedwilldialog0:
    hide screen battle
    show screen battleui
    with dis

    will @poweredangrybrow angrymouth "{font=fonts/alien.ttf}We ... ... ...\n... are ... danger\n... ... ... ... ...{/font}"

    show screen battle
    with dis
    return

label possessedwilldialog1:
    hide screen battle
    show screen battleui
    with dis

    will @poweredangrybrow angrymouth "{font=fonts/alien.ttf}We ... ... great treasure within ...\n... ... coming ... us\n... will take ... treasure{/font}"

    show screen battle
    with dis
    return

label possessedwilldialog2:
    hide screen battle
    show screen battleui
    with dis

    will @poweredangrybrow angrymouth "{font=fonts/alien.ttf}Beware\n... us\n... ... man ... ... ...!{/font}"

    show screen battle
    with dis
    return

init python:
    def possessedsabrinadialog(attributes):
        currentscene = None
        if (Turn == 1):
            currentscene = "possessedsabrinadialog0"
        elif (Turn == 2):
            currentscene = "possessedsabrinadialog1"
        elif (Turn == 3):
            currentscene = "possessedsabrinadialog2"

        if (currentscene != None and currentscene not in seencutscenes):
            seencutscenes.append(currentscene)
            renpy.call_in_new_context(currentscene)

label possessedsabrinadialog0:
    if (timeOfDay == "Night"):
        hide screen battle
        show screen battleui
        show sabrina casualoldhair poweredbrow at night
        with dis
    else:
        hide screen battle
        show screen battleui
        show sabrina casualoldhair poweredbrow
        with dis

    sabrina @angrymouth "{font=fonts/alien.ttf}We come ... ...\n... ... ... ...\n... ... ... for ...{/font}"

    show screen battle
    hide sabrina
    with dis
    return

label possessedsabrinadialog1:
    if (timeOfDay == "Night"):
        hide screen battle
        show screen battleui
        show sabrina casualoldhair poweredbrow at night
        with dis
    else:
        hide screen battle
        show screen battleui
        show sabrina casualoldhair poweredbrow
        with dis

    sabrina @angrymouth "{font=fonts/alien.ttf}... ... a great treasure ... us\n... ... coming for ...\n... ... ... our treasure{/font}"

    show screen battle
    hide sabrina
    with dis
    return

label possessedsabrinadialog2:
    if (timeOfDay == "Night"):
        hide screen battle
        show screen battleui
        show sabrina casualoldhair poweredbrow at night
        with dis
    else:
        hide screen battle
        show screen battleui
        show sabrina casualoldhair poweredbrow
        with dis

    sabrina @angrymouth "{font=fonts/alien.ttf}Beware\n... ...\nBeware ... man clad ... ...{/font}"

    show screen battle
    hide sabrina
    with dis
    return

init python:
    def possessedtiadialog(attributes):
        currentscene = None
        if (len(EnemyBattlers()) == 1 and EnemyBattlers()[0].Id == 380 and len(EnemyTrainers()[0].GetUnfaintedTeam()) == 1):
            currentscene = "possessedtiadialog0"

        if (currentscene != None and currentscene not in seencutscenes):
            seencutscenes.append(currentscene)
            renpy.call_in_new_context(currentscene)

label possessedtiadialog0:
    hide screen battle
    show screen battleui
    with dis

    narrator "Tia is out of useable Pokémon... Tia blacked out!"

    $ EnemyBattlers()[0].Health = 0

    show screen battle
    with dis
    return

init python:
    def deoxysdialog(attributes):
        currentscene = None
        if (len(EnemyBattlers()) == 0):
            currentscene = "deoxysabort"
        elif (Turn == 1):
            currentscene = "deoxysdialog0"
        elif (Turn == 2):
            currentscene = "deoxysdialog1"
        elif (Turn == 3):
            currentscene = "deoxysdialog2"
        elif (Turn == 4):
            currentscene = "deoxysdialog3"
        elif (Turn == 5):
            currentscene = "deoxysdialog4"

        if (currentscene != None and currentscene not in seencutscenes):
            seencutscenes.append(currentscene)
            renpy.call_in_new_context(currentscene)

label deoxysdialog0:
    hide screen battle
    show screen battleui
    show nate angrybrow frownmouth 
    with dis

    nate @talking2mouth "Keep this thing occupied! Don't let it get to [pika_name]!"

    blue @surprised "What am I, his damn guardian?"

    nate @talking2mouth "AZOTH1 has the ability to absorb and assimilate genetic material! We can't let it get access to that special Pikachu's power!"

    blue @angry "Psh! That rat only {i}got{/i} its power by taking it from Azoth in the first place! To me, it looks like Azoth is just taking back what [first_name] stole!"

    nate @talking2mouth "Look, just don't let it get past you!"

    blue @angrybrow happymouth "Easy! I'll put this thing in the ground, {i}again!{/i}"

    show nate:
        xpos 0.5
        ease 0.5 xpos 0.33

    show yellow sad with dis:
        xpos 0.66

    yellow @talkingmouth "W-wait! Don't hurt them!"

    nate @angry "Right now, we should be more worried about {i}it{/i} hurting {i}us{/i}!"

    hide nate
    hide yellow
    show screen battle
    with dis
    return

label deoxysdialog1:
    hide screen battle
    show screen battleui
    show nate angrybrow frownmouth 
    with dis

    nate @talking2mouth "Keep holding on! I'm locking onto it now!"

    if (len(FriendlyUnfainteds()) == 5):
        blue @desperateeyes scaredmouth "Hey, hey! This thing just one-shot my Pokémon! How much longer do you need me to hold on?"

    else:
        blue @happy "Hey, what do you take me for? I've got this in the bag!"

    hide nate
    show screen battle
    with dis
    return

label deoxysdialog2:
    hide screen battle
    show screen battleui
    show nate angrybrow frownmouth 
    with dis

    nate @talking2mouth "Almost done charging. Get ready!"

    blue @angrybrow talkingmouth "...Right. But... hey, this isn't going to hurt it, will it?"

    nate @surprised "Is that seriously your priority, right now?"

    if (len(FriendlyUnfainteds()) == 5):
        nate @surprised "It's torn through one of your Pokémon already!"
    elif (len(FriendlyUnfainteds()) == 4):
        nate @surprised "It's torn through two of your Pokémon already!"
    elif (len(FriendlyUnfainteds()) == 3):
        nate @surprised "It's torn through three of your Pokémon already!"
    elif (len(FriendlyUnfainteds()) == 2):
        nate @surprised "It's torn through four of your Pokémon already!"
    else:
        blue @talkingmouth "It's not like I'm taking any damage here! I mean, I'm not sure this thing is even all that strong!"

    hide nate
    show screen battle
    with dis
    return

label deoxysdialog3:
    hide screen battle
    show screen battleui
    show nate angrybrow frownmouth 
    with dis

    nate @talking2mouth "Okay, I'm done charging! Get out of the way!"

    blue @sad2eyes wistfulmouth "I'm not sure this is the only way, Nate! I mean, we've got Yellow, who can tell what Pokémon are feeling, and we've got [first_name], who Pokémon just {i}listen{/i} to."
    blue @surprisedbrow talkingmouth "Can't we try something else?"

    nate @angrymouth "Not until it calms down! And right now, it's in a frenzied state--it won't listen to us!"

    blue @angry "Rrrghhh... hold off. Just one more round, alright?"

    hide nate
    show screen battle
    with dis
    return

label deoxysdialog4:
    hide screen battle
    show screen battleui
    with dis

    blue @angry "Hey, you two! Are you getting anything from it?"

    show yellow sad:
        xpos 0.66

    show red frownmouth:
        xpos 0.33

    red @talking2mouth "It's completely shutting me out."

    yellow @talkingmouth "It won't listen to me. It's just mindlessly attacking, now..."

    nate @talking2mouth "That's enough, Blue! If you don't move out of the way, you're going to be hurt by my attack!"

    blue @talkingmouth "...Wait, okay? Just wait."

    $ Fled = True

    hide nate
    show screen battle
    with dis
    return

label deoxysabort:
    hide screen battle
    show screen battleui
    with dis

    $ EnemyBattlers()[0].Health = 1

    blue @closedbrow talking2mouth "Look, it's calmed down. Let's try talking things through."

    $ Fled = True
    return