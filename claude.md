---
name: Federated Learning Backend
description: Detailed documentation for the federated learning backend project
type: project
---

# Federated Learning Backend

## Project Overview

This is a FastAPI-based backend service for a Federated Learning Platform. It provides REST API endpoints for managing federated learning jobs, models, clients, data quality, and platform settings. The backend integrates with FedLBE (Federated Learning Backend Engine) for actual federated learning orchestration.

## Architecture

### Core Components

1. **FastAPI Application** (`app/main.py`)
   - Main entry point with lifespan management
   - CORS configuration
   - API route registration
   - Health check endpoints

2. **FedLBE Integration** (`app/fedlbe/`)
   - `job_manager.py`: Manages job state synchronization with FedLBE
   - `ws_client.py`: WebSocket client for FedLBE communication
   - `storage_client.py`: Client for retrieving training results
   - `client_registry.py`: Manages registered edge devices

3. **API Modules** (`app/api/`)
   - `dashboard.py`: Dashboard statistics and overview
   - `job.py`: Job management (CRUD operations)
   - `model.py`: Model management and storage
   - `client.py`: Client registration and monitoring
   - `data_quality.py`: Data quality analysis
   - `settings.py`: Platform configuration
   - `router.py`: Central route aggregation

4. **Services Layer** (`app/services/`)
   - Service pattern implementation
   - Mock service implementations for testing
   - Business logic separation

5. **Data Layer**
   - `models/`: SQLAlchemy ORM models
   - `schemas/`: Pydantic schemas for validation
   - `database.py`: Database configuration and session management

### Key Features

- **Dual Mode Operation**: Real database mode and mock mode for development
- **Real-time Monitoring**: WebSocket integration for live updates
- **Security**: JWT authentication with configurable settings
- **Data Quality Analysis**: Comprehensive metrics across clients
- **Flexible Deployment**: Supports both development and production modes

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Application
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-change-in-production

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/federated_learning

# FedLBE Integration
FEDLBE_WS_URL=ws://localhost:8200
STORAGE_URL=http://localhost:5000

# JWT
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Logging
LOG_LEVEL=INFO
```

### Settings Management

Settings are defined in `app/config.py` using Pydantic Settings:
- Automatic environment variable loading
- Type validation
- Default values for development
- Field validators for complex configurations

## API Endpoints

### Dashboard API (`/api/dashboard`)
- `GET /stats` - Get dashboard statistics
- `GET /current-jobs` - Get current running jobs
- `GET /clients-info` - Get client information
- `GET /chart-data` - Get chart data for visualization

### Job Management API (`/api/job`)
- `POST /list` - List jobs with pagination
- `POST /create` - Create a new federated learning job
- `POST /update` - Update job configuration
- `GET /{job_id}` - Get job details
- `POST /{job_id}/stop` - Stop a running job
- `GET /{job_id}/metrics` - Get job metrics

### Model Management API (`/api/model`)
- `POST /list` - List models with pagination
- `POST /upload` - Upload a model
- `GET /{model_id}` - Get model details
- `POST /{model_id}/compare` - Compare models
- `POST /{model_id}/download` - Download model file

### Client Management API (`/api/client`)
- `POST /list` - List clients with pagination
- `POST /register` - Register a new client
- `GET /{client_id}` - Get client details
- `POST /{client_id}/heartbeat` - Update client heartbeat
- `GET /{client_id}/jobs` - Get client's participated jobs

### Data Quality API (`/api/dataQuality`)
- `GET /stats` - Get data quality statistics
- `GET /distribution` - Get quality distribution
- `GET /nodes` - Get node quality metrics
- `GET /warnings` - Get data quality warnings

### Settings API (`/api/settings`)
- `GET /get` - Get current settings
- `POST /update` - Update platform settings
- `GET /connection` - Get connection settings
- `POST /connection/test` - Test connection to FedLBE

## Database Schema

### Core Models

1. **Job** (`app/models/job.py`)
   ```python
   id, name, description, status, job_type
   current_round, total_rounds, accuracy, loss
   config (JSON), created_at, started_at, completed_at
   ```

2. **Model** (`app/models/model.py`)
   ```python
   id, name, job_id, accuracy, loss, created_at
   framework, parameters, size, architecture, dataset
   ```

3. **Client** (`app/models/client.py`)
   ```python
   id, name, status, device_type, connected_at
   last_heartbeat, device_info (JSON), resource_usage (JSON)
   ```

4. **User** (`app/models/user.py`)
   ```python
   id, username, email, hashed_password, role, created_at
   ```

5. **Settings** (`app/models/settings.py`)
   ```python
   id, key, value, category, updated_at
   ```

## Mock Mode

The application supports mock mode for development and testing:

- Enable by setting environment variables or modifying `app/utils/mock_data.py`
- Generates realistic mock data for all entities
- No database connection required
- Full API functionality available

## Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Test Structure

- `tests/conftest.py`: Test configuration and fixtures
- `tests/test_api.py`: API endpoint tests
- Tests cover all major endpoints and status codes

## Development Workflow

### Starting the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

### API Documentation

- Swagger UI: `http://localhost:3000/docs`
- ReDoc: `http://localhost:3000/redoc`

### Code Organization

- **Modular Structure**: Each feature has its own API module and service
- **Dependency Injection**: Services are injected into API endpoints
- **Pydantic Validation**: All data structures use Pydantic models
- **Error Handling**: Consistent error responses with proper HTTP codes

## Security Considerations

- JWT-based authentication
- CORS configuration for cross-origin requests
- Input validation with Pydantic schemas
- Secure communication with FedLBE (WebSocket)
- Configurable security settings

## Performance Optimizations

- Database connection pooling
- Async/await throughout the application
- Efficient pagination for large datasets
- WebSocket for real-time updates
- Caching considerations for frequently accessed data

## Deployment

### Production Setup

1. **Environment Variables**: Set all production values
2. **Database**: Use production PostgreSQL instance
3. **FedLBE**: Ensure FedLBE services are running and accessible
4. **SSL/TLS**: Configure HTTPS for production
5. **Monitoring**: Set up logging and monitoring

### Docker Support

The project can be containerized:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 3000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
```

## Common Issues and Solutions

1. **Database Connection Issues**
   - Check DATABASE_URL configuration
   - Ensure database service is running
   - Verify credentials and permissions

2. **FedLBE Connection Issues**
   - Check FEDLBE_WS_URL configuration
   - Ensure FedLBE service is running
   - Verify WebSocket connectivity

3. **CORS Issues**
   - Check CORS_ORIGINS configuration
   - Ensure frontend URL is included in allowed origins

## Contributing

1. Follow the existing code structure
2. Add appropriate tests for new features
3. Update documentation when adding APIs
4. Use type hints consistently
5. Follow PEP 8 style guidelines

## Future Enhancements

- gRPC support for high-performance communication
- Advanced caching strategies
- Detailed monitoring and metrics
- Multi-tenant support
- Enhanced security features (RBAC, audit logging)