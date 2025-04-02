# CineTrack

CineTrack is a web application for managing your personal watchlist of movies, series, and anime. It integrates with IMDb to fetch content information and allows users to track their viewing progress.

## Features

- Search movies, series, and anime from IMDb
- Track watched episodes and movies
- User authentication with JWT
- Progress tracking for series and anime
- Modern, responsive UI with Material-UI
- Docker containerization for easy deployment

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- PostgreSQL (included in Docker setup)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Backend
JWT_SECRET=your-secret-key-here
IMDB_API_KEY=your-imdb-api-key-here

# Frontend
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cinetrack.git
cd cinetrack
```

2. Create the environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the application using Docker Compose:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Development

### Backend

The backend is built with FastAPI and uses PostgreSQL for data storage. To run the backend locally:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

The frontend is built with React and TypeScript. To run the frontend locally:

```bash
cd frontend
npm install
npm start
```

## API Endpoints

### Authentication
- POST `/api/v1/auth/register` - Register a new user
- POST `/api/v1/auth/login` - Login and get JWT token

### Content
- GET `/api/v1/content/search` - Search for movies, series, or anime
- GET `/api/v1/content/{imdb_id}` - Get detailed information about specific content

### Watchlist
- GET `/api/v1/watchlist` - Get user's watchlist
- POST `/api/v1/watchlist` - Add content to watchlist
- PUT `/api/v1/watchlist/{item_id}` - Update watchlist item progress
- DELETE `/api/v1/watchlist/{item_id}` - Remove content from watchlist

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 