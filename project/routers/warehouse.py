from flask import Blueprint, request, jsonify, make_response
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
import pandas as pd
import json


from project.managers import (
    WarehouseManager,
    CategoryManager,
    BenchmarkProductivityManager,
    WarehouseManpowerPlanner,
    DemandManager,
    RequirementManager,
    ResultManager
)
from project.schema_validators.warehouse import (
    UpdateBenchmarkProductivityValidator,
    BulkDemandValidator,
    UpdateDemandValidator,
    RequirementValidator,
    BulkWarehouseValidator,
    BulkCategoryValidator,
    BulkBenchmarkProductivityValidator
)

warehouse = Blueprint('warehouse', __name__)


@warehouse.route('/warehouses', methods=['GET', 'POST'])
@jwt_required()
def _warehouse():
    if request.method == "GET":
        warehouses = WarehouseManager.get_warehouses()
        return jsonify(warehouses), 200

    data = request.json
    validator = BulkWarehouseValidator()
    try:
        data = validator.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    created_warehouses, error_data = WarehouseManager.add_warehouses(data["warehouses"])
    return jsonify(warehouses=created_warehouses, error_data=error_data), 200


@warehouse.route('/category', methods=['GET', 'POST'])
@jwt_required()
def _category():
    if request.method == "GET":
        warehouses = CategoryManager.get_categories()
        return jsonify(warehouses), 200

    data = request.json
    validator = BulkCategoryValidator()
    try:
        data = validator.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    created_category, error_data = CategoryManager.add_bulk_category(data["category"])
    return jsonify(category=created_category, error_data=error_data), 200


@warehouse.route('/benchmark_productivity', methods=['POST'])
@jwt_required()
def add_benchmark_productivity():
    data = request.json
    validator = BulkBenchmarkProductivityValidator()
    try:
        data = validator.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    productivity_created, error_data = \
        BenchmarkProductivityManager.add_bulk_benchmark_productivity(data["productivity"])
    return jsonify(productivity_created=productivity_created, error_data=error_data), 200


@warehouse.route('/benchmark_productivity/<warehouse_id>', methods=['GET'])
@jwt_required()
def get_warehouse_productivity(warehouse_id: int):
    benchmark_productivity = BenchmarkProductivityManager.get_benchmark_productivity_by_warehouse_id(warehouse_id)
    return jsonify(benchmark_productivity), 200


@warehouse.route('/benchmark_productivity', methods=['PUT'])
@jwt_required()
def update_benchmark_productivity():
    data = request.json
    validator = UpdateBenchmarkProductivityValidator()
    try:
        data = validator.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    BenchmarkProductivityManager.update_benchmark_productivity(data["productivity"])
    return make_response("OK", 200)


@warehouse.route('/demands', methods=['POST'])
@jwt_required()
def _demand():
    data = request.json
    validator = BulkDemandValidator()
    try:
        data = validator.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    demands_created, error_data = DemandManager.add_demand_in_bulk(data["demands"])
    return jsonify(demands=demands_created, error_data=error_data)


@warehouse.route('/demands/<warehouse_id>', methods=['GET'])
@jwt_required()
def get_demands(warehouse_id: int):
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    if not start_date or not end_date:
        return jsonify(msg="start_date and end_date are required parameters"), 400
    return DemandManager.get_demands_by_warehouse_id(warehouse_id, start_date, end_date)


@warehouse.route('/demands', methods=['PUT'])
@jwt_required()
def update_demand():
    data = request.json
    validator = UpdateDemandValidator()
    try:
        data = validator.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    DemandManager.update_demand(data["demands"])
    return make_response("OK", 200)


@warehouse.route('/requirement/<warehouse_id>', methods=['GET'])
@jwt_required()
def get_requirement(warehouse_id):
    return jsonify(RequirementManager.get_requirements(warehouse_id))


@warehouse.route('/calculate', methods=['POST'])
@jwt_required()
def calculate():
    data = request.json
    validator = RequirementValidator()
    try:
        data = validator.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    result = WarehouseManpowerPlanner.calculate_manpower(data)
    return jsonify(result)


@warehouse.route('/result/<requirement_id>', methods=['GET'])
@jwt_required()
def _result(requirement_id: int):
    return jsonify(ResultManager.get_results_by_requirement_id(requirement_id))


@warehouse.route('/upload_productivity_file/<warehouse_id>', methods=['POST'])
@jwt_required()
def upload_productivity_excel(warehouse_id: int):
    warehouse_id = int(warehouse_id)
    if not WarehouseManager.get_warehouse_by_id(warehouse_id):
        return jsonify({'error': f'Warehouse not found with id {warehouse_id}'}), 403
    elif 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400

    file = request.files['file']

    if not file.filename.endswith('.xls') and not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'Invalid file extension.'}), 400

    df = pd.read_excel(file)

    required_columns = ['category', 'productivity_experienced_employee', 'productivity_new_employee']
    missing_columns = set(required_columns) - set(df.columns)
    extra_columns = set(df.columns) - set(required_columns)
    if missing_columns:
        return jsonify({'error': f'Missing columns: {missing_columns}.'}), 400
    elif extra_columns:
        return jsonify({'error': f'Extra columns: {extra_columns}.'}), 400

    data = df.to_json(orient='records')
    data = json.loads(data)
    category_data = CategoryManager.convert_excel_file_data_according_category(data)
    CategoryManager.add_bulk_category(category_data)
    BenchmarkProductivityManager.add_benchmark_category_from_excel_file_data(data, warehouse_id)

    return jsonify(status="success"), 201


@warehouse.route('/demand_forecast_file/<warehouse_id>', methods=['POST'])
@jwt_required()
def upload_demand_excel(warehouse_id: int):
    if not WarehouseManager.get_warehouse_by_id(warehouse_id):
        return jsonify({'error': f'Warehouse not found with id {warehouse_id}'}), 403
    elif 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400

    file = request.files['file']

    if not file.filename.endswith('.xls') and not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'Invalid file extension.'}), 400

    df = pd.read_excel(file)

    data = df.to_json(orient='records')
    data = json.loads(data)

    if df.columns[0].lower() != "date":
        return jsonify({'error': 'Date column is missing'}), 400

    invalid_categories = CategoryManager.check_invalid_categories(df.columns[1:])
    if invalid_categories:
        return jsonify({'error': f'Invalid categories : [{invalid_categories}]'}), 400

    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    if not start_date or not end_date:
        return jsonify({'error': "start_date and end_date should be present in form data of requests"}), 400

    converted_data, error = DemandManager.check_and_convert_excel_data_according_to_input_demand(start_date, end_date, data, warehouse_id)
    if error:
        return jsonify(error=error), 400
    DemandManager.add_demand_in_bulk(converted_data)
    return jsonify(status="success"), 201
