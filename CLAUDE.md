# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Recipe Management web application (Aplikacja do Zarządzania Recepturami) built with microservices architecture for managing product recipes, allowing users to add, modify, and search for recipes with automatic ingredient calculation for specified product quantities.

### Target Users
Production companies, laboratories, industrial kitchens, and other organizations managing product recipes and compositions.

## Architecture Overview

### Microservices Architecture
- **Product Service**: Manages product CRUD operations, search, and metadata
- **Recipe Service**: Handles recipe creation, modification, and hierarchical relationships
- **Calculator Service**: Performs ingredient calculations and proportional scaling
- **API Gateway**: Routes requests and handles cross-cutting concerns
- **Frontend Service**: React application with Trello-like UI components

## Technology Stack

### Backend Services
- **Language**: Python 3.11+
- **Framework**: Flask with Flask-RESTful
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Migration**: Flask-Migrate (Alembic)
- **Containerization**: Docker & Docker Compose
- **API Documentation**: Flask-SMOREST (OpenAPI/Swagger)

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI) for Trello-like card components
- **State Management**: React Query + Context API
- **Routing**: React Router v6
- **Build Tool**: Vite
- **Styling**: CSS Modules + MUI Theme

### Infrastructure
- **Reverse Proxy**: Nginx
- **Database**: PostgreSQL 15 (local installation)
- **Container Orchestration**: Docker Compose
- **Version Control**: GitHub
- **Development**: Hot reload for both frontend and backend

## Core Data Model

### Entities

**Product (Produkt)**
- ID (UUID), name, type (standard/kit/semi-product), unit (piece/gram), description
- Products can be ingredients in other recipes, creating hierarchical structures

**Recipe (Receptura)**  
- Belongs to a product, contains list of recipe ingredients
- Validates business rules and prevents circular dependencies

**Recipe Ingredient (Składnik Receptury)**
- References another product, has quantity, unit (piece/gram), and order
- Supports mixed units within recipes

### Key Business Logic

**Unit Handling**
- Products measured in pieces (szt): ingredients scaled by multiplication
- Products measured in grams (g): ingredients scaled proportionally by weight
- Mixed units allowed within recipes (e.g., 1 piece + 120g of another ingredient)

**Recipe Calculator**
- For piece-based products: multiply all ingredients by target quantity
- For gram-based products: scale all ingredients proportionally to target weight
- Results: 2 decimal places for grams, whole numbers for pieces

**Hierarchical Composition**
- Semi-products can be expanded to show their own recipe ingredients
- Multi-level ingredient hierarchies supported
- Prevents circular dependencies through validation

## Service Communication

### API Design
- RESTful APIs between services
- JSON payloads with standardized error responses
- Service-to-service communication via HTTP
- API Gateway handles authentication and routing

### Database Strategy
- Each microservice has its own database schema
- Shared PostgreSQL instance with separate schemas
- Event-driven updates for data consistency
- Read replicas for search optimization

## Frontend Architecture (Trello-like Design)

### UI Components
- **Product Cards**: Drag-and-drop cards showing product information
- **Recipe Boards**: Column-based layout for recipe management
- **Ingredient Lists**: Interactive cards for recipe ingredients
- **Search Interface**: Real-time search with auto-suggestions
- **Calculator Panel**: Side panel for quantity calculations

### Responsive Design
- Mobile-first approach with Material-UI breakpoints
- Touch-friendly interactions for mobile devices
- Progressive Web App (PWA) capabilities

## Key Features Implementation

### 1. Recipe Creation
- Dynamic ingredient tables with fuzzy search
- Drag-and-drop ingredient addition
- Real-time validation and error feedback
- Card-based ingredient management

### 2. Product Search
- Elasticsearch-like fuzzy search implementation
- Real-time suggestions as you type
- Search by name, ID, and partial matches
- Quick filters for product types

### 3. Product Details
- Card-based layout with expandable sections
- Hierarchical tree view for semi-products
- Interactive ingredient expansion
- Visual recipe composition

### 4. Recipe Calculator
- Side panel calculator with live updates
- Proportional scaling based on target quantity/weight
- Visual feedback for calculations
- Export calculation results

### 5. Recipe Modification
- In-place editing with validation
- Drag-and-drop ingredient reordering
- Batch operations on ingredients
- Change tracking and confirmation dialogs

### 6. Data Import
- CSV/JSON import with drag-and-drop
- Data mapping interface
- Import validation and error reporting
- Batch processing with progress indicators

## Development Workflow

### Local Development Setup
1. PostgreSQL installation and configuration
2. Docker and Docker Compose setup
3. Python virtual environments for each service
4. Node.js and npm for frontend development
5. GitHub repository initialization

### Code Organization
```
recipe-management/
├── services/
│   ├── product-service/
│   ├── recipe-service/
│   ├── calculator-service/
│   └── api-gateway/
├── frontend/
├── database/
├── docker-compose.yml
├── nginx.conf
└── README.md
```

### Testing Strategy
- Unit tests for each microservice
- Integration tests for service communication
- Frontend component testing with React Testing Library
- End-to-end testing with Playwright

## Validation Rules

- Ingredient quantities must be > 0
- At least one ingredient required per recipe  
- No circular dependencies in ingredient relationships
- Logical ingredient sums (especially for gram-based products)
- Unique product identifiers across the system

## Performance Requirements

- Search response time: < 300ms
- Support up to 1000 products without performance degradation
- Real-time UI updates with optimistic rendering
- Efficient hierarchical recipe expansion
- Database query optimization with proper indexing

## Security Considerations

- Input validation and sanitization
- SQL injection prevention through ORM
- CSRF protection for forms
- Rate limiting on API endpoints
- Docker container security best practices

## Deployment Strategy

- Docker Compose for local development
- Container registry for image storage
- Environment-specific configuration
- Database migration scripts
- Health checks for all services

## Development Notes

- Focus on intuitive UX with minimal clicks
- Real-time feedback and validation
- Confirm destructive actions with dialogs
- Consistent error handling across services
- Comprehensive logging and monitoring
- Code formatting with Black (Python) and Prettier (TypeScript)
- Git hooks for code quality checks
