# SmartQ 2.0 – Smart Hospital Queue Management System

## Project Overview
SmartQ 2.0 is a web-based hospital queue management system developed using Python and Streamlit. It helps patients book tokens online, monitor their waiting status, and visit the doctor when their token is called, reducing the need to stand in long queues.

## Features
- Patient Registration and Login
- Online Token Booking
- Automatic Token Generation
- Live Waiting List
- Estimated Waiting Time
- QR Code Generation and Scanning
- Admin Dashboard
- Call Next Patient Functionality
- Counter Number Display
- Simulated SMS Notifications
- Automatic Dashboard Updates

## Technologies Used
- Python
- Streamlit
- SQLite
- Pandas
- QR Code

## Project Structure
```text
SmartQ2_Final/
│
├── app.py
├── database.py
├── queue_manager.py
├── sms_service.py
├── requirements.txt
└── .gitignore
```

## Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/kolupula-akshitha/SmartQ-2.0.git
```

2. Open the project folder:

```bash
cd SmartQ-2.0
```

3. Create a virtual environment:

```bash
python -m venv venv
```

4. Activate the environment on Windows:

```bash
venv\Scripts\activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Run the application:

```bash
streamlit run app.py
```

## Admin Login
- Username: admin
- Password: admin123

## Notification
SMS notifications in this project are simulated for demonstration purposes. No real SMS messages are sent.

## Developer
Kolupula Akshitha  
B.Tech – Computer Science and Engineering (Data Science)

## GitHub Repository
https://github.com/kolupula-akshitha/SmartQ-2.0