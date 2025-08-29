import openai
import google.generativeai as genai
import os
import json
import logging
import re
from typing import Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ComplianceAnalyzer:
    def __init__(self, knowledge_base, jargon_resolver):
        self.kb = knowledge_base
        self.jargon_resolver = jargon_resolver
        
        gemini_api_key = os.getenv("GEMINI_API_KEY", "dummy-key")
        if gemini_api_key != "dummy-key":
            genai.configure(api_key=gemini_api_key)
            self.client = genai.GenerativeModel("gemini-2.5-flash") 
        else:
            self.client = None
        
        # Risk scoring weights
        self.risk_weights = {
            'child_safety': 40,
            'data_privacy': 30,
            'content_moderation': 25,
            'user_verification': 20,
            'algorithmic_transparency': 15,
            'data_localization': 10,
            'age_verification': 35,
            'content_blocking': 20,
            'parental_controls': 30
        }
        
        # High-risk keywords for different categories
        self.risk_keywords = {
            'child_safety': ['minor', 'child', 'youth', 'teen', 'age verification', 'parental', 'guardian', 'curfew'],
            'data_privacy': ['personal data', 'user data', 'tracking', 'profiling', 'analytics', 'targeting'],
            'content_moderation': ['harmful content', 'violence', 'hate', 'misinformation', 'content removal'],
            'algorithmic_transparency': ['recommendation', 'algorithm', 'personalization', 'feed', 'ranking'],
            'data_localization': ['data storage', 'server location', 'cross-border', 'data transfer']
        }

    def analyze_feature(self, title: str, description: str, prd: str = "", trd: str = "") -> Dict:
        """
        Main analysis function that determines if a feature requires geo-compliance
        """
        try:
            # Combine all text
            full_text = f"{title} {description} {prd} {trd}".strip()
            
            # Step 1: Resolve jargon
            jargon_resolved = self.jargon_resolver.resolve_jargon(full_text)
            resolved_text = self._apply_jargon_resolution(full_text, jargon_resolved)
            
            # Step 2: Check against knowledge base
            relevant_regulations = self.kb.find_relevant_regulations(resolved_text)
            
            # Step 3: LLM-based analysis
            llm_analysis = self._llm_compliance_check(resolved_text, relevant_regulations)
            
            # Step 4: Calculate risk score
            risk_score = self._calculate_risk_score(resolved_text, relevant_regulations, llm_analysis)
            
            # Step 5: Determine final flag
            requires_compliance = self._determine_compliance_flag(llm_analysis, risk_score, relevant_regulations)
            
            # Step 6: Extract regions and regulations
            regions_affected = self._extract_affected_regions(relevant_regulations, llm_analysis)
            regulation_names = [reg['name'] for reg in relevant_regulations]
            
            # Step 7: Generate evidence and reasoning
            evidence = self._generate_evidence(resolved_text, relevant_regulations, llm_analysis)
            reasoning = llm_analysis.get('reasoning', 'Analysis based on regulatory knowledge base matching')
            
            return {
                'requires_geo_compliance': requires_compliance,
                'reasoning': reasoning,
                'related_regulations': regulation_names,
                'risk_score': risk_score,
                'regions_affected': regions_affected,
                'evidence': evidence,
                'jargon_resolved': jargon_resolved
            }
            
        except Exception as e:
            logger.error(f"Feature analysis failed: {str(e)}")
            # Fallback response
            return {
                'requires_geo_compliance': False,
                'reasoning': f'Analysis failed: {str(e)}. Defaulting to no compliance required.',
                'related_regulations': [],
                'risk_score': 0,
                'regions_affected': [],
                'evidence': 'Error in analysis pipeline',
                'jargon_resolved': {}
            }

    def _apply_jargon_resolution(self, text: str, jargon_map: Dict[str, str]) -> str:
        """Apply jargon resolution to text"""
        resolved_text = text
        for jargon, meaning in jargon_map.items():
            # Replace jargon with meaning in text
            pattern = re.compile(re.escape(jargon), re.IGNORECASE)
            resolved_text = pattern.sub(f"{jargon} ({meaning})", resolved_text)
        return resolved_text

    def _llm_compliance_check(self, text: str, relevant_regulations: List[Dict]) -> Dict:
        """Use LLM to analyze compliance requirements"""
        try:
            # Prepare context
            reg_context = "\n".join([
                f"- Name: {reg['name']}\n"
                f"  Jurisdiction: {reg['jurisdiction']}\n"
                f"  Description: {reg['description']}\n"
                f"  Obligations: {', '.join(reg['key_obligations'])}\n"
                f"  Scope: {', '.join(reg['scope'])}"
                for reg in relevant_regulations[:3]
            ])
            
            allowed_jurisdictions = [reg['jurisdiction'] for reg in relevant_regulations]
            allowed_jurisdictions_str = ", ".join(allowed_jurisdictions)

            
            prompt = f"""
            You are a legal compliance expert analyzing whether a software feature requires geo-specific regulatory compliance.

            FEATURE DESCRIPTION:
            {text}

            RELEVANT REGULATIONS:
            {reg_context}

            Analyze this feature and determine:
            1. Does it require geo-specific compliance logic? (Yes/No)
            2. Why? (2-3 sentences)
            3. Which specific regulatory obligations might apply?
            4. What regions are most likely affected?**Only select from the following jurisdictions: {allowed_jurisdictions_str}**

            Respond in JSON format:
            {{
                "requires_compliance": boolean,
                "reasoning": "string",
                "obligations": ["string"],
                "likely_regions": ["string"],
                "confidence": 0-100
            }}
            """
            result = None
            if self.client:
                response = self.client.generate_content(prompt)
                # ✅ Gemini: extract text safely
                raw_text = ""
                try:
                    raw_text = response.candidates[0].content[0].text
                except Exception:
                     raw_text = getattr(response, "text", "")
                import re, json
                match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                if match:
                    try:
                        result = json.loads(match.group())
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse JSON from Gemini output")
                        result = self._fallback_compliance_analysis(text, relevant_regulations)
                    
            if not result:
                result = self._fallback_compliance_analysis(text, relevant_regulations)

            
            return result
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
            return self._fallback_compliance_analysis(text, relevant_regulations)

    def _fallback_compliance_analysis(self, text: str, relevant_regulations: List[Dict]) -> Dict:
        """Fallback analysis without LLM API"""
        # Simple keyword-based analysis
        text_lower = text.lower()
        
        requires_compliance = False
        obligations = []
        likely_regions = []
        reasoning = "Analysis based on keyword matching and regulation database. "
        
        # Check for high-risk keywords
        risk_categories = []
        for category, keywords in self.risk_keywords.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                risk_categories.append(category)
                requires_compliance = True
        
        if risk_categories:
            reasoning += f"Detected risk categories: {', '.join(risk_categories)}. "
        
        # Check relevant regulations
        if relevant_regulations:
            requires_compliance = True
            likely_regions = list(set([reg['jurisdiction'] for reg in relevant_regulations]))
            obligations = [reg['key_obligations'][0] if reg['key_obligations'] else 'General compliance' 
                          for reg in relevant_regulations[:3]]
            reasoning += f"Matched against {len(relevant_regulations)} relevant regulations."
        else:
            reasoning += "No specific regulations matched."
        
        return {
            'requires_compliance': requires_compliance,
            'reasoning': reasoning,
            'obligations': obligations,
            'likely_regions': likely_regions,
            'confidence': 75 if requires_compliance else 85
        }

    def _calculate_risk_score(self, text: str, regulations: List[Dict], llm_analysis: Dict) -> int:
        """Calculate risk score (0-100)"""
        score = 0
        text_lower = text.lower()
        
        # Base score from keyword matching
        for category, keywords in self.risk_keywords.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                score += self.risk_weights.get(category, 10)
        
        # Score from regulation count and severity
        if regulations:
            score += min(len(regulations) * 15, 30)
            
            # Higher score for child safety regulations
            for reg in regulations:
                if any(keyword in reg['name'].lower() for keyword in ['child', 'minor', 'youth']):
                    score += 20
                if 'california' in reg['jurisdiction'].lower():
                    score += 10  # CCPA/CPRA tend to be stricter
        
        # LLM confidence boost
        if llm_analysis.get('requires_compliance', False):
            confidence = llm_analysis.get('confidence', 50)
            score += int(confidence * 0.3)
        
        # Normalize to 0-100
        return min(max(score, 0), 100)

    def _determine_compliance_flag(self, llm_analysis: Dict, risk_score: int, regulations: List[Dict]) -> bool:
        """Determine final compliance flag"""
        # Multiple signals approach
        signals = []
        
        # LLM signal
        if llm_analysis.get('requires_compliance', False):
            signals.append(True)
        
        # Risk score signal
        if risk_score >= 30:
            signals.append(True)
        
        # Regulation match signal
        if regulations:
            signals.append(True)
        
        # Require at least 2/3 signals for positive flag
        return sum(signals) >= 2

    def _extract_affected_regions(self, regulations: List[Dict], llm_analysis: Dict) -> List[str]:
        """Extract list of affected regions/jurisdictions"""
        regions = set()
        
        # From regulations
        for reg in regulations:
            regions.add(reg['jurisdiction'])
        
        # From LLM analysis
        if 'likely_regions' in llm_analysis:
            regions.update(llm_analysis['likely_regions'])
        
        return sorted(list(regions))

    def _generate_evidence(self, text: str, regulations: List[Dict], llm_analysis: Dict) -> str:
        """Generate evidence string for audit trail"""
        evidence_parts = []
        
        # Text snippet
        text_snippet = text[:200] + "..." if len(text) > 200 else text
        evidence_parts.append(f"Feature text: {text_snippet}")
        
        # Matched regulations
        if regulations:
            reg_matches = []
            for reg in regulations[:3]:
                matched_keywords = [k for k in self.risk_keywords.keys() 
                    if any(kw in text.lower() for kw in self.risk_keywords[k])]
                reg_matches.append(f"{reg['name']} (matched keywords: {', '.join(matched_keywords)})")
            evidence_parts.append(f"Matched regulations: {', '.join(reg_matches)}")
        
        # LLM confidence
        if 'confidence' in llm_analysis:
            evidence_parts.append(f"Analysis confidence: {llm_analysis['confidence']}%")
        
        return " | ".join(evidence_parts)