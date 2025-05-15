from app.services.skill_extractor import SkillExtractor

# Initialize services
skill_extractor = SkillExtractor()

@app.route('/api/match', methods=['POST'])
def match_resumes():
    # Get skill matches for each resume
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
            "statistics": jd_stats,
            "skills": skill_matches[f"resume_{matches[0]['index']}"]["job_description_skills"] if matches else []
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