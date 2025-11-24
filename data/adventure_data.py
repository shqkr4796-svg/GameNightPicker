# 모험 시스템 데이터

# 기술 카드 정보
SKILLS = {
    '박치기': {
        '이름': 'Tackle',
        '한글': '박치기',
        '설명': '단순 물리 공격',
        '효과': '몬스터의 기본 공격력만큼 적 체력을 감소',
        '등급': '레어',
        '공격력_보정_min': 0.95,
        '공격력_보정_max': 1.05,
        '특수효과': None
    },
    '스매시': {
        '이름': 'Smash',
        '한글': '스매시',
        '설명': '강력한 물리 공격',
        '효과': '기본 공격력의 1.2배~1.4배 데미지',
        '등급': '에픽',
        '공격력_보정_min': 1.2,
        '공격력_보정_max': 1.4,
        '특수효과': None
    },
    '스핀어택': {
        '이름': 'Spin Attack',
        '한글': '스핀 어택',
        '설명': '회전하며 공격',
        '효과': '기본 공격력의 1.4배~1.6배 데미지',
        '등급': '유니크',
        '공격력_보정_min': 1.4,
        '공격력_보정_max': 1.6,
        '특수효과': None
    },
    '궁극베기': {
        '이름': 'Ultimate Slash',
        '한글': '궁극 베기',
        '설명': '절대적인 힘을 담은 공격',
        '효과': '기본 공격력의 1.9배~2.1배 데미지',
        '등급': '레전드리',
        '공격력_보정_min': 1.9,
        '공격력_보정_max': 2.1,
        '특수효과': None
    },
    '검은빛': {
        '이름': 'Black Light',
        '한글': '검은빛',
        '설명': '어둠의 에너지 공격',
        '효과': '기본 공격력의 1.1배~1.3배 + 상대방 공격력 15% 감소',
        '등급': '에픽',
        '공격력_보정_min': 1.1,
        '공격력_보정_max': 1.3,
        '특수효과': 'debuff_attack'
    },
    '불의폭발': {
        '이름': 'Inferno Blast',
        '한글': '불의 폭발',
        '설명': '불로 감싸인 공격',
        '효과': '기본 공격력의 1.3배~1.5배 데미지',
        '등급': '유니크',
        '공격력_보정_min': 1.3,
        '공격력_보정_max': 1.5,
        '특수효과': None
    },
    '빙결의칼': {
        '이름': 'Frozen Blade',
        '한글': '빙결의 칼',
        '설명': '얼음으로 무장한 공격',
        '효과': '기본 공격력의 1.25배~1.45배 데미지',
        '등급': '유니크',
        '공격력_보정_min': 1.25,
        '공격력_보정_max': 1.45,
        '특수효과': None
    },
    '번개참격': {
        '이름': 'Thunder Slash',
        '한글': '번개 참격',
        '설명': '전기 에너지로 강화된 공격',
        '효과': '기본 공격력의 1.5배~1.7배 데미지',
        '등급': '레전드리',
        '공격력_보정_min': 1.5,
        '공격력_보정_max': 1.7,
        '특수효과': None
    },
    '중력파동': {
        '이름': 'Gravity Wave',
        '한글': '중력 파동',
        '설명': '중력을 제어한 공격',
        '효과': '기본 공격력의 1.6배~1.8배 데미지',
        '등급': '레전드리',
        '공격력_보정_min': 1.6,
        '공격력_보정_max': 1.8,
        '특수효과': None
    },
    # 레어 추가
    '발차기': {
        '이름': 'Kick',
        '한글': '발차기',
        '설명': '강한 발을 날리는 공격',
        '효과': '기본 공격력의 0.9배~1.1배 데미지',
        '등급': '레어',
        '공격력_보정_min': 0.9,
        '공격력_보정_max': 1.1,
        '특수효과': None
    },
    '할퀴기': {
        '이름': 'Scratch',
        '한글': '할퀴기',
        '설명': '날카로운 발톱으로 공격',
        '효과': '기본 공격력의 0.85배~1.15배 데미지',
        '등급': '레어',
        '공격력_보정_min': 0.85,
        '공격력_보정_max': 1.15,
        '특수효과': None
    },
    # 에픽 추가
    '포이즌 파우더': {
        '이름': 'Poison Powder',
        '한글': '포이즌 파우더',
        '설명': '독 가루를 날리는 공격',
        '효과': '기본 공격력의 1.15배~1.35배 데미지',
        '등급': '에픽',
        '공격력_보정_min': 1.15,
        '공격력_보정_max': 1.35,
        '특수효과': None
    },
    '암석폭탄': {
        '이름': 'Rock Bomb',
        '한글': '암석 폭탄',
        '설명': '바위를 던져 공격',
        '효과': '기본 공격력의 1.25배~1.45배 데미지',
        '등급': '에픽',
        '공격력_보정_min': 1.25,
        '공격력_보정_max': 1.45,
        '특수효과': None
    },
    '날카로운투척': {
        '이름': 'Sharp Shot',
        '한글': '날카로운 투척',
        '설명': '예각물체를 투척',
        '효과': '기본 공격력의 1.1배~1.35배 데미지',
        '등급': '에픽',
        '공격력_보정_min': 1.1,
        '공격력_보정_max': 1.35,
        '특수효과': None
    },
    # 유니크 추가
    '용의숨결': {
        '이름': 'Dragon Breath',
        '한글': '용의 숨결',
        '설명': '용의 강력한 숨결로 공격',
        '효과': '기본 공격력의 1.5배~1.75배 데미지',
        '등급': '유니크',
        '공격력_보정_min': 1.5,
        '공격력_보정_max': 1.75,
        '특수효과': None
    },
    '암흑참격': {
        '이름': 'Dark Slash',
        '한글': '암흑 참격',
        '설명': '어둠으로 감싼 검의 일격',
        '효과': '기본 공격력의 1.35배~1.55배 데미지',
        '등급': '유니크',
        '공격력_보정_min': 1.35,
        '공격력_보정_max': 1.55,
        '특수효과': None
    },
    '신성한빛': {
        '이름': 'Holy Light',
        '한글': '신성한 빛',
        '설명': '신성한 에너지로 공격',
        '효과': '기본 공격력의 1.45배~1.65배 데미지',
        '등급': '유니크',
        '공격력_보정_min': 1.45,
        '공격력_보정_max': 1.65,
        '특수효과': None
    },
    # 레전드리 추가
    '하이퍼빔': {
        '이름': 'Hyper Beam',
        '한글': '하이퍼 빔',
        '설명': '강력한 에너지 광선',
        '효과': '기본 공격력의 1.8배~2.0배 데미지',
        '등급': '레전드리',
        '공격력_보정_min': 1.8,
        '공격력_보정_max': 2.0,
        '특수효과': None
    },
    '우주의힘': {
        '이름': 'Cosmic Power',
        '한글': '우주의 힘',
        '설명': '우주의 에너지로 공격',
        '효과': '기본 공격력의 1.85배~2.15배 데미지',
        '등급': '레전드리',
        '공격력_보정_min': 1.85,
        '공격력_보정_max': 2.15,
        '특수효과': None
    },
    '천벌의검': {
        '이름': 'Divine Sword',
        '한글': '천벌의 검',
        '설명': '천상의 검으로 내려치는 일격',
        '효과': '기본 공격력의 1.95배~2.25배 데미지',
        '등급': '레전드리',
        '공격력_보정_min': 1.95,
        '공격력_보정_max': 2.25,
        '특수효과': None
    },
}

# 스테이지 생성 함수
def generate_adventure_stages():
    """200개의 스테이지를 동적으로 생성"""
    stages = []
    
    for stage_id in range(1, 201):
        # 난이도 결정 (200개 스테이지에 맞게 단계적으로 상승)
        if stage_id <= 40:
            difficulty = '쉬움'
            enemy_count = 1
            hp_mult = 1.0 + (stage_id - 1) * 0.05
            atk_mult = 1.0 + (stage_id - 1) * 0.02
            rarities = ['레어']
            skill_reward = 0.02 + (stage_id - 1) * 0.002
        elif stage_id <= 80:
            difficulty = '보통'
            enemy_count = 1 + (stage_id - 40) // 15  # 1~3마리
            hp_mult = 3.0 + (stage_id - 40) * 0.08
            atk_mult = 1.8 + (stage_id - 40) * 0.03
            rarities = ['레어', '에픽']
            skill_reward = 0.05 + (stage_id - 40) * 0.002
        elif stage_id <= 120:
            difficulty = '어려움'
            enemy_count = 2 + (stage_id - 80) // 15  # 2~4마리
            hp_mult = 9.4 + (stage_id - 80) * 0.08
            atk_mult = 3.0 + (stage_id - 80) * 0.03
            rarities = ['에픽', '유니크']
            skill_reward = 0.07 + (stage_id - 80) * 0.001
        elif stage_id <= 160:
            difficulty = '매우 어려움'
            enemy_count = 3 + (stage_id - 120) // 15  # 3~5마리
            hp_mult = 12.2 + (stage_id - 120) * 0.08
            atk_mult = 4.2 + (stage_id - 120) * 0.02
            rarities = ['유니크', '레전드리']
            skill_reward = 0.09 + (stage_id - 120) * 0.0005
        else:
            difficulty = '극악'
            enemy_count = 4 + (stage_id - 160) // 10  # 4~8마리
            hp_mult = 15.4 + (stage_id - 160) * 0.08
            atk_mult = 5.2 + (stage_id - 160) * 0.02
            rarities = ['레전드리']
            skill_reward = 0.12 + (stage_id - 160) * 0.0002
        
        stage = {
            'stage_id': stage_id,
            '이름': f'Stage {stage_id}',
            '난이도': difficulty,
            'enemy_hp_multiplier': hp_mult,
            'enemy_attack_multiplier': atk_mult,
            'enemy_rarity': rarities,
            'skill_reward_rate': min(0.15, skill_reward),  # 최대 15%
            'enemy_count': enemy_count,  # 난이도별 몬스터 개수
        }
        stages.append(stage)
    
    return stages

# 스테이지 데이터 생성
ADVENTURE_STAGES = generate_adventure_stages()

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
def generate_skill_drop_pools():
    """스테이지별 기술 드롭 풀 생성"""
    pools = {}
    for stage_id in range(1, 201):
        pools[stage_id] = {
            '레어': ['박치기', '발차기', '할퀴기'],
            '에픽': ['스매시', '검은빛', '포이즌 파우더', '암석폭탄', '날카로운투척'],
            '유니크': ['스핀어택', '불의폭발', '빙결의칼', '용의숨결', '암흑참격', '신성한빛'],
            '레전드리': ['궁극베기', '번개참격', '중력파동', '하이퍼빔', '우주의힘', '천벌의검']
        }
    return pools

SKILL_DROP_POOLS = generate_skill_drop_pools()
