from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import logging
from dataclasses import dataclass
from enum import Enum
from sentence_transformers import SentenceTransformer
import torch

class SimilarityMetric(Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    COMBINED = "combined"

@dataclass
class SimilarityConfig:
    metric: SimilarityMetric = SimilarityMetric.COSINE
    threshold: float = 0.0
    top_k: int = 5
    weights: Optional[Dict[str, float]] = None

class SimilarityEngine:
    """Engine for computing semantic similarity between documents using BERT embeddings."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the similarity engine with a BERT model.
        
        Args:
            model_name: Name of the sentence-transformer model to use
        """
        self.logger = logging.getLogger(__name__)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = SentenceTransformer(model_name, device=self.device)
        self.logger.info(f"Initialized BERT model {model_name} on {self.device}")

    def compute_similarity(
        self,
        source_text: str,
        target_texts: List[str],
        config: SimilarityConfig
    ) -> List[Dict[str, Any]]:
        """
        Compute similarity between source text and target texts using BERT embeddings.
        Rank by combined (average) of cosine and euclidean similarity.
        """
        try:
            # Generate embeddings
            source_embedding = self.model.encode(source_text, convert_to_tensor=True)
            target_embeddings = self.model.encode(target_texts, convert_to_tensor=True)

            # Compute both similarities
            cosine_similarities = self._compute_cosine_similarity(source_embedding, target_embeddings)
            euclidean_similarities = self._compute_euclidean_similarity(source_embedding, target_embeddings)

            # Compute combined (average) score for each resume
            combined_scores = (cosine_similarities + euclidean_similarities) / 2

            # Build results using combined score for ranking
            results = [
                {
                    'index': i,
                    'similarity_score': float(combined_scores[i]),  # Use combined score for ranking
                    'cosine_similarity': float(cosine_similarities[i]),
                    'euclidean_similarity': float(euclidean_similarities[i]),
                    'rank': 0  # Will be updated after sorting
                }
                for i in range(len(combined_scores))
            ]

            # Sort by combined score
            results.sort(key=lambda x: x['similarity_score'], reverse=True)

            # Update rankings
            for i, result in enumerate(results):
                result['rank'] = i + 1

            print("Results to return:", results)

            return results

        except Exception as e:
            self.logger.error(f"Error computing similarity: {str(e)}")
            return []

    def get_ranking_summary(
        self,
        matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a summary of the ranking results.
        
        Args:
            matches: List of similarity matches with rankings
            
        Returns:
            Dictionary containing ranking summary
        """
        if not matches:
            return {
                'total_matches': 0,
                'average_score': 0.0,
                'score_distribution': {
                    'high': 0,
                    'medium': 0,
                    'low': 0
                }
            }

        scores = [match['similarity_score'] for match in matches]
        avg_score = sum(scores) / len(scores)

        # Categorize scores
        score_distribution = {
            'high': len([s for s in scores if s >= 0.7]),
            'medium': len([s for s in scores if 0.4 <= s < 0.7]),
            'low': len([s for s in scores if s < 0.4])
        }

        return {
            'total_matches': len(matches),
            'average_score': avg_score,
            'score_distribution': score_distribution,
            'top_ranked': [
                {
                    'rank': match['rank'],
                    'resume_id': f"resume_{match['index']}",
                    'score': match['similarity_score']
                }
                for match in matches[:3]  # Top 3 matches
            ]
        }

    def _compute_cosine_similarity(
        self,
        source_embedding: torch.Tensor,
        target_embeddings: torch.Tensor
    ) -> np.ndarray:
        """Compute cosine similarity between BERT embeddings."""
        from torch.nn.functional import cosine_similarity
        # source_embedding: [384], target_embeddings: [N, 384]
        if len(target_embeddings.shape) == 1:
            # Single vector, for explanation
            return cosine_similarity(source_embedding, target_embeddings, dim=0).item()
        else:
            # Batch, for compute_similarity
            similarities = cosine_similarity(target_embeddings, source_embedding.unsqueeze(0), dim=1)
            return similarities.cpu().numpy()

    def _compute_euclidean_similarity(
        self,
        source_embedding: torch.Tensor,
        target_embeddings: torch.Tensor
    ) -> np.ndarray:
        """Compute similarity based on Euclidean distance between BERT embeddings."""
        # source_embedding: [384], target_embeddings: [N, 384]
        if len(target_embeddings.shape) == 1:
            # Single vector, for explanation
            # Ensure both are 2D
            if len(source_embedding.shape) == 1:
                source_embedding = source_embedding.unsqueeze(0)
            if len(target_embeddings.shape) == 1:
                target_embeddings = target_embeddings.unsqueeze(0)
            distance = torch.cdist(source_embedding, target_embeddings, p=2)[0][0]
            similarity = 1 / (1 + distance)
            return similarity.item()
        else:
            # Batch, for compute_similarity
            distances = torch.cdist(target_embeddings, source_embedding.unsqueeze(0), p=2).squeeze(1)
            similarities = 1 / (1 + distances)
            return similarities.cpu().numpy()

    def _compute_combined_similarity(
        self,
        source_embedding: torch.Tensor,
        target_embeddings: torch.Tensor,
        weights: Optional[Dict[str, float]] = None
    ) -> np.ndarray:
        """Compute combined similarity using multiple metrics."""
        if weights is None:
            weights = {
                'cosine': 0.7,
                'euclidean': 0.3
            }

        # Compute individual similarities
        cosine_sim = self._compute_cosine_similarity(source_embedding, target_embeddings)
        euclidean_sim = self._compute_euclidean_similarity(source_embedding, target_embeddings)

        # Combine similarities with weights
        combined_sim = (
            weights['cosine'] * cosine_sim +
            weights['euclidean'] * euclidean_sim
        )

        return combined_sim

    def get_similarity_explanation(
        self,
        source_text: str,
        target_text: str,
        config: SimilarityConfig
    ) -> Dict[str, Any]:
        """
        Generate explanation for similarity score between two texts.
        
        Args:
            source_text: Source document text
            target_text: Target document text
            config: Similarity configuration
            
        Returns:
            Dictionary containing similarity explanation
        """
        try:
            # Generate embeddings
            source_embedding = self.model.encode(source_text, convert_to_tensor=True)
            target_embedding = self.model.encode(target_text, convert_to_tensor=True)

            # Ensure both are 1D tensors
            if len(source_embedding.shape) > 1:
                source_embedding = source_embedding.squeeze(0)
            if len(target_embedding.shape) > 1:
                target_embedding = target_embedding.squeeze(0)

            # Compute similarities
            cosine_score = float(self._compute_cosine_similarity(source_embedding, target_embedding))
            euclidean_score = float(self._compute_euclidean_similarity(source_embedding, target_embedding))

            # Generate explanation
            explanation = self._generate_explanation(cosine_score, euclidean_score)

            return {
                'cosine_similarity': cosine_score,
                'euclidean_similarity': euclidean_score,
                'explanation': explanation
            }

        except Exception as e:
            self.logger.error(f"Error generating similarity explanation: {str(e)}")
            return {
                'cosine_similarity': 0.0,
                'euclidean_similarity': 0.0,
                'explanation': "Error generating explanation"
            }

    def _generate_explanation(
        self,
        cosine_score: float,
        euclidean_score: float
    ) -> str:
        """Generate human-readable explanation of similarity scores."""
        if cosine_score >= 0.8:
            similarity_level = "very high"
        elif cosine_score >= 0.6:
            similarity_level = "high"
        elif cosine_score >= 0.4:
            similarity_level = "moderate"
        else:
            similarity_level = "low"

        explanation = (
            f"The documents show {similarity_level} semantic similarity "
            f"(cosine similarity: {cosine_score:.2f}, "
            f"euclidean similarity: {euclidean_score:.2f}). "
        )

        if cosine_score >= 0.8:
            explanation += "This indicates a strong match in terms of content and context."
        elif cosine_score >= 0.6:
            explanation += "This suggests a good match with some differences in specific details."
        elif cosine_score >= 0.4:
            explanation += "There is some overlap in content, but significant differences exist."
        else:
            explanation += "The documents appear to be quite different in terms of content and context."

        return explanation 