# Recipe Management System

A comprehensive web application for managing product recipes with microservices architecture, designed for production companies, laboratories, and industrial kitchens.

## Features

- **Product Management**: Add, modify, and search products with fuzzy search capabilities
- **Recipe Management**: Create hierarchical recipes with automatic ingredient calculations
- **Calculator Service**: Proportional scaling for specified product quantities
- **Trello-like UI**: Intuitive drag-and-drop interface with Material-UI components
- **Microservices Architecture**: Scalable backend with independent services

## Architecture

### Backend Services
- **Product Service**: Product CRUD operations and search functionality
- **Recipe Service**: Recipe creation and hierarchical relationship management
- **Calculator Service**: Ingredient calculations and proportional scaling
- **API Gateway**: Unified API routing and cross-cutting concerns

### Frontend
- **React 18** with TypeScript
- **Material-UI** for Trello-like card components
- **React Query** for server state management
- **Vite** for fast development and builds

### Database
- **PostgreSQL 15** with separate schemas per service
- **Flask-SQLAlchemy** ORM with migration support

## Technology Stack

- **Backend**: Python 3.11+, Flask, PostgreSQL 15
- **Frontend**: React 18, TypeScript, Material-UI, Vite
- **Infrastructure**: Docker, Docker Compose, Nginx
- **Documentation**: OpenAPI/Swagger

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15
- Docker & Docker Compose

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd recipe-management
   ```

2. **Setup Python environment**
   ```bash
   python -m venv recipe_env
   source recipe_env/bin/activate  # On Windows: recipe_env\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup database**
   ```bash
   # Create PostgreSQL database
   createdb recipe_management_dev
   
   # Run migrations
   flask db upgrade
   ```

4. **Start development servers**
   ```bash
   # Backend services
   docker-compose up -d
   
   # Frontend development server
   cd frontend
   npm install
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - API Gateway: http://localhost:8000

## Project Structure

```
recipe-management/
├── services/
│   ├── product-service/       # Product management API
│   ├── recipe-service/        # Recipe management API
│   ├── calculator-service/    # Calculation engine
│   └── api-gateway/          # API Gateway and routing
├── frontend/                 # React TypeScript application
├── database/                 # Database schemas and migrations
├── docker-compose.yml        # Development environment
├── nginx.conf               # Reverse proxy configuration
└── README.md
```

## Key Business Logic

### Unit Handling
- **Piece-based products**: Ingredients scaled by multiplication
- **Gram-based products**: Ingredients scaled proportionally by weight
- **Mixed units**: Support for both pieces and grams within recipes

### Recipe Calculator
- **Piece products**: Multiply all ingredients by target quantity
- **Gram products**: Scale ingredients proportionally to target weight
- **Precision**: 2 decimal places for grams, whole numbers for pieces

### Hierarchical Composition
- **Semi-products**: Can be expanded to show their own ingredients
- **Multi-level support**: Unlimited hierarchy depth
- **Circular dependency prevention**: Built-in validation

## API Documentation

Once the services are running, comprehensive API documentation is available at:
- Product Service: http://localhost:8001/docs
- Recipe Service: http://localhost:8002/docs
- Calculator Service: http://localhost:8003/docs
- Unified API: http://localhost:8000/docs

## Development

### Code Quality Standards
- **Python**: Black formatting, Flake8 linting, MyPy type checking
- **TypeScript**: Prettier formatting, ESLint linting
- **Testing**: Minimum 80% code coverage
- **Git**: Feature branch workflow with PR reviews

### Performance Requirements
- Search response time: < 300ms
- Support for 1000+ products
- Database queries: < 100ms average
- API responses: < 500ms

### Testing
```bash
# Backend tests
python -m pytest

# Frontend tests
cd frontend
npm test

# End-to-end tests
npm run test:e2e
```

## Docker Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions, please open an issue in the GitHub repository.
