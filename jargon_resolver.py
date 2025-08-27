import re
import json
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class JargonResolver:
    def __init__(self):
        """Initialize with TikTok-specific jargon dictionary"""
        self.jargon_dictionary = self._build_jargon_dictionary()
        
    def _build_jargon_dictionary(self) -> Dict[str, str]:
        """Build comprehensive jargon dictionary for TikTok internal terms"""
        return {
            # TikTok Internal Systems
            'jellybean': 'content moderation system',
            'glow': 'recommendation algorithm',
            'spanner': 'distributed database system',
            'libra': 'user safety framework',
            'compass': 'content policy engine',
            'lighthouse': 'compliance monitoring system',
            'prism': 'user analytics platform',
            'atlas': 'geographic content routing',
            'nexus': 'cross-platform integration',
            'quantum': 'real-time processing engine',
            
            # Content & Safety Terms
            'ugc': 'user-generated content',
            'csam': 'child sexual abuse material',
            'dmca': 'digital millennium copyright act takedown',
            'violative content': 'content that violates community guidelines',
            'shadow ban': 'content visibility restriction',
            'content takedown': 'content removal from platform',
            'deboost': 'reduce content reach in algorithm',
            'safety mode': 'restricted content viewing mode',
            'trust and safety': 'user protection and content moderation',
            
            # User & Account Terms
            'minor user': 'user under 18 years old',
            'verified account': 'account with verified identity',
            'creator fund': 'monetization program for content creators',
            'brand account': 'business or organization account',
            'influencer tier': 'classification based on follower count',
            'account restriction': 'limitation on account functionality',
            'age gate': 'age verification checkpoint',
            
            # Algorithm & Personalization
            'fyp': 'for you page recommendation feed',
            'engagement signal': 'user interaction metric',
            'content signal': 'algorithmic content quality indicator',
            'user signal': 'behavioral pattern indicator',
            'recommendation engine': 'algorithm suggesting content to users',
            'content ranking': 'algorithmic content prioritization',
            'personalization vector': 'user preference data representation',
            'interest graph': 'user interest mapping system',
            
            # Data & Privacy
            'pii': 'personally identifiable information',
            'device fingerprint': 'unique device identification method',
            'cross-device tracking': 'user activity tracking across devices',
            'data retention policy': 'rules for keeping user data',
            'gdpr compliance': 'general data protection regulation adherence',
            'ccpa compliance': 'california consumer privacy act adherence',
            'data localization': 'storing data within specific geographic boundaries',
            'user consent': 'explicit permission for data processing',
            
            # Regional & Compliance
            'geo-blocking': 'restricting content by geographic location',
            'region lock': 'limiting feature access by location',
            'compliance framework': 'regulatory adherence system',
            'age verification system': 'method to verify user age',
            'parental consent': 'guardian permission for minor accounts',
            'curfew mode': 'time-based usage restrictions',
            'local content policy': 'region-specific content rules',
            'regulatory sandbox': 'testing environment for compliance features',
            
            # Technical Terms
            'api endpoint': 'software interface access point',
            'microservice': 'independent software component',
            'feature flag': 'toggle for enabling/disabling features',
            'a/b test': 'comparing two versions of a feature',
            'circuit breaker': 'system failure protection mechanism',
            'rate limiting': 'controlling request frequency',
            'load balancer': 'traffic distribution system',
            'cdn': 'content delivery network',
            
            # Business Terms
            'kpi': 'key performance indicator',
            'dau': 'daily active users',
            'mau': 'monthly active users',
            'ltv': 'lifetime value',
            'churn rate': 'user retention metric',
            'conversion funnel': 'user journey tracking',
            'retention cohort': 'user group retention analysis',
            'growth hack': 'strategy to increase user adoption',
            
            # Content Types
            'short form video': 'video content under 60 seconds',
            'live streaming': 'real-time video broadcast',
            'duet': 'collaborative video format',
            'stitch': 'video remix feature',
            'sound bite': 'audio clip for video creation',
            'hashtag challenge': 'trending topic campaign',
            'branded content': 'sponsored or promotional material',
            
            # Moderation Terms
            'auto-mod': 'automated content moderation',
            'human review': 'manual content evaluation',
            'appeal process': 'user challenge to moderation decision',
            'strike system': 'progressive penalty framework',
            'community guidelines': 'platform usage rules',
            'terms of service': 'legal agreement for platform use',
            'content policy': 'rules governing acceptable content'
        }
    
    def resolve_jargon(self, text: str) -> Dict[str, str]:
        """
        Find and resolve jargon terms in the given text
        Returns a dictionary mapping found jargon to their meanings
        """
        try:
            resolved_terms = {}
            text_lower = text.lower()
            
            # Check for each jargon term
            for jargon, meaning in self.jargon_dictionary.items():
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(jargon.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    resolved_terms[jargon] = meaning
            
            # Check for common abbreviations and acronyms
            resolved_terms.update(self._find_acronyms(text))
            
            # Check for compound jargon terms
            resolved_terms.update(self._find_compound_terms(text))
            
            logger.info(f"Resolved {len(resolved_terms)} jargon terms")
            return resolved_terms
            
        except Exception as e:
            logger.error(f"Jargon resolution failed: {str(e)}")
            return {}
    
    def _find_acronyms(self, text: str) -> Dict[str, str]:
        """Find and resolve acronyms in text"""
        acronym_map = {
            'AI': 'artificial intelligence',
            'ML': 'machine learning',
            'NLP': 'natural language processing',
            'API': 'application programming interface',
            'SDK': 'software development kit',
            'CDN': 'content delivery network',
            'DNS': 'domain name system',
            'SSL': 'secure sockets layer',
            'HTTPS': 'hypertext transfer protocol secure',
            'JSON': 'javascript object notation',
            'XML': 'extensible markup language',
            'SQL': 'structured query language',
            'NoSQL': 'not only structured query language',
            'REST': 'representational state transfer',
            'CRUD': 'create read update delete',
            'QR': 'quick response',
            'IP': 'internet protocol',
            'TCP': 'transmission control protocol',
            'HTTP': 'hypertext transfer protocol',
            'FTP': 'file transfer protocol'
        }
        
        found_acronyms = {}
        
        # Look for uppercase acronyms
        acronym_pattern = r'\b[A-Z]{2,6}\b'
        matches = re.findall(acronym_pattern, text)
        
        for match in matches:
            if match in acronym_map:
                found_acronyms[match] = acronym_map[match]
        
        return found_acronyms
    
    def _find_compound_terms(self, text: str) -> Dict[str, str]:
        """Find compound jargon terms (multi-word expressions)"""
        compound_terms = {
            'machine learning model': 'algorithm that learns from data to make predictions',
            'content moderation pipeline': 'automated system for reviewing and filtering content',
            'user behavior analytics': 'analysis of user interaction patterns',
            'real-time processing': 'immediate data processing without delay',
            'distributed system': 'software running across multiple connected computers',
            'microservice architecture': 'software design using small independent services',
            'cloud infrastructure': 'computing resources provided over the internet',
            'data pipeline': 'series of processes for moving and transforming data',
            'feature engineering': 'process of selecting and transforming data for machine learning',
            'a/b testing framework': 'system for comparing different versions of features',
            'recommendation algorithm': 'system that suggests content based on user preferences',
            'content delivery network': 'distributed system for delivering web content efficiently',
            'load balancing': 'distributing workload across multiple computing resources',
            'auto-scaling': 'automatically adjusting computing resources based on demand',
            'fault tolerance': 'system ability to continue operating despite failures',
            'data governance': 'management of data availability, usability, integrity and security'
        }
        
        found_compounds = {}
        text_lower = text.lower()
        
        for compound, meaning in compound_terms.items():
            if compound.lower() in text_lower:
                found_compounds[compound] = meaning
        
        return found_compounds
    
    def add_custom_jargon(self, jargon: str, meaning: str):
        """Add custom jargon term to dictionary"""
        self.jargon_dictionary[jargon.lower()] = meaning
        logger.info(f"Added custom jargon: {jargon} -> {meaning}")
    
    def get_jargon_suggestions(self, text: str) -> List[str]:
        """Get suggestions for potential jargon that might need review"""
        suggestions = []
        
        # Look for patterns that might be jargon
        # CamelCase terms
        camel_case_pattern = r'\b[a-z]+[A-Z][a-zA-Z]*\b'
        camel_matches = re.findall(camel_case_pattern, text)
        suggestions.extend([f"CamelCase term: {match}" for match in camel_matches])
        
        # All caps words (potential acronyms)
        caps_pattern = r'\b[A-Z]{3,}\b'
        caps_matches = re.findall(caps_pattern, text)
        unknown_caps = [match for match in caps_matches if match.lower() not in self.jargon_dictionary]
        suggestions.extend([f"Potential acronym: {match}" for match in unknown_caps])
        
        # Technical-sounding compound words
        compound_pattern = r'\b\w+-\w+\b'
        compound_matches = re.findall(compound_pattern, text)
        suggestions.extend([f"Compound term: {match}" for match in compound_matches])
        
        return suggestions[:10]  # Limit suggestions
    
    def export_jargon_dictionary(self, filepath: str = 'data/jargon_dictionary.json'):
        """Export jargon dictionary to JSON file"""
        try:
            import os
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(self.jargon_dictionary, f, indent=2, sort_keys=True)
            
            logger.info(f"Jargon dictionary exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export jargon dictionary: {str(e)}")
    
    def load_custom_jargon(self, filepath: str):
        """Load custom jargon from JSON file"""
        try:
            with open(filepath, 'r') as f:
                custom_jargon = json.load(f)
            
            self.jargon_dictionary.update(custom_jargon)
            logger.info(f"Loaded {len(custom_jargon)} custom jargon terms from {filepath}")
            
        except Exception as e:
            logger.warning(f"Could not load custom jargon from {filepath}: {str(e)}")