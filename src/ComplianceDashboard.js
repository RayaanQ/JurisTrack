import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Upload, AlertTriangle, CheckCircle, FileText, Download, Search } from 'lucide-react';

const ComplianceDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analysisMode, setAnalysisMode] = useState('dashboard');
  const [singleFeature, setSingleFeature] = useState({
    title: '',
    description: '',
    prd: '',
    trd: ''
  });
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await fetch('/dashboard-data');
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else {
        // Fallback to mock data if backend is not available
        const mockData = {
          total_features: 12,
          flagged_count: 4,
          flagged_percentage: 33.3,
          risk_distribution: { 'Low': 8, 'Medium': 3, 'High': 1 },
          region_distribution: {
            'European Union': 2,
            'California, US': 2,
            'Utah, US': 1,
            'United States': 2,
            'United Kingdom': 1
          },
          recent_analyses: [
            {
              feature_title: 'Curfew Mode for Teen Users',
              requires_geo_compliance: true,
              risk_score: 85,
              reasoning: 'Age-based restrictions trigger Utah Social Media Act compliance',
              regions_affected: ['Utah, US', 'United States'], // Already an array
              timestamp: '2024-08-27T10:30:00'
            },
            {
              feature_title: 'Enhanced Content Personalization',
              requires_geo_compliance: true,
              risk_score: 65,
              reasoning: 'Data profiling requirements under GDPR and CCPA',
              regions_affected: ['European Union', 'California, US'], // Already an array
              timestamp: '2024-08-27T09:15:00'
            },
            {
              feature_title: 'Basic Video Upload',
              requires_geo_compliance: false,
              risk_score: 15,
              reasoning: 'Standard upload functionality with no geo-specific requirements',
              regions_affected: [], // Already an array
              timestamp: '2024-08-27T08:45:00'
            }
          ]
        };
        setDashboardData(mockData);
        setError('Using demo data - backend not connected');
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to connect to backend');
      setLoading(false);
    }
  };

  const analyzeSingleFeature = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/analyze-feature', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(singleFeature)
      });
      
      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result);
      } else {
        // Fallback analysis for demo
        const mockResult = {
          feature_id: 'feat_' + Math.random().toString(36).substr(2, 9),
          title: singleFeature.title,
          requires_geo_compliance: singleFeature.title.toLowerCase().includes('minor') || 
                                  singleFeature.description.toLowerCase().includes('child') ||
                                  singleFeature.description.toLowerCase().includes('curfew'),
          reasoning: singleFeature.title.toLowerCase().includes('minor') || 
                    singleFeature.description.toLowerCase().includes('child') ||
                    singleFeature.description.toLowerCase().includes('curfew')
            ? 'Feature involves minors or age restrictions, triggering child safety regulations in multiple jurisdictions'
            : 'No significant geo-compliance requirements detected based on feature analysis',
          related_regulations: singleFeature.title.toLowerCase().includes('minor') || 
                              singleFeature.description.toLowerCase().includes('child') ||
                              singleFeature.description.toLowerCase().includes('curfew')
            ? ['Utah Social Media Regulation Act', 'COPPA', 'UK Age Appropriate Design Code']
            : [],
          risk_score: singleFeature.title.toLowerCase().includes('minor') || 
                     singleFeature.description.toLowerCase().includes('child') ||
                     singleFeature.description.toLowerCase().includes('curfew') ? 78 : 25,
          regions_affected: singleFeature.title.toLowerCase().includes('minor') || 
                           singleFeature.description.toLowerCase().includes('child') ||
                           singleFeature.description.toLowerCase().includes('curfew')
            ? ['Utah, US', 'United States', 'United Kingdom']
            : [],
          evidence: `Feature analysis based on: ${singleFeature.title.substring(0, 100)}...`,
          jargon_resolved: {},
          timestamp: new Date().toISOString()
        };
        
        setAnalysisResult(mockResult);
        setError('Using demo analysis - backend not connected');
      }
      setLoading(false);
    } catch (err) {
      console.error('Analysis failed:', err);
      setError('Analysis failed - please check backend connection');
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (!dashboardData) return;
    
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Feature ID,Title,Requires Geo-Compliance,Risk Score,Reasoning,Regions Affected,Timestamp\n"
      + dashboardData.recent_analyses.map(item => {
          // Safely handle regions_affected - it should already be an array
          const regions = Array.isArray(item.regions_affected) 
            ? item.regions_affected 
            : [];
          return `"${Math.random().toString(36).substr(2, 9)}","${item.feature_title}","${item.requires_geo_compliance}","${item.risk_score}","${item.reasoning}","${regions.join('; ')}","${item.timestamp}"`;
        }).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `compliance_analysis_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading && !dashboardData) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading Compliance Radar...</div>
      </div>
    );
  }

  const COLORS = ['#EF4444', '#10B981','#F59E0B' ];
  const riskData = dashboardData ? Object.entries(dashboardData.risk_distribution).map(([key, value]) => ({
    name: key,
    value: value
  })) : [];

  const regionData = dashboardData ? Object.entries(dashboardData.region_distribution).map(([key, value]) => ({
    region: key,
    count: value
  })) : [];

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              JurisTrack: Geo-Regulation Compliance Radar
            </h1>
            <p className="text-gray-400 mt-1">Automated feature compliance analysis with LLMs</p>
            {error && (
              <div className="mt-2 px-3 py-1 bg-yellow-900 text-yellow-200 rounded text-sm">
                {error}
              </div>
            )}
          </div>
          
          <div className="flex space-x-4">
            <button
              onClick={() => setAnalysisMode('dashboard')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                analysisMode === 'dashboard' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setAnalysisMode('analyze')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                analysisMode === 'analyze' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Analyze Feature
            </button>
            <button
              onClick={downloadCSV}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors flex items-center space-x-2"
            >
              <Download size={16} />
              <span>Export CSV</span>
            </button>
            </div>
        </div>
      </div>

      {/* Dashboard Mode */}
      {analysisMode === 'dashboard' && dashboardData && (
        <div className="p-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Features</p>
                  <p className="text-3xl font-bold">{dashboardData.total_features}</p>
                </div>
                <FileText className="text-blue-400" size={24} />
              </div>
            </div>
            
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Flagged for Compliance</p>
                  <p className="text-3xl font-bold text-red-400">{dashboardData.flagged_count}</p>
                </div>
                <AlertTriangle className="text-red-400" size={24} />
              </div>
            </div>
            
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Flagged Percentage</p>
                  <p className="text-3xl font-bold text-yellow-400">{dashboardData.flagged_percentage}%</p>
                </div>
                <div className="text-yellow-400 text-2xl font-bold">%</div>
              </div>
            </div>
            
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Compliance Status</p>
                  <p className="text-3xl font-bold text-green-400">Active</p>
                </div>
                <CheckCircle className="text-green-400" size={24} />
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Risk Distribution */}
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
              <h3 className="text-xl font-semibold mb-4">Risk Score Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={riskData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {riskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Region Distribution */}
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
              <h3 className="text-xl font-semibold mb-4">Features by Region</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={regionData} margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    dataKey="region" 
                    tick={{ fill: '#9CA3AF', fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis tick={{ fill: '#9CA3AF' }} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar dataKey="count" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Recent Analysis */}
          <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
            <h3 className="text-xl font-semibold mb-4">Recent Analysis</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="text-left p-3">Feature</th>
                    <th className="text-left p-3">Compliance Required</th>
                    <th className="text-left p-3">Risk Score</th>
                    <th className="text-left p-3">Regions</th>
                    <th className="text-left p-3">Reasoning</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboardData.recent_analyses.map((item, index) => (
                    <tr key={index} className="border-b border-gray-700 hover:bg-gray-700">
                      <td className="p-3 font-medium">{item.feature_title}</td>
                      <td className="p-3">
                        {item.requires_geo_compliance ? (
                          <span className="px-2 py-1 bg-red-900 text-red-200 rounded-full text-xs">
                            Yes
                          </span>
                        ) : (
                          <span className="px-2 py-1 bg-green-900 text-green-200 rounded-full text-xs">
                            No
                          </span>
                        )}
                      </td>
                      <td className="p-3">
                        <div className="flex items-center space-x-2">
                          <div className={`w-3 h-3 rounded-full ${
                            item.risk_score >= 70 ? 'bg-red-400' : 
                            item.risk_score >= 30 ? 'bg-yellow-400' : 'bg-green-400'
                          }`}></div>
                          <span>{item.risk_score}</span>
                        </div>
                      </td>
                      <td className="p-3">
                        {/* Fixed: Handle regions_affected safely */}
                        {Array.isArray(item.regions_affected) && item.regions_affected.length > 0 ? 
                          item.regions_affected.join(', ') : 
                          'None'
                        }
                      </td>
                      <td className="p-3 max-w-xs truncate" title={item.reasoning}>
                        {item.reasoning}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Mode */}
      {analysisMode === 'analyze' && (
        <div className="p-6">
          <div className="max-w-4xl mx-auto">
            <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
              <h3 className="text-xl font-semibold mb-6">Analyze New Feature</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-2">Feature Title</label>
                  <input
                    type="text"
                    value={singleFeature.title}
                    onChange={(e) => setSingleFeature({...singleFeature, title: e.target.value})}
                    placeholder="e.g., Curfew Mode for Minor Users"
                    className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Feature Description</label>
                  <textarea
                    value={singleFeature.description}
                    onChange={(e) => setSingleFeature({...singleFeature, description: e.target.value})}
                    placeholder="Brief description of the feature functionality..."
                    className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent h-24 resize-none text-white"
                  />
                </div>
              </div>
              
              <div className="mt-6">
                <label className="block text-sm font-medium mb-2">PRD Content (Optional)</label>
                <textarea
                  value={singleFeature.prd}
                  onChange={(e) => setSingleFeature({...singleFeature, prd: e.target.value})}
                  placeholder="Product requirements document content..."
                  className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent h-32 resize-none text-white"
                />
              </div>
              
              <div className="mt-6">
                <label className="block text-sm font-medium mb-2">TRD Content (Optional)</label>
                <textarea
                  value={singleFeature.trd}
                  onChange={(e) => setSingleFeature({...singleFeature, trd: e.target.value})}
                  placeholder="Technical requirements document content..."
                  className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent h-32 resize-none text-white"
                />
              </div>
              
              <button
                onClick={analyzeSingleFeature}
                disabled={!singleFeature.title || !singleFeature.description || loading}
                className="mt-6 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-colors flex items-center space-x-2"
              >
                <Search size={16} />
                <span>{loading ? 'Analyzing...' : 'Analyze Feature'}</span>
              </button>
            </div>

            {/* Analysis Results */}
            {analysisResult && (
              <div className="mt-8 bg-gray-800 p-6 rounded-xl border border-gray-700">
                <h3 className="text-xl font-semibold mb-6">Analysis Results</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-400 mb-2">Compliance Required</label>
                      <span className={`px-4 py-2 rounded-lg text-sm font-medium ${
                        analysisResult.requires_geo_compliance 
                          ? 'bg-red-900 text-red-200' 
                          : 'bg-green-900 text-green-200'
                      }`}>
                        {analysisResult.requires_geo_compliance ? 'YES' : 'NO'}
                      </span>
                    </div>
                    
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-400 mb-2">Risk Score</label>
                      <div className="flex items-center space-x-3">
                        <div className="flex-1 bg-gray-700 rounded-full h-3">
                          <div 
                            className={`h-3 rounded-full ${
                              analysisResult.risk_score >= 70 ? 'bg-red-400' : 
                              analysisResult.risk_score >= 30 ? 'bg-yellow-400' : 'bg-green-400'
                            }`}
                            style={{width: `${analysisResult.risk_score}%`}}
                          ></div>
                        </div>
                        <span className="text-lg font-bold">{analysisResult.risk_score}</span>
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-400 mb-2">Affected Regions</label>
                      <div className="flex flex-wrap gap-2">
                        {analysisResult.regions_affected && analysisResult.regions_affected.length > 0 ? (
                          analysisResult.regions_affected.map((region, index) => (
                            <span key={index} className="px-3 py-1 bg-purple-900 text-purple-200 rounded-full text-sm">
                              {region}
                            </span>
                          ))
                        ) : (
                          <span className="text-gray-500 italic">None</span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-400 mb-2">Related Regulations</label>
                      <div className="space-y-2">
                        {analysisResult.related_regulations && analysisResult.related_regulations.length > 0 ? (
                          analysisResult.related_regulations.map((reg, index) => (
                            <div key={index} className="p-3 bg-gray-700 rounded-lg text-sm">
                              {reg}
                            </div>
                          ))
                        ) : (
                          <span className="text-gray-500 italic">None identified</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-400 mb-2">Reasoning</label>
                  <div className="p-4 bg-gray-700 rounded-lg text-sm leading-relaxed">
                    {analysisResult.reasoning}
                  </div>
                </div>
                
                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-400 mb-2">Evidence</label>
                  <div className="p-4 bg-gray-700 rounded-lg text-sm leading-relaxed">
                    {analysisResult.evidence}
                  </div>
                </div>
                
                <div className="mt-6 flex space-x-4">
                  <button
                    onClick={() => {
                      const csvContent = "data:text/csv;charset=utf-8," 
                        + "Feature ID,Title,Requires Geo-Compliance,Risk Score,Reasoning,Regions Affected,Related Regulations,Timestamp\n"
                        + `"${analysisResult.feature_id}","${analysisResult.title}","${analysisResult.requires_geo_compliance}","${analysisResult.risk_score}","${analysisResult.reasoning}","${analysisResult.regions_affected ? analysisResult.regions_affected.join('; ') : ''}","${analysisResult.related_regulations ? analysisResult.related_regulations.join('; ') : ''}","${analysisResult.timestamp}"`;

                      const encodedUri = encodeURI(csvContent);
                      const link = document.createElement("a");
                      link.setAttribute("href", encodedUri);
                      link.setAttribute("download", `feature_analysis_${analysisResult.feature_id}.csv`);
                      document.body.appendChild(link);
                      link.click();
                      document.body.removeChild(link);
                    }}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors flex items-center space-x-2"
                  >
                    <Download size={16} />
                    <span>Export Result</span>
                  </button>
                  
                  <button
                    onClick={() => {
                      setSingleFeature({ title: '', description: '', prd: '', trd: '' });
                      setAnalysisResult(null);
                    }}
                    className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    Reset
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="bg-gray-800 border-t border-gray-700 px-6 py-4 mt-8">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div>
            Geo-Regulation Compliance System | Built with React + FastAPI + OpenAI
          </div>
          <div>
            Hackathon - From Guesswork to Governance
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComplianceDashboard;