# Life Simulation Game

## Overview

A text-based life simulation game built with Flask where players can create characters, develop skills through English vocabulary quizzes, pursue careers, buy real estate, and track achievements. The game features a progression system with levels, stats, various life activities, and a comprehensive monster collection system with Word Dungeon.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme
- **UI Framework**: Bootstrap 5 with custom CSS animations and responsive design
- **JavaScript**: Vanilla JavaScript with Web Audio API for monster sound effects, Feather icons for interactive elements
- **Static Assets**: CSS animations, progress bars, monster images (planned), sound effects
- **Audio System**: Rarity-based monster appearance sound effects (Rare, Epic, Unique, Legendary)

### Backend Architecture
- **Web Framework**: Flask with session-based state management
- **Game Logic**: Modular Python functions handling player progression, dungeon mechanics, and monster system
- **Data Storage**: JSON file-based persistence + monsters.py for monster database
- **Route Structure**: RESTful endpoints for dungeons, monsters, compendium, and trading

### Data Management
- **Save System**: JSON file storage for player progress with automatic save/load functionality
- **Monster System**: Fixed monster database (42 unique monsters) with individual stat ranges
- **Compendium**: Player monster collection with captured monsters stored by monster ID
- **Game Data**: Vocabulary words, jobs, real estate, monsters, dungeons

### Game Mechanics
- **Word Dungeon**: Quiz-based dungeon with:
  - 42 unique pre-defined monsters (Rare: 10, Epic: 10, Unique: 10, Legendary: 12)
  - Rarity-based random spawning
  - Monster-specific stat generation with randomization
  - Multiple choice vocabulary questions per monster
  - Capture probability based on rarity (Rare: 50%, Epic: 10%, Unique: 5%, Legendary: 1%)
  - Compendium tracking of captured monsters

- **Monster System**: 
  - Fixed monster roster with individual names and stat ranges
  - Rarity-based appearance rates in dungeons
  - Combat: Answer questions to deal damage, lose HP on wrong answers
  - Capture on monster defeat (with probability check)

- **Audio Effects**: Distinct sound signatures per rarity tier using Web Audio API
  - Rare: Simple sine wave tone
  - Epic: Square wave with ascending pitch
  - Unique: Multi-harmonic blend with pulsing effect
  - Legendary: Drum-like kick + high-frequency effect combo

- **Progression**: Level-based system with experience, stat allocation, and tier ranks

## Monster Database

**Location**: `data/monsters.py`
**Total Monsters**: 42
- Rare (10): Slime, Goblin, Vampire Bat, Golem, Skeleton, Orc, Werewolf, Tooth Ghost, Fire Spider, Ice Elemental
- Epic (10): Necromancer, Black Knight, Frost Wizard, Dragon Hunter, Dark Priest, Legendary Warrior, Fire Wizard, Poison Archer, Kraken, Sky God
- Unique (10): Shepherd of Tartarus, Azure Dragon, Ancient Vampire, Spirit of Infinity, Shadow of Despair, Heavenly Knight, Last Emperor, Guardian of Time, Resurrected King, Pope of Darkness
- Legendary (12): Yama Raja, Creator of Heaven and Earth, Eternal Demon, King of Abyss, Azure Dragon, Fury of Flame, The Absolute, Infinite Judge, God of Annihilation, Keeper of Eternal Night, Avatar of Chaos, Last Dragon

## Monster Images

Status: **Images placeholder (empty strings)**
- Monster images will be added later
- Current system supports white background monster images
- Images directory ready at: `/static/monsters/`

## Recent Changes (Nov 21, 2025)

1. ✅ Created `data/monsters.py` with 42 unique monsters
2. ✅ Modified `game_logic.py`:
   - Changed `next_monster()` to select from pre-defined monster roster
   - Updated `get_monster_stats()` to use individual monster stat ranges
   - Modified `update_compendium()` to use original monster names
   - Updated `get_all_monster_images()` for new monster system
3. ✅ Monster pokapture system:
   - Dungeon encounters now spawn specific monsters (not word-based)
   - Compendium displays collected monsters with original names
   - Each monster instance has randomized stats within its defined range

## External Dependencies

- **Flask**: Web framework for routing and session management
- **Bootstrap 5**: Frontend UI framework with dark theme support
- **Chart.js**: Data visualization for player statistics
- **Feather Icons**: Scalable vector icons
- **Web Audio API**: Browser-native sound effects (no external audio files)

The application uses a self-contained architecture perfect for local deployment and development.