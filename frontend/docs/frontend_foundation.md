# Thirukkural Educational AI - Frontend Foundation Documentation

## Overview

This document outlines the frontend foundation implemented for the Thirukkural Educational AI System. The foundation establishes the core architecture, design system, routing, API layer, and reusable UI components that future application features will build upon.

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Query (TanStack Query)
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **Icons**: Lucide React (via custom implementation)
- **Code Quality**: ESLint, Prettier, TypeScript strict mode

## Project Structure

```
frontend/
├── src/
│   ├── assets/           # Static assets (images, icons, etc.)
│   ├── components/       # Reusable UI components
│   │   ├── layout/       # Layout components (Navbar, Footer, etc.)
│   │   └── ui/           # Primitive UI components (Button, Input, etc.)
│   ├── config/           # Configuration files
│   ├── hooks/            # Custom React hooks
│   ├── layout/           # Layout components (AppLayout, etc.)
│   ├── pages/            # Page components (Home, About, etc.)
│   ├── services/         # Service layers (API clients)
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── App.tsx           # Root application component
│   ├── main.tsx          # Application entry point
│   └── index.css         # Tailwind CSS base styles
├── public/               # Static public files
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # Tailwind CSS configuration
├── postcss.config.js     # PostCSS configuration
└── tsconfig.json         # TypeScript configuration
```

## Design System

### Color Palette

The design system uses a clean, professional palette suitable for an educational application:

- **Primary**: Deep blue (#2563EB) - for primary actions and branding
- **Secondary**: Gray (#6B7280) - for secondary actions and text
- **Background**: White (#FFFFFF) - main background
- **Surface**: Light gray (#F9FAFB) - for cards, containers
- **Border**: Light gray (#E5E7EB) - for dividers, input borders
- **Text**: 
  - Primary: Dark gray (#1F2937) - main text
  - Secondary: Gray (#6B7280) - secondary text, placeholder
- **Status Colors**:
  - Success: Green (#10B981)
  - Warning: Amber (#F59E0B)
  - Error: Red (#EF4444)
  - Info: Blue (#3B82F6)

These colors are implemented as Tailwind CSS custom properties in `tailwind.config.js`.

### Typography

The system uses the Inter font family exclusively for a clean, readable interface:

- **Display**: 3rem / 4rem (48px/64px) - for major headings
- **Heading**: 2.25rem / 3rem (36px/48px) - for section titles
- **Subheading**: 1.5rem / 2rem (24px/32px) - for subsection headings
- **Body**: 1rem / 1.5rem (16px/24px) - for paragraph text
- **Caption**: 0.875rem / 1.25rem (14px/20px) - for helper text, captions

All text styles use appropriate font weights (400 for regular, 600 for semi-bold, 700 for bold) and line heights for optimal readability.

### Spacing System

A consistent 8px-based spacing scale is implemented:

- 0.5rem = 8px
- 1rem = 16px
- 1.5rem = 24px
- 2rem = 32px
- 3rem = 48px
- 4rem = 64px
- 6rem = 96px
- 8rem = 128px

This scale is applied to padding, margin, gap, and spacing utilities throughout the application.

## Core Components

### Layout Components

- **AppLayout**: Main layout wrapper containing navigation bar and main content area
- **Navbar**: Responsive navigation with brand logo and menu links
- **Container**: Centers content with appropriate max-width and padding

### UI Primitives (src/components/ui/)

All primitive components follow a consistent API with variants and sizes:

#### Button
- Variants: primary, secondary, outline, ghost
- Sizes: sm, md, lg
- Properties: block (full width), loading state

#### Input
- Variants: default, outline, filled
- Sizes: sm, md, lg
- Supports: all standard input types (text, email, password, number, etc.)

#### TextArea
- Same variants and sizes as Input
- Auto-resizing capability
- Form integration support

#### Card
- Container with elevation and border
- Supports header, title, content, and footer sections
- Flexible padding and spacing

#### Badge
- Status indicators (success, warning, error, info)
- Various sizes and outline variants
- Pill and rounded options

#### Avatar
- Image fallback to initials
- Various sizes (xs, sm, md, lg, xl)
- Status indicators (online, offline, busy)

#### Loading States
- Spinner component
- Skeleton loaders for content placeholders
- Bar and circle variants

#### Feedback Components
- Alert (success, warning, error, info)
- Toast notifications (via react-hot-toast)
- Modal dialogs
- Confirmation dialogs

### Navigation Structure

The application uses React Router v6 with lazy-loaded routes for code splitting:

```
/
  ├── Home (landing page)
  ├── Results (search/quiz results)
  ├── Chat (AI tutor interface)
  ├── About (application information)
  ├── Research (academic resources)
  └── * (404 Not Found)
```

Each route:
- Loads components lazily for better initial load performance
- Includes proper error boundaries
- Maintains scroll position on navigation
- Supports browser history and deep linking

### API Layer

#### Axios Instance (src/services/api.ts)
- Centralized API client with base URL from environment variables
- Request/response interceptors for:
  - Automatic token attachment (for future auth implementation)
  - Error handling and normalization
  - Loading state management
- Configurable timeout (10 seconds)
- CORS handling

#### Configuration (src/config/environment.ts)
- Centralized configuration management
- Environment-specific variables
- Application metadata (name, version)
- Feature flags (for future implementation)

## State Management

### React Query Setup (src/main.tsx)
- Global QueryClientProvider for data fetching and state synchronization
- Customizable defaults:
  - Stale time: 5 minutes
  - Cache time: 5 minutes
  - Retry attempts: 3
  - Refetch on window focus: true
- Devtools enabled in development

## Error Handling

### Global Error Boundary (src/components/common/ErrorBoundary.tsx)
- Catches and displays unexpected errors in the component tree
- Provides retry mechanism for recoverable errors
- Logs errors to console for development
- Customizable fallback UI

### API Error Handling
- Standardized error responses from the API layer
- HTTP status code handling
- Network error detection
- Validation error formatting

## Accessibility Features

- Semantic HTML elements throughout
- Proper ARIA labels and attributes
- Keyboard navigation support
- Focus management in interactive components
- Sufficient color contrast (WCAG AA compliant)
- Responsive design for mobile and tablet devices
- Screen reader friendly announcements for dynamic content

## Performance Optimizations

- Code splitting via React.lazy() and dynamic imports
- Image optimization (placeholder sources, lazy loading)
- Bundle analysis setup
- Memoization of expensive computations
- Virtual scrolling prepared for large lists (future implementation)

## Development Experience

- Fast Refresh with Vite
- ESLint with Airbnb base configuration + TypeScript plugin
- Prettier for consistent code formatting
- TypeScript strict mode enabled
- Jest and React Testing Library setup (configured but not implemented in this phase)
- Storyboard ready for component documentation (configuration placeholder)

## Environment Variables

Required environment variables (in .env file):

```
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Thirukkural Educational AI
VITE_APP_VERSION=1.0.0
```

## Future Extension Points

### State Management
- Ready for Zustand or Redux Toolkit integration if global state requirements grow
- Custom hooks pattern established for reusable logic

### Styling Enhancements
- Dark mode support (CSS variables already in place)
- Theme customization capabilities
- Advanced animation utilities (Framer Motion ready)

### Internationalization
- i18n-ready structure with translation function pattern
- Message extraction setup

### Testing
- Unit testing foundation with Jest configuration
- Component testing with React Testing Library
- E2E testing readiness with Cypress configuration placeholder

### Performance
- Advanced caching strategies
- Request deduplication
- Pagination and infinite scroll helpers
- Web worker integration points

## Guidelines for Future Development

### Component Creation
1. Place new UI components in `src/components/ui/` following the existing pattern
2. Compose components from primitives in `src/components/` subdirectories
3. Use TypeScript interfaces for all props
4. Follow existing styling conventions (Tailwind utility classes)
5. Include proper accessibility attributes
6. Add JSDoc comments for complex components

### Page Creation
1. Create new pages in `src/pages/`
2. Use lazy loading with React.lazy() and Suspense
3. Connect to data services via custom hooks
4. Implement proper error and loading states
5. Follow the existing layout structure with AppLayout

### State Management
1. Use React Query for server state
2. Use React Context or custom hooks for client state
3. Follow separation of concerns between UI and logic
4. Implement proper loading, error, and empty states

### Styling
1. Extend Tailwind configuration in tailwind.config.js for new colors/utilities
2. Use CSS variables for theme-related values
3. Follow the established spacing and typography scale
4. Maintain consistent hover, focus, and active states

### Accessibility
1. Ensure all interactive elements are keyboard accessible
2. Provide meaningful ARIA labels and roles
3. Maintain sufficient color contrast
4. Test with screen readers regularly
5. Follow WCAG 2.1 AA guidelines

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run type-check` - TypeScript type checking

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (responsive design)

## License

MIT License - see LICENSE file for details.

---
*This foundation provides a solid, scalable base for building the Thirukkural Educational AI System while maintaining code quality, performance, and accessibility standards.*