import json
import logging
import numpy as np
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

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
    
    def _load_regulation_data(self) -> List[Dict]:
        """Load regulation data (hardcoded for prototype)"""
        regulations = [
            {
                'id': 'eu_dsa_2022',
                'name': 'EU Digital Services Act (DSA)',
                'jurisdiction': 'European Union',
                'description': 'Regulation on digital services, content moderation, and platform accountability. Requires risk assessment for large platforms and transparency in content moderation.',
                'key_obligations': [
                    'Content moderation transparency reports',
                    'Risk assessment for systemic risks',
                    'User notification of content decisions',
                    'Appeals process for content moderation',
                    'Age-appropriate design for minors'
                ],
                'scope': [
                    'content moderation',
                    'recommendation systems',
                    'user safety',
                    'algorithmic transparency',
                    'harmful content removal'
                ],
                'penalties': 'Up to 6% of global annual turnover',
                'effective_date': '2024-02-17'
            },
            {
                'id': 'ca_ccpa_2020',
                'name': 'California Consumer Privacy Act (CCPA)',
                'jurisdiction': 'California, US',
                'description': 'Privacy law giving California residents rights over their personal information including right to know, delete, and opt-out of sale.',
                'key_obligations': [
                    'Privacy policy disclosures',
                    'Right to know data collection',
                    'Right to delete personal information',
                    'Right to opt-out of data sale',
                    'Non-discrimination for privacy rights exercise'
                ],
                'scope': [
                    'personal data collection',
                    'data sharing',
                    'user profiling',
                    'targeted advertising',
                    'data analytics'
                ],
                'penalties': 'Up to $7,500 per violation',
                'effective_date': '2020-01-01'
            },
            {
                'id': 'fl_social_media_2021',
                'name': 'Florida Social Media Law',
                'jurisdiction': 'Florida, US',
                'description': 'Law restricting social media platforms from deplatforming political candidates and requiring disclosure of content moderation practices.',
                'key_obligations': [
                    'Cannot deplatform political candidates',
                    'Content moderation standards disclosure',
                    'Consistent application of community standards',
                    'User notification of content actions'
                ],
                'scope': [
                    'content moderation',
                    'political content',
                    'deplatforming',
                    'community standards'
                ],
                'penalties': 'Up to $250,000 per day for candidates',
                'effective_date': '2021-07-01'
            },
            {
                'id': 'ut_social_media_2023',
                'name': 'Utah Social Media Regulation Act',
                'jurisdiction': 'Utah, US',
                'description': 'Law requiring age verification and parental consent for minors, restricting certain features for youth users.',
                'key_obligations': [
                    'Age verification for users under 18',
                    'Parental consent for minor accounts',
                    'Curfew features (10pm-6am restriction)',
                    'Prohibit certain addictive features for minors',
                    'Default privacy settings for minors'
                ],
                'scope': [
                    'age verification',
                    'minors protection',
                    'parental controls',
                    'curfew enforcement',
                    'addictive design features'
                ],
                'penalties': 'Civil penalties up to $5,000 per violation',
                'effective_date': '2024-03-01'
            },
            {
                'id': 'us_coppa_1998',
                'name': 'Children\'s Online Privacy Protection Act (COPPA)',
                'jurisdiction': 'United States',
                'description': 'Federal law protecting privacy of children under 13, requiring parental consent for data collection.',
                'key_obligations': [
                    'Parental consent for data collection under 13',
                    'Privacy notice for parents',
                    'Limited collection and use of children\'s data',
                    'No behavioral advertising to children',
                    'Data deletion upon parent request'
                ],
                'scope': [
                    'children under 13',
                    'parental consent',
                    'data collection',
                    'behavioral advertising',
                    'age-appropriate features'
                ],
                'penalties': 'Up to $43,792 per violation',
                'effective_date': '2000-04-21'
            },
            {
                'id': 'us_ncmec_reporting',
                'name': 'NCMEC Reporting Requirements',
                'jurisdiction': 'United States',
                'description': 'Federal law requiring electronic service providers to report child sexual abuse material (CSAM) to NCMEC.',
                'key_obligations': [
                    'Report known CSAM to NCMEC',
                    'Preserve reported content',
                    'Provide technical assistance to law enforcement',
                    'Maintain reporting procedures'
                ],
                'scope': [
                    'child safety',
                    'content scanning',
                    'csam detection',
                    'law enforcement cooperation',
                    'content preservation'
                ],
                'penalties': 'Criminal penalties and civil liability',
                'effective_date': '1998-10-30'
            },
            {
                'id': 'uk_age_appropriate_design',
                'name': 'UK Age Appropriate Design Code',
                'jurisdiction': 'United Kingdom',
                'description': 'Code requiring age-appropriate design for services likely to be accessed by children.',
                'key_obligations': [
                    'Age-appropriate design by default',
                    'Data protection impact assessments',
                    'High privacy settings by default for children',
                    'Minimize data collection from children',
                    'No profiling or automated decision-making for children'
                ],
                'scope': [
                    'age-appropriate design',
                    'children\'s privacy',
                    'default settings',
                    'profiling restrictions',
                    'data minimization'
                ],
                'penalties': 'Up to 4% of global annual turnover',
                'effective_date': '2021-09-02'
            },
            {
                'id': 'gdpr_2018',
                'name': 'General Data Protection Regulation (GDPR)',
                'jurisdiction': 'European Union',
                'description': 'Comprehensive data protection regulation governing processing of personal data of EU residents.',
                'key_obligations': [
                    'Lawful basis for processing',
                    'Data subject consent',
                    'Right to be forgotten',
                    'Data portability',
                    'Privacy by design and default'
                ],
                'scope': [
                    'personal data processing',
                    'user consent',
                    'data transfers',
                    'profiling',
                    'automated decision-making'
                ],
                'penalties': 'Up to 4% of global annual turnover',
                'effective_date': '2018-05-25'
            }
        ]
        
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