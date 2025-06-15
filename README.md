# Travel Expense Tracker

A Streamlit-based web application for tracking personal and group travel expenses.

## Features

- User authentication (login/signup)
- Personal expense tracking
- Group expense management
- Expense analytics and visualization
- Group creation and management
- Group expense splitting and balance tracking

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd travel-expense-tracker
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run main.py
```

## Usage

1. Open your web browser and navigate to `http://localhost:8501`
2. Create a new account or log in with existing credentials
3. Start tracking your expenses!

### Personal Expenses

- Add new expenses with date, amount, category, and description
- View expense analytics including total spent, monthly breakdowns, and category distribution
- Track your spending patterns over time

### Group Expenses

- Create new groups and invite members
- Add group expenses and track shared costs
- View group balances and settle debts
- Monitor group spending patterns

## Data Storage

The application uses JSON files for data storage:
- `users.json`: User credentials
- `expenses.json`: Expense records
- `groups.json`: Group information and memberships

## Contributing

Feel free to submit issues and enhancement requests!

---

## 🚀 Features

- 📅 Add travel expenses with date, category, amount, location & description
- 🔍 Filter by date range or category
- 📊 Visual summary with pie and bar charts
- ☁ Real-time data sync using Google Sheets
- 🔐 Secrets managed securely with Streamlit Cloud
- 📥 CSV/Excel export support (coming soon)

---

## 🛠 Tech Stack

| Layer        | Tools Used                        |
|--------------|-----------------------------------|
| Frontend     | Streamlit                         |
| Backend/API  | Python + gspread + pandas         |
| Data Store   | Google Sheets                     |
| Visualization| Plotly                            |

---

## 💻 How to Run Locally

### 🔧 Prerequisites
- Python 3.9 or later
- Streamlit, gspread, oauth2client, pandas, plotly

### 📦 Installation

```bash
git clone https://github.com/kalmeshsaunshi01/travel-expense-tracker.git
cd travel-expense-tracker
pip install -r requirements.txt

