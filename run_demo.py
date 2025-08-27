#!/usr/bin/env python3
"""
Demo script for Geo-Regulation Compliance System
Runs sample features through the analysis pipeline and generates results
"""

import json
import pandas as pd
from datetime import datetime
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from compliance_analyzer import ComplianceAnalyzer
from regulation_kb import RegulationKnowledgeBase
from jargon_resolver import JargonResolver

class ComplianceDemo:
    def __init__(self):
        print("🚀 Initializing Geo-Regulation Compliance System...")
        
        # Initialize components
        self.kb = RegulationKnowledgeBase()
        self.jargon_resolver = JargonResolver()
        
        print("📚 Building regulation knowledge base...")
        self.kb.build_knowledge_base()
        
        print("🔧 Initializing compliance analyzer...")
        self.analyzer = ComplianceAnalyzer(self.kb, self.jargon_resolver)
        
        print("✅ System initialization complete!\n")

    def load_sample_features(self):
        """Load sample features for testing"""
        try:
            with open('sample_features.json', 'r') as f:
                data = json.load(f)
            return data['sample_features']
        except FileNotFoundError:
            print("⚠️  Sample features file not found, using hardcoded examples...")
            return self._get_hardcoded_samples()

    def _get_hardcoded_samples(self):
        """Hardcoded sample features if file is not available"""
        return [
            {
                "title": "Curfew Mode for Teen Users",
                "description": "Automatically logs out users under 18 between 10pm and 6am based on their registered age and device location.",
                "prd": "The Curfew Mode feature implements time-based restrictions for minor users with parental controls.",
                "trd": "Technical implementation using age verification and location services for compliance."
            },
            {
                "title": "Enhanced Personalization Engine", 
                "description": "Advanced machine learning system analyzing user behavior and engagement patterns for personalized content recommendations.",
                "prd": "Personalization Engine v2.0 with behavioral analytics and cross-device tracking.",
                "trd": "Requires PII collection, device fingerprinting, and cross-border data transfers."
            },
            {
                "title": "Basic Video Upload Service",
                "description": "Standard video upload functionality with format conversion and quality optimization.",
                "prd": "Video Upload Service v1.5 with reliable video processing pipeline.",
                "trd": "Standard video processing with basic content safety scanning only."
            }
        ]

    def run_analysis(self, features):
        """Run compliance analysis on all features"""
        print("🔍 Running compliance analysis...\n")
        results = []
        
        for i, feature in enumerate(features, 1):
            print(f"📊 Analyzing Feature {i}/{len(features)}: {feature['title']}")
            
            # Run analysis
            result = self.analyzer.analyze_feature(
                title=feature['title'],
                description=feature['description'],
                prd=feature.get('prd', ''),
                trd=feature.get('trd', '')
            )
            
            # Add metadata
            result['feature_id'] = f"feat_{i:03d}"
            result['title'] = feature['title']
            result['timestamp'] = datetime.now().isoformat()
            
            results.append(result)
            
            # Display results
            self._display_feature_result(result)
            print("-" * 80)
        
        return results

    def _display_feature_result(self, result):
        """Display analysis result for a single feature"""
        print(f"  📝 Title: {result['title']}")
        
        # Compliance flag
        flag_emoji = "🚨" if result['requires_geo_compliance'] else "✅"
        flag_text = "REQUIRED" if result['requires_geo_compliance'] else "NOT REQUIRED"
        print(f"  {flag_emoji} Geo-Compliance: {flag_text}")
        
        # Risk score
        risk_emoji = "🔴" if result['risk_score'] >= 70 else "🟡" if result['risk_score'] >= 30 else "🟢"
        print(f"  {risk_emoji} Risk Score: {result['risk_score']}/100")
        
        # Regions
        if result['regions_affected']:
            print(f"  🌍 Affected Regions: {', '.join(result['regions_affected'])}")
        
        # Regulations
        if result['related_regulations']:
            print(f"  📜 Related Regulations: {', '.join(result['related_regulations'])}")
        
        # Reasoning
        print(f"  💭 Reasoning: {result['reasoning']}")
        
        # Jargon resolved
        if result['jargon_resolved']:
            print(f"  🔤 Jargon Resolved: {len(result['jargon_resolved'])} terms")
            for jargon, meaning in list(result['jargon_resolved'].items())[:3]:
                print(f"      • {jargon} → {meaning}")

    def generate_csv_report(self, results):
        """Generate CSV report from analysis results"""
        print("\n📊 Generating CSV report...")
        
        # Prepare data for CSV
        csv_data = []
        for result in results:
            csv_data.append({
                'Feature_ID': result['feature_id'],
                'Title': result['title'],
                'Requires_Geo_Compliance': result['requires_geo_compliance'],
                'Risk_Score': result['risk_score'],
                'Reasoning': result['reasoning'],
                'Related_Regulations': '; '.join(result['related_regulations']),
                'Regions_Affected': '; '.join(result['regions_affected']),
                'Evidence': result['evidence'],
                'Jargon_Terms_Resolved': len(result['jargon_resolved']),
                'Analysis_Timestamp': result['timestamp']
            })
        
        # Create DataFrame and save CSV
        df = pd.DataFrame(csv_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"compliance_analysis_demo_{timestamp}.csv"
        
        df.to_csv(filename, index=False)
        print(f"✅ CSV report saved: {filename}")
        
        return filename, df

    def display_summary_statistics(self, results):
        """Display summary statistics from the analysis"""
        print("\n" + "="*80)
        print("📈 COMPLIANCE ANALYSIS SUMMARY")
        print("="*80)
        
        total_features = len(results)
        flagged_features = sum(1 for r in results if r['requires_geo_compliance'])
        flagged_percentage = (flagged_features / total_features) * 100
        
        print(f"📊 Total Features Analyzed: {total_features}")
        print(f"🚨 Features Requiring Geo-Compliance: {flagged_features}")
        print(f"📈 Flagged Percentage: {flagged_percentage:.1f}%")
        
        # Risk distribution
        risk_scores = [r['risk_score'] for r in results]
        avg_risk = sum(risk_scores) / len(risk_scores)
        high_risk = sum(1 for score in risk_scores if score >= 70)
        medium_risk = sum(1 for score in risk_scores if 30 <= score < 70)
        low_risk = sum(1 for score in risk_scores if score < 30)
        
        print(f"\n🎯 Risk Score Analysis:")
        print(f"  📊 Average Risk Score: {avg_risk:.1f}")
        print(f"  🔴 High Risk (70-100): {high_risk} features")
        print(f"  🟡 Medium Risk (30-69): {medium_risk} features") 
        print(f"  🟢 Low Risk (0-29): {low_risk} features")
        
        # Most common regulations
        all_regulations = []
        for r in results:
            all_regulations.extend(r['related_regulations'])
        
        if all_regulations:
            reg_counts = {}
            for reg in all_regulations:
                reg_counts[reg] = reg_counts.get(reg, 0) + 1
            
            print(f"\n📜 Most Triggered Regulations:")
            for reg, count in sorted(reg_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  • {reg}: {count} features")
        
        # Most affected regions
        all_regions = []
        for r in results:
            all_regions.extend(r['regions_affected'])
        
        if all_regions:
            region_counts = {}
            for region in all_regions:
                region_counts[region] = region_counts.get(region, 0) + 1
            
            print(f"\n🌍 Most Affected Regions:")
            for region, count in sorted(region_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  • {region}: {count} features")

    def run_demo(self):
        """Run the complete demo"""
        print("🎯 STARTING GEO-REGULATION COMPLIANCE DEMO")
        print("="*60)
        
        try:
            # Load sample features
            features = self.load_sample_features()
            print(f"📁 Loaded {len(features)} sample features")
            
            # Run analysis
            results = self.run_analysis(features)
            
            # Generate CSV report
            csv_filename, df = self.generate_csv_report(results)
            
            # Display summary
            self.display_summary_statistics(results)
            
            print(f"\n🎉 Demo completed successfully!")
            print(f"📄 Results saved to: {csv_filename}")
            print(f"🚀 Ready for hackathon presentation!")
            
            return results, csv_filename
            
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None

def main():
    """Main entry point"""
    print("🚀 Geo-Regulation Compliance System Demo")
    print("From Guesswork to Governance: Automating Geo-Regulation with LLMs")
    print("="*80)
    
    # Check environment
    if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'dummy-key':
        print("🔑 OpenAI API key detected - using full LLM analysis")
    else:
        print("🔄 No OpenAI API key - using fallback analysis mode")
    
    print()
    
    # Initialize and run demo
    demo = ComplianceDemo()
    results, csv_file = demo.run_demo()
    
    if results:
        print(f"\n📊 Analysis complete! Check {csv_file} for detailed results.")
        print("🔗 Start the FastAPI server (python main.py) and React frontend (npm start) for the dashboard view.")
    
if __name__ == "__main__":
    main()