from project import db
from project.models.warehouse import (
    BenchmarkProductivity,
    Category,
)
from project.utils import update_model_object, remove_unwanted_keys
from sqlalchemy.exc import IntegrityError



class BenchmarkProductivityManager:

    @classmethod
    def add_bulk_benchmark_productivity(cls, benchmark_productivity: list) -> tuple[list, list]:
        new_productivity_with_ids = []
        error_data = []
        for productivity in benchmark_productivity:
            new_category = BenchmarkProductivity(**remove_unwanted_keys(BenchmarkProductivity, productivity))
            try:
                db.session.add(new_category)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                old_productivity = BenchmarkProductivity.query.filter_by(category_id=productivity["category_id"], warehouse_id=int(productivity["warehouse_id"])).first()
                update_model_object(old_productivity, productivity)
                db.session.commit()
            except Exception as e:
                productivity["error"] = str(e)
                error_data.append(productivity)
                db.session.rollback()
                continue
            productivity.update({"id": new_category.id})
            new_productivity_with_ids.append(productivity)
        return new_productivity_with_ids, error_data

    @classmethod
    def update_benchmark_productivity(cls, list_of_updated_productivity: list):
        for new_benchmark_productivity in list_of_updated_productivity:
            old_benchmark_productivity = BenchmarkProductivity.query.filter_by(
                id=new_benchmark_productivity["id"]).first()
            if old_benchmark_productivity:
                update_model_object(old_benchmark_productivity, new_benchmark_productivity)
        db.session.commit()

    @classmethod
    def get_benchmark_productivity_by_warehouse_id(cls, warehouse_id: int) -> list[dict] or None:
        records = BenchmarkProductivity.query.filter_by(warehouse_id=warehouse_id)
        if records:
            return [{
                "id": record.id,
                "warehouse_id": record.warehouse_id,
                "category_name": Category.get_category_by_id(record.category_id).name,
                "created_on": record.created_on,
                "updated_on": record.updated_on,
                "productivity_experienced_employee": record.productivity_experienced_employee,
                "productivity_new_employee": record.productivity_new_employee
            } for record in records]
        return None

    @classmethod
    def add_benchmark_category_from_excel_file_data(cls, file_data, warehouse_id):
        category_name_to_id_mapping = Category.category_name_to_id_mapping()

        benchmark_productivity_data = [
            {
                "category_id": category_name_to_id_mapping[record["category"]],
                "warehouse_id": warehouse_id,
                "productivity_experienced_employee": record["productivity_experienced_employee"],
                "productivity_new_employee": record["productivity_new_employee"]
            } for record in file_data
        ]
        return cls.add_bulk_benchmark_productivity(benchmark_productivity_data)