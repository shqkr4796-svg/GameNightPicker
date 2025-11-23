# 기술 카드 데이터

RARITY_COLORS = {
    '레어': '#4169E1',      # Royal Blue
    '에픽': '#9932CC',      # Dark Orchid
    '유니크': '#FFD700',    # Gold
    '레전드리': '#FF1493',  # Deep Pink
}

RARITY_NAMES = {
    '레어': 'RARE',
    '에픽': 'EPIC',
    '유니크': 'UNIQUE',
    '레전드리': 'LEGENDARY',
}

# 기술 정보 (자세히)
SKILL_INFO = {
    '박치기': {
        'name_en': 'Tackle',
        'description': 'A basic physical attack',
        'effect': 'Deal your base attack power as damage',
        'rarity': '레어',
        'multiplier': 1.0,
        'color': '#4169E1',
        'icon': '⚔️',
    },
    '스매시': {
        'name_en': 'Smash',
        'description': 'A powerful crushing blow',
        'effect': 'Deal 1.3x your attack power as damage',
        'rarity': '에픽',
        'multiplier': 1.3,
        'color': '#9932CC',
        'icon': '💥',
    },
    '스핀어택': {
        'name_en': 'Spin Attack',
        'description': 'A spinning aerial attack',
        'effect': 'Deal 1.5x your attack power as damage',
        'rarity': '유니크',
        'multiplier': 1.5,
        'color': '#FFD700',
        'icon': '🌪️',
    },
    '궁극베기': {
        'name_en': 'Ultimate Slash',
        'description': 'The ultimate technique',
        'effect': 'Deal 2.0x your attack power as damage',
        'rarity': '레전드리',
        'multiplier': 2.0,
        'color': '#FF1493',
        'icon': '⚡',
    },
    '검은빛': {
        'name_en': 'Black Light',
        'description': 'Dark energy attack',
        'effect': 'Deal 1.2x damage and reduce enemy attack by 15%',
        'rarity': '에픽',
        'multiplier': 1.2,
        'color': '#9932CC',
        'icon': '🌑',
    },
    '불의폭발': {
        'name_en': 'Inferno Blast',
        'description': 'Engulfed in flames',
        'effect': 'Deal 1.4x your attack power as damage',
        'rarity': '유니크',
        'multiplier': 1.4,
        'color': '#FFD700',
        'icon': '🔥',
    },
    '빙결의칼': {
        'name_en': 'Frozen Blade',
        'description': 'Armed with ice',
        'effect': 'Deal 1.35x your attack power as damage',
        'rarity': '유니크',
        'multiplier': 1.35,
        'color': '#FFD700',
        'icon': '❄️',
    },
    '번개참격': {
        'name_en': 'Thunder Slash',
        'description': 'Amplified with electricity',
        'effect': 'Deal 1.6x your attack power as damage',
        'rarity': '레전드리',
        'multiplier': 1.6,
        'color': '#FF1493',
        'icon': '⚡',
    },
    '중력파동': {
        'name_en': 'Gravity Wave',
        'description': 'Controls gravity itself',
        'effect': 'Deal 1.7x your attack power as damage',
        'rarity': '레전드리',
        'multiplier': 1.7,
        'color': '#FF1493',
        'icon': '🌀',
    },
}
