import json
import logging
import numpy as np
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class RegulationKnowledgeBase:
    def __init__(self):
        self.regulations = []
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.regulation_vectors = None
        self.is_built = False
        
    def build_knowledge_base(self):
        """Build the regulation knowledge base"""
        try:
            # Load regulation data
            self.regulations = self._load_regulation_data()
            
            # Build search index
            self._build_search_index()
            
            self.is_built = True
            logger.info(f"Knowledge base built with {len(self.regulations)} regulations")
            
        except Exception as e:
            logger.error(f"Failed to build knowledge base: {str(e)}")
            raise
    
    def fetch_dsa_from_eurlex(self) -> Dict:
        """
        Fetch EU Digital Services Act (DSA) from EUR-Lex API (demo).
        Falls back to static content if request fails.
        """
        url = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32022R2065"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")
            
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find("h1").text.strip() if soup.find("h1") else "EU Digital Services Act (DSA)"
            paragraphs = [p.text.strip() for p in soup.find_all("p")[:5]]
            
            return {
                'id': 'eu_dsa_2022',
                'name': title,
                'jurisdiction': 'European Union',
                'description': " ".join(paragraphs),
                'key_obligations': [
                    'Content moderation transparency reports',
                    'Risk assessment for systemic risks',
                    'User notification of content moderation decisions',
                    'Appeals process for users',
                    'Age-appropriate design for minors'
                ],
                'scope': [
                    'content moderation',
                    'recommendation systems',
                    'user safety',
                    'algorithmic transparency',
                    'child protection'
                ],
                'penalties': 'Up to 6% of global annual turnover',
                'effective_date': '2024-02-17'
            }
        except Exception as e:
            logger.warning(f"Failed to fetch live DSA from EUR-Lex: {e}. Using static fallback.")
            return {
                'id': 'eu_dsa_2022',
                'name': 'EU Digital Services Act (DSA)',
                'jurisdiction': 'European Union',
                'description': 'Regulation governing online platforms, requiring transparency, risk assessment, and user protection, with special focus on minors and algorithmic accountability.',
                'key_obligations': [
                    'Content moderation transparency reports',
                    'Risk assessment for systemic risks',
                    'User notification of content moderation decisions',
                    'Appeals process for users',
                    'Age-appropriate design for minors'
                ],
                'scope': [
                    'content moderation',
                    'recommendation systems',
                    'user safety',
                    'algorithmic transparency',
                    'child protection'
                ],
                'penalties': 'Up to 6% of global annual turnover',
                'effective_date': '2024-02-17'
            }
    
    def _load_regulation_data(self) -> List[Dict]:
        """Load regulation data (focused on hackathon scope)"""
        
        regulations = []
        # Try live fetch for EU DSA
        regulations.append(self.fetch_dsa_from_eurlex())
        
        regulations.extend([
        {
            'id': 'ca_kids_addiction_2024',
            'name': 'California Protecting Our Kids from Social Media Addiction Act',
            'jurisdiction': 'California, US',
            'description': 'California state law targeting addictive design features in social media that affect minors.',
            'key_obligations': [
                'Ban use of addictive design features for minors',
                'Age verification for users',
                'Default high-privacy settings for minors',
                'Provide parental controls for minor accounts'
            ],
            'scope': [
                'minors protection',
                'addictive features',
                'age verification',
                'parental controls',
                'privacy by default'
            ],
            'penalties': 'Civil penalties and potential damages per affected child',
            'effective_date': '2024-07-01'
        },
        {
            'id': 'fl_online_protections_2024',
            'name': 'Florida Online Protections for Minors Act',
            'jurisdiction': 'Florida, US',
            'description': 'Law requiring social media platforms to restrict harmful content and addictive features for minors in Florida.',
            'key_obligations': [
                'Ban accounts for users under 14',
                'Require parental consent for users under 16',
                'Restrict addictive design features for minors',
                'Provide parental access controls'
            ],
            'scope': [
                'age restrictions',
                'parental consent',
                'addictive design',
                'minor account restrictions'
            ],
            'penalties': 'Civil penalties per violation; private right of action',
            'effective_date': '2024-07-01'
        },
        {
            'id': 'ut_social_media_2023',
            'name': 'Utah Social Media Regulation Act',
            'jurisdiction': 'Utah, US',
            'description': 'Utah law requiring strict parental oversight, age verification, and time restrictions for minors using social media.',
            'key_obligations': [
                'Mandatory age verification for all users',
                'Parental consent for minor accounts',
                'Nighttime curfew for minors (10pm-6am)',
                'Prohibit certain addictive features for minors',
                'Provide parents with account access'
            ],
            'scope': [
                'age verification',
                'parental oversight',
                'curfew enforcement',
                'addictive design features',
                'minor protection'
            ],
            'penalties': 'Civil penalties up to $5,000 per violation',
            'effective_date': '2024-03-01'
        },
        {
            'id': 'us_ncmec_reporting',
            'name': 'US Law - Reporting Child Sexual Abuse Content to NCMEC',
            'jurisdiction': 'United States',
            'description': 'Federal requirement for electronic service providers to report child sexual abuse material (CSAM) to the National Center for Missing and Exploited Children (NCMEC).',
            'key_obligations': [
                'Report known CSAM to NCMEC immediately',
                'Preserve reported content for law enforcement',
                'Provide technical assistance during investigations',
                'Maintain procedures to detect and report CSAM'
            ],
            'scope': [
                'child safety',
                'content scanning',
                'law enforcement reporting',
                'CSAM detection',
                'content preservation'
            ],
            'penalties': 'Criminal penalties and civil liability for non-compliance',
            'effective_date': '1998-10-30'
        }
        ])
        return regulations

    
    def _build_search_index(self):
        """Build TF-IDF search index for regulations"""
        try:
            # Combine text fields for each regulation
            regulation_texts = []
            for reg in self.regulations:
                combined_text = f"{reg['name']} {reg['description']} {' '.join(reg['key_obligations'])} {' '.join(reg['scope'])}"
                regulation_texts.append(combined_text)
            
            # Build TF-IDF vectors
            self.regulation_vectors = self.vectorizer.fit_transform(regulation_texts)
            
            # Save index for faster loading
            self._save_index()
            
        except Exception as e:
            logger.error(f"Failed to build search index: {str(e)}")
            raise
    
    def _save_index(self):
        """Save vectorizer and vectors to disk"""
        try:
            os.makedirs('data', exist_ok=True)
            
            with open('data/vectorizer.pkl', 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            with open('data/regulation_vectors.pkl', 'wb') as f:
                pickle.dump(self.regulation_vectors, f)
                
        except Exception as e:
            logger.warning(f"Could not save index: {str(e)}")
    
    def find_relevant_regulations(self, text: str, threshold: float = 0.1, max_results: int = 5) -> List[Dict]:
        """Find regulations relevant to the given text"""
        if not self.is_built:
            logger.warning("Knowledge base not built, returning empty results")
            return []
        
        try:
            # Vectorize input text
            text_vector = self.vectorizer.transform([text])
            
            # Calculate similarities
            similarities = cosine_similarity(text_vector, self.regulation_vectors).flatten()
            
            # Get top matches above threshold
            relevant_indices = []
            for i, sim in enumerate(similarities):
                if sim >= threshold:
                    relevant_indices.append((i, sim))
            
            # Sort by similarity and limit results
            relevant_indices.sort(key=lambda x: x[1], reverse=True)
            relevant_indices = relevant_indices[:max_results]
            
            # Return relevant regulations with similarity scores
            relevant_regs = []
            for idx, similarity in relevant_indices:
                reg = self.regulations[idx].copy()
                reg['similarity_score'] = similarity
                relevant_regs.append(reg)
            
            logger.info(f"Found {len(relevant_regs)} relevant regulations for query")
            return relevant_regs
            
        except Exception as e:
            logger.error(f"Regulation search failed: {str(e)}")
            return []
    
    def get_regulation_by_id(self, reg_id: str) -> Dict:
        """Get specific regulation by ID"""
        for reg in self.regulations:
            if reg['id'] == reg_id:
                return reg
        return None
    
    def get_regulations_by_jurisdiction(self, jurisdiction: str) -> List[Dict]:
        """Get all regulations for a specific jurisdiction"""
        return [reg for reg in self.regulations if jurisdiction.lower() in reg['jurisdiction'].lower()]
    
    def get_all_jurisdictions(self) -> List[str]:
        """Get list of all jurisdictions in knowledge base"""
        jurisdictions = set()
        for reg in self.regulations:
            jurisdictions.add(reg['jurisdiction'])
        return sorted(list(jurisdictions))