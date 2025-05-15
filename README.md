# RezScan Project

A smart Applicant Tracking System (ATS) for matching resumes to job descriptions using BERT-based semantic analysis and skill extraction.

## What This Project Does

- Upload a job description and multiple resumes via a web interface
- Extracts and preprocesses text from PDFs/DOCX files
- Uses BERT (Sentence-BERT) embeddings to compute semantic similarity between job description and resumes
- Ranks resumes by match score (cosine, euclidean, or combined)
- Extracts and compares required skills vs. resume skills using NLP
- Visualizes results with:
  - Ranked match table
  - Interactive skill match heatmap
- Allows PDF report download of results
- Provides a modern, user-friendly UI (React frontend) and robust API (Python backend)

## High-Level Workflow

1. User uploads job description and resumes on the frontend
2. Frontend sends files and options to backend API
3. Backend parses, preprocesses, and embeds documents
4. Backend computes similarity scores and skill matches
5. Results are returned to the frontend for visualization and reporting

---

See `/backend/README.md` and `/frontend/README.md` for more details on each part.
