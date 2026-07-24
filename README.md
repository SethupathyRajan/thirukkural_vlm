# Thirukkural Educational AI Application

## Overview
This application helps you discover the wisdom of Thirukkural through pictures. You upload an image, and the AI finds a relevant Thirukkural (wise Tamil couplet) that matches what you see in your photo.

## How to Run the Application

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup
1. Navigate to the project root directory
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the backend server:
   ```bash
   python backend/main.py
   ```
   The API will be available at http://localhost:8000

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Start the frontend development server:
   ```bash
   npm run dev
   ```
   The application will be available at http://localhost:5173

### Usage
1. Open your browser to http://localhost:5173
2. Click to upload an image (PNG, JPG, or JPEG format, under 5MB)
3. Wait for the analysis to complete
4. View the Thirukkural, its meaning, life lesson, confidence score, and explanation
5. Ask follow-up questions in the chat area to learn more
6. Click "Back to Upload" to try another image

## Project Structure
- `backend/` - Contains the FastAPI application
- `frontend/` - Contains the React application
- `src/` - Contains the core AI components (inference, explanation, conversation engines)
- `config/` - Configuration files

## Notes
- This application has been cleaned up to remove testing/debugging scripts that are not required for production
- The core application only requires the essential Python files in `/src/` and `/backend/` to function
- Removed files include benchmarking, debugging, exploration, and test scripts
