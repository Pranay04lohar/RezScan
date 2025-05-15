# import re
# from typing import List, Dict, Any
# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer
# import string
# import logging

# class TextPreprocessor:
#     """Text preprocessing pipeline for resume and job description analysis."""
    
#     def __init__(self):
#         self.logger = logging.getLogger(__name__)
#         self.stemmer = PorterStemmer()
        
#         # Download required NLTK data
#         try:
#             nltk.data.find('tokenizers/punkt')
#             nltk.data.find('corpora/stopwords')
#         except LookupError:
#             nltk.download('punkt')
#             nltk.download('stopwords')
        
#         self.stop_words = set(stopwords.words('english'))
#         # Add custom stop words specific to resumes and job descriptions
#         self.custom_stop_words = {
#             'experience', 'work', 'job', 'position', 'role', 'company',
#             'year', 'years', 'month', 'months', 'day', 'days',
#             'skill', 'skills', 'responsibility', 'responsibilities',
#             'duty', 'duties', 'requirement', 'requirements'
#         }
#         self.stop_words.update(self.custom_stop_words)

#     def preprocess_text(self, text: str) -> str:
#         """
#         Preprocess a single text document.
        
#         Args:
#             text: Raw text to preprocess
            
#         Returns:
#             Preprocessed text
#         """
#         if not text:
#             return ""

#         try:
#             # Convert to lowercase
#             text = text.lower()
            
#             # Remove lines that are mostly non-alphanumeric (e.g., lines of underscores)
#             lines = text.split('\n')
#             lines = [line for line in lines if sum(c.isalnum() for c in line) > len(line) * 0.3]
#             text = '\n'.join(lines)
            
#             # Remove URLs
#             text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            
#             # Remove email addresses
#             text = re.sub(r'\S+@\S+', '', text)
            
#             # Remove special characters and digits
#             text = re.sub(r'[^\w\s]', ' ', text)
#             text = re.sub(r'\d+', '', text)
            
#             # Remove extra whitespace
#             text = ' '.join(text.split())
            
#             # Tokenize
#             tokens = word_tokenize(text)
            
#             # Remove stop words, stem, and filter out non-alphanumeric tokens and short tokens
#             processed_tokens = [
#                 self.stemmer.stem(token)
#                 for token in tokens
#                 if token.isalnum() and token not in self.stop_words and len(token) > 2
#             ]
            
#             return ' '.join(processed_tokens)
            
#         except Exception as e:
#             self.logger.error(f"Error preprocessing text: {str(e)}")
#             return ""

#     def preprocess_batch(self, documents: Dict[str, str]) -> Dict[str, str]:
#         """
#         Preprocess multiple documents.
        
#         Args:
#             documents: Dictionary mapping document IDs to their text content
            
#         Returns:
#             Dictionary mapping document IDs to preprocessed text
#         """
#         return {
#             doc_id: self.preprocess_text(text)
#             for doc_id, text in documents.items()
#         }

#     def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
#         """
#         Extract top keywords from text.
        
#         Args:
#             text: Preprocessed text
#             top_n: Number of top keywords to extract
            
#         Returns:
#             List of top keywords
#         """
#         if not text:
#             return []
            
#         # Tokenize and count frequencies
#         tokens = word_tokenize(text.lower())
#         word_freq = {}
        
#         for token in tokens:
#             if token not in self.stop_words and len(token) > 2:
#                 word_freq[token] = word_freq.get(token, 0) + 1
        
#         # Sort by frequency and get top N
#         sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
#         return [word for word, _ in sorted_words[:top_n]]

#     def get_text_statistics(self, text: str) -> Dict[str, Any]:
#         """
#         Get basic statistics about the text.
        
#         Args:
#             text: Raw text to analyze
            
#         Returns:
#             Dictionary containing text statistics
#         """
#         if not text:
#             return {
#                 'word_count': 0,
#                 'unique_words': 0,
#                 'avg_word_length': 0,
#                 'keyword_density': 0
#             }
            
#         # Basic statistics
#         words = word_tokenize(text.lower())
#         unique_words = set(words)
        
#         # Calculate average word length
#         total_length = sum(len(word) for word in words)
#         avg_length = total_length / len(words) if words else 0
        
#         # Calculate keyword density (percentage of non-stop words)
#         keywords = [word for word in words if word not in self.stop_words]
#         keyword_density = len(keywords) / len(words) if words else 0
        
#         return {
#             'word_count': len(words),
#             'unique_words': len(unique_words),
#             'avg_word_length': round(avg_length, 2),
#             'keyword_density': round(keyword_density * 100, 2)
#         } 


import re
from typing import List, Dict, Any
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
import string
import logging

class TextPreprocessor:
    """Text preprocessing pipeline for resume and job description analysis."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.lemmatizer = WordNetLemmatizer()
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
            nltk.download('averaged_perceptron_tagger')
        
        self.stop_words = set(stopwords.words('english'))
        # Add custom stop words specific to resumes and job descriptions
        self.custom_stop_words = {
            'experience', 'work', 'job', 'position', 'role', 'company',
            'year', 'years', 'month', 'months', 'day', 'days',
            'skill', 'skills', 'responsibility', 'responsibilities',
            'duty', 'duties', 'requirement', 'requirements'
        }
        self.stop_words.update(self.custom_stop_words)

    def get_wordnet_pos(self, treebank_tag: str) -> str:
        """Map POS tag to a format recognized by WordNetLemmatizer."""
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN  # Default to noun

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess a single text document.
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Preprocessed text
        """
        if not text:
            return ""

        try:
            # Convert to lowercase
            text = text.lower()
            
            # Remove lines that are mostly non-alphanumeric (e.g., lines of underscores)
            lines = text.split('\n')
            lines = [line for line in lines if sum(c.isalnum() for c in line) > len(line) * 0.3]
            text = '\n'.join(lines)
            
            # Remove URLs
            text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
            
            # Remove email addresses
            text = re.sub(r'\S+@\S+', '', text)
            
            # Remove special characters and digits
            text = re.sub(r'[^\w\s]', ' ', text)
            text = re.sub(r'\d+', '', text)
            
            # Remove extra whitespace
            text = ' '.join(text.split())
            
            # Tokenize
            tokens = word_tokenize(text)
            
            # POS tagging
            pos_tags = pos_tag(tokens)
            
            # Lemmatize with POS tags, remove stopwords, filter out non-alphanumeric tokens and short tokens
            processed_tokens = [
                self.lemmatizer.lemmatize(token, self.get_wordnet_pos(pos))
                for token, pos in pos_tags
                if token.isalnum() and token not in self.stop_words and len(token) > 2
            ]
            
            return ' '.join(processed_tokens)
            
        except Exception as e:
            self.logger.error(f"Error preprocessing text: {str(e)}")
            return ""

    def preprocess_batch(self, documents: Dict[str, str]) -> Dict[str, str]:
        """
        Preprocess multiple documents.
        
        Args:
            documents: Dictionary mapping document IDs to their text content
            
        Returns:
            Dictionary mapping document IDs to preprocessed text
        """
        return {
            doc_id: self.preprocess_text(text)
            for doc_id, text in documents.items()
        }

    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract top keywords from text.
        
        Args:
            text: Preprocessed text
            top_n: Number of top keywords to extract
            
        Returns:
            List of top keywords
        """
        if not text:
            return []
            
        # Tokenize and count frequencies
        tokens = word_tokenize(text.lower())
        word_freq = {}
        
        for token in tokens:
            if token not in self.stop_words and len(token) > 2:
                word_freq[token] = word_freq.get(token, 0) + 1
        
        # Sort by frequency and get top N
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:top_n]]

    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """
        Get basic statistics about the text.
        
        Args:
            text: Raw text to analyze
            
        Returns:
            Dictionary containing text statistics
        """
        if not text:
            return {
                'word_count': 0,
                'unique_words': 0,
                'avg_word_length': 0,
                'keyword_density': 0
            }
            
        # Basic statistics
        words = word_tokenize(text.lower())
        unique_words = set(words)
        
        # Calculate average word length
        total_length = sum(len(word) for word in words)
        avg_length = total_length / len(words) if words else 0
        
        # Calculate keyword density (percentage of non-stop words)
        keywords = [word for word in words if word not in self.stop_words]
        keyword_density = len(keywords) / len(words) if words else 0
        
        return {
            'word_count': len(words),
            'unique_words': len(unique_words),
            'avg_word_length': round(avg_length, 2),
            'keyword_density': round(keyword_density * 100, 2)
        }
