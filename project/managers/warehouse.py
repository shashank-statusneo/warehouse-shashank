from typing import List, Any

from project import db
from project.models.warehouse import (
    Warehouse,
    Category
)


class WarehouseManager:

    @classmethod
    def add_warehouses(cls, warehouses_data: dict) -> tuple[list, list]:
        new_warehouses_with_ids = []
        error_data = []
        for warehouse in warehouses_data:
            new_warehouse = Warehouse(**warehouse)
            try:
                db.session.add(new_warehouse)
                db.session.commit()
            except Exception as e:
                warehouse["error"] = str(e)
                error_data.append(warehouse)
                db.session.rollback()
                continue
            warehouse.update({"id": new_warehouse.id})
            new_warehouses_with_ids.append(warehouse)
        return new_warehouses_with_ids, error_data

    @classmethod
    def get_warehouses(cls) -> list:
        warehouses = Warehouse.query.all()
        return [
            {
                "id": warehouse.id,
                "name": warehouse.name,
                "description": warehouse.description
            } for warehouse in warehouses
        ]

    @classmethod
    def get_warehouse_by_id(cls, warehouse_id: int):
        warehouse = Warehouse.query.filter_by(id=warehouse_id).first()
        if warehouse:
            return {
                "id": warehouse.id,
                "name": warehouse.name,
                "description": warehouse.description
            }
        return None


class CategoryManager:

    @classmethod
    def add_bulk_category(cls, category_data: dict) -> tuple[list, list]:
        new_category_with_ids = []
        error_data = []
        for category in category_data:
            new_category = Category(**category)
            try:
                db.session.add(new_category)
                db.session.commit()
            except Exception as e:
                category["error"] = str(e)
                error_data.append(category)
                db.session.rollback()
                continue
            category.update({"id": new_category.id})
            new_category_with_ids.append(category)
        return new_category_with_ids, error_data

    @classmethod
    def get_categories(cls) -> list:
        categories = Category.query.all()
        return [
            {
                "id": category.id,
                "name": category.name,
                "description": category.description
            } for category in categories
        ]

    @classmethod
    def get_category_by_id(cls, category_id: int):
        return Category.query.filter_by(id=category_id).first()

    @classmethod
    def convert_excel_file_data_according_category(cls, data):
        return [{"name": p["category"], "description": p["category"]} for p in data]

    @staticmethod
    def check_invalid_categories(categories: list) -> list[Any]:
        return [category_name for category_name in categories if
                category_name not in Category.category_name_to_id_mapping()]
