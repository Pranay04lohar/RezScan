from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import tempfile
from app.services.file_handler import FileHandler
from app.services.parser import DocumentParser
from app.services.batch_processor import TextPreprocessor
from app.services.similarity_engine import SimilarityEngine, SimilarityMetric, SimilarityConfig
from flask_cors import CORS
from app.services.skill_extractor import SkillExtractor
# import azure.functions as func  # Not needed for Hugging Face Spaces

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
# Allow specific origins from environment variable, or allow all in development
cors_origins = os.environ.get('CORS_ORIGINS', '*')
if cors_origins == '*':
    # Development: allow all origins
    CORS(app)
else:
    # Production: allow specific origins (comma-separated)
    origins = [origin.strip() for origin in cors_origins.split(',')]
    CORS(app, origins=origins)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}  # Added txt for testing
app.config['SERVER_NAME'] = None  # Remove server name constraint
app.config['PREFERRED_URL_SCHEME'] = 'http'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize services
file_handler = FileHandler(app.config['UPLOAD_FOLDER'])
document_parser = DocumentParser()
text_preprocessor = TextPreprocessor()
similarity_engine = SimilarityEngine()
skill_extractor = SkillExtractor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "message": "Welcome to RezScan API",
        "endpoints": {
            "health": "/api/health",
            "match": "/api/match"
        },
        "usage": {
            "health_check": "GET /api/health",
            "resume_matching": "POST /api/match"
        },
        "note": "Please use HTTP for development server"
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "RezScan API is running"})

# /api/match
@app.route('/api/match', methods=['POST'])
def match_resumes():
    if 'job_description' not in request.files:
        return jsonify({"error": "No job description file provided"}), 400
    
    job_description = request.files['job_description']
    if not job_description or not allowed_file(job_description.filename):
        return jsonify({"error": "Invalid job description file"}), 400

    if 'resumes' not in request.files:
        return jsonify({"error": "No resume files provided"}), 400

    resumes = request.files.getlist('resumes')
    if not resumes:
        return jsonify({"error": "No resume files provided"}), 400

    # Get similarity configuration
    similarity_metric = request.form.get('similarity_metric', 'cosine')
    try:
        metric = SimilarityMetric(similarity_metric)
    except ValueError:
        metric = SimilarityMetric.COSINE

    # Get optional parameters
    top_k = int(request.form.get('top_k', 5))
    similarity_threshold = float(request.form.get('similarity_threshold', 0.0))
    
    # Create similarity config
    similarity_config = SimilarityConfig(
        metric=metric,
        threshold=similarity_threshold,
        top_k=top_k
    )

    try:
        # Save uploaded files
        jd_path, resume_paths = file_handler.save_files(job_description, resumes)

        # Parse job description
        jd_text = document_parser.parse_document(jd_path)
        if not jd_text:
            return jsonify({"error": "Failed to parse job description"}), 400

        # Parse resumes
        resume_texts = []
        for resume_path in resume_paths:
            text = document_parser.parse_document(resume_path)
            print(f"Parsing {resume_path}:")
            print(f"Extracted text (first 200 chars): {text[:200] if text else 'None'}")
            if text:
                resume_texts.append(text)

        if not resume_texts:
            return jsonify({"error": "Failed to parse any resumes"}), 400

        # Preprocess texts
        jd_processed = text_preprocessor.preprocess_text(jd_text)
        resume_processed = text_preprocessor.preprocess_batch({
            f"resume_{i}": text for i, text in enumerate(resume_texts)
        })

        print("Preprocessed JD:", jd_processed)
        print("Preprocessed resumes:", resume_processed)

        # Get text statistics
        jd_stats = text_preprocessor.get_text_statistics(jd_text)
        resume_stats = [
            text_preprocessor.get_text_statistics(text)
            for text in resume_texts
        ]

        # Compute similarities using BERT
        matches = similarity_engine.compute_similarity(
            jd_processed,
            list(resume_processed.values()),
            similarity_config
        )
        
        print("Matches:", matches)
        
        # Get ranking summary
        ranking_summary = similarity_engine.get_ranking_summary(matches)
        
        # Get explanations for matches
        match_explanations = {}
        for match in matches:
            resume_idx = match['index']
            explanation = similarity_engine.get_similarity_explanation(
                jd_processed,
                resume_processed[f"resume_{resume_idx}"],
                similarity_config
            )
            match_explanations[f"resume_{resume_idx}"] = explanation
        
        skill_matches = {}
        for match in matches:
            resume_idx = match['index']
            skill_match = skill_extractor.get_skill_match(
                jd_text,
                resume_texts[resume_idx]
            )
            skill_matches[f"resume_{resume_idx}"] = skill_match

        response = {
            "message": "Files processed successfully with BERT",
            "similarity_metric": similarity_metric,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
            "ranking_summary": ranking_summary,
            "job_description": {
                "statistics": jd_stats
            },
            "matches": [
                {
                    "resume_id": f"resume_{match['index']}",
                    "rank": match['rank'],
                    "similarity_score": match['similarity_score'],
                    "explanation": match_explanations[f"resume_{match['index']}"],
                    "skill_match": skill_matches[f"resume_{match['index']}"]
                }
                for match in matches
            ],
            "resumes": {
                "count": len(resume_texts),
                "statistics": resume_stats
            }
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up uploaded files
        file_handler.cleanup_files(jd_path, resume_paths)

# Azure Functions handler - not needed for Hugging Face Spaces
# def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
#     return func.WsgiMiddleware(app.wsgi_app).handle(req, context)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False) 

