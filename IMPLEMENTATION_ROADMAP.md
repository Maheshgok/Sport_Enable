# Implementation Roadmap
## Sport-Specific Analysis + Login Integration

This document outlines the practical steps to implement the sport-specific analysis system integrated with the login features.

---

## Phase 1: Database Setup (Week 1)

### 1.1 Run Sport Schema Migration

```bash
cd database
psql -U postgres -d moove_db -f schema/06_sport_analysis.sql
```

This creates:
- `sports` table
- `sport_video_types` table
- `sport_baselines` table
- `video_analyses` table
- `analysis_metrics` table
- Helper views and functions

### 1.2 Seed Sport Configuration

Create a seed script to populate sports from `sports_config.py`:

```bash
python seed_sports_config.py
```

### 1.3 Update Athlete Profiles

Athletes need to select their sport during registration or profile update.

---

## Phase 2: Backend API Updates (Week 1-2)

### 2.1 Add Sport Selection to Registration

Update `POST /api/auth/register` to include sport selection for athletes:

```python
# In api/app.py
if 'athlete' in roles:
    sport_id = data.get('sport_id')
    position = data.get('position')
    
    # Create athlete profile with sport
    execute_query("""
        INSERT INTO physio_app.athlete_profiles 
        (user_id, sport_id, position_in_sport, sport, position)
        VALUES (%s, %s, %s, ...)
    """, (...))
```

### 2.2 Create Video Analysis Endpoints

Add new endpoints in `api/app.py`:

```python
@app.route('/api/sports', methods=['GET'])
def list_sports():
    """Get all available sports"""
    from sports_config import get_all_sports
    return jsonify(get_all_sports())

@app.route('/api/sports/<sport_id>/video-types', methods=['GET'])
def get_video_types(sport_id):
    """Get video types for a sport"""
    from sports_config import get_video_types_for_sport
    return jsonify(get_video_types_for_sport(sport_id))

@app.route('/api/analysis/upload', methods=['POST'])
@require_auth()
def upload_analysis_video():
    """Upload video for sport-specific analysis"""
    # Implementation below

@app.route('/api/analysis/<analysis_id>', methods=['GET'])
@require_auth()
def get_analysis(analysis_id):
    """Get analysis results"""
    # Implementation below

@app.route('/api/analysis/<analysis_id>/pdf', methods=['GET'])
@require_auth()
def download_report_pdf(analysis_id):
    """Download PDF report"""
    # Implementation below
```

### 2.3 Implement Video Upload + Analysis Trigger

```python
@app.route('/api/analysis/upload', methods=['POST'])
@require_auth(roles=['athlete', 'physiotherapist', 'coach'])
def upload_analysis_video():
    current_user = request.current_user
    
    # Get form data
    athlete_id = request.form.get('athlete_id')
    video_type_code = request.form.get('video_type')
    
    # Get athlete's sport
    athlete = execute_query("""
        SELECT a.*, u.first_name, u.last_name, a.sport_id, a.position_in_sport
        FROM physio_app.athlete_profiles a
        JOIN physio_app.users u ON a.user_id = u.user_id
        WHERE a.athlete_id = %s
    """, (athlete_id,), fetch_one=True)
    
    if not athlete:
        return jsonify({'error': 'Athlete not found'}), 404
    
    # Get sport config
    from sports_config import get_sport_config
    sport_config = get_sport_config(athlete['sport_id'])
    
    # Validate video type
    if not validate_video_type(athlete['sport_id'], video_type_code):
        return jsonify({'error': 'Invalid video type for this sport'}), 400
    
    # Upload videos to GCS
    video_urls = {}
    for view in ['front', 'side', 'top']:
        if f'{view}_video' in request.files:
            file = request.files[f'{view}_video']
            # Upload to GCS
            video_url = upload_to_gcs(file, athlete_id, video_type_code, view)
            video_urls[view] = video_url
    
    # Create analysis record
    analysis_id = str(uuid.uuid4())
    execute_query("""
        INSERT INTO physio_app.video_analyses 
        (analysis_id, athlete_id, uploaded_by, sport_id, video_type_code,
         video_urls, status, athlete_height_cm, athlete_weight_kg)
        VALUES (%s, %s, %s, %s, %s, %s, 'pending', %s, %s)
    """, (analysis_id, athlete_id, current_user['user_id'], 
          athlete['sport_id'], video_type_code, json.dumps(video_urls),
          request.form.get('athlete_height_cm'),
          request.form.get('athlete_weight_kg')))
    
    # Trigger Cloud Run function (async)
    trigger_sport_analysis(
        analysis_id=analysis_id,
        sport_config=sport_config,
        video_urls=video_urls,
        athlete_data=athlete
    )
    
    return jsonify({
        'success': True,
        'analysis_id': analysis_id,
        'status': 'processing'
    }), 202
```

---

## Phase 3: Cloud Run Functions (Week 2-3)

### 3.1 Setup Cloud Run Project Structure

```bash
mkdir -p cloud-functions/football-analysis
mkdir -p cloud-functions/basketball-analysis
mkdir -p cloud-functions/running-analysis
```

### 3.2 Create Football Analysis Function

```
cloud-functions/football-analysis/
├── main.py              # Cloud Run entry point
├── Dockerfile
├── requirements.txt
└── .env.example
```

**main.py:**

```python
from flask import Flask, request, jsonify
import os
import sys

# Add parent to path for shared modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from football_analyzer import FootballAnalyzer
from report_generator import ReportGenerator
from sports_config import SPORTS_CONFIG

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze football video"""
    data = request.get_json()
    
    analysis_id = data['analysis_id']
    video_urls = data['video_urls']
    athlete_data = data['athlete_data']
    video_type = data['video_type']
    
    # Initialize analyzer
    sport_config = SPORTS_CONFIG['football']
    analyzer = FootballAnalyzer(sport_config)
    
    # Process video
    try:
        results = analyzer.process_video(
            video_urls.get('front') or video_urls.get('side'),
            video_type,
            athlete_data
        )
        
        # Generate PDF report
        report_gen = ReportGenerator()
        pdf_bytes = report_gen.generate_pdf(results, athlete_data)
        pdf_url = report_gen.upload_to_gcs(pdf_bytes, analysis_id)
        
        # Return results
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'results': results,
            'report_pdf_url': pdf_url
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
COPY ../base_analyzer.py .
COPY ../football_analyzer.py .
COPY ../report_generator.py .
COPY ../sports_config.py .

# Download MediaPipe model
RUN wget https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task

EXPOSE 8080

CMD ["python", "main.py"]
```

**requirements.txt:**

```
Flask==3.0.0
opencv-python-headless==4.8.0.76
mediapipe==0.10.8
numpy==1.24.3
scipy==1.11.0
matplotlib==3.7.1
seaborn==0.12.2
markdown==3.4.4
pdfkit==1.0.0
jinja2==3.1.2
google-cloud-storage==2.14.0
```

### 3.3 Deploy to Cloud Run

```bash
cd cloud-functions/football-analysis

# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT/football-analysis

# Deploy
gcloud run deploy football-analysis \
    --image gcr.io/YOUR_PROJECT/football-analysis \
    --platform managed \
    --region asia-south1 \
    --memory 2Gi \
    --timeout 900 \
    --max-instances 10
```

### 3.4 Repeat for Other Sports

- Basketball: Copy structure, use `BasketballAnalyzer`
- Running: Copy structure, use `RunningAnalyzer`
- Cricket: Copy structure, use `CricketAnalyzer`

---

## Phase 4: Frontend Integration (Week 3-4)

### 4.1 Add Sport Selection to Registration

```jsx
// src/components/auth/Login.jsx
const [formData, setFormData] = useState({
  // ... existing fields
  sport_id: 'football',
  position: ''
});

// Add sport selection to form
{!isLogin && formData.roles.includes('athlete') && (
  <>
    <select name="sport_id" value={formData.sport_id} onChange={handleChange}>
      <option value="football">Football/Soccer</option>
      <option value="basketball">Basketball</option>
      <option value="running">Running/Athletics</option>
      <option value="cricket">Cricket</option>
    </select>
    
    <input
      name="position"
      type="text"
      placeholder="Position (e.g., Forward, Midfielder)"
      value={formData.position}
      onChange={handleChange}
    />
  </>
)}
```

### 4.2 Create Video Upload Component

```jsx
// src/components/VideoAnalysisUpload.jsx
import { useState, useEffect } from 'react';
import { authFetch } from './auth/Login';

export default function VideoAnalysisUpload({ athleteId }) {
  const [sports, setSports] = useState([]);
  const [videoTypes, setVideoTypes] = useState([]);
  const [selectedSport, setSelectedSport] = useState('');
  const [selectedVideoType, setSelectedVideoType] = useState('');
  const [frontVideo, setFrontVideo] = useState(null);
  const [sideVideo, setSideVideo] = useState(null);
  const [uploading, setUploading] = useState(false);
  
  useEffect(() => {
    loadSports();
  }, []);
  
  const loadSports = async () => {
    const response = await authFetch('/api/sports');
    const data = await response.json();
    setSports(Object.values(data));
  };
  
  const handleSportChange = async (sportId) => {
    setSelectedSport(sportId);
    const response = await authFetch(`/api/sports/${sportId}/video-types`);
    const data = await response.json();
    setVideoTypes(data);
  };
  
  const handleUpload = async (e) => {
    e.preventDefault();
    setUploading(true);
    
    const formData = new FormData();
    formData.append('athlete_id', athleteId);
    formData.append('video_type', selectedVideoType);
    if (frontVideo) formData.append('front_video', frontVideo);
    if (sideVideo) formData.append('side_video', sideVideo);
    formData.append('athlete_height_cm', 175); // Get from profile
    
    try {
      const response = await authFetch('/api/analysis/upload', {
        method: 'POST',
        body: formData,
        headers: {} // Let browser set Content-Type for FormData
      });
      
      const data = await response.json();
      
      if (data.success) {
        alert(`Analysis started! ID: ${data.analysis_id}`);
        // Redirect to results page or show processing status
      } else {
        alert('Upload failed');
      }
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setUploading(false);
    }
  };
  
  return (
    <div className="video-upload-form">
      <h2>Upload Video for Analysis</h2>
      
      <form onSubmit={handleUpload}>
        <select value={selectedSport} onChange={(e) => handleSportChange(e.target.value)}>
          <option value="">Select Sport</option>
          {sports.map(sport => (
            <option key={sport.sport_id} value={sport.sport_id}>
              {sport.name}
            </option>
          ))}
        </select>
        
        {videoTypes.length > 0 && (
          <select value={selectedVideoType} onChange={(e) => setSelectedVideoType(e.target.value)}>
            <option value="">Select Video Type</option>
            {videoTypes.map(vt => (
              <option key={vt.id} value={vt.id}>
                {vt.name} - {vt.description}
              </option>
            ))}
          </select>
        )}
        
        <div>
          <label>Front View Video:</label>
          <input type="file" accept="video/*" onChange={(e) => setFrontVideo(e.target.files[0])} />
        </div>
        
        <div>
          <label>Side View Video (optional):</label>
          <input type="file" accept="video/*" onChange={(e) => setSideVideo(e.target.files[0])} />
        </div>
        
        <button type="submit" disabled={uploading || !selectedVideoType}>
          {uploading ? 'Uploading...' : 'Upload and Analyze'}
        </button>
      </form>
    </div>
  );
}
```

### 4.3 Create PDF Report Viewer

```jsx
// src/components/AnalysisReports.jsx
export default function AnalysisReports({ athleteId }) {
  const [analyses, setAnalyses] = useState([]);
  
  useEffect(() => {
    loadAnalyses();
  }, [athleteId]);
  
  const loadAnalyses = async () => {
    const response = await authFetch(`/api/athletes/${athleteId}/analyses`);
    const data = await response.json();
    setAnalyses(data.analyses);
  };
  
  const viewReport = (analysisId) => {
    window.open(`/api/analysis/${analysisId}/pdf`, '_blank');
  };
  
  return (
    <div>
      <h2>Analysis Reports</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Sport</th>
            <th>Video Type</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {analyses.map(analysis => (
            <tr key={analysis.analysis_id}>
              <td>{new Date(analysis.created_at).toLocaleDateString()}</td>
              <td>{analysis.sport_name}</td>
              <td>{analysis.video_type_code}</td>
              <td>{analysis.status}</td>
              <td>
                {analysis.status === 'completed' && (
                  <button onClick={() => viewReport(analysis.analysis_id)}>
                    View PDF Report
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## Phase 5: Testing & Deployment (Week 4-5)

### 5.1 Test Complete Flow

1. Register athlete with sport selection
2. Login
3. Upload video for analysis
4. Monitor processing status
5. View PDF report

### 5.2 Monitor Cloud Run Functions

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Monitor metrics
gcloud run services describe football-analysis --region asia-south1
```

### 5.3 Deploy to Production

- Update environment variables
- Configure proper authentication
- Set up monitoring and alerts
- Enable auto-scaling

---

## Quick Start Commands

```bash
# 1. Setup database
cd database
psql -U postgres -d moove_db -f schema/06_sport_analysis.sql

# 2. Create super user
python create_super_user.py

# 3. Start API
cd api
python app.py

# 4. Deploy Cloud Run (when ready)
cd cloud-functions/football-analysis
gcloud run deploy football-analysis --source .

# 5. Start frontend
npm run dev
```

---

## Next Priority Tasks

1. ✅ Complete Phase 1: Database setup
2. ✅ Test login system with sport selection
3. ⏳ Implement video upload endpoint
4. ⏳ Deploy first Cloud Run function (football)
5. ⏳ Create frontend upload UI
6. ⏳ Test end-to-end flow
7. ⏳ Add remaining sports

---

## Key Integration Points

### Login → Sport Selection
- Athlete registers with sport
- Sport determines available video types
- Sports stored in athlete profile

### Upload → Analysis
- Upload triggers correct Cloud Run function based on sport
- Function analyzes with sport-specific baselines
- Results stored in database

### Analysis → Report
- Analysis generates structured data
- Report generator creates PDF
- PDF stored in GCS and linked to analysis

### View → Access Control
- Athletes see own reports
- Physiotherapists see assigned athletes
- Coaches see team members
- Admins see all

---

Ready to start implementing! Begin with Phase 1 (database setup) and work through sequentially.
