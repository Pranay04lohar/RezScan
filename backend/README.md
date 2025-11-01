# RezScan Backend

This backend powers the RezScan Applicant Tracking System (ATS) and provides APIs for intelligent resume and job description matching using BERT embeddings and skill extraction.

---

sdk: python
sdk_version: 3.12.0
app_file: app.py

---

## Features

- **File Upload:** Accepts job description and multiple resume files (PDF, DOCX, TXT) via the `/api/match` endpoint.
- **Parsing:** Extracts and cleans text from uploaded documents using PDF and DOCX parsers.
- **Preprocessing:** Cleans and preprocesses text for semantic analysis.
- **Similarity Computation:** Uses BERT embeddings to compute similarity scores (cosine, euclidean, or combined) between the job description and each resume.
- **Skill Extraction:** Extracts technical and soft skills from both job descriptions and resumes using NLP (spaCy) and keyword matching.
- **Skill Match Analysis:** Compares required skills from the job description with those found in each resume, reporting matching, missing, and extra skills.
- **API Endpoints:**
  - `POST /api/match`: Main endpoint for uploading files and receiving match results.
  - `GET /api/health`: Health check endpoint.
- **Configurable Limits:** Maximum upload size (default 16MB), similarity metric, top-K results, and similarity threshold.

## How BERT is Used for Semantic Matching

### Model Used

- **Model:** The backend uses a pre-trained Sentence-BERT (SBERT) model, typically `all-MiniLM-L6-v2` from the [sentence-transformers](https://www.sbert.net/) library. This model is well-suited for generating high-quality sentence and document embeddings for semantic similarity tasks.
- **Why SBERT:** Unlike vanilla BERT, SBERT is specifically designed for producing semantically meaningful vector representations that can be compared using cosine or euclidean distance.

### How It Works

1. **Text Embedding:**

   - The job description and each resume are preprocessed (cleaned, lowercased, etc.).
   - Each document is passed through the SBERT model to obtain a fixed-size embedding vector (typically 384 dimensions for `all-MiniLM-L6-v2`).

2. **Similarity Computation:**

   - For each resume, the backend computes the similarity between the job description embedding and the resume embedding.
   - **Cosine Similarity:** Measures the cosine of the angle between the two vectors (ranges from -1 to 1, higher means more similar).
   - **Euclidean Similarity:** Measures the inverse of the Euclidean distance between the two vectors (lower distance = higher similarity).
   - **Combined Score:** Optionally, the average of cosine and euclidean similarity is used for ranking.

3. **Ranking:**
   - All resumes are ranked based on the selected similarity metric.
   - Top-K resumes above the similarity threshold are returned as the best matches.

### Why This Approach?

- **Semantic Understanding:** BERT-based models capture the context and meaning of text, not just keyword overlap. This allows for more accurate matching between job requirements and resume content, even if the wording is different.
- **Efficiency:** SBERT models are optimized for fast, large-scale similarity search.
- **Flexibility:** The backend can easily switch to other transformer models (e.g., `paraphrase-MiniLM-L6-v2`, `distilroberta-base-msmarco-v2`) if needed, depending on accuracy and performance requirements.

### Example (Pseudo-code)

```python
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')
emb_jd = model.encode(job_description_text)
emb_resume = model.encode(resume_text)
cosine_sim = util.cos_sim(emb_jd, emb_resume)
```

## How It Works

1. **File Upload:**

   - The frontend sends a job description and one or more resumes to `/api/match`.
   - Supported formats: PDF, DOCX, TXT.

2. **Parsing:**

   - Each file is parsed to extract raw text using PyPDF2 (PDF) and python-docx (DOCX).
   - Text is cleaned and normalized.

3. **Preprocessing:**

   - Text is further preprocessed (lowercased, stopwords removed, etc.) for embedding and skill extraction.

4. **Similarity Computation:**

   - BERT embeddings are generated for the job description and each resume.
   - Similarity scores are computed using the selected metric (cosine, euclidean, or combined).
   - Top-K matches are selected based on scores and threshold.

5. **Skill Extraction & Matching:**

   - Skills are extracted from the job description and each resume using spaCy NER and keyword lists.
   - For each resume, the backend computes:
     - `job_description_skills`: Skills required by the job description
     - `resume_skills`: Skills found in the resume
     - `matching_skills`: Skills present in both
     - `missing_skills`: Required skills not found in the resume
     - `extra_skills`: Skills in the resume but not required
     - `match_percentage`: Proportion of required skills found in the resume

6. **Response:**
   - The API returns a JSON object with:
     - Overall analysis results and ranking summary
     - Detailed match table (scores, explanations)
     - Skill match analysis for each resume
     - Text statistics for job description and resumes

## API Endpoints

### `POST /api/match`

- **Description:** Upload job description and resumes, receive match and skill analysis.
- **Request:**
  - `job_description`: File (PDF/DOCX/TXT)
  - `resumes`: Multiple files (PDF/DOCX/TXT)
  - `similarity_metric`: 'cosine', 'euclidean', or 'combined' (optional)
  - `top_k`: Number of top matches to return (optional)
  - `similarity_threshold`: Minimum similarity score (optional)
- **Response:** JSON with match results, skill analysis, and statistics.

### `GET /api/health`

- **Description:** Health check endpoint.
- **Response:** `{ "status": "healthy", "message": "RezScan API is running" }`

## Configuration

- **Max upload size:** Set in `api/main.py` via `app.config['MAX_CONTENT_LENGTH']` (default 16MB).
- **Allowed file types:** PDF, DOCX, TXT.
- **Similarity metric, top_k, threshold:** Configurable via API request.

## Setup & Installation

1. **Create and activate a Python environment (conda recommended):**
   ```bash
   conda create -n rezscan python=3.12
   conda activate rezscan
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
3. **Run the backend:**
   ```bash
   python run.py
   ```
4. **Access the API:**
   - Health check: [http://localhost:5000/api/health](http://localhost:5000/api/health)
   - Match endpoint: [http://localhost:5000/api/match](http://localhost:5000/api/match)

## Notes

- For OCR support, Tesseract must be installed on your system if you want to extract text from images in PDFs.
- All temporary files are cleaned up after processing.
- The backend is designed to work with the RezScan frontend for a seamless ATS experience.

## Hugging Face Spaces Deployment

For deploying to Hugging Face Spaces (free tier with >2GB RAM), see [HUGGINGFACE_SPACES.md](./HUGGINGFACE_SPACES.md) for detailed instructions.

Quick setup:

1. Create a new Space on Hugging Face with Python SDK
2. Connect your GitHub repository and set Space directory to `backend/`
3. Ensure `app.py` entry point is in the backend directory (already created)
4. Set environment variables in Space settings
5. Deploy and get your Space URL
6. Update Vercel frontend with `VITE_API_URL` environment variable

## Azure Container Deployment

### Prerequisites

1. Azure CLI installed
2. Docker installed locally
3. Azure subscription

### Deployment Steps

1. **Login to Azure**

```bash
az login
```

2. **Create Azure Container Registry (ACR)**

```bash
# Create a resource group
az group create --name rezscan-rg --location eastus

# Create ACR
az acr create --resource-group rezscan-rg --name rezscanregistry --sku Basic

# Enable admin access
az acr update -n rezscanregistry --admin-enabled true
```

3. **Build and Push Docker Image**

```bash
# Login to ACR
az acr login --name rezscanregistry

# Build the image
docker build -t rezscanregistry.azurecr.io/rezscan-backend:latest .

# Push the image
docker push rezscanregistry.azurecr.io/rezscan-backend:latest
```

4. **Create Azure Container App**

```bash
# Create Container App environment
az containerapp env create \
  --name rezscan-env \
  --resource-group rezscan-rg \
  --location eastus

# Create Container App
az containerapp create \
  --name rezscan-backend \
  --resource-group rezscan-rg \
  --environment rezscan-env \
  --image rezscanregistry.azurecr.io/rezscan-backend:latest \
  --target-port 5000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --env-vars "FLASK_ENV=production"
```

5. **Get the Container App URL**

```bash
az containerapp show \
  --name rezscan-backend \
  --resource-group rezscan-rg \
  --query properties.configuration.ingress.fqdn
```

### Environment Variables

Make sure to set the following environment variables in your Azure Container App:

- `FLASK_ENV=production`
- Add any other environment variables your application needs

### Monitoring

You can monitor your application using Azure Portal:

1. Go to Azure Portal
2. Navigate to your Container App
3. Check the "Monitoring" section for logs and metrics

### Scaling

The Container App is configured to scale between 1 and 3 replicas. You can adjust these values based on your needs:

```bash
az containerapp update \
  --name rezscan-backend \
  --resource-group rezscan-rg \
  --min-replicas 1 \
  --max-replicas 5
```

---

For questions or issues, please contact the project maintainer.
