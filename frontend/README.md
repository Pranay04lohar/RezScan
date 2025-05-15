# RezScan Frontend

This is the frontend for the RezScan Applicant Tracking System (ATS), providing an intuitive web interface for uploading job descriptions and resumes, visualizing match results, and exploring skill analysis.

## Features

- **File Upload:** Users can upload a job description and multiple resumes (PDF/DOCX) via a simple drag-and-drop or file picker interface.
- **Similarity Metric Selection:** Users can choose between cosine, euclidean, or combined similarity for matching.
- **Progress Feedback:** Real-time progress bar and status messages during analysis.
- **Results Dashboard:**
  - **Analysis Summary:** Displays total resumes, average score, and score distribution.
  - **Detailed Match Table:** Shows ranked resumes with similarity scores and allows PDF report download.
  - **Skill Match Visualization:** Interactive heatmap showing which resumes cover which required skills (green = present, red = missing).
- **Error Handling:** User-friendly error messages for upload, processing, and API issues.
- **Modern UI:** Clean, responsive design using React and a component library for a professional look.

## User Flow

1. **Upload Files:**
   - User uploads a job description and one or more resumes.
2. **Select Similarity Metric:**
   - User chooses the matching algorithm (cosine, euclidean, or combined).
3. **Start Analysis:**
   - User clicks "Analyze" to send files and settings to the backend API.
4. **View Results:**
   - Dashboard displays ranked matches, skill match heatmap, and summary statistics.
   - User can download a PDF report or start a new analysis.

## Key Components

- **Index Page (`pages/Index.tsx`):** Main page for uploading files, selecting options, and displaying results.
- **SkillMatchComparison (`components/SkillMatchComparison.tsx`):** Renders the skill match heatmap table for visualizing skill coverage across resumes.
- **API Service (`lib/api.ts`):** Handles communication with the backend API, including file upload and result parsing.
- **UI Components:** Cards, tables, buttons, progress bars, and notifications for a smooth user experience.

## Interaction with Backend

- The frontend sends a POST request to `/api/match` with the uploaded files and selected options.
- Receives a JSON response with match results, skill analysis, and statistics.
- Visualizes the results and provides actionable insights to the user.

## Setup & Installation

1. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```
2. **Start the development server:**
   ```bash
   npm run dev
   # or
   yarn dev
   ```
3. **Open the app:**
   - Visit [http://localhost:5173](http://localhost:5173) (or the port shown in your terminal).

## Notes

- The frontend expects the backend to be running and accessible at the configured API URL.
- For best results, use the latest version of Chrome, Firefox, or Edge.

---

For questions or issues, please contact the project maintainer.
