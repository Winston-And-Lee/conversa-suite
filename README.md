# Conversa Suite AI Chatbot

This project integrates LangChain with LangGraph to create an AI chatbot with a FastAPI backend and a Next.js frontend using Assistant-UI.

## Project Structure

- **Backend**: FastAPI application with LangChain and LangGraph integration
- **Frontend**: Next.js application with Assistant-UI for the chat interface

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.template` to `.env`
   - Update the OpenAI API key and other settings

4. Run the backend server:
   ```
   python main.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Set up environment variables:
   - Update `.env.local` with your backend API URL

4. Run the frontend development server:
   ```
   npm run dev
   ```

5. Open your browser and navigate to `http://localhost:3000`

## API Endpoints

The backend provides the following API endpoints for the chatbot:

- `POST /api/chatbot/sessions`: Create a new chat session
- `POST /api/chatbot/sessions/{session_id}/messages`: Send a message to the chatbot
- `GET /api/chatbot/sessions/{session_id}/history`: Get the message history for a session
- `DELETE /api/chatbot/sessions/{session_id}`: Delete a chat session

## Technologies Used

- **Backend**:
  - FastAPI
  - LangChain
  - LangGraph
  - OpenAI

- **Frontend**:
  - Next.js
  - Assistant-UI
  - Tailwind CSS

## License

MIT 