# NeuroHire Frontend

Next.js 15 + TypeScript + Tailwind CSS frontend for the NeuroHire AI recruitment platform.

## Features

- 🎨 **Modern UI** - Dark theme with NeuroHire design system
- ⚡ **Next.js 15** - Latest React framework with App Router
- 🎯 **Atomic Design** - Organized component architecture (atoms → molecules → organisms → templates)
- 🔄 **Real-time Updates** - WebSocket integration for live agent status
- 🎬 **Smooth Animations** - Framer Motion + GSAP for polished interactions
- 🎛️ **State Management** - Zustand for lightweight, efficient state
- 🔐 **Authentication** - NextAuth.js integration
- 📊 **Type Safety** - Full TypeScript coverage
- 🚀 **Performance** - Optimized builds, lazy loading, code splitting

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Auth routes
│   ├── dashboard/         # Recruiter dashboard
│   ├── candidate/         # Candidate portal
│   └── layout.tsx         # Root layout
├── components/            # Reusable components
│   ├── atoms/            # Smallest UI units (Button, Badge, Avatar)
│   ├── molecules/        # Simple combinations (CandidateCard, JobCard)
│   ├── organisms/        # Complex components (ShortlistTable, Kanban)
│   ├── templates/        # Page-level layouts
│   └── ui/              # shadcn/ui overrides
├── animations/           # Framer Motion variants & GSAP configs
├── hooks/               # Custom React hooks
├── store/               # Zustand state management
├── lib/                 # Utilities & configs
├── types/               # TypeScript types
└── styles/              # Global styles & tokens
```

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.local.example .env.local

# Run development server
npm run dev
```

Visit http://localhost:3000

### Build & Production

```bash
# Build for production
npm run build

# Start production server
npm start

# Type check
npm run type-check
```

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## Components

### Atoms
- `Button` - Customizable button with variants
- `Badge` - Status/tag display
- `Avatar` - User profile images
- `Spinner` - Loading indicator
- `ScoreBar` - Progress/score visualization

### Molecules
- `CandidateCard` - Individual candidate display
- `JobCard` - Job listing card
- `AgentStatusBadge` - Agent status indicator
- `ScoreGauge` - Circular score display
- `SearchBar` - Search input

### Organisms
- `ShortlistTable` - Candidate table with sorting
- `PipelineKanban` - Drag-drop job pipeline
- `AgentActivityFeed` - Real-time agent updates
- `JDEditorPanel` - Job description editor
- `InterviewScheduler` - Schedule interviews

## API Integration

The frontend uses axios with NextAuth for secure API communication:

```typescript
import api from '@/lib/api'

// Requests automatically include auth token
const response = await api.get('/jobs')
```

## Real-time Features

WebSocket connections for live agent status:

```typescript
import { useAgentStream } from '@/hooks/useAgentStream'

const { ws, connect } = useAgentStream('jd-architect')
```

## Deployment

### Render.com

```bash
# Deployment config included in render.yaml
# Connect GitHub repo and Render will auto-deploy
```

### Docker

```bash
docker build -t neurohire-frontend .
docker run -p 3000:3000 neurohire-frontend
```

## Technologies

- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS + CSS-in-JS
- **Animations**: Framer Motion + GSAP
- **State**: Zustand
- **API**: Axios + NextAuth.js
- **Query**: TanStack Query (React Query)
- **Utils**: clsx, date-fns, tailwind-merge

## Development Commands

```bash
npm run dev       # Start dev server
npm run build     # Production build
npm start         # Start production server
npm run lint      # Run ESLint
npm run type-check # TypeScript validation
```

## Contributing

Follow the atomic design principles when adding components. Keep components small, focused, and reusable.

## License

Proprietary - NeuroHire Inc.
