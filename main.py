from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from typing import List, Optional, Dict
import pandas as pd
import numpy as np
import json
import sqlite3
import os
from datetime import datetime
import uuid
import logging
from pathlib import Path

# Import our custom modules
from compliance_analyzer import ComplianceAnalyzer
from regulation_kb import RegulationKnowledgeBase
from jargon_resolver import JargonResolver

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Geo-Regulation Compliance API", version="1.0.0")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class FeatureRequest(BaseModel):
    title: str
    description: str
    prd: Optional[str] = ""
    trd: Optional[str] = ""

class ComplianceResponse(BaseModel):
    feature_id: str
    title: str
    requires_geo_compliance: bool
    reasoning: str
    related_regulations: List[str]
    risk_score: int
    regions_affected: List[str]
    evidence: str
    jargon_resolved: Dict[str, str]
    timestamp: str

class BatchAnalysisRequest(BaseModel):
    features: List[FeatureRequest]

# Initialize components
def initialize_system():
    """Initialize all system components"""
    try:
        # Ensure directories exist
        Path("data").mkdir(exist_ok=True)
        Path("exports").mkdir(exist_ok=True)
        
        # Initialize knowledge base
        kb = RegulationKnowledgeBase()
        kb.build_knowledge_base()
        
        # Initialize jargon resolver
        jargon_resolver = JargonResolver()
        
        # Initialize compliance analyzer
        analyzer = ComplianceAnalyzer(kb, jargon_resolver)
        
        # Initialize database
        init_database()
        
        logger.info("System initialization complete")
        return analyzer
        
    except Exception as e:
        logger.error(f"System initialization failed: {str(e)}")
        raise

def init_database():
    """Initialize SQLite database for audit trails"""
    conn = sqlite3.connect('data/audit_trail.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compliance_analysis (
            id TEXT PRIMARY KEY,
            feature_title TEXT,
            requires_geo_compliance BOOLEAN,
            reasoning TEXT,
            related_regulations TEXT,
            risk_score INTEGER,
            regions_affected TEXT,
            evidence TEXT,
            jargon_resolved TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Global analyzer instance
analyzer = None

@app.on_event("startup")
async def startup_event():
    global analyzer
    analyzer = initialize_system()

@app.get("/")
async def root():
    return {"message": "Geo-Regulation Compliance API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/test-gemini")
async def test_gemini():
    """Test if Gemini API key is working"""
    try:
        # Minimal prompt
        prompt = "Say hello in a single sentence."

        # Call Gemini directly
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        return {
            "status": "success",
            "response": response.text  # Gemini's content is here
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/analyze-feature", response_model=ComplianceResponse)
async def analyze_feature(feature: FeatureRequest):
    """Analyze a single feature for geo-compliance requirements"""
    try:
        if not analyzer:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        # Generate unique ID
        feature_id = str(uuid.uuid4())
        
        # Analyze feature
        result = analyzer.analyze_feature(
            title=feature.title,
            description=feature.description,
            prd=feature.prd,
            trd=feature.trd
        )
        
        # Create response
        response = ComplianceResponse(
            feature_id=feature_id,
            title=feature.title,
            requires_geo_compliance=result['requires_geo_compliance'],
            reasoning=result['reasoning'],
            related_regulations=result['related_regulations'],
            risk_score=result['risk_score'],
            regions_affected=result['regions_affected'],
            evidence=result['evidence'],
            jargon_resolved=result['jargon_resolved'],
            timestamp=datetime.now().isoformat()
        )
        
        # Save to database
        save_to_database(feature_id, response)
        
        return response
        
    except Exception as e:
        logger.error(f"Feature analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-batch")
async def analyze_batch(request: BatchAnalysisRequest):
    """Analyze multiple features and return CSV download link"""
    try:
        if not analyzer:
            raise HTTPException(status_code=500, detail="System not initialized")
        
        results = []
        
        for feature in request.features:
            feature_id = str(uuid.uuid4())
            
            result = analyzer.analyze_feature(
                title=feature.title,
                description=feature.description,
                prd=feature.prd,
                trd=feature.trd
            )
            
            response = ComplianceResponse(
                feature_id=feature_id,
                title=feature.title,
                requires_geo_compliance=result['requires_geo_compliance'],
                reasoning=result['reasoning'],
                related_regulations=result['related_regulations'],
                risk_score=result['risk_score'],
                regions_affected=result['regions_affected'],
                evidence=result['evidence'],
                jargon_resolved=result['jargon_resolved'],
                timestamp=datetime.now().isoformat()
            )
            
            results.append(response)
            save_to_database(feature_id, response)
        
        # Generate CSV
        csv_filename = generate_csv_export(results)
        
        return {
            "message": f"Analyzed {len(results)} features",
            "results": results,
            "csv_export": csv_filename
        }
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard-data")
async def get_dashboard_data():
    """Get aggregated data for dashboard visualization"""
    try:
        conn = sqlite3.connect('data/audit_trail.db')
        
        # Get all records
        df = pd.read_sql_query('''
            SELECT * FROM compliance_analysis 
            ORDER BY timestamp DESC
        ''', conn)
        
        if df.empty:
            return {
                "total_features": 0,
                "flagged_percentage": 0,
                "risk_distribution": {},
                "region_distribution": {},
                "recent_analyses": []
            }
        
        # Parse JSON fields
        df['regions_affected'] = df['regions_affected'].apply(
            lambda x: json.loads(x) if x else []
        )
        df['related_regulations'] = df['related_regulations'].apply(
            lambda x: json.loads(x) if x else []
        )
        
        # Calculate statistics
        total_features = len(df)
        flagged_count = df['requires_geo_compliance'].sum()
        flagged_percentage = round((flagged_count / total_features) * 100, 1)
        
        # Risk distribution
        risk_bins = pd.cut(df['risk_score'], bins=[0, 30, 70, 100], labels=['Low', 'Medium', 'High'])
        risk_distribution = risk_bins.value_counts().to_dict()
        
        # Region distribution
        all_regions = []
        for regions in df['regions_affected']:
            all_regions.extend(regions)
        region_distribution = pd.Series(all_regions).value_counts().head(10).to_dict()
        
        # Recent analyses
        recent_analyses = df.head(10).to_dict('records')
        
        conn.close()
        
        return {
            "total_features": total_features,
            "flagged_count": int(flagged_count),
            "flagged_percentage": flagged_percentage,
            "risk_distribution": {str(k): int(v) for k, v in risk_distribution.items()},
            "region_distribution": region_distribution,
            "recent_analyses": recent_analyses
        }
        
    except Exception as e:
        logger.error(f"Dashboard data retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export-csv/{filename}")
async def download_csv(filename: str):
    """Download CSV export file"""
    filepath = f"exports/{filename}"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return {"download_url": f"/static/{filename}"}

def save_to_database(feature_id: str, response: ComplianceResponse):
    """Save analysis result to database"""
    conn = sqlite3.connect('data/audit_trail.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO compliance_analysis 
        (id, feature_title, requires_geo_compliance, reasoning, related_regulations, 
         risk_score, regions_affected, evidence, jargon_resolved, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        feature_id,
        response.title,
        response.requires_geo_compliance,
        response.reasoning,
        json.dumps(response.related_regulations),
        response.risk_score,
        json.dumps(response.regions_affected),
        response.evidence,
        json.dumps(response.jargon_resolved),
        response.timestamp
    ))
    
    conn.commit()
    conn.close()

def generate_csv_export(results: List[ComplianceResponse]) -> str:
    """Generate CSV export from analysis results"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"compliance_analysis_{timestamp}.csv"
    
    # Convert to DataFrame
    data = []
    for result in results:
        data.append({
            'Feature ID': result.feature_id,
            'Title': result.title,
            'Requires Geo-Compliance': result.requires_geo_compliance,
            'Risk Score': result.risk_score,
            'Reasoning': result.reasoning,
            'Related Regulations': ', '.join(result.related_regulations),
            'Regions Affected': ', '.join(result.regions_affected),
            'Evidence': result.evidence,
            'Jargon Resolved': ', '.join([f"{k}→{v}" for k, v in result.jargon_resolved.items()]),
            'Timestamp': result.timestamp
        })
    
    df = pd.DataFrame(data)
    filepath = f"exports/{filename}"
    df.to_csv(filepath, index=False)
    
    return filename

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)