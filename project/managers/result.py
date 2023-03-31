from project import db
from project.models.warehouse import (
    ManpowerPlanningResult,
    Category
)
from datetime import datetime
from project.utils import remove_unwanted_keys


class ResultManager:

    @classmethod
    def add_bulk_results(cls, requirement_id: int, result_data: dict):
        category_name_to_id_mapping = Category.category_name_to_id_mapping()

        for date in result_data:
            if date in ["total", "additional_data"]:
                continue
            new_data = {
                "requirement_id": requirement_id,
                "date": datetime.strptime(date, "%Y-%m-%d").date()
            }

            for category in result_data[date]:
                new_data["num_existing_to_be_deployed"] = result_data[date][category]["num_of_existing_to_deploy"]
                new_data["num_new_to_be_deployed"] = result_data[date][category]["num_of_new_to_deploy"]
                new_data["category_id"] = category_name_to_id_mapping[category]
                data = ManpowerPlanningResult(**new_data)
                db.session.add(data)
        db.session.commit()

    @classmethod
    def get_results_by_requirement_id(cls, requirement_id: int) -> list[dict] or None:
        records = ManpowerPlanningResult.query.filter_by(requirement_id=requirement_id)
        if records:
            return [{
                "id": record.id,
                "date": record.date,
                "category_name": Category.get_category_by_id(record.category_id).name,
                "num_existing_to_be_deployed": record.num_existing_to_be_deployed,
                "num_new_to_be_deployed": record.num_new_to_be_deployed,
                "created_on": record.created_on
            } for record in records]
        return None
