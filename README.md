
#   Chat Appointment System

This project is a full-stack AI-powered appointment scheduling system, combining a **React-based chat interface** on the client side with a **Python/Flask API server** integrated with **Google Cloud APIs** on the backend.

##  Tech Stack

### Frontend (React)
- React (JSX Components)
- Custom Chat UI Components
- Dynamic message handling

### Backend (Python)
- Flask REST API
- Google Cloud integration (Dialogflow or Calendar)
- dotenv-based configuration
- Modular architecture with logic separation and validation layers

##  Project Structure

```
my-project/
│
├── client/                 # React Frontend
│   └── ChatBox/            # Custom chat components
│
├── server/                 # Python Backend
│   ├── api.py              # Entry point for API endpoints
│   ├── logic.py            # Chatbot logic and appointment rules
│   ├── validator.py        # Input validation logic
│   ├── config.py           # Configuration handling
│   ├── credentials.json    # Google OAuth credentials (secured)
│   └── req.txt             # Python dependencies
```

## Getting Started

### Prerequisites

- Node.js (v14+)
- Python 3.11
- Google Cloud project with OAuth credentials

### Install & Run (Development)

#### Frontend

```bash
cd client
npm install
npm start
```

#### Backend

```bash
cd server/python
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r req.txt
flask run
```

> Make sure to set your `.env` file and `credentials.json` with your Google Cloud credentials.

## API & Integrations

The backend interfaces with Google APIs via:

- `google-api-python-client`
- `google-auth`, `oauthlib`
- Custom logic for interpreting user inputs and scheduling appointments dynamically.

##  Usage Example

User: "I want to book an appointment next Monday at 10am"

→ The chatbot parses the date/time and interfaces with the backend to create the event in Google Calendar.

## API Endpoints

- `POST /chat`: Accepts user message, returns chatbot response
- `GET /health`: Server health check
- `POST/appointments`Create a new appointment. Validates user ID, phone, email, and availability. Saves to DB and Google Calendar.
- `PUT/appointments/<event_id>`Update existing appointment. Validates and modifies both calendar and database.                  
- `DELETE/appointments/<event_id>` Delete appointment from Google Calendar and database. Handles calendar API exceptions. 
- `GET/appointments/user/<user_id>` Fetch all appointments for a given user by Israeli ID, combining database and calendar records.               |
- `GET/appointments/all` Admin endpoint to retrieve all appointments from the database.                                                |
- `GET/events` Fetch upcoming events from Google Calendar, formatted for frontend display.                                   |


##  Testing

- Manual testing for chat flows
- Python backend ready for unit tests with `pytest`

##  Future Enhancements

- NLP integration with ChatGPT
- Multi-language support
- Admin dashboard for appointments

##  Team

Developed by: shoshana packer
Inspiration: Google Cloud AI, modern conversational interfaces

##  Deployment Options

- **Frontend**: Vercel, Netlify
- **Backend**: Railway, Render, Google App Engine, Docker

##  Security Note

Ensure that `credentials.json` and `.env` files are excluded from version control via `.gitignore`.

