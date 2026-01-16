# 🚞 VoyageSense

**VoyageSense** is an intelligent, AI-powered travel recommendation system designed to help users discover the perfect Indian travel destinations based on their personalized preferences.

## 🚀 Features

-   **Personalized Recommendations**: Uses Content-Based Filtering (Cosine Similarity) to match destinations with user interests (Nature, Heritage, Adventure, etc.).
-   **AI Explanations**: Integrates **Google Gemini Pro** to generate personalized narratives explaining *why* a destination fits the user.
-   **Sentiment Analysis**: Analyzes synthetic reviews using **NLTK VADER** to gauge visitor sentiment.
-   **Immersive Experience**: Embeds relevant **YouTube Travel Vlogs** directly in the UI.
-   **Smart Constraints**: Filters based on Budget, Duration, and Travel Zone.

## 🛠️ Tech Stack

-   **Frontend**: Streamlit
-   **Backend**: Python, SQLite
-   **ML/NLP**: Scikit-Learn, NLTK
-   **APIs**: Google Gemini (GenAI), Google YouTube Data API

## 📦 Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/zach-codes932/VoyageSense.git
    cd VoyageSense
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup API Keys**
    This project requires API keys for Google Gemini and YouTube.
    
    Create a file named `src/config.py` (this file is git-ignored for security):
    ```python
    # src/config.py
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
    GEMINI_MODEL = "gemini-1.5-flash"
    YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"
    ```

4.  **Initialize Database (First Run Only)**
    ```bash
    python src/setup_database.py
    ```

5.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

## 📂 Project Structure

-   `app.py`: Main Streamlit application entry point.
-   `src/`: Core logic (Recommender, Feature Engine, Database Setup).
-   `data/`: SQLite database and processed datasets.
-   `notebooks/`: Jupyter notebooks for data analysis and experiments.

## 📜 License

This project is open-source.
