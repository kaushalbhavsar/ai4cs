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

The FAISS index and text chunks are saved to `index.faiss` and `chunks.json` by default so embeddings persist across restarts. Use the `INDEX_PATH` and `CHUNKS_PATH` environment variables to change these locations.

You can upload new PDF files through the web interface or by sending a `POST` request with a `file` field to `/upload`. Uploaded PDFs are immediately indexed and saved.

## UI Features

The chat interface mimics a messenger-style layout. It automatically scrolls to
the latest message and displays a typing indicator while the bot is generating a
response.
