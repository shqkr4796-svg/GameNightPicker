# Life Simulation Game

## Overview

A text-based life simulation game built with Flask where players can create characters, develop skills through English vocabulary quizzes, pursue careers, buy real estate, and track achievements. The game features a progression system with levels, stats, and various life activities that simulate real-world experiences.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme
- **UI Framework**: Bootstrap 5 with custom CSS animations and responsive design
- **JavaScript**: Vanilla JavaScript with Feather icons for interactive elements
- **Static Assets**: CSS animations, progress bars, and custom styling for game elements

### Backend Architecture
- **Web Framework**: Flask with session-based state management
- **Game Logic**: Modular Python functions handling player progression, level-ups, and game mechanics
- **Data Storage**: JSON file-based persistence for save games and events
- **Route Structure**: RESTful endpoints for game actions (work, quiz, shop, real estate)

### Data Management
- **Save System**: JSON file storage for player progress with automatic save/load functionality
- **Game Data**: Static data structures for vocabulary words, jobs, real estate, and shop items
- **Session Management**: Flask sessions for maintaining player state during gameplay

### Game Mechanics
- **Character Progression**: Level-based system with experience points and stat allocation
- **Quiz System**: English vocabulary learning with randomized questions and progress tracking
- **Economic System**: Money management through jobs, purchases, and real estate investments
- **Time System**: Day/hour progression affecting energy and daily activities

## External Dependencies

- **Flask**: Web framework for routing and session management
- **Bootstrap 5**: Frontend UI framework with dark theme support
- **Chart.js**: Data visualization for player statistics and progress charts
- **Feather Icons**: Scalable vector icons for consistent UI elements
- **JSON**: File-based data persistence without external database requirements

The application uses a self-contained architecture with no external APIs or database connections, making it suitable for local deployment and development environments.