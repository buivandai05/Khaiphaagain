from io import BytesIO

from flask import Blueprint, jsonify, render_template, request, send_file

from services.mining_service import MiningService

main_bp = Blueprint("main", __name__)
mining_service = MiningService()


@main_bp.route("/")
def dashboard():
    try:
        stats = mining_service.get_dashboard_stats()
    except Exception as exc:
        stats = {"error": str(exc)}
    return render_template("dashboard.html", stats=stats)


@main_bp.route("/data-management")
def data_management():
    return render_template("data_management.html")


@main_bp.route("/preprocessing")
def preprocessing():
    return render_template("preprocessing.html")


@main_bp.route("/apriori")
def apriori_page():
    return render_template("apriori.html", defaults=mining_service.DEFAULTS)


@main_bp.route("/fpgrowth")
def fpgrowth_page():
    return render_template("fpgrowth.html", defaults=mining_service.DEFAULTS)


@main_bp.route("/association-rules")
def association_rules_page():
    return render_template("association_rules.html", defaults=mining_service.DEFAULTS)


@main_bp.route("/comparison")
def comparison_page():
    return render_template("comparison.html", defaults=mining_service.DEFAULTS)


@main_bp.route("/reports")
def reports_page():
    return render_template("reports.html", defaults=mining_service.DEFAULTS)


def _params(source):
    return source if isinstance(source, dict) else {}


@main_bp.route("/api/stats")
def api_stats():
    try:
        return jsonify(mining_service.get_dashboard_stats())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@main_bp.route("/api/preprocessing")
def api_preprocessing():
    try:
        return jsonify(mining_service.get_preprocessing_data(
            request.args.get("page", 1), request.args.get("per_page", 25)
        ))
    except (ValueError, FileNotFoundError) as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@main_bp.route("/api/data-management")
def api_data_management():
    try:
        return jsonify(mining_service.get_data_management())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@main_bp.route("/api/mining/<algorithm>", methods=["POST"])
def api_mining(algorithm):
    try:
        return jsonify(mining_service.run_algorithm(algorithm, _params(request.get_json(silent=True))))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Không thể chạy khai phá: {exc}"}), 500


@main_bp.route("/api/compare", methods=["POST"])
def api_compare():
    try:
        return jsonify(mining_service.run_comparison(_params(request.get_json(silent=True))))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Không thể so sánh thuật toán: {exc}"}), 500


@main_bp.route("/api/association-rules", methods=["POST"])
def api_association_rules():
    try:
        return jsonify(mining_service.get_association_overview(_params(request.get_json(silent=True))))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Không thể tổng hợp luật: {exc}"}), 500


@main_bp.route("/api/reports/<report_type>.csv")
def api_report(report_type):
    params = {key: request.args.get(key, value) for key, value in mining_service.DEFAULTS.items()}
    try:
        frame = mining_service.export_frame(report_type, params)
        if frame.empty:
            return jsonify({"error": "Không có kết quả để xuất với cấu hình này."}), 404
        output = BytesIO(frame.to_csv(index=False).encode("utf-8-sig"))
        filename = f"aog_{report_type}.csv"
        return send_file(output, mimetype="text/csv; charset=utf-8", as_attachment=True, download_name=filename)
    except LookupError as exc:
        return jsonify({"error": str(exc)}), 409
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
