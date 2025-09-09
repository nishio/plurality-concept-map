# CLAUDE.md - WebUI Development Guide

This file provides guidance to Claude Code when working with the React-based WebUI for the Plurality Concept Map tool.

## Project Overview

This is the WebUI component of the Plurality Concept Map tool - a React-based interactive visualization interface that displays concept maps extracted from documents. The WebUI provides an efficient development environment while maintaining the ability to generate static HTML files for deployment.

## Architecture

### Technology Stack
- **React 18** with TypeScript for component-based development
- **Vite** for fast development server and build tooling
- **D3.js v7** for interactive graph visualization
- **CSS Variables** for consistent theming

### Project Structure
```
webui/
├── src/
│   ├── components/           # React components
│   │   ├── ConceptDetails.tsx   # Sidebar concept information panel
│   │   ├── D3Graph.tsx         # Main graph visualization component
│   │   └── Toolbar.tsx         # Filter controls and legend
│   ├── types/               # TypeScript type definitions
│   │   └── index.ts            # GraphData, Concept, Edge, TierFilter types
│   ├── utils/               # Utility functions
│   │   └── dataLoader.ts       # Graph data loading logic
│   ├── data/                # Sample/test data
│   │   └── sample.ts           # Sample concept map data
│   ├── App.tsx              # Main application component
│   ├── App.css              # Global styles (ported from original viewer.html)
│   └── main.tsx             # React entry point
├── scripts/                 # Build and deployment scripts
│   └── generate-static.js      # Static HTML generation script
├── dist/                    # Build output directory
├── viewer.html              # Legacy HTML viewer (preserved)
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Development Commands

### Setup and Installation
```bash
# Install dependencies
npm install

# Start development server with HMR
npm run dev                  # http://localhost:3000

# Build for production
npm run build               # React SPA build

# Build with static HTML generation
npm run build:static        # Includes legacy and static viewers
```

### Development Workflow
1. **Development**: Use `npm run dev` for hot module reload
2. **Testing**: Build with `npm run build` to test production bundle
3. **Deployment**: Use `npm run build:static` to generate all deployment formats

## Data Integration

### Data Format Compatibility
The WebUI maintains 100% compatibility with the existing `graph.json` format:
```typescript
interface GraphData {
  nodes: Concept[];    // Array of concept objects
  edges: Edge[];       // Array of relationship objects
}

interface Concept {
  id: string;
  label: string;
  definition: string;
  tier: 'core' | 'supplementary' | 'advanced';
  aliases: string[];
  evidence: Evidence[];
}
```

### Data Loading Strategy
1. **Development**: Uses sample data from `src/data/sample.ts`
2. **Production**: Attempts to load `./graph.json`, falls back to sample data
3. **Static**: Embeds data directly in HTML file

## Component Architecture

### Key Components

**App.tsx**
- Main application container
- State management for selected concept and filters
- Data loading and error handling

**D3Graph.tsx**
- Core visualization component using D3.js
- Force-directed graph layout with zoom/pan
- Node selection and interaction handling
- Filter application for concept tiers

**ConceptDetails.tsx**
- Displays detailed information for selected concepts
- Shows evidence, aliases, and definitions
- Responsive design for mobile compatibility

**Toolbar.tsx**
- Concept tier filtering (Core/Supplementary/Advanced)
- Relationship type legend
- Clean checkbox-based UI

### Performance Optimizations
- `useMemo` for data processing to prevent unnecessary recalculation
- `useCallback` for stable event handlers
- Proper dependency arrays in `useEffect` to prevent infinite re-renders
- D3 cleanup on component unmount

## Styling and Theming

### CSS Architecture
- **CSS Variables**: Consistent color scheme and spacing
- **Mobile-first**: Responsive design with sidebar collapse
- **Japanese Typography**: Optimized for Japanese text with Noto Sans JP
- **Accessibility**: High contrast ratios and keyboard navigation support

### Key CSS Variables
```css
:root {
  --primary-color: #2563eb;      /* Primary brand color */
  --success-color: #10b981;      /* Supplementary concepts */
  --warning-color: #f59e0b;      /* Advanced concepts */
  --text-primary: #1e293b;       /* Main text */
  --text-secondary: #64748b;     /* Secondary text */
}
```

## Build Output Formats

### Multiple Deployment Options
1. **React SPA** (`dist/index.html`): Modern single-page application
2. **Legacy Viewer** (`dist/viewer_legacy.html`): Original HTML with D3.js
3. **Static Viewer** (`dist/viewer_static.html`): Self-contained with embedded data
4. **Data File** (`dist/graph.json`): JSON data for external consumption

### Static Generation Process
The `scripts/generate-static.js` script:
- Copies legacy viewer for backward compatibility
- Generates sample `graph.json` for testing
- Creates static HTML with embedded data
- Provides usage instructions for different deployment scenarios

## Integration with Pipeline

### Data Flow
```
pipeline.py → graph.json → WebUI → Interactive Visualization
```

### File Placement
- Place generated `graph.json` in `webui/public/` for development
- Place generated `graph.json` in `webui/dist/` for production serving
- Use `npm run build:static` to generate self-contained deployments

## Development Best Practices

### Code Quality
- **TypeScript**: Strict type checking enabled
- **Component Props**: Always define interfaces for component props
- **Error Handling**: Graceful fallbacks for missing data
- **Performance**: Avoid unnecessary re-renders with proper memoization

### Common Patterns
```typescript
// Stable event handlers
const handleNodeSelect = useCallback((concept: Concept) => {
  onNodeSelect(concept);
}, [onNodeSelect]);

// Memoized data processing
const processedData = useMemo(() => {
  // expensive computation
}, [dependencies]);
```

### D3.js Integration
- Use `useRef` for DOM element references
- Clean up D3 selections in useEffect cleanup
- Handle D3 events through React state management
- Separate D3 rendering logic from React lifecycle

## Troubleshooting

### Common Issues
1. **Infinite re-renders**: Check useEffect dependencies, avoid including state that's modified within the effect
2. **D3 conflicts**: Ensure proper cleanup of D3 selections and event listeners
3. **Data loading**: Verify `graph.json` format and accessibility
4. **Build errors**: Check TypeScript types and import paths

### Performance Issues
- Use React DevTools Profiler to identify slow components
- Check for unnecessary re-renders with dependency arrays
- Monitor D3 simulation performance for large datasets

## Deployment Considerations

### Static Hosting
- All build outputs are static files suitable for CDN deployment
- No server-side requirements
- Compatible with GitHub Pages, Netlify, Vercel

### Data Updates
- Replace `graph.json` file for data updates
- Rebuild static viewers when data format changes
- Consider versioning for data schema evolution

## Future Enhancements

### Planned Features
- Search functionality for concepts
- Export capabilities (PNG, SVG, PDF)
- Concept grouping and clustering
- Interactive relationship editing
- Multi-language support improvements

### Technical Improvements
- Web Workers for heavy D3 computations
- Virtual scrolling for large concept lists
- Progressive Web App (PWA) capabilities
- Advanced filtering and sorting options