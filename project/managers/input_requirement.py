from project import db
from project.models.warehouse import InputRequirements
from project.utils import remove_unwanted_keys


class RequirementManager:

    @classmethod
    def add_requirement(cls, requirement_data):
        new_requirement = InputRequirements(
            **remove_unwanted_keys(InputRequirements, requirement_data))

        db.session.add(new_requirement)
        db.session.commit()
        return new_requirement

    @classmethod
    def get_requirements(cls, warehouse_id: int):
        records = InputRequirements.query.filter_by(warehouse_id=warehouse_id)
        return [
            {
                "id": record.id,
                "warehouse_id": record.warehouse_id,
                "num_current_employees": record.num_current_employees,
                "plan_from_date": record.plan_from_date,
                "plan_to_date": record.plan_to_date,
                "percentage_absent_expected": record.percentage_absent_expected,
                "day_working_hours": record.day_working_hours,
                "cost_per_employee_per_month": record.cost_per_employee_per_month,
                "total_hiring_budget": record.total_hiring_budget,
                "created_on": record.created_on,
                "updated_on": record.updated_on,
            } for record in records
        ]
