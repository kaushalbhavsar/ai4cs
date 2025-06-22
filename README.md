# PDF Assistant Bot

This project provides a simple Flask web app that loads PDF files, indexes them using OpenAI embeddings and FAISS, and answers user questions. The web UI can be embedded in another site via an iframe. Each user session can ask up to seven questions.
## UI Features

- Messenger-style chat interface
- Automatically scrolls to the newest message
- Shows a "typing..." indicator while the bot responds

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Place your training PDFs inside a folder named `pdfs/` in the project root (or specify another path with the `PDF_DIR` environment variable).

3. Export your OpenAI API key:

```bash
export OPENAI_API_KEY=your_key
```

4. Run the server:

```bash
python -m pdf_bot.app
```

The app will be available on `http://localhost:5000` and can be embedded in an `<iframe>`.

## UI Features

The chat interface mimics a messenger-style layout. It automatically scrolls to
the latest message and displays a typing indicator while the bot is generating a
response.
