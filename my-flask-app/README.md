# My Flask App

This is a Flask application designed for live streaming video content. It allows users to upload video files and stream them to a specified platform using RTMP.

## Project Structure

```
my-flask-app
├── app.py               # Main application code for the Flask app
├── requirements.txt     # Dependencies required for the Flask application
├── vercel.json          # Configuration for deploying the Flask application to Vercel
└── README.md            # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd my-flask-app
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```
   python app.py
   ```

   The application will be available at `http://127.0.0.1:5000`.

## Usage

- Navigate to the home page to upload a video file.
- Enter the stream key and video size.
- Optionally enable looping and specify the number of loops.
- Click on "Start Stream" to begin streaming.
- Use the "Stop Stream" button to end the streaming session.

## Deployment

This application can be deployed to Vercel. Ensure that the `vercel.json` file is correctly configured for your deployment settings.

## License

This project is licensed under the MIT License.