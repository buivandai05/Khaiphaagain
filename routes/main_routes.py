from flask import Blueprint, jsonify, render_template, request
from services.mining_service import MiningService

main_bp = Blueprint('main', __name__)
mining_service = MiningService()

@main_bp.route('/')
def dashboard():
    stats = mining_service.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)

@main_bp.route('/data-management')
def data_management():
    return render_template('data_management.html')

@main_bp.route('/preprocessing')
def preprocessing():
    return render_template('preprocessing.html')

@main_bp.route('/apriori')
def apriori_page():
    return render_template('apriori.html')

@main_bp.route('/fpgrowth')
def fpgrowth_page():
    return render_template('fpgrowth.html')

@main_bp.route('/association-rules')
def association_rules_page():
    return render_template('association_rules.html')

@main_bp.route('/comparison')
def comparison_page():
    return render_template('comparison.html')

@main_bp.route('/reports')
def reports_page():
    return render_template('reports.html')

# --- API ENDPOINTS ---
@main_bp.route('/api/stats', methods=['GET'])
def api_stats():
    return jsonify(mining_service.get_dashboard_stats())

@main_bp.route('/api/compare', methods=['POST'])
def api_compare():
    data = request.json or {}
    min_sup = float(data.get('min_support', 0.03))
    min_conf = float(data.get('min_confidence', 0.5))
    min_lift = float(data.get('min_lift', 1.0))
    res = mining_service.run_comparison(min_sup, min_conf, min_lift)
    return jsonify(res)