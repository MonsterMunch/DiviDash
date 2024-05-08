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

### 2. Backend

#### Flask or FastAPI
- Python frameworks for building APIs.
- **Endpoints**:
  - `GET /portfolios`: Retrieve portfolio details.
  - `POST /portfolio`: Update or create a portfolio.
  - `GET /dividends`: Calculate dividends for given portfolio settings.

### 3. Frontend

#### React or Vue.js
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

## Markdown Tips for GitHub

- **Use Headers**: Organize content with headers to make information easy to find.
- **Code Blocks**: Use triple backticks ``` to format code blocks.
- **Links and Images**: Use Markdown syntax to add links and images to enrich the documentation.
