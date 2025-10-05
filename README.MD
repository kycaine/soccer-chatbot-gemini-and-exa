# ⚽ Football Chatbot (Streamlit + Gemini + Exa)

An intelligent football chatbot built with **Python**, **Streamlit**, and **Google Gemini AI**, designed to deliver the latest football news, match insights, and Q&A.  
This project demonstrates modular design — easily extendable for other sports (e.g., badminton, basketball) in the future.

---

## 🧠 Features

- 💬 Chatbot interface powered by **Streamlit**
- 🧠 Uses **Google Gemini AI** for natural language understanding
- 🔍 Retrieves real-time football news using **Exa API**
- 🌐 User enters API keys directly in the web interface
- 🧩 Modular structure for multi-sport expansion

---

## 🧰 Tech Stack

| Component | Description |
|------------|-------------|
| **Python 3.10+** | Core programming language |
| **Streamlit** | Web-based chatbot UI |
| **google-generativeai** | Gemini AI SDK |
| **exa-py** | Exa API client for football news |
| **re / dataclasses** | For text cleaning and data models |

---

## 📦 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/kycaine/soccer-chatbot-gemini-and-exa
cd soccer-chatbot-gemini-and-exa
```

### 2️⃣ (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate       # On macOS/Linux
venv\Scripts\activate          # On Windows

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Running the App
Run the Streamlit app using:
```bash
streamlit run app.py
```

### 5️⃣ open the app on browser 
Once it starts, open the URL shown in your terminal (usually http://localhost:8501).

🔑 Entering API Keys
![alt text](/images/image.png)


### 6️⃣ Use it
![alt text](</images/Screenshot 2025-10-05 155450.png>)


