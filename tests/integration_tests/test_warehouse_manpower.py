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


def test_upload_benchmark_productivity_file(client, add_fixtures):
    headers = get_headers(client)
    test_file_dir = os.path.abspath(os.path.dirname(__file__)).replace("integration_tests", "xls_files")

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
