import json

import pandas as pd
from flask import jsonify, make_response, request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource

from main.modules.warehouse_manpower.controller import (
    BenchmarkProductivityController,
    CategoryController,
    DemandController,
    ResultController,
    WarehouseController,
)
from main.modules.warehouse_manpower.schema_validator import (
    BulkWarehouseValidator,
    RequirementValidator,
    UpdateBenchmarkProductivityValidator,
    UpdateDemandValidator,
)
from main.utils import get_data_from_request_or_raise_validation_error


class Warehouses(Resource):
    # method_decorators = [jwt_required()]

    def get(self):
        warehouses = WarehouseController.get_warehouses()
        return make_response(jsonify(warehouses), 200)

    def post(self):
        data = get_data_from_request_or_raise_validation_error(BulkWarehouseValidator, request.json)
        created_warehouses, error_data = WarehouseController.add_warehouses(data["warehouses"])
        return make_response(jsonify(warehouses=created_warehouses, error_data=error_data), 201)


class WarehouseBenchmarkProductivity(Resource):
    # method_decorators = [jwt_required()]

    def get(self, warehouse_id: int):
        benchmark_productivity = BenchmarkProductivityController.get_benchmark_productivity_by_warehouse_id(
            warehouse_id
        )
        return make_response(jsonify(benchmark_productivity), 200)


class BenchmarkProductivity(Resource):
    # method_decorators = [jwt_required()]

    def put(self):
        data = get_data_from_request_or_raise_validation_error(UpdateBenchmarkProductivityValidator, request.json)
        BenchmarkProductivityController.update_benchmark_productivity(data["productivity"])
        return make_response(jsonify(status="success"), 200)


class WarehouseDemands(Resource):
    # method_decorators = [jwt_required()]

    def get(self, warehouse_id: int):
        start_date, end_date = request.args.get("start_date"), request.args.get("end_date")
        if not start_date or not end_date:
            return make_response(jsonify(error="start_date and end_date are required parameters"), 400)
        demands = DemandController.get_demands_by_warehouse_id(warehouse_id, start_date, end_date)
        return make_response(jsonify(demands), 200)


class Demands(Resource):
    # method_decorators = [jwt_required()]

    def put(self):
        data = get_data_from_request_or_raise_validation_error(UpdateDemandValidator, request.json)
        DemandController.update_demand(data["demands"])
        return make_response(jsonify(status="success"), 200)


class CalculateManpower(Resource):
    # method_decorators = [jwt_required()]

    def post(self):
        data = get_data_from_request_or_raise_validation_error(RequirementValidator, request.json)
        result = ResultController.calculate_manpower(data)
        return make_response(jsonify(result), 200)


class ProductivityFile(Resource):
    # method_decorators = [jwt_required()]

    def post(self, warehouse_id: int):
        warehouse_id = int(warehouse_id)
        if not WarehouseController.get_warehouse_by_id(warehouse_id):
            return make_response(jsonify({"error": f"Warehouse not found with id {warehouse_id}"}), 403)
        elif "file" not in request.files:
            return make_response(jsonify({"error": "No file uploaded."}), 400)

        file = request.files["file"]

        if not file.filename.endswith(".xls") and not file.filename.endswith(".xlsx"):
            return make_response(jsonify({"error": "Invalid file extension."}), 400)

        df = pd.read_excel(file)

        required_columns = ["category", "productivity_experienced_employee", "productivity_new_employee"]
        missing_columns = set(required_columns) - set(df.columns)
        extra_columns = set(df.columns) - set(required_columns)
        if missing_columns:
            return make_response(jsonify({"error": f"Missing columns: {missing_columns}."}), 400)
        elif extra_columns:
            return make_response(jsonify({"error": f"Extra columns: {extra_columns}."}), 400)

        data = df.to_json(orient="records")
        data = json.loads(data)
        category_data, error = CategoryController.convert_excel_file_data_according_to_category(data)
        if error:
            return make_response(jsonify(error=error), 400)

        CategoryController.add_categories(category_data)
        BenchmarkProductivityController.add_benchmark_category_from_excel_file_data(data, warehouse_id)

        return make_response(jsonify(status="success"), 201)


class DemandFile(Resource):
    # method_decorators = [jwt_required()]

    def post(self, warehouse_id: int):
        if not WarehouseController.get_warehouse_by_id(warehouse_id):
            return make_response(jsonify({"error": f"Warehouse not found with id {warehouse_id}"}), 403)
        elif "file" not in request.files:
            return make_response(jsonify({"error": "No file uploaded."}), 400)

        file = request.files["file"]

        if not file.filename.endswith(".xls") and not file.filename.endswith(".xlsx"):
            return make_response(jsonify({"error": "Invalid file extension."}), 400)

        df = pd.read_excel(file)

        data = df.to_json(orient="records")
        data = json.loads(data)

        if df.columns[0].lower() != "date":
            return make_response(jsonify({"error": "Date column is missing"}), 400)

        invalid_categories = CategoryController.check_invalid_categories(df.columns[1:])
        if invalid_categories:
            return make_response(jsonify({"error": f"Invalid categories : [{invalid_categories}]"}), 400)

        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        if not start_date or not end_date:
            return make_response(
                jsonify({"error": "start_date and end_date should be present in form data of requests"}), 400
            )

        converted_data, error = DemandController.check_and_convert_excel_data_according_to_input_demand(
            start_date, end_date, data, warehouse_id
        )
        if error:
            return make_response(jsonify(error=error), 400)
        DemandController.add_demands(converted_data)
        return make_response(jsonify(status="success"), 201)


#  wmp = warehouse manpower planner

wmp_namespace = Namespace("wmp", description="Address Operations")
wmp_namespace.add_resource(Warehouses, "/warehouses")
wmp_namespace.add_resource(WarehouseBenchmarkProductivity, "/benchmark_productivity/<int:warehouse_id>")
wmp_namespace.add_resource(BenchmarkProductivity, "/benchmark_productivity")
wmp_namespace.add_resource(WarehouseDemands, "/demands/<int:warehouse_id>")
wmp_namespace.add_resource(Demands, "/demands")
wmp_namespace.add_resource(CalculateManpower, "/calculate")
wmp_namespace.add_resource(ProductivityFile, "/upload_productivity_file/<int:warehouse_id>")
wmp_namespace.add_resource(DemandFile, "/demand_forecast_file/<int:warehouse_id>")
