from flask import Blueprint, render_template, send_from_directory

views_bp = Blueprint('views', __name__)

# Handle static file requests from HTML
@views_bp.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('static', filename)

@views_bp.route('/static/assets/<path:filename>')
def serve_static_assets(filename):
    return send_from_directory('static', filename)

# Page routes
@views_bp.route('/')
@views_bp.route('/index.html')
def home():
    return render_template('index.html')

@views_bp.route('/about')
@views_bp.route('/about.html')
def about():
    return render_template('about.html')

@views_bp.route('/chart')
@views_bp.route('/chart.html')
def chart():
    return render_template('chart.html')

@views_bp.route('/roadmap')
@views_bp.route('/roadmap.html')
def roadmap():
    return render_template('roadmap.html')
