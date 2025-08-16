# Overview

This is a local-only clinic patient management system for "The Kids Clinic / Allergy and Asthma Center" designed for use on two dedicated laptops: one for the consultant and one for the receptionist. The application provides specialized interfaces: Consultant view (completely read-only display showing what receptionist does), Receptionist view (full patient management, registration, queue management, and administrative functions), and Reports for generating consultation summaries. The system operates entirely offline with automated shortcuts that remember laptop roles and auto-start/close the server.

**Current Status**: Complete system ready for deployment with automated shortcuts, cross-device printing setup, and comprehensive documentation.

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
- **Role-based interfaces**: Consultant (read-only view), Receptionist (full management), Reports (data analytics)
- **Automated deployment**: Shortcuts remember laptop roles and auto-start appropriate interface
- **Enhanced patient data**: Weight tracking per visit, email addresses, parent names
- **Streamlined workflow**: Receptionist handles all patient actions, consultant only views information
- **Compact print layouts**: Optimized patient information with age integrated into birth date

## Data Flow
- Receptionist creates patients with comprehensive data (weight, email, parent names)
- Consultant views assigned patients in completely read-only display (no interactions)
- Patient information automatically appears in consultant view when receptionist selects patients
- Receptionist manages all visit status transitions and patient actions
- Weight is recorded for each visit with historical tracking
- Reports aggregate completed visits by date ranges with enhanced patient data
- Real-time synchronization between receptionist actions and consultant display
- Automated startup shortcuts for role-based laptop deployment
- Cross-device printing configuration with network printer sharing
- Auto-refresh queue management (10-second intervals) with manual refresh option
- Multiple patient visits per day support with enhanced visit tracking
- Network configuration: Receptionist laptop (192.168.1.2), Consultant laptop (192.168.1.12)

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