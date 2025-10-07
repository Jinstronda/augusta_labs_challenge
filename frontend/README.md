# Incentive Query UI - Frontend

React + TypeScript frontend for querying Portuguese public incentives and companies.

## Overview

This UI provides a ChatGPT-like interface for querying the incentive-company matching system. Users can ask about incentives or companies, and the system will:
- Classify the query (INCENTIVE vs COMPANY)
- Search the appropriate data
- Display results with matched companies/incentives

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Router** - Navigation
- **Axios** - API client
- **React Markdown** - Markdown rendering

## Development

### Prerequisites
- Node.js 20+ 
- Backend API running on http://localhost:8000

### Install Dependencies
```bash
npm install
```

### Run Development Server
```bash
npm run dev
```

The app will be available at http://localhost:5173

### Build for Production
```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/     # React components
│   ├── pages/          # Page components
│   ├── services/       # API client
│   ├── types/          # TypeScript types
│   ├── utils/          # Utility functions
│   ├── App.tsx         # Main app component
│   └── main.tsx        # Entry point
├── public/             # Static assets
└── index.html          # HTML template
```

## Features

### Query Interface
- ChatGPT-like chat interface
- Auto-classification (INCENTIVE vs COMPANY)
- Real-time search results
- Loading states and error handling

### Incentive View
- Incentive details (title, description, criteria, etc.)
- Top 5 matched companies with scores
- Clickable company cards → company detail view

### Company View
- Company details (name, CAE, activities, location)
- Eligible incentives ranked by score
- Clickable incentive cards → incentive detail view

### Navigation
- `/` - Chat interface (home)
- `/incentive/:id` - Incentive detail page
- `/company/:id` - Company detail page

## API Integration

The frontend connects to the backend API at `http://localhost:8000/api`:

- `POST /api/query` - Main query endpoint
- `GET /api/incentive/:id` - Get incentive details
- `GET /api/company/:id` - Get company details

See `backend/README.md` for API documentation.

## Styling

Uses TailwindCSS with a custom theme:
- Primary color: Blue (similar to ChatGPT)
- Clean, minimal design
- Responsive layout
- Dark mode support (optional)

## Development Notes

- This is a frontend for an EXISTING backend system
- Don't modify the main project README.md
- Backend must be running for the UI to work
- See main project docs for full system architecture
