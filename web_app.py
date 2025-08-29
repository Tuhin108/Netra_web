from flask import Flask, render_template, request, jsonify, session
import threading
import time
import uuid
from functools import partial
import json

from core.scanner import scan_url
from core.models import TraceResult, Verdict

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# In-memory storage for scan results (use database in production)
scan_results = {}

def _web_progress_callback(scan_id, progress, message):
    """Callback function to update scan progress for web interface."""
    if scan_id in scan_results:
        scan_results[scan_id]['progress'] = progress
        scan_results[scan_id]['message'] = message
        scan_results[scan_id]['last_update'] = time.time()

def scan_url_thread(scan_id, url):
    """Thread function to run URL scan."""
    try:
        # Create progress callback specific to this scan
        progress_callback = partial(_web_progress_callback, scan_id)
        
        # Run the scan
        trace_result, verdict = scan_url(url, progress_callback)
        
        # Store final results
        scan_results[scan_id].update({
            'status': 'completed',
            'trace_result': {
                'input_url': trace_result.input_url,
                'final_url': trace_result.final_url,
                'hops': [{
                    'url': hop.url,
                    'status_code': hop.status_code,
                    'reason': hop.reason,
                    'elapsed_ms': hop.elapsed_ms
                } for hop in trace_result.hops],
                'js_or_meta_followed': trace_result.js_or_meta_followed,
                'content_type': trace_result.content_type,
                'has_login_form': trace_result.has_login_form,
                'errors': trace_result.errors
            },
            'verdict': {
                'label': verdict.label,
                'score': verdict.score,
                'reasons': verdict.reasons
            },
            'completed_at': time.time()
        })
        
    except Exception as e:
        scan_results[scan_id].update({
            'status': 'error',
            'error': str(e),
            'completed_at': time.time()
        })

@app.route('/')
def index():
    """Main page with URL scanning form."""
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def start_scan():
    """Start a new URL scan."""
    url = request.form.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Generate unique scan ID
    scan_id = str(uuid.uuid4())
    
    # Initialize scan entry
    scan_results[scan_id] = {
        'status': 'processing',
        'url': url,
        'progress': 0.0,
        'message': 'Starting scan...',
        'started_at': time.time(),
        'last_update': time.time()
    }
    
    # Start scan in background thread
    thread = threading.Thread(target=scan_url_thread, args=(scan_id, url))
    thread.daemon = True
    thread.start()
    
    return jsonify({'scan_id': scan_id})

@app.route('/scan/<scan_id>/status')
def get_scan_status(scan_id):
    """Get the current status of a scan."""
    if scan_id not in scan_results:
        return jsonify({'error': 'Scan not found'}), 404
    
    scan_data = scan_results[scan_id]
    
    # Clean up old completed scans (optional)
    if scan_data['status'] in ['completed', 'error']:
        # Keep completed scans for 1 hour
        if time.time() - scan_data.get('completed_at', 0) > 3600:
            del scan_results[scan_id]
            return jsonify({'error': 'Scan expired'}), 404
    
    return jsonify(scan_data)

@app.route('/results/<scan_id>')
def show_results(scan_id):
    """Display scan results."""
    if scan_id not in scan_results or scan_results[scan_id]['status'] != 'completed':
        return render_template('error.html', message='Scan not found or not completed'), 404
    
    scan_data = scan_results[scan_id]
    return render_template('results.html', 
                         scan_data=scan_data,
                         trace_result=scan_data['trace_result'],
                         verdict=scan_data['verdict'])

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """API endpoint for programmatic scanning."""
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        # Run scan synchronously for API
        def api_progress_callback(progress, message):
            pass  # No progress updates for API
        
        trace_result, verdict = scan_url(url, api_progress_callback)
        
        return jsonify({
            'url': url,
            'trace_result': {
                'input_url': trace_result.input_url,
                'final_url': trace_result.final_url,
                'hops': [{
                    'url': hop.url,
                    'status_code': hop.status_code,
                    'reason': hop.reason,
                    'elapsed_ms': hop.elapsed_ms
                } for hop in trace_result.hops],
                'js_or_meta_followed': trace_result.js_or_meta_followed,
                'content_type': trace_result.content_type,
                'has_login_form': trace_result.has_login_form,
                'errors': trace_result.errors
            },
            'verdict': {
                'label': verdict.label,
                'score': verdict.score,
                'reasons': verdict.reasons
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
