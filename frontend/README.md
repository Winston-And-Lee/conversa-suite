# Conversa Suite Frontend

This frontend application provides a user interface for the Conversa Suite chatbot system. It's built using React with TypeScript, and uses Refine.dev and Ant Design UI framework.

## Features

- Chat interface to interact with AI assistants
- Session management (create, view, delete)
- Chat history viewing
- Multiple assistant selection

## Setup and Installation

### Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```
   cd frontend
   ```
3. Install dependencies:
   ```
   npm install
   ```

### Configuration

The application uses environment variables for configuration. Create a `.env` file in the frontend directory with the following variables:

```
REACT_APP_API_URL=http://localhost:8000
```

Adjust the URL as necessary to match your backend API location.

### Running the Application

To start the development server:

```
npm start
```

This will run the app in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Building for Production

To build the application for production:

```
npm run build
```

This builds the app for production to the `build` folder, optimizing the build for the best performance.

## API Integration

The application communicates with the following API endpoints:

- `POST /chatbot/sessions` - Create a new chat session
- `POST /chatbot/sessions/{session_id}/messages` - Send a message to the chatbot
- `GET /chatbot/sessions/{session_id}/history` - Get the chat history
- `DELETE /chatbot/sessions/{session_id}` - Delete a chat session

## Technologies Used

- React
- TypeScript
- Refine.dev
- Ant Design (UI framework)
- Axios (HTTP client)
- React Router
