import os

import pytest

from main.modules.auth.controller import AuthUserController
from main.modules.warehouse_manpower.controller import WarehouseController
from tests.utils import get_user_role_login_credentials


def get_headers(client, with_refresh_token=False):
    login_credentials = get_user_role_login_credentials()
    response = client.post("/auth/login", json=login_credentials)
    assert response.status_code == 200
    if with_refresh_token:
        return {"Authorization": f"Bearer {response.json['refresh_token']}"}
    return {"Authorization": f"Bearer {response.json['access_token']}"}


@pytest.fixture(scope="function")
def add_fixtures(load_data_to_model_using_controller_from_file):
    load_data_to_model_using_controller_from_file(
        AuthUserController.create_new_user, "integration_tests/fixtures/auth_users.json"
    )
    load_data_to_model_using_controller_from_file(
        WarehouseController.add_warehouses, "integration_tests/fixtures/warehouses.json"
    )


def test_add_and_get_warehouses(client, add_fixtures):
    headers = get_headers(client)
    response = client.post(
        "/wmp/warehouses",
        headers=headers,
        json={
            "warehouses": [
                {"name": "Warehouse B", "description": "Warehouse B"},
                {"name": "Warehouse F", "description": "Warehouse F"},
                {"name": "Warehouse G", "description": "Warehouse G"},
            ]
        },
    )
    assert response.status_code == 201

    response = client.get("/wmp/warehouses", headers=headers)
    assert response.status_code == 200
    assert len(response.json) == 4


def test_upload_get_and_update_benchmark_productivity(client, add_fixtures):
    headers = get_headers(client)
    test_file_dir = os.path.abspath(os.path.dirname(__file__)).replace("integration_tests", "xls_files")
    # Upload from a file.

    # Invalid warehouse id
    response = client.post("/wmp/upload_productivity_file/100", headers=headers)
    assert response.status_code == 403

    # Without any file.
    response = client.post("/wmp/upload_productivity_file/1", headers=headers)
    assert response.status_code == 400
    assert response.json == {"error": "No file uploaded."}

    # Invalid File Extension
    with open(test_file_dir + "/invalid_file.txt", "rb") as file:
        files = {"file": file}
        response = client.post("/wmp/upload_productivity_file/1", data=files, headers=headers)
    assert response.status_code == 400
    assert response.json == {"error": "Invalid file extension."}

    # Invalid File with Extra Columns
    with open(test_file_dir + "/Invalid_Productivity.xlsx", "rb") as file:
        files = {"file": file}
        response = client.post("/wmp/upload_productivity_file/1", data=files, headers=headers)
    assert response.status_code == 400
    assert response.json == {"error": "Extra columns: {'extra_column'}."}

    # Invalid File with missing required columns
    with open(test_file_dir + "/Invalid_Productivity_Missing_Column.xlsx", "rb") as file:
        files = {"file": file}
        response = client.post("/wmp/upload_productivity_file/1", data=files, headers=headers)
    assert response.status_code == 400
    assert response.json == {"error": "Missing columns: {'productivity_new_employee'}."}

    # Invalid File with Invalid column value
    with open(test_file_dir + "/Invalid_Value_Productivity.xlsx", "rb") as file:
        files = {"file": file}
        response = client.post("/wmp/upload_productivity_file/1", data=files, headers=headers)
    assert response.status_code == 400
    assert response.json == {"error": ["Invalid value(s) for : category 8"]}

    # Valid File
    with open(test_file_dir + "/Productivity.xlsx", "rb") as file:
        files = {"file": file}
        response = client.post("/wmp/upload_productivity_file/1", data=files, headers=headers)
    assert response.status_code == 201

    # Get benchmark productivity

    response = client.get("/wmp/benchmark_productivity/1", headers=headers)
    assert response.status_code == 200
    assert len(response.json) == 24
    assert response.json[0]["productivity_new_employee"] == 70
    benchmark_productivity_id = response.json[0]["id"]

    # Update benchmark productivity

    data = {"productivity": [{"id": benchmark_productivity_id, "productivity_new_employee": 80}]}
    response = client.put("/wmp/benchmark_productivity", headers=headers, json=data)
    assert response.status_code == 200

    # Check if the value got updated or not

    response = client.get("/wmp/benchmark_productivity/1", headers=headers)
    assert response.status_code == 200
    assert response.json[0]["productivity_new_employee"] == 80


def test_upload_get_and_test_demands(client, add_fixtures):
    headers = get_headers(client)
    test_file_dir = os.path.abspath(os.path.dirname(__file__)).replace("integration_tests", "xls_files")
    # Upload from a file.

    # Invalid warehouse id
    response = client.post("/wmp/demand_forecast_file/100", headers=headers)
    assert response.status_code == 403

    # Without any file.
    response = client.post("/wmp/demand_forecast_file/1", headers=headers)
    assert response.status_code == 400
    assert response.json == {"error": "No file uploaded."}

    # Invalid File Extension
    with open(test_file_dir + "/invalid_file.txt", "rb") as file:
        files = {"file": file}
        response = client.post("/wmp/demand_forecast_file/1", data=files, headers=headers)
    assert response.status_code == 400
    assert response.json == {"error": "Invalid file extension."}

    # Missing Date Column.
    with open(test_file_dir + "/Invalid_Demand_Missing_Date.xlsx", "rb") as file:
        files = {"file": file}
        response = client.post("/wmp/demand_forecast_file/1", data=files, headers=headers)
    assert response.status_code == 400
    assert response.json == {"error": "Date column is missing"}

    # Invalid Demand Category
    with open(test_file_dir + "/Productivity.xlsx", "rb") as file:
        files = {"file": file}
        response = client.post("/wmp/upload_productivity_file/1", data=files, headers=headers)
    assert response.status_code == 201

    with open(test_file_dir + "/Invalid_Demand_Categories.xlsx", "rb") as file:
        files = {"file": file}
        response = client.post("/wmp/demand_forecast_file/1", data=files, headers=headers)
    assert response.status_code == 400
    assert response.json == {"error": "Invalid categories : [['invalid category', 'invalid category 2']]"}

    # Without passing start_date and end_date
    with open(test_file_dir + "/Invalid_Demand_Value.xlsx", "rb") as file:
        files = {"file": file}
        response = client.post("/wmp/demand_forecast_file/1", data=files, headers=headers)
    assert response.status_code == 400
    assert response.json == {"error": "start_date and end_date should be present in form data of requests"}

    # Invalid Demand value
    with open(test_file_dir + "/Invalid_Demand_Value.xlsx", "rb") as file:
        files = {"file": file, "start_date": "2023-05-24", "end_date": "2023-05-31"}
        response = client.post("/wmp/demand_forecast_file/1", data=files, headers=headers)
    assert response.status_code == 400
    assert response.json == {"error": ["Invalid Demand (276sd) for date : 2023-05-31 category : category 1"]}

    # Valid File
    with open(test_file_dir + "/Demand.xlsx", "rb") as file:
        files = {"file": file, "start_date": "2023-05-24", "end_date": "2023-05-31"}
        response = client.post("/wmp/demand_forecast_file/1", data=files, headers=headers)
    assert response.status_code == 201

    # Get demands

    response = client.get("/wmp/demands/1?start_date=2023-05-24", headers=headers)
    assert response.status_code == 400
    assert response.json == {"error": "start_date and end_date are required parameters"}

    response = client.get("/wmp/demands/1?start_date=2023-05-24&end_date=2023-05-31", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json, dict)
    assert "total" in response.json
    assert len(response.json.keys()) == 9
    assert response.json["2023-05-24"]["category 1"]["demand"] == 269

    demand_id = response.json["2023-05-24"]["category 1"]["id"]

    #  Update Demand
    data = {"demands": [{"id": demand_id, "demand": 900}]}
    response = client.put("/wmp/demands", headers=headers, json=data)
    assert response.status_code == 200

    response = client.get("/wmp/demands/1?start_date=2023-05-24&end_date=2023-05-31", headers=headers)
    assert response.status_code == 200
    assert response.json["2023-05-24"]["category 1"]["demand"] == 900


def test_calculate_result(client, add_fixtures, monkeypatch):
    headers = get_headers(client)
    test_file_dir = os.path.abspath(os.path.dirname(__file__)).replace("integration_tests", "xls_files")

    with open(test_file_dir + "/Productivity.xlsx", "rb") as file:
        files = {"file": file}
        response = client.post("/wmp/upload_productivity_file/1", data=files, headers=headers)
    assert response.status_code == 201

    with open(test_file_dir + "/Demand.xlsx", "rb") as file:
        files = {"file": file, "start_date": "2023-05-24", "end_date": "2023-05-31"}
        response = client.post("/wmp/demand_forecast_file/1", data=files, headers=headers)
    assert response.status_code == 201

    def mocked_f(input_date):
        return True

    monkeypatch.setattr("main.utils.greater_or_equal_to_current_date", mocked_f)

    input_requirements = {
        "warehouse_id": 1,
        "num_current_employees": 10,
        "plan_from_date": "2023-05-24",
        "plan_to_date": "2023-05-31",
        "percentage_absent_expected": 5,
        "day_working_hours": 8,
        "cost_per_employee_per_month": 10000,
        "total_hiring_budget": 200000,
    }
    response = client.post("/wmp/calculate", headers=headers, json=input_requirements)
    assert response.status_code == 200
