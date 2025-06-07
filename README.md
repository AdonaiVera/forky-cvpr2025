# Forky for CVPR: Your AI Research Companion

🌟 Powered by Google Cloud credits through the #AISprint program ✨


https://github.com/user-attachments/assets/cdd04252-d8bb-49e3-9679-702c44092c75


I know how challenging it can be to navigate through CVPR's massive collection of over 2,500 amazing papers from around the world. The fear of missing out on groundbreaking research that could help your company, research group, or personal project is real. That's why I created Forky for CVPR - to make your conference experience more manageable and productive!

## 🎯 What Forky for CVPR Does

Forky for CVPR helps you navigate through the overwhelming number of papers at CVPR 2025 by:

1. **Smart Paper Search**: Using MongoDB Atlas vector search to find the top 15 most relevant papers based on your query
2. **AI-Powered Ranking**: Leveraging Gemini to analyze and rank the top 5 papers that best match your interests
3. **Detailed Match Reasons**: Providing clear explanations of why each paper is relevant to your research
4. **Poster Session Info**: Including poster session and location details for easy navigation at the conference

## 🚀 How It Works

1. **Paper Collection**: Retrieves the complete list of CVPR 2025 papers
2. **Vector Search**: Uses MongoDB Atlas vector search to find the top 15 most similar papers
3. **AI Analysis**: Employs Gemini to analyze and rank the top 5 papers
4. **Smart Recommendations**: Provides detailed explanations of why each paper is relevant to your query

## 🛠️ Technology Stack

- **FastAPI**: High-performance web framework
- **Gemini 2.0**: Google's advanced AI model for paper analysis
- **MongoDB Atlas**: Vector search for efficient paper retrieval
- **Tailwind CSS**: Modern UI design

## 🎯 Core Features

### Smart Paper Search
- **Vector-Based Search**: Advanced paper search using MongoDB Atlas vector search
- **AI-Powered Ranking**: Intelligent ranking based on Gemini's analysis
- **Detailed Match Reasons**: Clear explanations of why each paper matches your query
- **Poster Information**: Session and location details for easy navigation

### Interactive Features
- **Natural Language Queries**: Search papers using natural language
- **Real-time Results**: Instant paper recommendations
- **Detailed Explanations**: Understand why each paper is relevant to your research

## 🏗️ Project Structure

```plaintext
forky-cvpr/
├── src/                    # Main source code
│   ├── server/            # Backend server implementation
│   │   ├── ai/           # AI/ML models and Gemini integration
│   │   ├── routers/      # FastAPI route handlers
│   │   ├── templates/    # Jinja2 HTML templates
│   │   └── main.py      # Application entry point
│   ├── static/           # Static assets
│   └── config.py        # Configuration settings
```

## 🛠️ Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/AdonaiVera/forky-cvpr2025.git
   cd forky-cvpr2025
   ```

2. Set up virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Environment configuration:
   - Copy `.env.example` to `.env`
   - Add your Google Cloud credentials and MongoDB URI

## 🚀 Running the Application

### Local Development
```bash
cd src/
python -m uvicorn server.main:app --reload
```

The application will be available at `http://localhost:8000`

## 🤝 Let's Connect!

I'll be at CVPR 2025! If you'd like to grab a coffee and chat about research, AI, or just say hi, feel free to reach out! 

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📜 Code of Conduct

Details about our Code of Conduct can be found in the [code of conduct](.github/CODE_OF_CONDUCT.md) file.

## 🙏 Acknowledgments

- Google Cloud for providing credits through #AISprint
- All the amazing researchers at CVPR 2025
