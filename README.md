# StudyShelf

StudyShelf is a local-first exam preparation workspace. Faculty PDFs, their extracted text, and the ChromaDB index stay on your computer. Text embeddings run locally on CPU with `sentence-transformers/all-MiniLM-L6-v2`; answer generation uses the OpenAI-compatible Chat Completions API from the backend only. OpenRouter is supported through `OPENAI_BASE_URL`.

## Prerequisites

- Ubuntu or another Linux/macOS environment
- Python 3.11 or 3.12 (Python 3.12 is recommended)
- Node.js 20.19+ and npm
- Network access during setup and first embedding-model download
- An OpenRouter or OpenAI API key to generate answers, exam responses, and quizzes. Do not paste it into chat or frontend code.

## Installation

From the repository root:

```bash
python3.12 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
cd frontend
npm install
cd ..
```

Run `cp backend/.env.example backend/.env`, then set `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and, if desired, `OPENAI_MODEL`. The default configuration uses OpenRouter's OpenAI-compatible endpoint at `https://openrouter.ai/api/v1` with `nvidia/nemotron-3.5-super-vl:free`. Configure `CHROMA_PATH`, `UPLOAD_DIR`, `TOP_K`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `MAX_UPLOAD_MB`, and `EMBEDDING_MODEL` there. Relative data paths resolve from `backend/`.

## Start the app

Start the API from the repository root:

```bash
backend/.venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Or, after installing dependencies, start both with `./scripts/start.sh`. The UI is at <http://127.0.0.1:5173>; API documentation is at <http://127.0.0.1:8000/docs>. Both servers bind to loopback only. Stop them with Ctrl+C.

## Using StudyShelf

1. Open **PDF Library**, choose a text PDF, optionally classify it by subject, semester, unit, and document type, and select **Upload & index**. The CPU embedding model downloads on first index if not cached.
2. Open **Ask your PDFs** and ask a question. Retrieved sources show filename, page, preview, and source IDs; selecting a source opens the original PDF at its page.
3. **Exam answers** offers 2, 5, and 10 mark formats.
4. **Quiz generator** creates validated four-option questions. Select answers and choose **Check answers** for score, explanations, and source pages.
5. Library filters scope question retrieval by subject and unit. Documents can be reclassified or deleted in the library.
6. **Settings** shows whether cloud generation is configured and where to configure the key.

## API

- `GET /api/health`
- `GET /api/documents`
- `POST /api/documents/upload` (multipart PDF plus optional subject/semester/unit/document_type)
- `DELETE /api/documents/{document_id}`
- `PATCH /api/documents/{document_id}/metadata`
- `GET /api/documents/{document_id}/file`
- `POST /api/chat`
- `POST /api/exam-answer`
- `POST /api/quiz/generate`

## Tests and smoke checks

Run backend tests from repository root:

```bash
backend/.venv/bin/python -m pytest backend/tests -q
```

Build the frontend with `cd frontend && npm run build`. The tests generate a two-page synthetic PDF in memory and mock model output; they do not require OpenAI credits. A separate two-page sample is included at `backend/tests/fixtures/synthetic_notes.pdf` for manual upload. Check `/api/health`, upload that sample, and submit a question for an end-to-end check when the model, dependencies, and API key are configured.

Generation uses the OpenAI-compatible Chat Completions API, with OpenRouter configured by default. Local embeddings (`sentence-transformers/all-MiniLM-L6-v2`) and ChromaDB remain unchanged.

## Troubleshooting

- **Missing API key:** copy `backend/.env.example` to `backend/.env` and set `OPENAI_API_KEY` locally. The backend returns a helpful setup message and does not reveal the key.
- **Model/network errors:** verify the key, `OPENAI_BASE_URL`, model name, account access, and internet connectivity. The app uses the Chat Completions API with a bounded request timeout and does not send API keys to the frontend.
- **Indexing fails on first use:** ensure the local embedding model can download and enough disk space is available. Set `HF_HOME` locally if you need a different model cache directory.
- **Scanned PDFs:** StudyShelf reports when no selectable text exists. OCR is not included yet.
- **Address already in use:** stop the other local process or choose another port and update the frontend API address/CORS settings.
- **Python version:** use Python 3.11 or 3.12 if a dependency lacks a compatible wheel, then recreate the virtual environment.

## Data and backup

Uploaded originals and a small document manifest are stored under `data/uploads/`; the persistent ChromaDB index is under `data/chroma/`. Stop the app and copy both directories together for a consistent backup. These generated files are ignored by Git. Deleting a library document removes its vectors and stored PDF. Duplicate PDFs are detected by content hash.

## Security and limitations

The dev servers bind to `127.0.0.1`; CORS is limited to the local Vite origins. File names are not used as filesystem paths. PDF excerpts are treated as untrusted evidence in generation prompts. OCR, authentication, multi-user support, and remote deployment are not included. LLM generation requires network access and an OpenRouter or OpenAI-compatible API key; upload/indexing are designed for local processing.
