# AI Checkers Bot
AI Checkers Bot is a full-stack checkers game project where you can play against bots with three difficulty levels: easy, medium, hard. The game has an AI-powered hint system that uses Gemini API to suggest helpful moves when the player is stuck or unsure how to improve their position. The app is based on Lithuanian-style checkers rules, including mandatory captures, multi-capture sequences, flying kings, AI-generated move hints and other relevant features.

The app was primarily built with React and Vite for the frontend and FastAPI with Pydantic for the backend. The backend owns the game rules and validates all the moves, while the frontend focuses on displaying the board and handling user interactions. The project also has Docker Compose support, allowing an easier access to run the app locally. The app itself is deployed with Render, with the frontend hosted as a static site and the backend hosted as a web service.

## Demo
You can try playing checkers here:
https://ai-checkers-bot.onrender.com  

## Tech Stack
### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- Pydantic
- Gemini API
- Uvicorn
- python-dotenv

### DevOps

- Docker
- Docker Compose
- Render

## Features

- Lithuanian checkers rules
- Three bot difficulty levels: easy, medium and hard
- Mandatory captures and multi-capture sequences
- Piece promotion
- Move validations
- AI-powered move hints
- Bot's behavior based on difficulty
- Score tracker
- Draw system
- Responsive game interface
- Docker setup
- Render deployment

## Screenshots

### Game Board

![Game board](./screenshots/game-board.png)

### Choose Bot Difficulty

![Choose bot difficulty](./screenshots/choose-difficulty.png)

### AI Hint

![AI hint](./screenshots/ai-hint.png)

### Draw and Surrender Flow

![Draw or surrender flow](./screenshots/draw-surrender.png)
