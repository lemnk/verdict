# VerdictVault Frontend

Modern React frontend for the VerdictVault legal document analysis platform.

## Features

- **Authentication**: JWT-based login system
- **Document Upload**: Drag-and-drop PDF upload with validation
- **Document Parsing**: View parsed chunks and metadata
- **RAG Questions**: AI-powered legal question answering
- **Query History**: Track performance metrics and costs
- **Responsive Design**: Mobile-friendly interface

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Custom shadcn/ui-style components
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **State Management**: React hooks

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Update `.env` with your API configuration:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

4. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # Base UI components (Button, Input, Card)
│   ├── FileUploader.tsx
│   ├── AnswerView.tsx
│   ├── CitationList.tsx
│   ├── StatBadge.tsx
│   └── NavBar.tsx
├── pages/               # Page components
│   ├── Login.tsx
│   ├── Upload.tsx
│   ├── Ask.tsx
│   ├── History.tsx
│   └── Document.tsx
├── lib/                 # Utilities and API client
│   ├── api.ts          # Typed API client
│   ├── auth.ts         # Authentication utilities
│   └── utils.ts        # Helper functions
├── routes.tsx           # Router configuration
├── App.tsx             # Main app component
└── main.tsx            # Entry point
```

## Usage

1. **Login**: Use test credentials (test@example.com / password)
2. **Upload**: Drag and drop PDF files (max 20MB)
3. **Parse**: Extract text chunks and generate embeddings
4. **Ask**: Submit legal questions using RAG system
5. **History**: View query performance and costs
6. **Documents**: Browse parsed chunks and metadata

## Development

### Adding New Components

Create components in `src/components/` following the existing pattern:

```tsx
import { Button } from './ui/Button'

interface MyComponentProps {
  title: string
}

export function MyComponent({ title }: MyComponentProps) {
  return (
    <div>
      <h1>{title}</h1>
    </div>
  )
}
```

### API Integration

Add new API endpoints in `src/lib/api.ts`:

```tsx
async newEndpoint(data: NewData): Promise<ResponseType> {
  const response = await this.client.post('/api/new-endpoint', data)
  return response.data
}
```

### Styling

Use Tailwind CSS classes for styling. For custom components, extend the design system in `tailwind.config.js`.

## Testing

```bash
npm run test
```

## Deployment

The app builds to static files in `dist/` that can be served from any static hosting service.

## License

MIT