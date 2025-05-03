# Health Hub.AI - Multiple Disease Prediction Streamlit App

A unified AI-driven health & fitness platform — predict, train, plan, and secure your health journey, all in one place.

## Database Implementation

This application uses SQLite for data storage. The SQLite database is stored locally in the `data/healthhub.db` file. Key tables include:

- `users`: Doctors and trainers information
- `appointments`: Appointment/session bookings
- `health_records`: Patient health records with blockchain verification

## Getting Started

1. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:

   ```bash
   streamlit run app.py
   ```

The database will be automatically created on first run in the `data/` directory.

## Adding Test Data

To add test users (doctors and trainers), use the Admin Panel accessible from the app's sidebar.
