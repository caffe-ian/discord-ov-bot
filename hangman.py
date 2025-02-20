roles = [
    "easter bunny",
    "accomplice",
    "sect member",
    "fortune teller",
    "werewolf",
    "santa claus",
    "doctor",
    "bodyguard",
    'vigilante',
    'jailer',
    'red lady',
    'priest',
    'seer',
    'aura seer',
    'detective',
    'medium',
    'mayor',
    'witch',
    'beast hunter',
    'loudmouth',
    'flower child',
    'cupid',
    'cursed',
    'junior werewolf',
    'nightmare werewolf',
    'wolf shaman',
    'shadow wolf',
    'guardian wolf',
    'alpha werewolf',
    'wolf seer',
    'fool',
    'headhunter',
    'serial killer',
    'arsonist',
    'corruptor',
    'bandit',
    'night watchman',
    'tough guy',
    'flagger',
    'gunner',
    'warden',
    'ghost lady',
    'marksman',
    'analyst',
    'gambler',
    'spirit seer',
    'mortician',
    'seer apprentice',
    'violinist',
    'sheriff',
    'ritualist',
    'baker',
    'preacher',
    'astronomer',
    'forger',
    'avenger',
    'trapper',
    'pacifist',
    'grumpy grandma',
    'instigator',
    'werewolf fan',
    'grave robber',
    'voodoo werewolf',
    'kitten wolf',
    'wolf pacifist',
    'jelly wolf',
    'werewolf berserk',
    'wolf summoner',
    'stubborn werewolf',
    'split wolf',
    'wolf trickster',
    'sorcerer',
    'bomber',
    'cannibal',
    'illusionist',
    'sect leader',
    'zombie',
    'alchemist',
    'evil detective',
    'villager',
    'president',
    'regular werewolf',
    'santa',
    'pumpkin king'
    ]

while True:
    matches = []

    char = input()
    char2 = None
    if len(char.split(" ")) > 1:
        char2 = int(char.split(" ")[1])
        char = int(char.split(" ")[0])
    else:
        char = int(char)

    for role in roles:
        if char2 is None:
            if len(role.split(" ")) == 1 and len(role) == char:
                matches.append(role)
        elif char2 is not None:
            if len(role.split(" ")[0]) == char and len(role.split(" ")) > 1 and len(role.split(" ")[1]) == char2:
                matches.append(role)
                
    occurrence = {}
    similar = []
    for letter in set("".join(matches).replace(' ', '')):
        if all(letter in match for match in matches):
            similar.append(letter)
        else:
            occurrence[letter] = "".join(matches).count(letter)

    suggestion = sorted(list(occurrence.keys()), key=lambda x: occurrence[x], reverse=True)

    print(f"Matches: {', '.join(matches)}\nSimilar: {', '.join(similar)}\nSuggested: {', '.join(suggestion)}")

    wrong = []
    while True:
        current = input()
        wrong.append(current)
        if current != "1":
            print(f"Matches: {', '.join(match for match in matches if all(True if letter not in match else False for letter in wrong))}\nSimilar: {', '.join(similar)}\nSuggested: {', '.join(letter for letter in suggestion if all(True if l != letter else False for l in wrong) and letter in ''.join(match for match in matches if all(True if letter not in match else False for letter in wrong)))}")
        else:
            break