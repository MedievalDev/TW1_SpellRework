"""Texts of the SpellRework mod, German and English (Language/ZZ_SpellRework.lan).

Keys carry the 'translate' prefix. translateSkillBurn is a format string
(level, chance, seconds): literal percent signs are doubled there. The
spell descriptions are shown as they are; they avoid the percent sign.
"""

W = '<0xFFFFFFFF>'   # white: spell name
G = '<0xFFAAAAAA>'   # grey: text
V = '<0xFF90FF90>'   # green: values
R = '<0xFFFF8888>'   # red: warning
E = '<*>'            # end of colour

TEXTS = {
    'de': {
        'translateART_MAGIC_TORNADO': 'Tornado',
        'translateMAGIC_TORNADO':
            W + 'Tornado' + G + '\nRuft am Zielort einen Wirbelsturm, der vier Sekunden lang '
            'Blitz- und Stichschaden austeilt. Gefangene Feinde kommen nicht von der Stelle '
            'und werden je nach Betäubungsschlag-Fertigkeit betäubt.',
        'translateMAGIC_OVERPOWER':
            W + 'Übermacht' + G + '\nVerstärkt den nächsten Angriffszauber um 10 Prozent je Karte.\n'
            'Dazu entfacht sie eine Feuernova um dich: Feinde in der Nähe nehmen Feuerschaden '
            'und fangen Feuer (Wirkung von Verbrennen).',
        'translateMAGIC_CONCENTRATION':
            W + 'Konzentration' + G + '\nVerstärkt den nächsten Angriffszauber um 10 Prozent je Karte.\n'
            'Dazu entlädt sich eine Blitznova um dich: Feinde in der Nähe nehmen Blitzschaden '
            'und sind mit etwas Glück drei Sekunden betäubt (mit Luftmagie öfter).',
        'translateMAGIC_BLESS':
            W + 'Segen' + G + '\nVerstärkt für kurze Zeit Stärke und Geschick.',
        'translateMAGIC_PUSH':
            W + 'Schockwelle' + G + '\nSchleudert gleich mehrere Feinde zurück und verteilt Schadenspunkte. '
            'Getroffene Feinde stürzen oft zu Boden (mit Luftmagie öfter).',
        'translateMAGIC_PUSH_WAVE':
            W + 'Konzentrische Schockwelle' + G + '\nDu befindest dich im Zentrum einer konzentrischen Welle, '
            'die deine Feinde zurück schleudert. Getroffene Feinde stürzen oft zu Boden (mit Luftmagie öfter).',
        'translateSkillBurn':
            'Verbrennen ' + G + '(level %d)\n<0xFFFFAAAA>Aktive Fähigkeit\n' + G +
            'Wie wäre es damit, dem Gegner eine brennende Fackel ins Gesicht zu drücken? \n' + G +
            'Chance: ' + V + '%d%% \n' + G + 'Brenndauer: ' + V + '%d Sek\n' + G +
            'Ein brennender Gegner verliert jede Sekunde Lebenspunkte, kämpft und verteidigt sich aber weiter.\n'
            'Jeder Schlag gegen ihn richtet ' + V + '20%%' + G + ' mehr Schaden je Stufe an (höchstens 200%%).\n' +
            W + 'Kritischer Treffer, Betäubungsschlag, Klinge brechen und Schild entreißen' + G +
            '\ngelingen bei brennenden Gegnern doppelt so oft.\n\n' + R + 'Achtung! \n'
            ' - Hierfür benötigt man natürlich eine Fackel.' + E,
    },
    'en': {
        'translateART_MAGIC_TORNADO': 'Tornado',
        'translateMAGIC_TORNADO':
            W + 'Tornado' + G + '\nCalls up a whirlwind at the target that deals lightning and '
            'piercing damage for four seconds. Enemies caught in it cannot move away and may '
            'be stunned, depending on your Stun skill.',
        'translateMAGIC_OVERPOWER':
            W + 'Overpower' + G + '\nYour next attack spell deals 10 percent more damage per card.\n'
            'It also sets off a fire nova around you: nearby enemies take fire damage and catch '
            'fire (Burn effect).',
        'translateMAGIC_CONCENTRATION':
            W + 'Concentration' + G + '\nYour next attack spell deals 10 percent more damage per card.\n'
            'It also sets off a lightning nova around you: nearby enemies take lightning damage '
            'and may be stunned for three seconds (more often with Air Magic).',
        'translateMAGIC_BLESS':
            W + 'Blessing' + G + '\nRaises strength and dexterity for a short time.',
        'translateMAGIC_PUSH':
            W + 'Push' + G + '\nHurls several enemies back with a shock wave. Enemies hit are '
            'often knocked to the ground (more often with Air Magic).',
        'translateMAGIC_PUSH_WAVE':
            W + 'Push Wave' + G + '\nYou stand in the eye of a circular wave that hurls your '
            'enemies back. Enemies hit are often knocked to the ground (more often with Air Magic).',
        'translateSkillBurn':
            'Burn ' + G + '(level %d)\n<0xFFFFAAAA>Active skill\n' + G +
            'The hero sticks a torch into his enemy\'s face and sets him on fire.\n' + G +
            'Probability: ' + V + '%d%% \n' + G + 'Burn time: ' + V + '%d sec\n' + G +
            'A burning enemy loses health every second but keeps fighting and defending.\n'
            'Each strike against him deals ' + V + '20%%' + G + ' more damage per level (up to 200%%).\n' +
            W + 'Critical hit, stun, sword break and pull shield' + G +
            '\nwork twice as often on a burning enemy.\n\n' + R + 'Warning! \n'
            ' - Can be executed only with a torch.' + E,
    },
}
