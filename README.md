# Chronic Pain Tracker

<p align="center">
  <img src="static/images/chronic-care-title.png" alt="Chronic Care Logo" height="60px">
</p>
A web-based application designed to help individuals with chronic pain manage medical appointments, documents, and reminders with ease. The application prioritizes simplicity, accessibility, and privacy, making it suitable for users of all ages, including caregivers.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [Team Members](#team-members)

---

## Overview

Chronic Pain Tracker is a Flask-based data analytics application that allows users to:

- Log appointments and view them in a calendar format
- Upload, categorize, and manage medical documents
- Get notified about upcoming appointments, expiring referrals, and insurance
- Share selected documents with medical providers or pharmacists

All data is stored privately per user, with secure authentication and controlled sharing options.

---

## Features

- **User Authentication**: Register and log in securely
- **Dashboard**: View upcoming appointments and alerts for expiring items
- **Appointments Manager**: Add, edit, delete and view past and upcoming medical appointments
- **Calendar View**: See all appointments and reminders in a month-based layout
- **Medical Document Manager**: Upload and manage test results, referrals, invoices, and prescriptions
- **Document Sharing**: Select and bundle documents to share externally
- **Profile Settings** (optional): Change email, password, and delete account

---

## Tech Stack

| Category | Tools/Libraries                          |
| -------- | ---------------------------------------- |
| Frontend | HTML, CSS, Bootstrap, JavaScript, JQuery |
| Backend  | Python, Flask                            |
| Database | SQLite with SQLAlchemy ORM               |
| Other    | AJAX, Flask-WTF, WTForms                 |

---

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/YOUR-TEAM/chronic-pain-tracker.git
   cd chronic-pain-tracker

   ```

2. **Create a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   Run the app
   flask run

   ```

4. **Open your browser and go to: http://localhost:5000**

## Team Members

<h2>Team Members</h2>

<table>
  <tr>
    <th>No.</th>
    <th>UWA ID</th>
    <th>Name</th>
    <th>GitHub Username</th>
  </tr>
  <tr>
    <td>1</td>
    <td>23032563</td>
    <td>Aleksandra Lozyk</td>
    <td>@olalozyk</td>
  </tr>
  <tr>
    <td>2</td>
    <td>23804104</td>
    <td>Siena Isaacs</td>
    <td>@enahen77</td>
  </tr>
  <tr>
    <td>3</td>
    <td>24250666</td>
    <td>Wei Shen Hong</td>
    <td>@weishen1113</td>
  </tr>
  <tr>
    <td>4</td>
    <td>23832333</td>
    <td>Dharun Somalingam</td>
    <td>@DharunSomalingam</td>
  </tr>
</table>
