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

### Embedding Example

To embed the chat widget on another website, point an `<iframe>` to the `/widget` route of your running server:

```html
<iframe src="http://localhost:5000/widget" width="420" height="600" style="border:0"></iframe>
```

The FAISS index and text chunks are saved to `index.faiss` and `chunks.json` by default so embeddings persist across restarts. Use the `INDEX_PATH` and `CHUNKS_PATH` environment variables to change these locations.

## UI Features

The chat interface mimics a messenger-style layout. It automatically scrolls to
the latest message and displays a typing indicator while the bot is generating a
response.

## Visa Consultancy Bot

`visa_bot` provides a minimal example of a chatbot for visa consultancies. It answers common questions from a small FAQ file, captures lead information, returns simple document checklists, and records appointment requests.

### Running

```bash
python -m visa_bot.app
```

The default web interface is available on `http://localhost:5000`.
