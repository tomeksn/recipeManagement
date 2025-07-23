# PLANNING.md - Recipe Management System

## Vision & Goals

### Project Vision
Create a modern, scalable Recipe Management web application that enables production companies, laboratories, and industrial kitchens to efficiently manage product recipes with automatic ingredient calculations and hierarchical composition tracking.

### Primary Goals
- **Centralized Recipe Management**: Single source of truth for all product recipes
- **Flexible Unit Handling**: Support both piece-based and weight-based products with mixed units
- **Hierarchical Composition**: Enable multi-level ingredient relationships and expansion
- **Real-time Calculations**: Automatic scaling of ingredients based on target quantities
- **Intuitive User Experience**: Trello-like interface for easy recipe management
- **Data Integration**: Support for importing existing product databases

### Success Metrics
- Support 1000+ products without performance degradation
- Search response time < 300ms
- Intuitive UI requiring minimal training
- 99.9% uptime for production environments
- Real-time validation with immediate feedback

## Architecture Overview

### Microservices Architecture

#### Core Services

**1. Product Service**
- **Purpose**: Manages product CRUD operations, metadata, and search functionality
- **Responsibilities**:
  - Product creation, updates, deletion
  - Product search with fuzzy matching
  - Product type and unit management
  - Data validation and business rules
- **Technology**: Python Flask, SQLAlchemy, PostgreSQL
- **Database Schema**: `product_service`

**2. Recipe Service**
- **Purpose**: Handles recipe creation, modification, and hierarchical relationships
- **Responsibilities**:
  - Recipe CRUD operations
  - Ingredient management
  - Hierarchical recipe expansion
  - Circular dependency prevention
  - Recipe validation
- **Technology**: Python Flask, SQLAlchemy, PostgreSQL
- **Database Schema**: `recipe_service`

**3. Calculator Service**
- **Purpose**: Performs ingredient calculations and proportional scaling
- **Responsibilities**:
  - Quantity scaling for piece-based products
  - Proportional scaling for weight-based products
  - Mixed unit calculations
  - Result formatting and precision
- **Technology**: Python Flask, NumPy (for calculations)
- **Database Schema**: `calculator_service` (caching)

**4. API Gateway**
- **Purpose**: Routes requests, handles cross-cutting concerns
- **Responsibilities**:
  - Request routing to appropriate services
  - Authentication and authorization
  - Rate limiting
  - Request/response logging
  - API documentation aggregation
- **Technology**: Python Flask, Flask-CORS, Flask-Limiter

**5. Frontend Service**
- **Purpose**: React-based user interface with Trello-like design
- **Responsibilities**:
  - User interface components
  - State management
  - Real-time updates
  - Responsive design
  - Progressive Web App features
- **Technology**: React 18, TypeScript, Material-UI

### Service Communication

**Inter-Service Communication**
- RESTful HTTP APIs between services
- JSON payload format with standardized schemas
- Service discovery through Docker Compose networking
- Circuit breaker pattern for resilience
- Retry mechanisms with exponential backoff

**API Design Principles**
- RESTful resource-oriented URLs
- HTTP status codes for response status
- Consistent error response format
- API versioning (v1, v2, etc.)
- OpenAPI/Swagger documentation

### Database Strategy

**PostgreSQL Architecture**
- Single PostgreSQL 15 instance
- Separate schemas per microservice:
  - `product_service`: Products and metadata
  - `recipe_service`: Recipes and ingredients
  - `calculator_service`: Calculation cache and history
  - `gateway_service`: Authentication and logs

**Data Consistency**
- ACID transactions within services
- Event-driven updates between services
- Eventual consistency for cross-service data
- Database migration scripts per service

## Technology Stack

### Backend Technologies

**Core Framework**
- **Python 3.11+**: Primary programming language
- **Flask 2.3+**: Lightweight web framework
- **Flask-RESTful**: RESTful API development
- **Flask-SQLAlchemy**: ORM and database integration
- **Flask-Migrate**: Database migrations
- **Flask-SMOREST**: OpenAPI documentation
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-Limiter**: Rate limiting

**Database & Storage**
- **PostgreSQL 15**: Primary database
- **SQLAlchemy 2.0**: ORM with type hints
- **Alembic**: Database migration tool
- **Redis**: Caching and session storage
- **psycopg2**: PostgreSQL adapter

**Development & Testing**
- **pytest**: Unit and integration testing
- **pytest-flask**: Flask-specific testing utilities
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Static type checking
- **coverage**: Test coverage reporting

### Frontend Technologies

**Core Framework**
- **React 18**: User interface framework
- **TypeScript 5.0**: Type-safe JavaScript
- **Vite 4.0**: Build tool and development server
- **React Router v6**: Client-side routing

**UI & Styling**
- **Material-UI (MUI) 5**: Component library for Trello-like design
- **@mui/x-data-grid**: Advanced data grid components
- **@mui/x-tree-view**: Hierarchical tree components
- **@emotion/react**: CSS-in-JS styling
- **CSS Modules**: Component-scoped styling

**State Management**
- **React Query (TanStack Query)**: Server state management
- **React Context API**: Global client state
- **React Hook Form**: Form state management
- **Zustand**: Lightweight state management (if needed)

**Development Tools**
- **ESLint**: Code linting
- **Prettier**: Code formatting
- **React Testing Library**: Component testing
- **Playwright**: End-to-end testing
- **Storybook**: Component development

### Infrastructure & DevOps

**Containerization**
- **Docker**: Container runtime
- **Docker Compose**: Multi-container orchestration
- **Multi-stage builds**: Optimized container images
- **Health checks**: Container monitoring

**Reverse Proxy & Load Balancing**
- **Nginx**: Reverse proxy and static file serving
- **SSL/TLS termination**: Security layer
- **Load balancing**: Traffic distribution
- **Gzip compression**: Performance optimization

**Development Tools**
- **Git**: Version control
- **GitHub**: Repository hosting and CI/CD
- **GitHub Actions**: Automated testing and deployment
- **Docker Hub/GitHub Container Registry**: Container image storage

### Required Tools & Setup

#### Local Development Environment

**System Requirements**
- **Operating System**: Linux, macOS, or Windows with WSL2
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 20GB available space
- **Network**: Internet connection for package downloads

**Required Software**

1. **Database**
   - PostgreSQL 15+
   - pgAdmin (optional GUI)
   - psql (command-line client)

2. **Container Platform**
   - Docker 24.0+
   - Docker Compose 2.20+

3. **Backend Development**
   - Python 3.11+
   - pip (package manager)
   - virtualenv or pyenv
   - Git

4. **Frontend Development**
   - Node.js 18+ (LTS)
   - npm 9+ or yarn 3+
   - Modern web browser (Chrome, Firefox, Safari, Edge)

5. **Development Tools**
   - Code editor (VS Code recommended)
   - Postman or similar API testing tool
   - Terminal/Command line

#### Installation Guide

**1. PostgreSQL Setup**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql
brew services start postgresql

# Windows
# Download from postgresql.org
```

**2. Docker Setup**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# macOS
brew install docker docker-compose

# Windows
# Download Docker Desktop
```

**3. Python Environment**
```bash
# Install Python 3.11+
python3 --version
pip3 install virtualenv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

**4. Node.js Setup**
```bash
# Using Node Version Manager (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Or direct installation
# Download from nodejs.org
```

## Development Workflow

### Project Structure
```
recipe-management/
├── services/
│   ├── product-service/
│   │   ├── app/
│   │   ├── migrations/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── recipe-service/
│   │   ├── app/
│   │   ├── migrations/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── calculator-service/
│   │   ├── app/
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── api-gateway/
│       ├── app/
│       ├── tests/
│       ├── Dockerfile
│       └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── database/
│   ├── init-scripts/
│   └── migrations/
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
└── README.md
```

### Development Process

**1. Local Development**
- Each service runs in its own container
- Hot reload enabled for development
- Shared PostgreSQL database
- Nginx proxy for unified endpoint

**2. Version Control**
- Feature branch workflow
- Pull request reviews
- Automated testing on commits
- Semantic versioning

**3. Testing Strategy**
- Unit tests for business logic
- Integration tests for API endpoints
- Component tests for React components
- End-to-end tests for user workflows
- Minimum 80% code coverage

**4. Code Quality**
- Automated code formatting
- Linting and type checking
- Pre-commit hooks
- Code review requirements

## Security Considerations

### Backend Security
- Input validation and sanitization
- SQL injection prevention via ORM
- Rate limiting on API endpoints
- CORS configuration
- Environment variable secrets
- Container security best practices

### Frontend Security
- XSS prevention
- CSRF protection
- Secure API communication (HTTPS)
- Input validation
- Content Security Policy

### Database Security
- Connection encryption
- User authentication
- Role-based access control
- Regular security updates
- Backup encryption

## Performance Requirements

### Response Time Targets
- Product search: < 300ms
- Recipe calculations: < 500ms
- Page load time: < 2 seconds
- Database queries: < 100ms average

### Scalability Targets
- 1000+ products without degradation
- 100+ concurrent users
- 50+ requests per second per service
- Database connection pooling

### Optimization Strategies
- Database indexing
- Query optimization
- Caching strategies
- CDN for static assets
- Image optimization
- Code splitting

## Deployment Strategy

### Local Development
```yaml
# docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:15
  product-service:
    build: ./services/product-service
  recipe-service:
    build: ./services/recipe-service
  calculator-service:
    build: ./services/calculator-service
  api-gateway:
    build: ./services/api-gateway
  frontend:
    build: ./frontend
  nginx:
    image: nginx:alpine
```

### Production Deployment
- Docker Compose with production overrides
- Environment-specific configuration
- SSL/TLS certificates
- Database backups
- Monitoring and logging
- Health checks

## Risk Assessment & Mitigation

### Technical Risks
1. **Service Communication Failures**
   - Mitigation: Circuit breakers, retry logic, timeouts

2. **Database Performance Issues**
   - Mitigation: Query optimization, indexing, connection pooling

3. **Container Orchestration Complexity**
   - Mitigation: Comprehensive documentation, monitoring

### Business Risks
1. **User Adoption**
   - Mitigation: Intuitive UI design, user testing, training materials

2. **Data Migration Challenges**
   - Mitigation: Robust import validation, data mapping tools

3. **Performance Degradation**
   - Mitigation: Load testing, performance monitoring, scaling strategies

## Success Criteria

### Technical Success
- All services deployable via Docker Compose
- 99.9% uptime in production
- < 300ms search response time
- Zero data loss incidents
- Automated testing pipeline

### User Experience Success
- Intuitive Trello-like interface
- Real-time validation feedback
- Mobile-responsive design
- Minimal training required
- Positive user feedback

### Business Success
- Support for 1000+ products
- Successful data migration
- Integration with existing workflows
- Reduced recipe management time
- Improved data accuracy
