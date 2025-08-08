# Overview

This is a local-only clinic patient management system designed for use on two laptops connected via LAN. The application provides three main interfaces: Reception for patient registration and search, Consultant for managing patient queues and consultations, and Reports for generating consultation summaries within specified date ranges. The system operates entirely offline without any external services or internet connectivity requirements.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework
- **Flask** serves as the lightweight web framework with a simple structure
- **SQLAlchemy** provides ORM capabilities for database interactions
- **Werkzeug ProxyFix** handles reverse proxy headers for deployment flexibility

## Database Design
- **SQLite** database stored locally as `clinic.db` file
- Three main entities:
  - **Patient**: Stores registration details, demographics, and assigned consultant
  - **Consultant**: Manages doctor information with default seeding
  - **Visit**: Tracks consultation status (waiting/completed) and timestamps
- Automatic registration number generation using date-based prefixes
- Foreign key relationships maintain data integrity between patients, consultants, and visits

## Frontend Architecture
- **Server-side rendering** using Jinja2 templates with Bootstrap dark theme
- **Responsive design** with mobile-first approach using Bootstrap grid system
- **Interactive JavaScript** for real-time search, patient selection, and queue management
- **Print-optimized CSS** for generating patient consultation summaries

## Application Structure
- **Route-based organization** with separate modules for models, routes, and app configuration
- **Three main interfaces**: Reception (patient management), Consultant (queue management), Report (data analytics)
- **Real-time patient search** with partial matching on names and contact numbers
- **Session management** for maintaining consultant selections and patient states

## Data Flow
- Reception creates patients and assigns to consultants
- Consultants view assigned patients in chronological queues
- Visit status transitions from 'waiting' to 'completed' through consultant actions
- Reports aggregate completed visits by date ranges

# External Dependencies

## Frontend Libraries
- **Bootstrap CSS** (via CDN) for responsive UI components and dark theme
- **Feather Icons** (via CDN) for consistent iconography throughout the interface

## Python Packages
- **Flask** - Core web framework
- **Flask-SQLAlchemy** - Database ORM and management
- **SQLAlchemy** - Database toolkit and object-relational mapping
- **Werkzeug** - WSGI utilities and middleware

## Development Setup
- **SQLite** database file stored locally (no external database server required)
- **Static file serving** through Flask for CSS and JavaScript assets
- **Template rendering** using Jinja2 for dynamic HTML generation