# 🤖 AI Chat Application

A modern ChatGPT-like application with a clean, intuitive interface. Built with React Native for the frontend and FastAPI for the backend.

## ✨ Features

- **ChatGPT-like Interface**: Clean, modern chat interface similar to ChatGPT
- **AI Integration**: Connect to any AI model API (OpenAI, Claude, DeepSeek, etc.)
- **Real-time Chat**: Send messages and receive AI responses instantly
- **Message History**: View and manage your chat history
- **User Authentication**: Secure login and registration system
- **Modern UI**: Beautiful, responsive design with dark/light theme support
- **Cross-platform**: Works on both iOS and Android

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- MySQL database
- AI API key (OpenAI, Claude, etc.)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd "BE ChatApp"
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database**:
   - Update `config/settings.py` with your MySQL credentials
   - Create a database named `chatbotapp`

4. **Configure AI model**:
   - Edit `config/ai_config.py`
   - Replace `your-api-key-here` with your actual API key
   - Choose your preferred AI provider (OpenAI, Claude, DeepSeek, etc.)

5. **Start the backend**:
   ```bash
   python main.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd ChatApp
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure API endpoint**:
   - Edit `constants/config.js`
   - Update `BASE_URL` to match your backend URL

4. **Start the app**:
   ```bash
   npx react-native run-android
   # or
   npx react-native run-ios
   ```

## 🔧 Configuration

### AI Model Configuration

Edit `BE ChatApp/config/ai_config.py` to configure your AI model:

```python
AI_CONFIG = {
    "api_url": "https://api.openai.com/v1/chat/completions",
    "api_key": "your-api-key-here",
    "model_name": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 1000,
    # ... other settings
}
```

### Supported AI Providers

1. **OpenAI** (GPT-3.5, GPT-4):
   ```python
   "api_url": "https://api.openai.com/v1/chat/completions"
   ```

2. **Anthropic** (Claude):
   ```python
   "api_url": "https://api.anthropic.com/v1/messages"
   ```

3. **DeepSeek**:
   ```python
   "api_url": "https://api.deepseek.com/v1/chat/completions"
   ```

### Database Configuration

Update `BE ChatApp/config/settings.py`:

```python
DATABASE_URL = "mysql+pymysql://username:password@localhost:3306/chatbotapp"
```

## 📱 App Structure

### Backend (`BE ChatApp/`)
- `api/v1/endpoints/chat.py` - Chat endpoints
- `config/ai_config.py` - AI model configuration
- `models.py` - Database models
- `schemas/chat.py` - Pydantic schemas
- `crud/chat.py` - Database operations

### Frontend (`ChatApp/`)
- `screens/ChatScreen.tsx` - Main chat interface
- `screens/HomeScreen.tsx` - Welcome screen
- `services/api.ts` - API service
- `navigation/AppNavigator.tsx` - Navigation setup

## 🎨 Features

### Chat Interface
- **Real-time messaging**: Send messages and get instant AI responses
- **Message history**: View all your previous conversations
- **Delete messages**: Remove individual messages or clear all
- **Loading states**: Visual feedback during message sending

### User Experience
- **Modern UI**: Clean, intuitive interface
- **Theme support**: Dark/light mode
- **Responsive design**: Works on all screen sizes
- **Keyboard handling**: Smooth input experience

### Backend Features
- **RESTful API**: Clean, well-documented endpoints
- **Database persistence**: All messages saved to MySQL
- **Error handling**: Robust error management
- **Logging**: Comprehensive logging for debugging

## 🔌 API Endpoints

### Chat Endpoints
- `POST /api/v1/chat/send` - Send a message
- `GET /api/v1/chat/messages` - Get user messages
- `DELETE /api/v1/chat/messages/{id}` - Delete a message
- `DELETE /api/v1/chat/messages` - Clear all messages
- `GET /api/v1/chat/statistics` - Get chat statistics

### Auth Endpoints
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

## 🛠️ Development

### Adding New AI Providers

1. Add configuration to `ai_config.py`:
   ```python
   AI_CONFIG = {
       "api_url": "your-api-endpoint",
       "api_key": "your-api-key",
       "model_name": "your-model",
       # ... other settings
   }
   ```

2. Update the `generate_ai_response` function in `chat.py` if needed

### Customizing the UI

- Edit `ChatApp/screens/ChatScreen.tsx` for chat interface
- Modify `ChatApp/contexts/ThemeContext.tsx` for theming
- Update `ChatApp/constants/config.js` for app configuration

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Check MySQL is running
   - Verify database credentials in `settings.py`
   - Ensure database `chatbotapp` exists

2. **AI API Errors**:
   - Verify API key is correct
   - Check API endpoint URL
   - Ensure you have sufficient API credits

3. **Frontend Connection Issues**:
   - Verify backend is running on correct port
   - Check `BASE_URL` in `config.js`
   - Ensure network connectivity

### Debug Mode

Enable debug logging in `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Happy Chatting! 🤖💬**
