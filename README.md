---
title: Ekalavya
emoji: 🎓
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🎓 Ekalavya — AI-Powered Early Intervention Platform

> **Empowering Early Educational Intervention Through Artificial Intelligence**

Ekalavya is an AI-powered educational decision support platform that helps identify students who may require academic support before learning challenges become critical. By analyzing educational, demographic, and socioeconomic indicators, the platform predicts student learning outcomes and provides actionable recommendations to educators, NGOs, mentors, volunteers, and community learning centres.

> **Educational Purpose Only:** Ekalavya is intended for educational research, demonstration, and decision-support purposes. It complements—not replaces—professional educational assessment and intervention.

---

## 🌍 Mission

Every child deserves equal opportunities to learn and succeed.

Ekalavya empowers educators and community organizations with AI-driven insights to enable **early identification**, **timely intervention**, and **personalized educational support** for underprivileged and vulnerable learners.

---

# ✨ Key Features

### 🤖 AI-Powered Student Assessment
Analyzes **29 educational, demographic, and socioeconomic factors** to evaluate student learning outcomes.

### 📊 Early Risk Prediction

Classifies students into one of three categories:

- ✅ On Track
- ⚠️ At Risk
- 🚨 Dropout Risk

---

### 🧠 Intelligent Educational Insights

Automatically generates:

- Student Readiness Score
- Risk Assessment
- Academic Strength Analysis
- Learning Challenges
- Personalized Recommendations
- Educational Summary

---

### 📈 Interactive Dashboard

Modern dashboard including:

- Radar Chart
- Risk Meter
- Academic Performance Visualization
- Confidence Indicator
- Educational Summary Cards
- AI Recommendation Panel

---

### 📄 Download Assessment Report

Generate a professional assessment report containing:

- Student Information
- Prediction Results
- Risk Analysis
- AI Recommendations
- Visual Analytics

---

### 🌙 Dark Mode

- Automatic Theme Detection
- Manual Theme Toggle
- Persistent User Preference

---

### 📱 Responsive Design

Optimized for:

- Desktop
- Laptop
- Tablet
- Mobile

---

### ⚡ Real-Time Prediction

Student information is processed in real time.

No student information is permanently stored.

---

### 🔒 Secure Configuration

Application credentials are securely managed using environment variables.

No sensitive information is hardcoded.

---

# 🏗 Project Structure

```
Ekalavya/
│
├── app.py
├── Dockerfile
├── README.md
├── requirements.txt
│
├── utils/
│   ├── __init__.py
│   └── ibm_wml.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── assessment.html
│   └── result.html
│
└── static/
    ├── css/
    │   └── styles.css
    │
    └── js/
        └── main.js
```

---

# 🚀 Quick Start

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/Ekalavya.git

cd Ekalavya
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file.

```env
IBM_API_KEY=your_api_key

IBM_WML_URL=https://your-region.ml.cloud.ibm.com

IBM_SPACE_ID=your_space_id

IBM_DEPLOYMENT_ID=your_deployment_id

FLASK_SECRET_KEY=your_secret_key
```

---

## 5. Run Application

```bash
python app.py
```

Open your browser:

```
http://localhost:5000
```

---

# 🧠 Machine Learning Workflow

```
Student Assessment
        │
        ▼
Input Validation
        │
        ▼
Machine Learning Prediction
        │
        ▼
Educational Risk Classification
        │
        ▼
AI Insight Generation
        │
        ▼
Personalized Recommendations
        │
        ▼
Interactive Dashboard
        │
        ▼
Assessment Report
```

---

# 📊 Dataset Information

| Property | Value |
|-----------|-------|
| Dataset | Ekalavya Student Dataset |
| Dataset Type | Synthetic Educational Dataset |
| Records | 10,000 |
| Features | 29 |
| Prediction Classes | 3 |
| Prediction Type | Multiclass Classification |

---

## Prediction Classes

- ✅ On Track
- ⚠️ At Risk
- 🚨 Dropout Risk

---

## Features Used

The model evaluates multiple educational indicators including:

- Age
- Gender
- Class Grade
- School Type
- Attendance Percentage
- Mathematics Score
- Science Score
- English Score
- Social Science Score
- Previous Academic Performance
- Study Hours
- Homework Completion
- Learning Difficulty
- Internet Access
- Digital Device Availability
- Parent Education
- Parent Occupation
- Annual Family Income
- Family Size
- Distance to School
- Transportation
- Scholarship Status
- Mentoring Support
- Extracurricular Participation
- Health Issues
- Family Dropout History
- Motivation Level
- Teacher Assessment

---

# 💻 Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend Programming |
| Flask | Web Framework |
| Machine Learning | Student Risk Prediction |
| HTML5 | Frontend |
| CSS3 | Styling |
| JavaScript | User Interaction |
| Bootstrap | Responsive UI |
| Chart.js | Data Visualization |
| Gunicorn | Production Server |
| Docker | Containerization |

---

# 🐳 Docker Deployment

Build the Docker image:

```bash
docker build -t ekalavya .
```

Run the container:

```bash
docker run -p 5000:5000 --env-file .env ekalavya
```

---

# 🔒 Security

- Environment variables for credentials
- No hardcoded secrets
- Secure API communication
- Input validation
- HTTPS recommended in production

Generate a Flask Secret Key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

# 📦 Dependencies

| Package | Purpose |
|----------|---------|
| Flask | Web Framework |
| Werkzeug | WSGI Utilities |
| python-dotenv | Environment Variables |
| requests | REST API Communication |
| gunicorn | Production Server |

---

# 🚀 Future Roadmap

- Explainable AI (Feature Importance)
- Student Progress Tracking
- NGO Dashboard
- Teacher Dashboard
- Offline Assessment
- Multi-language Support
- Community Analytics
- Role-Based Authentication
- Mobile Application
- Cloud Database Integration

---

# 🤝 Contributing

Contributions are welcome.

Feel free to fork the repository, improve the project, and submit a pull request.

---

# 📄 License

This project is licensed under the **MIT License**.

---

# ⚠️ Disclaimer

Ekalavya is an educational decision-support platform developed for research, learning, and demonstration purposes.

The predictions generated by this platform are intended to assist educators, mentors, volunteers, NGOs, and community organizations in making informed educational decisions.

They should **not** be considered a substitute for professional educational evaluation or institutional decision-making.

---

# ❤️ Acknowledgements

Built with ❤️ using **Python**, **Flask**, **Machine Learning**, **Bootstrap**, **Chart.js**, **Docker**, and modern web technologies to promote **inclusive**, **data-driven**, and **early educational intervention**.

---

## ⭐ Support

If you found this project helpful, consider giving it a ⭐ on GitHub.

Your support helps improve and expand Ekalavya for the benefit of educators and learners.