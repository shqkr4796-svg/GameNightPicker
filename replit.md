# Life Simulation Game

## Overview
A text-based life simulation game built with Flask where players create characters, develop skills via English vocabulary quizzes, pursue careers, buy real estate, and track achievements. It features a progression system with levels, stats, diverse life activities, and a comprehensive monster collection system integrated with a Word Dungeon. The project also includes a fully functional mobile application built with React Native and Expo, offering a complete cross-platform experience.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
-   **Web Frontend**: Jinja2 templates with Bootstrap 5 dark theme, custom CSS animations, responsive design, Feather icons.
-   **Mobile Frontend**: React Native with Expo, consistent dark theme, API integration.
-   **Audio System**: Web Audio API for rarity-based monster sound effects (sine, square, multi-harmonic, drum+high-frequency), RPG battle background music (Am-G-C-F progression with drums and synth), and vibration feedback for mobile.

### Technical Implementations
-   **Web Backend**: Flask with session-based state management.
-   **Mobile Backend**: Node.js/Express with JWT authentication and file-based storage.
-   **Game Logic**: Modular Python functions (Web) and JavaScript/TypeScript (Mobile) for player progression, dungeon mechanics, monster system, turn-based combat, and skill management.
-   **Data Storage**: JSON file-based persistence for player progress and game data (monsters, skills, adventures).

### Feature Specifications
-   **Word Dungeon**: Quiz-based dungeon with 42 unique monsters across four rarities (Rare, Epic, Unique, Legendary). Features multiple-choice vocabulary questions, rarity-based spawning, monster-specific stat generation, and capture probability based on rarity.
-   **Adventure System**: 200 stages in normal difficulty, unlockable 200 stages in hard difficulty (2x enemy stats, 2x skill card drop rate). Features 3-monster team battles, turn-based combat, text-to-speech for vocabulary practice, and automatic stage resets.
-   **Monster System**: Fixed roster of 42 monsters with individual stat ranges, rarity-based appearance, combat requiring correct answers to deal damage, and probabilistic capture.
-   **Progression**: Level-based system with experience, stat allocation, and tier ranks.
-   **Skill System**: Acquisition, replacement (up to 4 slots), and item-based management (skill rechargers, skill resetters).
-   **Daily Expressions**: System for daily vocabulary practice.
-   **Shop System**: For purchasing items.
-   **Real Estate System**: For buying properties and collecting rent.
-   **Job System**: For selecting careers and earning income.

### System Design Choices
-   **Cross-platform Development**: Separate Flask web application and Expo/React Native mobile application sharing core game logic and data concepts, with dedicated backends.
-   **API-driven Architecture**: Mobile application communicates via RESTful APIs for all game interactions.
-   **Modular Design**: Clear separation of concerns for game mechanics, UI, and data management.

## External Dependencies
-   **Flask**: Web framework.
-   **Node.js/Express**: Mobile backend framework.
-   **React Native/Expo**: Mobile application development.
-   **Bootstrap 5**: Web UI framework.
-   **Jinja2**: Web template engine.
-   **Feather Icons**: Scalable vector icons.
-   **Web Audio API**: Browser-native audio functionality.
-   **Axios**: HTTP client for API requests in mobile app.
-   **React Navigation**: Routing and navigation for React Native.
-   **Chart.js**: (Planned for data visualization).