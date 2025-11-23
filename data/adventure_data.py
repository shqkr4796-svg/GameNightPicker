# 모험 시스템 데이터

# 기술 카드 정보
SKILLS = {
    '박치기': {
        '이름': 'Tackle',
        '한글': '박치기',
        '설명': '단순 물리 공격',
        '효과': '몬스터의 기본 공격력만큼 적 체력을 감소',
        '등급': '레어',
        '공격력_보정': 1.0,  # 기본 공격력 그대로
        '특수효과': None
    },
    '스매시': {
        '이름': 'Smash',
        '한글': '스매시',
        '설명': '강력한 물리 공격',
        '효과': '기본 공격력의 1.3배 데미지',
        '등급': '에픽',
        '공격력_보정': 1.3,
        '특수효과': None
    },
    '스핀어택': {
        '이름': 'Spin Attack',
        '한글': '스핀 어택',
        '설명': '회전하며 공격',
        '효과': '기본 공격력의 1.5배 데미지',
        '등급': '유니크',
        '공격력_보정': 1.5,
        '특수효과': None
    },
    '궁극베기': {
        '이름': 'Ultimate Slash',
        '한글': '궁극 베기',
        '설명': '절대적인 힘을 담은 공격',
        '효과': '기본 공격력의 2.0배 데미지',
        '등급': '레전드리',
        '공격력_보정': 2.0,
        '특수효과': None
    },
    '검은빛': {
        '이름': 'Black Light',
        '한글': '검은빛',
        '설명': '어둠의 에너지 공격',
        '효과': '기본 공격력의 1.2배 + 상대방 공격력 15% 감소',
        '등급': '에픽',
        '공격력_보정': 1.2,
        '특수효과': 'debuff_attack'
    },
    '불의폭발': {
        '이름': 'Inferno Blast',
        '한글': '불의 폭발',
        '설명': '불로 감싸인 공격',
        '효과': '기본 공격력의 1.4배 데미지',
        '등급': '유니크',
        '공격력_보정': 1.4,
        '특수효과': None
    },
    '빙결의칼': {
        '이름': 'Frozen Blade',
        '한글': '빙결의 칼',
        '설명': '얼음으로 무장한 공격',
        '효과': '기본 공격력의 1.35배 데미지',
        '등급': '유니크',
        '공격력_보정': 1.35,
        '특수효과': None
    },
    '번개참격': {
        '이름': 'Thunder Slash',
        '한글': '번개 참격',
        '설명': '전기 에너지로 강화된 공격',
        '효과': '기본 공격력의 1.6배 데미지',
        '등급': '레전드리',
        '공격력_보정': 1.6,
        '특수효과': None
    },
    '중력파동': {
        '이름': 'Gravity Wave',
        '한글': '중력 파동',
        '설명': '중력을 제어한 공격',
        '효과': '기본 공격력의 1.7배 데미지',
        '등급': '레전드리',
        '공격력_보정': 1.7,
        '특수효과': None
    },
}

# 스테이지별 적 몬스터 설정
ADVENTURE_STAGES = [
    {
        'stage_id': 1,
        '이름': 'Stage 1: 숲의 입구',
        '난이도': '쉬움',
        'enemy_hp_multiplier': 1.0,
        'enemy_attack_multiplier': 1.0,
        'enemy_rarity': ['레어'],
        'skill_reward_rate': 0.02,  # 2% 확률
    },
    {
        'stage_id': 2,
        '이름': 'Stage 2: 어두운 숲',
        '난이도': '쉬움',
        'enemy_hp_multiplier': 1.2,
        'enemy_attack_multiplier': 1.1,
        'enemy_rarity': ['레어'],
        'skill_reward_rate': 0.03,
    },
    {
        'stage_id': 3,
        '이름': 'Stage 3: 폐허된 성',
        '난이도': '보통',
        'enemy_hp_multiplier': 1.4,
        'enemy_attack_multiplier': 1.2,
        'enemy_rarity': ['레어', '에픽'],
        'skill_reward_rate': 0.04,
    },
    {
        'stage_id': 4,
        '이름': 'Stage 4: 마법의 타워',
        '난이도': '보통',
        'enemy_hp_multiplier': 1.6,
        'enemy_attack_multiplier': 1.3,
        'enemy_rarity': ['레어', '에픽'],
        'skill_reward_rate': 0.05,
    },
    {
        'stage_id': 5,
        '이름': 'Stage 5: 용암 동굴',
        '난이도': '어려움',
        'enemy_hp_multiplier': 1.8,
        'enemy_attack_multiplier': 1.4,
        'enemy_rarity': ['에픽', '유니크'],
        'skill_reward_rate': 0.06,
    },
    {
        'stage_id': 6,
        '이름': 'Stage 6: 무한의 깊이',
        '난이도': '어려움',
        'enemy_hp_multiplier': 2.0,
        'enemy_attack_multiplier': 1.5,
        'enemy_rarity': ['에픽', '유니크'],
        'skill_reward_rate': 0.08,
    },
    {
        'stage_id': 7,
        '이름': 'Stage 7: 신비한 섬',
        '난이도': '매우 어려움',
        'enemy_hp_multiplier': 2.3,
        'enemy_attack_multiplier': 1.6,
        'enemy_rarity': ['유니크', '레전드리'],
        'skill_reward_rate': 0.10,
    },
    {
        'stage_id': 8,
        '이름': 'Stage 8: 최강자의 성',
        '난이도': '최악',
        'enemy_hp_multiplier': 2.6,
        'enemy_attack_multiplier': 1.8,
        'enemy_rarity': ['유니크', '레전드리'],
        'skill_reward_rate': 0.12,
    },
]

# 적 몬스터 대사 (자연스러운 영어)
ENEMY_DIALOGUES = {
    'level_1': [
        "Let's see what you've got.",
        "You won't beat me that easily.",
        "Time for a battle!",
        "Show me what you can do.",
        "I'm not going down without a fight!",
    ],
    'level_2': [
        "You think you can take me on?",
        "This will be interesting.",
        "Bring it on!",
        "Let's make this quick.",
        "I've beaten stronger opponents than you.",
    ],
    'level_3': [
        "You're making a mistake.",
        "I'll show you real power.",
        "This ends now!",
        "Don't underestimate me.",
        "You're out of your league.",
    ],
    'level_4': [
        "Prepare yourself!",
        "This is where it gets serious.",
        "You'll regret challenging me!",
        "I'll crush your pathetic attempts.",
        "Your journey ends here!",
    ],
}

# 플레이어 몬스터 대사
PLAYER_DIALOGUES = {
    'level_1': [
        "I can handle this.",
        "Let's do this!",
        "I'm ready!",
        "Let's go!",
        "Here I come!",
    ],
    'level_2': [
        "I won't back down.",
        "Watch me shine!",
        "This is my moment!",
        "Time to prove myself!",
        "Let's settle this!",
    ],
    'level_3': [
        "I've got this!",
        "Nothing can stop me now!",
        "I'm at full power!",
        "Feel my strength!",
        "Victory is mine!",
    ],
    'level_4': [
        "This is my ultimate form!",
        "I'll show you true strength!",
        "No more holding back!",
        "Prepare to be amazed!",
        "This is the final battle!",
    ],
}

# 보상 아이템
REWARD_ITEMS = {
    '체력회복제': {'한글': '체력회복제', '효과': 'heal_health', '값': 100},
    '공격력증가제': {'한글': '공격력증가제', '효과': 'boost_attack', '값': 150},
    '방어력증가제': {'한글': '방어력증가제', '효과': 'boost_defense', '값': 150},
    '경험치보석': {'한글': '경험치 보석', '효과': 'exp_bonus', '값': 200},
    '운의부적': {'한글': "운의 부적", '효과': 'luck_charm', '값': 250},
    '불사의약': {'한글': '불사의 약', '효과': 'immunity', '값': 300},
}

# 스테이지별 기술 카드 드롭 풀
SKILL_DROP_POOLS = {
    1: {'에픽': ['스매시'], '유니크': [], '레전드리': []},
    2: {'에픽': ['스매시', '검은빛'], '유니크': [], '레전드리': []},
    3: {'에픽': ['스매시', '검은빛'], '유니크': ['스핀어택', '불의폭발', '빙결의칼'], '레전드리': []},
    4: {'에픽': ['스매시', '검은빛'], '유니크': ['스핀어택', '불의폭발', '빙결의칼'], '레전드리': []},
    5: {'에픽': ['스매시', '검은빛'], '유니크': ['스핀어택', '불의폭발', '빙결의칼'], '레전드리': ['궁극베기', '번개참격']},
    6: {'에픽': ['스매시', '검은빛'], '유니크': ['스핀어택', '불의폭발', '빙결의칼'], '레전드리': ['궁극베기', '번개참격', '중력파동']},
    7: {'에픽': ['스매시', '검은빛'], '유니크': ['스핀어택', '불의폭발', '빙결의칼'], '레전드리': ['궁극베기', '번개참격', '중력파동']},
    8: {'에픽': ['스매시', '검은빛'], '유니크': ['스핀어택', '불의폭발', '빙결의칼'], '레전드리': ['궁극베기', '번개참격', '중력파동']},
}
