import { useState, useRef } from 'react';
import Card from '../components/common/Card';
import { Upload, Play, Download, FileText, Video, BarChart3, Activity, AlertCircle, CheckCircle, Loader } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const VideoAnalysisTool = () => {
  const [frontVideo, setFrontVideo] = useState(null);
  const [sideVideo, setSideVideo] = useState(null);
  const [athleteHeight, setAthleteHeight] = useState('');
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, processing, completed, error
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analysisData, setAnalysisData] = useState(null);
  const [summaryReport, setSummaryReport] = useState(null);
  const [movementData, setMovementData] = useState(null);
  const [analyticsData, setAnalyticsData] = useState(null);
  const [visualizations, setVisualizations] = useState(null);
  const frontInputRef = useRef(null);
  const sideInputRef = useRef(null);

  const handleFileSelect = (event, videoType) => {
    const file = event.target.files[0];
    if (file) {
      // Check file type
      const validTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska', 'video/webm'];
      if (!validTypes.includes(file.type)) {
        setError('Invalid file type. Please upload MP4, AVI, MOV, MKV, or WEBM files.');
        return;
      }

      // Check file size (500MB max)
      if (file.size > 500 * 1024 * 1024) {
        setError('File too large. Maximum size is 500MB.');
        return;
      }

      if (videoType === 'front') {
        setFrontVideo(file);
      } else {
        setSideVideo(file);
      }
      
      setError(null);
      setJobId(null);
      setResults(null);
    }
  };

  const processJob = async (uploadedJobId) => {
    try {
      setStatus('processing');
      setError(null);

      const response = await fetch(`${API_BASE_URL}/api/process/${uploadedJobId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ trigger: 'auto' })
      });

      const data = await response.json();

      if (response.ok) {
        setStatus('completed');
        fetchResults(uploadedJobId);
      } else {
        setError(data.error || 'Processing failed');
        setStatus('error');
      }

    } catch (err) {
      setError(err.message);
      setStatus('error');
    }
  };

  const handleUpload = async () => {
    if (!frontVideo) {
      setError('Please upload at least the front view video');
      return;
    }

    if (!athleteHeight || parseFloat(athleteHeight) <= 0) {
      setError('Please enter a valid athlete height in cm');
      return;
    }

    try {
      setStatus('uploading');
      setError(null);
      setUploadProgress(0);

      const formData = new FormData();
      formData.append('front_video', frontVideo);
      if (sideVideo) {
        formData.append('side_video', sideVideo);
      }
      formData.append('athlete_height', athleteHeight);

      const xhr = new XMLHttpRequest();

      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = Math.round((e.loaded / e.total) * 100);
          setUploadProgress(progress);
        }
      });

      // Handle response
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          setJobId(response.job_id);
          setUploadProgress(100);
          processJob(response.job_id);
        } else {
          const error = JSON.parse(xhr.responseText);
          setError(error.error || 'Upload failed');
          setStatus('error');
        }
      });

      xhr.addEventListener('error', () => {
        setError('Network error during upload');
        setStatus('error');
      });

      xhr.open('POST', `${API_BASE_URL}/api/upload`);
      xhr.send(formData);

    } catch (err) {
      setError(err.message);
      setStatus('error');
    }
  };

  const fetchResults = async (targetJobId = jobId) => {
    if (!targetJobId) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/results/${targetJobId}`);
      const data = await response.json();

      if (response.ok) {
        setResults(data.files);
        
        // Fetch additional analysis data
        await fetchAnalysisData(data.files, targetJobId);
      } else {
        setError(data.error || 'Failed to fetch results');
      }

    } catch (err) {
      setError(err.message);
    }
  };

  const fetchAnalysisData = async (files, targetJobId = jobId) => {
    if (!files || files.length === 0) return;

    try {
      // Find summary report and movement data files
      const summaryFile = files.find(f => f.filename.includes('summary_report'));
      const movementFile = files.find(f => f.filename.includes('joint_movements'));

      // Fetch summary report
      if (summaryFile) {
        const summaryResponse = await fetch(
          `${API_BASE_URL}/api/download/${targetJobId}/${summaryFile.filename}`
        );
        const summaryText = await summaryResponse.text();
        setSummaryReport(parseSummaryReport(summaryText));
      }

      // Fetch movement data CSV
      if (movementFile) {
        const movementResponse = await fetch(
          `${API_BASE_URL}/api/download/${targetJobId}/${movementFile.filename}`
        );
        const csvText = await movementResponse.text();
        setMovementData(parseCSV(csvText));
      }

      // Fetch analytics JSON with visualization info
      try {
        const analyticsResponse = await fetch(`${API_BASE_URL}/api/analytics/${targetJobId}`);
        const analyticsData = await analyticsResponse.json();
        if (analyticsResponse.ok && analyticsData.success) {
          setAnalyticsData(analyticsData.analytics);
          
          // Extract visualization files
          const vizFiles = files.filter(f => 
            f.filename.includes('joint_angles_view') || 
            f.filename.includes('range_of_motion') ||
            f.filename.includes('movement_reversals') ||
            f.filename.includes('gait_analysis') ||
            f.filename.includes('stride_analysis')
          );
          setVisualizations(vizFiles);
        }
      } catch (vizErr) {
        console.error('Error fetching analytics:', vizErr);
      }

    } catch (err) {
      console.error('Error fetching analysis data:', err);
    }
  };

  const parseSummaryReport = (text) => {
    const sections = {};
    const lines = text.split('\n');
    let currentSection = null;
    let sectionContent = [];

    for (const line of lines) {
      if (line.includes('=======')) {
        if (currentSection && sectionContent.length > 0) {
          sections[currentSection] = sectionContent.join('\n');
          sectionContent = [];
        }
        continue;
      }

      if (line.trim() && !line.startsWith('===')) {
        if (line.match(/^[A-Z][A-Z\s\-()]+$/)) {
          // This is a section title
          if (currentSection && sectionContent.length > 0) {
            sections[currentSection] = sectionContent.join('\n');
            sectionContent = [];
          }
          currentSection = line.trim();
        } else if (currentSection) {
          sectionContent.push(line);
        }
      }
    }

    if (currentSection && sectionContent.length > 0) {
      sections[currentSection] = sectionContent.join('\n');
    }

    return sections;
  };

  const parseCSV = (text) => {
    const lines = text.trim().split('\n');
    if (lines.length < 2) return [];

    const headers = lines[0].split(',').map(h => h.trim());
    const data = [];

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      const row = {};
      headers.forEach((header, index) => {
        row[header] = values[index];
      });
      data.push(row);
    }

    return data;
  };

  const handleDownload = (filename) => {
    window.open(`${API_BASE_URL}/api/download/${jobId}/${filename}`, '_blank');
  };

  const handleReset = () => {
    setFrontVideo(null);
    setSideVideo(null);
    setAthleteHeight('');
    setJobId(null);
    setStatus('idle');
    setError(null);
    setResults(null);
    setUploadProgress(0);
    setAnalysisData(null);
    setSummaryReport(null);
    setMovementData(null);
    setAnalyticsData(null);
    setVisualizations(null);
    if (frontInputRef.current) {
      frontInputRef.current.value = '';
    }
    if (sideInputRef.current) {
      sideInputRef.current.value = '';
    }
  };

  const getFileIcon = (filename) => {
    if (filename.endsWith('.mp4')) return <Video className="w-5 h-5 text-blue-500" />;
    if (filename.endsWith('.csv')) return <BarChart3 className="w-5 h-5 text-green-500" />;
    if (filename.endsWith('.txt')) return <FileText className="w-5 h-5 text-gray-500" />;
    if (filename.endsWith('.png')) return <Activity className="w-5 h-5 text-purple-500" />;
    return <FileText className="w-5 h-5 text-gray-500" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Video Movement Analysis Tool
        </h1>
        <p className="text-gray-600">
          Upload a video to analyze human movement patterns, joint angles, and biomechanics
        </p>
      </div>

      {/* Upload Section */}
      <Card>
        <div className="p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Upload Videos & Athlete Info
          </h2>

          <div className="space-y-4">
            {/* Athlete Height Input */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Athlete Height (cm) *
              </label>
              <input
                type="number"
                value={athleteHeight}
                onChange={(e) => setAthleteHeight(e.target.value)}
                placeholder="e.g., 175"
                min="100"
                max="250"
                step="0.1"
                disabled={status === 'processing' || status === 'uploading'}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-600 mt-1">
                Enter the athlete's height in centimeters for accurate distance calculations
              </p>
            </div>

            {/* Front Video Upload */}
            <div className="border-2 border-dashed border-blue-300 rounded-lg p-6 bg-blue-50">
              <input
                ref={frontInputRef}
                type="file"
                accept="video/mp4,video/avi,video/quicktime,video/x-matroska,video/webm"
                onChange={(e) => handleFileSelect(e, 'front')}
                className="hidden"
                id="front-video-upload"
                disabled={status === 'processing' || status === 'uploading'}
              />
              <label
                htmlFor="front-video-upload"
                className="cursor-pointer flex flex-col items-center gap-2"
              >
                <Video className="w-10 h-10 text-blue-500" />
                <span className="text-lg font-medium text-gray-700">
                  Front View Video * {frontVideo && '✓'}
                </span>
                {frontVideo ? (
                  <>
                    <span className="text-sm text-blue-600 font-medium">{frontVideo.name}</span>
                    <span className="text-xs text-gray-600">Size: {formatFileSize(frontVideo.size)}</span>
                  </>
                ) : (
                  <span className="text-sm text-gray-500">Click to select front view video</span>
                )}
              </label>
            </div>

            {/* Side Video Upload */}
            <div className="border-2 border-dashed border-purple-300 rounded-lg p-6 bg-purple-50">
              <input
                ref={sideInputRef}
                type="file"
                accept="video/mp4,video/avi,video/quicktime,video/x-matroska,video/webm"
                onChange={(e) => handleFileSelect(e, 'side')}
                className="hidden"
                id="side-video-upload"
                disabled={status === 'processing' || status === 'uploading'}
              />
              <label
                htmlFor="side-video-upload"
                className="cursor-pointer flex flex-col items-center gap-2"
              >
                <Video className="w-10 h-10 text-purple-500" />
                <span className="text-lg font-medium text-gray-700">
                  Side View Video (Optional) {sideVideo && '✓'}
                </span>
                {sideVideo ? (
                  <>
                    <span className="text-sm text-purple-600 font-medium">{sideVideo.name}</span>
                    <span className="text-xs text-gray-600">Size: {formatFileSize(sideVideo.size)}</span>
                  </>
                ) : (
                  <span className="text-sm text-gray-500">Click to select side view video</span>
                )}
              </label>
            </div>

            <div className="text-xs text-gray-600 bg-gray-50 p-3 rounded">
              <p>📹 <strong>Front View:</strong> Camera facing the athlete's front</p>
              <p>📹 <strong>Side View:</strong> Camera perpendicular to athlete's movement (optional but recommended for better 3D analysis)</p>
              <p>⚠️ Max file size: 500MB per video | Supported: MP4, AVI, MOV, MKV, WEBM</p>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              {status === 'idle' && frontVideo && athleteHeight && (
                <button
                  onClick={handleUpload}
                  className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Play className="w-5 h-5" />
                  Analyze {sideVideo ? '2 Videos' : 'Video'}
                </button>
              )}

              {(status === 'completed' || status === 'error') && (
                <button
                  onClick={handleReset}
                  className="flex-1 bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors"
                >
                  Analyze Another Athlete
                </button>
              )}
            </div>

            {/* Progress */}
            {status === 'uploading' && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Uploading...</span>
                  <span className="font-medium text-blue-600">{uploadProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}

            {status === 'processing' && (
              <div className="flex items-center justify-center gap-3 py-4">
                <Loader className="w-6 h-6 animate-spin text-blue-600" />
                <span className="text-lg text-gray-700">
                  Processing video... This may take a few minutes.
                </span>
              </div>
            )}

            {/* Status Messages */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-red-800">Error</p>
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              </div>
            )}

            {status === 'completed' && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-green-800">Processing Complete!</p>
                  <p className="text-green-700 text-sm">
                    Your video has been analyzed. Download the results below.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Results Section */}
      {status === 'completed' && results && results.length > 0 && (
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Download className="w-5 h-5" />
              Analysis Results
            </h2>

            <div className="space-y-2">
              {results.map((file) => (
                <div
                  key={file.filename}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-3 flex-1">
                    {getFileIcon(file.filename)}
                    <div>
                      <p className="font-medium text-gray-800">{file.filename}</p>
                      <p className="text-sm text-gray-500">{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDownload(file.filename)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">Understanding Your Results:</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• <strong>annotated_video_*.mp4</strong> - Video with pose skeleton overlay</li>
                <li>• <strong>frame_data_*.csv</strong> - Complete movement data for every frame</li>
                <li>• <strong>joint_angles_minmax_*.csv</strong> - Min/Max angles for all joints</li>
                <li>• <strong>joint_movements_*.csv</strong> - Movement distances in cm and velocity</li>
                <li>• <strong className="text-purple-700">phase_analysis_*.csv</strong> - 🔥 Landing, Mid-Stance, Push-Off angles & velocities</li>
                <li>• <strong className="text-purple-700">phase_analysis_*.json</strong> - 🔥 Structured phase data with cycle breakdown</li>
                <li>• <strong>summary_report_*.txt</strong> - Human-readable analysis with phase details</li>
                <li>• <strong>analytics_*.json</strong> - Structured data for API access and custom analysis</li>
                <li>• <strong>joint_angles_view_*.png</strong> - Visual joint angle diagrams (anterior/posterior views)</li>
                <li>• <strong>range_of_motion_*.png</strong> - Bar chart comparing joint flexibility</li>
                <li>• <strong>movement_reversals_*.png</strong> - Detection of sudden direction changes</li>
                <li>• <strong>gait_analysis_*.png</strong> - Running biomechanics and coordination patterns</li>
                <li>• <strong>stride_analysis_*.png</strong> - Foot strike patterns and stride metrics</li>
                <li>• <strong className="text-purple-700">phase_timeline_*.png</strong> - 🔥 Visual timeline of Landing, Mid-Stance, Push-Off</li>
                <li>• <strong className="text-purple-700">phase_angles_*.png</strong> - 🔥 Joint angles across movement cycles</li>
                <li>• <strong className="text-purple-700">phase_avg_angles_*.png</strong> - 🔥 Average angles at each phase</li>
              </ul>
            </div>
          </div>
        </Card>
      )}

      {/* Movement Analysis Display */}
      {status === 'completed' && movementData && movementData.length > 0 && (
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Joint Movement Analysis (Real-World Distances)
            </h2>

            <div className="mb-4 space-y-2">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-800">
                  <strong>Reference Scale:</strong> Measurements calibrated using athlete height or torso reference
                </p>
              </div>
              
              {summaryReport && summaryReport['VIDEO SYNCHRONIZATION'] && (
                <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                  <h3 className="text-sm font-semibold text-purple-900 mb-2">📹 Video Synchronization</h3>
                  <div className="text-sm text-purple-800 space-y-1">
                    {summaryReport['VIDEO SYNCHRONIZATION'].split('\n').map((line, i) => (
                      line.trim() && <p key={i}>{line}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="text-left p-3 font-semibold">Joint</th>
                    <th className="text-right p-3 font-semibold">Total Distance</th>
                    <th className="text-right p-3 font-semibold">3D Range</th>
                    <th className="text-right p-3 font-semibold">X-Range</th>
                    <th className="text-right p-3 font-semibold">Y-Range</th>
                    <th className="text-right p-3 font-semibold">Z-Range</th>
                  </tr>
                </thead>
                <tbody>
                  {movementData
                    .sort((a, b) => parseFloat(b.total_distance_cm) - parseFloat(a.total_distance_cm))
                    .map((joint, index) => (
                      <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="p-3 font-medium capitalize">
                          {joint.joint.replace(/_/g, ' ')}
                        </td>
                        <td className="p-3 text-right text-blue-600 font-semibold">
                          {parseFloat(joint.total_distance_cm).toFixed(2)} cm
                        </td>
                        <td className="p-3 text-right">
                          {parseFloat(joint.total_range_cm).toFixed(2)} cm
                        </td>
                        <td className="p-3 text-right text-gray-600">
                          {parseFloat(joint.x_range_cm).toFixed(2)} cm
                        </td>
                        <td className="p-3 text-right text-gray-600">
                          {parseFloat(joint.y_range_cm).toFixed(2)} cm
                        </td>
                        <td className="p-3 text-right text-gray-600">
                          {parseFloat(joint.z_range_cm).toFixed(2)} cm
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>

            <div className="mt-4 grid md:grid-cols-3 gap-4">
              <div className="p-4 bg-green-50 rounded-lg">
                <h4 className="text-sm font-semibold text-green-800 mb-1">Most Active Joint</h4>
                <p className="text-2xl font-bold text-green-600">
                  {movementData[0]?.joint.replace(/_/g, ' ')}
                </p>
                <p className="text-sm text-green-700">
                  {parseFloat(movementData[0]?.total_distance_cm).toFixed(2)} cm traveled
                </p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <h4 className="text-sm font-semibold text-purple-800 mb-1">Largest Range</h4>
                <p className="text-2xl font-bold text-purple-600">
                  {movementData.reduce((max, j) => 
                    parseFloat(j.total_range_cm) > parseFloat(max.total_range_cm) ? j : max
                  )?.joint.replace(/_/g, ' ')}
                </p>
                <p className="text-sm text-purple-700">
                  {parseFloat(movementData.reduce((max, j) => 
                    parseFloat(j.total_range_cm) > parseFloat(max.total_range_cm) ? j : max
                  )?.total_range_cm).toFixed(2)} cm range
                </p>
              </div>
              <div className="p-4 bg-orange-50 rounded-lg">
                <h4 className="text-sm font-semibold text-orange-800 mb-1">Total Joints</h4>
                <p className="text-2xl font-bold text-orange-600">
                  {movementData.length}
                </p>
                <p className="text-sm text-orange-700">tracked and analyzed</p>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Summary Report Display */}
      {status === 'completed' && summaryReport && (
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Detailed Analysis Summary
            </h2>

            <div className="space-y-6">
              {Object.entries(summaryReport).map(([section, content]) => (
                <div key={section} className="border-l-4 border-blue-500 pl-4">
                  <h3 className="font-semibold text-gray-800 mb-2">{section}</h3>
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono bg-gray-50 p-3 rounded">
                    {content}
                  </pre>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Visualization Display */}
      {status === 'completed' && visualizations && visualizations.length > 0 && (
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Graphical Analysis & Visualizations
            </h2>
            
            <div className="grid gap-6">
              {visualizations.map((viz, index) => (
                <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-3 border-b border-gray-200">
                    <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                      {getFileIcon(viz.filename)}
                      {viz.filename.includes('joint_angles') && '📊 Joint Angle Analysis - Multiple Views'}
                      {viz.filename.includes('range_of_motion') && '📏 Range of Motion Comparison'}
                      {viz.filename.includes('movement_reversals') && '🔄 Movement Reversal Points'}
                      {viz.filename.includes('gait_analysis') && '🏃 Gait Analysis - Running Biomechanics'}
                      {viz.filename.includes('stride_analysis') && '👣 Stride & Foot Strike Analysis'}
                      {viz.filename.includes('phase_timeline') && '⏱️ Movement Phase Timeline - Landing/Mid-Stance/Push-Off'}
                      {viz.filename.includes('phase_angles') && '📈 Phase-Specific Joint Angles Across Cycles'}
                      {viz.filename.includes('phase_avg_angles') && '📊 Average Angles by Movement Phase'}
                    </h3>
                    <p className="text-xs text-gray-600 mt-1">{viz.filename}</p>
                  </div>
                  <div className="p-4 bg-white">
                    <img 
                      src={`${API_BASE_URL}/api/download/${jobId}/${viz.filename}`}
                      alt={viz.filename}
                      className="w-full h-auto rounded shadow-lg"
                      loading="lazy"
                    />
                    <button
                      onClick={() => handleDownload(viz.filename)}
                      className="mt-3 w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                    >
                      <Download className="w-4 h-4" />
                      Download High-Resolution Image
                    </button>
                  </div>
                </div>
              ))}
            </div>
            
            {analyticsData && analyticsData.movement_reversals && (
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h3 className="font-semibold text-yellow-900 mb-3">Movement Reversal Summary</h3>
                <div className="grid md:grid-cols-3 gap-3 text-sm">
                  {Object.entries(analyticsData.movement_reversals).map(([joint, data]) => (
                    <div key={joint} className="bg-white p-3 rounded">
                      <p className="font-medium text-gray-800 capitalize">{joint.replace(/_/g, ' ')}</p>
                      <p className="text-2xl font-bold text-yellow-600">{data.count}</p>
                      <p className="text-xs text-gray-600">direction changes</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Info Section */}
      <Card>
        <div className="p-6 bg-gradient-to-r from-blue-50 to-purple-50">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">
            What This Tool Analyzes:
          </h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm text-gray-700">
            <div>
              <h4 className="font-semibold mb-2">Body Landmarks:</h4>
              <ul className="space-y-1">
                <li>✓ Shoulders, Elbows, Wrists</li>
                <li>✓ Hips, Knees, Ankles</li>
                <li>✓ Head and Neck Position</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Movement Metrics:</h4>
              <ul className="space-y-1">
                <li>✓ Joint Angles (14 different angles)</li>
                <li>✓ Range of Motion</li>
                <li>✓ Real-world distances (cm/mm)</li>
                <li className="text-purple-700 font-semibold">✓ Phase Analysis: Landing, Mid-Stance, Push-Off</li>
                <li className="text-purple-700 font-semibold">✓ Cycle-by-Cycle Breakdown</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Visual Analytics:</h4>
              <ul className="space-y-1">
                <li>✓ Joint angle diagrams (4 views)</li>
                <li>✓ Range of motion charts</li>
                <li>✓ Movement reversal detection</li>
                <li>✓ Gait cycle analysis</li>
                <li>✓ Stride & foot strike patterns</li>
                <li>✓ Hip-knee coordination</li>
                <li className="text-purple-700 font-semibold">✓ Phase timeline visualization</li>
                <li className="text-purple-700 font-semibold">✓ Phase-specific joint anglesection</li>
                <li>✓ Gait cycle analysis</li>
                <li>✓ Stride & foot strike patterns</li>
                <li>✓ Hip-knee coordination</li>
              </ul>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default VideoAnalysisTool;
