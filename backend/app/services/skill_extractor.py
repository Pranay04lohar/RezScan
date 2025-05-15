import spacy
import re
from typing import List, Dict, Any
import logging

class SkillExtractor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.logger.warning("Downloading spaCy model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from text using NER and keyword extraction.
        
        Args:
            text: Input text to extract skills from
            
        Returns:
            List of extracted skills
        """
        # Common technical skills and programming languages
        technical_skills = {
            'programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'laravel', 'rails', 'asp.net'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'cassandra'],
            'cloud': ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes', 'terraform'],
            'tools': ['git', 'jenkins', 'jira', 'confluence', 'slack', 'trello', 'figma', 'sketch'],
            'methodologies': ['agile', 'scrum', 'kanban', 'waterfall', 'devops', 'ci/cd'],
        }

        # Convert text to lowercase for better matching
        text_lower = text.lower()
        
        # Extract skills using NER
        doc = self.nlp(text)
        ner_skills = []
        for ent in doc.ents:
            if ent.label_ in ['PRODUCT', 'ORG', 'LANGUAGE']:
                ner_skills.append(ent.text.lower())

        # Extract skills using keyword matching
        keyword_skills = []
        for category, skills in technical_skills.items():
            for skill in skills:
                if skill in text_lower:
                    keyword_skills.append(skill)

        # Combine and deduplicate skills
        all_skills = list(set(ner_skills + keyword_skills))
        
        # Clean up skills
        cleaned_skills = []
        for skill in all_skills:
            # Remove common words and clean up
            skill = re.sub(r'\b(and|or|the|a|an)\b', '', skill)
            skill = skill.strip()
            if len(skill) > 1:  # Only keep skills with more than 1 character
                cleaned_skills.append(skill)

        return list(set(cleaned_skills))  # Remove any remaining duplicates

    def get_skill_match(self, job_description: str, resume: str) -> Dict[str, Any]:
        """
        Compare skills between job description and resume.
        
        Args:
            job_description: Job description text
            resume: Resume text
            
        Returns:
            Dictionary containing skill match analysis
        """
        jd_skills = self.extract_skills(job_description)
        resume_skills = self.extract_skills(resume)
        
        # Find matching and missing skills
        matching_skills = list(set(jd_skills) & set(resume_skills))
        missing_skills = list(set(jd_skills) - set(resume_skills))
        extra_skills = list(set(resume_skills) - set(jd_skills))
        
        # Calculate match percentage
        match_percentage = len(matching_skills) / len(jd_skills) if jd_skills else 0
        
        return {
            'job_description_skills': jd_skills,
            'resume_skills': resume_skills,
            'matching_skills': matching_skills,
            'missing_skills': missing_skills,
            'extra_skills': extra_skills,
            'match_percentage': match_percentage
        } 