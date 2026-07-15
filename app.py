# ============================================================
# Smart Community Resource & Volunteer Allocation System
# Flask Backend - app.py
# ============================================================

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import mysql.connector
import bcrypt
import os
from functools import wraps
from datetime import datetime
import math

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'smart_community_secret_2024')
CORS(app)

# ============================================================
# Database Configuration
# Update these values to match your MySQL setup
# ============================================================
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'Moorthy@123'),
    'database': os.environ.get('DB_NAME', 'smart_community'),
    'autocommit': True
}

# ============================================================
# Database Helper: Get a fresh connection
# ============================================================
def get_db():
    """Returns a new MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)


# ============================================================
# Smart Logic: Auto-calculate priority
# Rule: HIGH priority if people_affected > 100 AND severity = 'high'
# ============================================================
def calculate_priority(people_affected, severity):
    if people_affected > 100 and severity == 'high':
        return 'high'
    return 'normal'


# ============================================================
# Smart Logic: Calculate distance between two lat/lng points (km)
# Uses Haversine formula
# ============================================================
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


# ============================================================
# Auth Decorator: Require volunteer login
# ============================================================
def volunteer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'volunteer_id' not in session:
            return redirect(url_for('volunteer_page'))
        return f(*args, **kwargs)
    return decorated


# ============================================================
# PAGE ROUTES
# ============================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Admin dashboard with charts"""
    return render_template('dashboard.html')


@app.route('/add_issue')
def add_issue_page():
    """Add community issue form"""
    return render_template('add_issue.html')


@app.route('/volunteer')
def volunteer_page():
    """Volunteer login/register page"""
    return render_template('volunteer.html')


@app.route('/map')
def map_page():
    """Interactive map of all issues"""
    return render_template('map.html')


# ============================================================
# API: Add a new community issue
# POST /add_issue
# ============================================================
@app.route('/api/add_issue', methods=['POST'])
def add_issue():
    try:
        data = request.get_json()

        # Validate required fields
        required = ['title', 'location', 'severity', 'people_affected']
        for field in required:
            if field not in data or not str(data[field]).strip():
                return jsonify({'error': f'Missing required field: {field}'}), 400

        title = data['title'].strip()
        description = data.get('description', '').strip()
        location = data['location'].strip()
        latitude = float(data.get('latitude', 11.9416))
        longitude = float(data.get('longitude', 77.7178))
        severity = data['severity'].lower()
        people_affected = int(data['people_affected'])
        category = data.get('category', 'general').strip()

        # Auto-calculate priority using smart logic
        priority = calculate_priority(people_affected, severity)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO issues (title, description, location, latitude, longitude,
                                severity, people_affected, priority, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, description, location, latitude, longitude,
              severity, people_affected, priority, category))

        issue_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({
            'message': 'Issue added successfully',
            'id': issue_id,
            'priority': priority,
            'auto_flagged': priority == 'high'
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# API: Get all issues (with optional filters)
# GET /get_issues
# ============================================================
@app.route('/api/get_issues', methods=['GET'])
def get_issues():
    try:
        severity_filter = request.args.get('severity')
        priority_filter = request.args.get('priority')
        status_filter = request.args.get('status')

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM issues WHERE 1=1"
        params = []

        if severity_filter:
            query += " AND severity = %s"
            params.append(severity_filter)
        if priority_filter:
            query += " AND priority = %s"
            params.append(priority_filter)
        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)

        query += " ORDER BY priority DESC, people_affected DESC, created_at DESC"

        cursor.execute(query, params)
        issues = cursor.fetchall()

        # Convert datetime to string for JSON serialization
        for issue in issues:
            if issue.get('created_at'):
                issue['created_at'] = issue['created_at'].strftime('%Y-%m-%d %H:%M:%S')

        cursor.close()
        conn.close()

        return jsonify(issues), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# API: Register a new volunteer
# POST /register_volunteer
# ============================================================
@app.route('/api/register_volunteer', methods=['POST'])
def register_volunteer():
    try:
        data = request.get_json()

        required = ['name', 'email', 'password', 'skill', 'location']
        for field in required:
            if field not in data or not str(data[field]).strip():
                return jsonify({'error': f'Missing required field: {field}'}), 400

        name = data['name'].strip()
        email = data['email'].strip().lower()
        skill = data['skill'].strip()
        location = data['location'].strip()
        latitude = float(data.get('latitude', 11.9416))
        longitude = float(data.get('longitude', 77.7178))
        phone = data.get('phone', '').strip()

        # Hash password securely with bcrypt
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = get_db()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT id FROM volunteers WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'Email already registered'}), 409

        cursor.execute("""
            INSERT INTO volunteers (name, email, password_hash, skill, location, latitude, longitude, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, email, password_hash, skill, location, latitude, longitude, phone))

        volunteer_id = cursor.lastrowid
        cursor.close()
        conn.close()

        # Auto-login after registration
        session['volunteer_id'] = volunteer_id
        session['volunteer_name'] = name

        return jsonify({
            'message': 'Volunteer registered successfully',
            'id': volunteer_id,
            'name': name
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# API: Volunteer login
# POST /login_volunteer
# ============================================================
@app.route('/api/login_volunteer', methods=['POST'])
def login_volunteer():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM volunteers WHERE email = %s", (email,))
        volunteer = cursor.fetchone()
        cursor.close()
        conn.close()

        if not volunteer:
            return jsonify({'error': 'Invalid email or password'}), 401

        # Verify password against hash
        if not bcrypt.checkpw(password.encode('utf-8'), volunteer['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401

        session['volunteer_id'] = volunteer['id']
        session['volunteer_name'] = volunteer['name']

        return jsonify({
            'message': 'Login successful',
            'id': volunteer['id'],
            'name': volunteer['name'],
            'skill': volunteer['skill'],
            'location': volunteer['location']
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# API: Logout volunteer
# ============================================================
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'}), 200


# ============================================================
# API: Assign a volunteer to an issue (Smart Matching)
# POST /assign_volunteer
# Matches based on skill relevance + location proximity
# ============================================================
@app.route('/api/assign_volunteer', methods=['POST'])
def assign_volunteer():
    try:
        data = request.get_json()
        issue_id = data.get('issue_id')
        volunteer_id = data.get('volunteer_id')

        if not issue_id or not volunteer_id:
            return jsonify({'error': 'issue_id and volunteer_id required'}), 400

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # Verify issue exists
        cursor.execute("SELECT * FROM issues WHERE id = %s", (issue_id,))
        issue = cursor.fetchone()
        if not issue:
            cursor.close(); conn.close()
            return jsonify({'error': 'Issue not found'}), 404

        # Verify volunteer exists
        cursor.execute("SELECT * FROM volunteers WHERE id = %s", (volunteer_id,))
        volunteer = cursor.fetchone()
        if not volunteer:
            cursor.close(); conn.close()
            return jsonify({'error': 'Volunteer not found'}), 404

        # Check if already assigned
        cursor.execute(
            "SELECT id FROM assignments WHERE issue_id = %s AND volunteer_id = %s",
            (issue_id, volunteer_id)
        )
        if cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({'error': 'Volunteer already assigned to this issue'}), 409

        # Create the assignment
        cursor.execute("""
            INSERT INTO assignments (issue_id, volunteer_id)
            VALUES (%s, %s)
        """, (issue_id, volunteer_id))

        # Update issue status to in_progress
        cursor.execute("UPDATE issues SET status = 'in_progress' WHERE id = %s", (issue_id,))

        cursor.close()
        conn.close()

        return jsonify({
            'message': f'{volunteer["name"]} assigned to "{issue["title"]}"',
            'assignment': {
                'issue': issue['title'],
                'volunteer': volunteer['name'],
                'skill': volunteer['skill']
            }
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# API: Smart volunteer matching for an issue
# GET /match_volunteers/<issue_id>
# Returns volunteers ranked by skill match + proximity
# ============================================================
@app.route('/api/match_volunteers/<int:issue_id>', methods=['GET'])
def match_volunteers(issue_id):
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM issues WHERE id = %s", (issue_id,))
        issue = cursor.fetchone()
        if not issue:
            return jsonify({'error': 'Issue not found'}), 404

        # Get available volunteers not already assigned to this issue
        cursor.execute("""
            SELECT v.* FROM volunteers v
            WHERE v.is_available = TRUE
            AND v.id NOT IN (
                SELECT volunteer_id FROM assignments WHERE issue_id = %s
            )
        """, (issue_id,))
        volunteers = cursor.fetchall()
        cursor.close()
        conn.close()

        # Score-based matching: skill match + distance
        SKILL_CATEGORY_MAP = {
            'medical': ['doctor', 'nurse'],
            'disaster': ['driver', 'general', 'engineer'],
            'education': ['teacher'],
            'water': ['engineer', 'general'],
            'infrastructure': ['engineer', 'driver'],
            'general': ['general']
        }

        relevant_skills = SKILL_CATEGORY_MAP.get(issue.get('category', 'general'), ['general'])
        issue_lat = float(issue.get('latitude', 11.9416))
        issue_lon = float(issue.get('longitude', 77.7178))

        scored = []
        for v in volunteers:
            score = 0

            # Skill match bonus (+50 points)
            if v['skill'] in relevant_skills:
                score += 50

            # Distance score: closer = higher score (max +30 points)
            try:
                dist = haversine_distance(
                    float(v.get('latitude', 11.9416)),
                    float(v.get('longitude', 77.7178)),
                    issue_lat, issue_lon
                )
                v['distance_km'] = round(dist, 1)
                dist_score = max(0, 30 - dist)  # Lose 1 point per km, min 0
                score += dist_score
            except:
                v['distance_km'] = 999

            v['match_score'] = round(score, 1)
            v['skill_matched'] = v['skill'] in relevant_skills
            scored.append(v)

        # Sort by match score descending
        scored.sort(key=lambda x: x['match_score'], reverse=True)

        # Remove password hash from response
        for v in scored:
            v.pop('password_hash', None)
            if v.get('created_at'):
                v['created_at'] = v['created_at'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(scored), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# API: Get assignments for a volunteer (their tasks)
# GET /my_tasks
# ============================================================
@app.route('/api/my_tasks', methods=['GET'])
def my_tasks():
    try:
        volunteer_id = request.args.get('volunteer_id') or session.get('volunteer_id')
        if not volunteer_id:
            return jsonify({'error': 'Not logged in'}), 401

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.id as assignment_id, a.assigned_at, a.status as assignment_status,
                   i.title, i.description, i.location, i.severity, i.people_affected,
                   i.priority, i.status as issue_status, i.category
            FROM assignments a
            JOIN issues i ON a.issue_id = i.id
            WHERE a.volunteer_id = %s
            ORDER BY a.assigned_at DESC
        """, (volunteer_id,))
        tasks = cursor.fetchall()

        for t in tasks:
            if t.get('assigned_at'):
                t['assigned_at'] = t['assigned_at'].strftime('%Y-%m-%d %H:%M:%S')

        cursor.close()
        conn.close()

        return jsonify(tasks), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# API: Dashboard statistics
# GET /stats
# ============================================================
@app.route('/api/stats', methods=['GET'])
def stats():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # Total counts
        cursor.execute("SELECT COUNT(*) as total FROM issues")
        total_issues = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM issues WHERE priority = 'high'")
        high_priority = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM volunteers")
        total_volunteers = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM assignments")
        total_assignments = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM issues WHERE status = 'resolved'")
        resolved = cursor.fetchone()['total']

        cursor.execute("SELECT SUM(people_affected) as total FROM issues")
        total_affected = cursor.fetchone()['total'] or 0

        # Breakdown by severity
        cursor.execute("""
            SELECT severity, COUNT(*) as count FROM issues GROUP BY severity
        """)
        by_severity = {row['severity']: row['count'] for row in cursor.fetchall()}

        # Breakdown by category
        cursor.execute("""
            SELECT category, COUNT(*) as count FROM issues GROUP BY category
        """)
        by_category = {row['category']: row['count'] for row in cursor.fetchall()}

        # Breakdown by volunteer skill
        cursor.execute("""
            SELECT skill, COUNT(*) as count FROM volunteers GROUP BY skill
        """)
        by_skill = {row['skill']: row['count'] for row in cursor.fetchall()}

        # Recent issues
        cursor.execute("""
            SELECT id, title, severity, priority, people_affected, created_at
            FROM issues ORDER BY created_at DESC LIMIT 5
        """)
        recent = cursor.fetchall()
        for r in recent:
            if r.get('created_at'):
                r['created_at'] = r['created_at'].strftime('%Y-%m-%d %H:%M')

        cursor.close()
        conn.close()

        return jsonify({
            'total_issues': total_issues,
            'high_priority': high_priority,
            'total_volunteers': total_volunteers,
            'total_assignments': total_assignments,
            'resolved': resolved,
            'total_affected': int(total_affected),
            'by_severity': by_severity,
            'by_category': by_category,
            'by_skill': by_skill,
            'recent_issues': recent
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# API: Update issue status
# PATCH /update_issue/<id>
# ============================================================
@app.route('/api/update_issue/<int:issue_id>', methods=['PATCH'])
def update_issue(issue_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        if new_status not in ['open', 'in_progress', 'resolved']:
            return jsonify({'error': 'Invalid status'}), 400

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE issues SET status = %s WHERE id = %s", (new_status, issue_id))
        cursor.close()
        conn.close()

        return jsonify({'message': 'Issue updated', 'status': new_status}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# API: Get all volunteers (for admin)
# GET /get_volunteers
# ============================================================
@app.route('/api/get_volunteers', methods=['GET'])
def get_volunteers():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, skill, location, phone, is_available, created_at FROM volunteers")
        volunteers = cursor.fetchall()
        for v in volunteers:
            if v.get('created_at'):
                v['created_at'] = v['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        cursor.close()
        conn.close()
        return jsonify(volunteers), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# Entry Point
# ============================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
