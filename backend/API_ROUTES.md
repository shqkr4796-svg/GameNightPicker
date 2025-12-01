# Backend API Routes

## Authentication
All routes require JWT token in header: `Authorization: Bearer {token}`

---

## Player API (`/api/player`)

### Start Game
- **POST** `/api/player/start`
- Returns: JWT token and initial player data

### Get Player Info
- **GET** `/api/player/info`
- Returns: Current player stats and status

### Save Game
- **POST** `/api/player/save`
- Body: `{ playerData }`
- Returns: Save confirmation

### Load Game
- **GET** `/api/player/load`
- Returns: Last saved player data

### Sleep (Rest)
- **POST** `/api/player/sleep`
- Returns: Updated stats after rest

### Allocate Stats
- **POST** `/api/player/allocate_stats`
- Body: `{ stat_name, points }`
- Returns: Updated stats

---

## Dungeon API (`/api/dungeon`)

### List Dungeons
- **GET** `/api/dungeon/list`
- Returns: Available dungeons

### Dungeon Preview
- **GET** `/api/dungeon/:dungeon_id/preview`
- Returns: Dungeon details and vocabulary list

### Start Dungeon
- **POST** `/api/dungeon/start`
- Body: `{ dungeon_id }`
- Returns: Dungeon session

### Answer Question
- **POST** `/api/dungeon/answer`
- Body: `{ choice }`
- Returns: Correct/incorrect feedback

### Leave Dungeon
- **POST** `/api/dungeon/leave`
- Returns: Confirmation

---

## Adventure API (`/api/adventure`)

### Select Adventure
- **GET** `/api/adventure/select`
- Returns: Available stages and monsters

### Start Battle
- **POST** `/api/adventure/start`
- Body: `{ stage_id, monster_ids }`
- Returns: Battle state

### Execute Action
- **POST** `/api/adventure/action`
- Body: `{ action_type, skill_name }`
- Returns: Updated battle state

---

## Quiz API (`/api/quiz`)

### Get Quiz
- **GET** `/api/quiz`
- Query: `?category=all&language=random`
- Returns: Word bank and current question

### Answer Quiz
- **POST** `/api/quiz/answer`
- Body: `{ answer, correct_answer }`
- Returns: Quiz feedback

---

## Compendium API (`/api/compendium`)

### View Compendium
- **GET** `/api/compendium`
- Returns: All captured monsters and stats

### Monster Details
- **GET** `/api/compendium/:monster_id`
- Returns: Individual monster info

### Capture Monster
- **POST** `/api/compendium/capture`
- Body: `{ monster_id, monster_data }`
- Returns: Capture confirmation

---

## Shop API (`/api/shop`)

### View Shop
- **GET** `/api/shop`
- Returns: Available items and inventory

### Buy Item
- **POST** `/api/shop/buy`
- Body: `{ item_id, quantity }`
- Returns: Purchase confirmation

### Use Item
- **POST** `/api/shop/use_item`
- Body: `{ item_id }`
- Returns: Item effect

---

## Real Estate API (`/api/realestate`)

### View Properties
- **GET** `/api/realestate`
- Returns: Available and owned properties

### Buy Property
- **POST** `/api/realestate/buy`
- Body: `{ property_id }`
- Returns: Purchase confirmation

### Collect Rent
- **POST** `/api/realestate/collect_rent`
- Returns: Total rent collected

---

## Response Format

Success:
```json
{
  "success": true,
  "data": { ... }
}
```

Error:
```json
{
  "success": false,
  "error": "Error message"
}
```
