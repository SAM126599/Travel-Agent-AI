# ✈️ AI Travel Agent – Frontend

A modern and interactive frontend for the **AI Travel Agent** built with **Streamlit**. This application enables users to enter travel queries in natural language and receive AI-generated flight and hotel recommendations through a clean, responsive web interface.

## 📌 Features

* 🌍 Simple and intuitive user interface
* ✈️ Natural language travel query input
* 🏨 Displays AI-generated flight and hotel recommendations
* 💰 Shows travel prices and booking information
* 📧 Send travel details directly via email
* 🎨 Custom CSS for an enhanced user experience
* 🔄 Session state management for maintaining user interactions
* ⚡ Fast and lightweight Streamlit application

## 🛠️ Technologies Used

* Python
* Streamlit
* LangChain
* LangGraph
* OpenAI API
* SMTP Email Service
* Python Dotenv

## 📂 Project Structure

```text
frontend/
│── app.py                 # Main Streamlit application
│── requirements.txt       # Project dependencies
│── .env                   # Environment variables
│── README.md              # Project documentation
│── images/
│   └── ai-travel.png      # Sidebar image
```

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-travel-agent-frontend.git
cd ai-travel-agent-frontend
```

### 2. Create a virtual environment (Optional)

```bash
python -m venv venv
```

Activate the environment:

**Windows**

```bash
venv\Scripts\activate
```

**macOS/Linux**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and add:

```env
OPENAI_API_KEY=your_openai_api_key
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

### 5. Run the application

```bash
streamlit run app.py
```

The application will start locally at:

```text
http://localhost:8501
```

## 💻 How to Use

1. Launch the Streamlit application.
2. Enter your travel query (for example, "Plan a 5-day trip to Dubai with flights and hotels").
3. Click **Get Travel Information**.
4. View the AI-generated travel recommendations.
5. Optionally send the travel details via email using the integrated email form.

## 📸 Interface

The frontend includes:

* AI Travel Agent dashboard
* Travel query text area
* Travel information display section
* Email sharing form
* Sidebar branding image

## 🔗 Backend Integration

This frontend communicates with the AI backend, which is responsible for:

* Processing user queries
* Calling flight and hotel search tools
* Generating AI responses
* Managing conversation workflow using LangGraph

## 🔮 Future Improvements

* Dark mode support
* Chat-style conversation interface
* Voice input
* Interactive maps
* Travel itinerary timeline
* User authentication
* Booking integration
* Mobile-responsive enhancements

## 📄 License

This project is developed for educational and demonstration purposes.
