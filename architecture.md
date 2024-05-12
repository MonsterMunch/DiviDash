# DividendDashboard Architecture

## Project Overview

**DividendDashboard** is a web application designed to visualize and manage monthly dividend income from investment portfolios. This tool allows users to modify portfolio allocations and immediately see the impact on expected dividend payouts.

## System Architecture

### 1. Data Storage

#### SQLite
- A lightweight database perfect for small projects.
- **Schema**:
  - **Assets Table**: Stores details like name, type, dividend yield.
  - **Portfolios Table**: Links assets to portfolios with allocation percentages.

## 2. Backend

### Flask
- **Framework**: Flask is used as the Python framework for building the API.
- **File Structure**:
  - `app.py`: Initializes the Flask application and includes basic configurations.
  - `models.py`: Contains all SQLAlchemy database models, defining the structure of the database.
  - `routes.py`: Manages all the routes and endpoints, separating routing logic from the application setup for cleaner code management.

### API Endpoints
Endpoints are defined in `routes.py` to handle various functionalities:

- `GET /portfolios`: Retrieve details of all portfolios. This endpoint fetches and returns data about every portfolio stored in the database.
- `POST /portfolio`: Update an existing portfolio or create a new one. This endpoint handles both the creation of new portfolios and updating existing ones based on the provided data.
- `GET /dividends/<int:portfolio_id>`: Calculate and return dividends for a given portfolio based on its settings and current assets.

Each endpoint uses models defined in `models.py` to interact with the database, ensuring data persistence and integrity.


### 3. Frontend

#### React
- To build interactive UIs.
- **Components**:
  - **Portfolio Editor**: Users can modify asset allocations.
  - **Dividend Visualizer**: Shows monthly dividends based on current portfolio.

### 4. Version Control and Deployment

#### GitHub
- Hosts the repository and manages version control.
- **CI/CD**: GitHub Actions for automated testing and deployment.
- **Deployment**: Frontend on Netlify, Backend on Heroku.

## Implementation Phases

### Phase 1: Basic Backend and Database
- **Goal**: Set up the database and basic API functionality.
- **Tasks**:
  - Define database schema and initialize SQLite database.
  - Develop basic CRUD operations for assets and portfolios using Flask.
  - Write unit tests for API endpoints.

### Phase 2: Basic GUI Development
- **Goal**: Create a simple UI to interact with the backend.
- **Tasks**:
  - Set up React application.
  - Develop components for displaying and editing portfolios.
  - Integrate with the backend to retrieve and send data.

### Phase 3: Dividend Calculation and Display
- **Goal**: Allow users to view calculated dividends based on portfolios.
- **Tasks**:
  - Implement the dividend calculation logic in the backend.
  - Create a dividend display component in the frontend.
  - Enhance the API to support dividend calculation requests.

### Phase 4: Advanced Features and Deployment
- **Goal**: Add advanced functionalities and deploy the application.
- **Tasks**:
  - Add user authentication and portfolio saving/loading.
  - Set up GitHub Actions for CI/CD pipeline.
  - Deploy the frontend to Netlify and the backend to Heroku.

### Phase 5: Quality Assurance and Final Testing
- **Goal**: Ensure the application is robust and user-friendly.
- **Tasks**:
  - Conduct extensive testing including unit, integration, and e2e tests.
  - Perform usability testing to gather user feedback.
  - Make final adjustments based on test results and feedback.


## Overview of the Flask Application Components:
Flask App (app): The core of your web application, responsible for handling requests, routing them to the appropriate functions, and returning responses.
SQLAlchemy (db): Serves as the Object-Relational Mapper (ORM) that facilitates interactions between Python objects and the database.
Models (Asset, Portfolio): Define the database schema and data interactions.
Blueprints (main): A way to organize a group of related views and other code. It’s like a mini-application that can be registered on the actual application.
Routes/Views: Functions that respond to requests to different URLs.
Templates: HTML files that allow Python-like expressions and control flow and are used to render the website content dynamically.

## Explanation and Diagram:
Flask Application (app): Initiates a Flask application instance, handles configurations (like the database URI), and registers blueprints and routes.
SQLAlchemy (db): Links to the Flask app through the configuration and is responsible for all database interactions.
Models (Asset, Portfolio): Define the structure of your database tables and include methods to represent object instances conveniently.
Blueprint (main): Defines routes that are registered under a blueprint to organize code better.
Routes/Views: Different endpoints (like /, /assets, /portfolios) defined either directly on the app or through a blueprint to handle various URLs.
Templates: These are HTML files with placeholders for displaying data passed from the Flask views.
### The diagram below illustrates these components and their relationships:

```
+------------------+
| Flask Application|
+------------------+
        ||
        || Registers
        \/
+------------------+    +---------------+    +---------------+
|  Blueprint (main)|----|  Route (/)    |    | Route (/ports)|
+------------------+    +---------------+    +---------------+
        ||
        || Uses
        \/
+------------------+    +----------------------+
| SQLAlchemy (db)  |----| Models (Asset, Port) |
+------------------+    +----------------------+
        ||
        || Interacts With
        \/
+------------------+
| SQLite Database  |
+------------------+
```

Clarifications:
Routes defined in the blueprint and directly on the app: Notice that you have routes defined in both the blueprint and directly on the application. This setup works but can cause confusion if routes overlap. Make sure routes names and endpoints are managed carefully to avoid collisions.
Rendering templates: render_template is used to generate HTML from templates. It fills placeholders in your templates with actual data, allowing dynamic content rendering based on the current state of the database.
- **Code Blocks**: Use triple backticks ``` to format code blocks.
- **Links and Images**: Use Markdown syntax to add links and images to enrich the documentation.
