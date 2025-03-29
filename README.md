# Perfect Shade team's implementation of GatherSpot

## Overview
GatherSpot is a one-stop platform for discovering and managing eveents, catering to both individuals and organizations. Users can search for events, sign up, create their own, and engage with other users through reviews, ratings, and social interactions.


## Start the project
1. Clone the project from remote repository
```shell
git clone https://github.com/Valentine-456/PerfectShade_GatherSpot.git
cd ./PerfectShade_GatherSpot
```

2. Set up Python virtual environment
```shell
# If you're in another venv or conda env, deactivate it
deactivate  
# or `conda deactivate`
python -m venv .venv

source .venv/Scripts/activate
# OR for PowerShell:
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

3. Run the project
```shell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

4. To start working on a feature
```shell
git checkout -b feature/example
# work on code...
git add .
git commit -m "Example message"
git push -u origin feature/example
```

5. Sync with main regularly
Before starting new work or after someone merges a PR:
```shell
git checkout main
git pull origin main
```


You will be able to accesss the project on [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Technologies Used
- **Backend:** Python + Django
- **Frontend:** JavaScript/TypeScript + React
- **Project Management:** Jira (for time estimation, sprint planning, and task tracking)
- **Version Control:** GitHub (for code collaboration and repository management)
- **Google Maps API:** Used for displaying event locations interactively

## Project Organization
- **[Link to Jira](https://perfectshade.atlassian.net/jira/people)**
- Tasks are assigned based on developers' skill sets
- **Story Points** are used to estimate task complexity
- Roles:
  - **Backend Developers:** Implement API endpoints, database models, and business logic
  - **Frontend Developers:** Develop UI components and handle API integration
  - **Project Managers:** Oversee project timeline and ensure deliverables are met

## System Architecture
GatherSpot follows a **client-server architecture** to ensure scalability and efficiency. It consists of:
- **Client:** A React-based frontend that handles user interactions and renders event-related data
- **Server:** A Django backend that processes client requests, manages business logic, and interacts with the database
- **Database:** Stores user information, events, tickets, and reviews
- **Google Maps API Integration:** Enhances event discovery by visualizing event locations

## Core Functionalities
### For Individual Users
- Discover and filter events based on interests
- View event details (including map location)
- Sign up for events and invite friends
- Create and manage events
- Leave reviews and ratings
- Connect with other users (send friend requests, view profiles)

### For Organizations
- Create and promote events for maximum reach
- Verify accounts for credibility
- Manage event listings with additional promotional features

### For Administrators
- Manage user accounts and events
- Monitor platform content and enforce policies
- Verify organization accounts

## API Endpoints
The system utilizes a **RESTful API** over HTTPS, with messages structured in JSON format.

### Key Operations
- **Account Management:** User authentication (signup, login), profile updates, and account deletion
- **Event Management:** Create, modify, delete, and promote events
- **Discovery & Search:** Search for users and events with filtering options
- **Notifications:** Receive updates on events, friend requests, and invitations

## Development Setup
### Prerequisites
- **Backend:** Python 3.x, Django
- **Frontend:** Node.js, npm/yarn, React
- **Database:** PostgreSQL (or SQLite for development)

## Contribution Guidelines
- Use feature branches and follow **Git Flow**
- Code should follow **PEP 8** for Python and **ESLint rules** for JavaScript/TypeScript
- Submit **Pull Requests** with clear descriptions and appropriate documentation
- Write **unit tests** for backend and frontend functionalities

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact
For further questions or contributions, please reach out to the project team via GitHub Issues.

