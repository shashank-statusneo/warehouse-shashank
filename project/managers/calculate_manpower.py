from random import randint

from project.managers import (
    DemandManager,
    BenchmarkProductivityManager,
    RequirementManager,
    ResultManager
)
from project.models.warehouse import Category


class WarehouseManpowerPlanner:

    @classmethod
    def calculate_manpower(cls, requirement_data):
        new_requirement = RequirementManager.add_requirement(requirement_data)
        expected_demand = DemandManager.get_demands_by_warehouse_id(
            new_requirement.warehouse_id,
            new_requirement.plan_from_date,
            new_requirement.plan_to_date
        )

        productivity = BenchmarkProductivityManager.get_benchmark_productivity_by_warehouse_id(
            new_requirement.warehouse_id)

        requirement_data["expected_demand"] = expected_demand
        requirement_data["productivity"] = productivity

        result = cls.get_dummy_output(requirement_data)
        ResultManager.add_bulk_results(new_requirement.id, result)
        demand_vs_fulfillment_data = [
            {
                "date": key,
                "demand": value["total"],
                "expectedFulfillmentQty": value["total"] - randint(-250, 250)}
            for key, value in expected_demand.items() if key != "total"
        ]
        additional_data = {
            "project_fulfillment": randint(80, 96),
            "total_hiring_budget": requirement_data["total_hiring_budget"] - randint(100, 1000)
        }
        return {
            "input_data": requirement_data,
            "requirement_id": new_requirement.id,
            "output": result,
            "demand_vs_fulfillment_data": demand_vs_fulfillment_data,
            "additional_data": additional_data
        }

    @staticmethod
    def get_dummy_output(requirement_data):
        # dummy_output = {"total": dict(), "additional_data": dict()}
        category_name_to_id_mapping = Category.category_name_to_id_mapping()
        dummy_output = {}
        for date in requirement_data["expected_demand"]:
            if date == "extra" or date == "total":
                continue
            if date not in dummy_output:
                dummy_output[date] = dict()
            for category in requirement_data["expected_demand"][date]:
                if category == "total":
                    continue
                existing = randint(2, 7)
                new = randint(2, 7)
                dummy_output[date][category] = {
                    "num_of_existing_to_deploy": existing,
                    "num_of_new_to_deploy": new,
                    "category_id": category_name_to_id_mapping[category],
                    "total": existing + new
                }

        #         dummy_output["total"]["num_of_existing_to_deploy"] = dummy_output["total"].get(
        #             "num_of_existing_to_deploy", 0) + existing
        #         dummy_output["total"]["num_of_new_to_deploy"] = dummy_output["total"].get(
        #             "num_of_new_to_deploy", 0) + new
        #         dummy_output["total"]["total"] = dummy_output["total"].get("total", 0) + new + existing
        #
        # if dummy_output["total"].get("num_of_new_to_deploy"):
        #     dummy_output["additional_data"]["additional_employee_required"] = \
        #         dummy_output["total"].get("num_of_new_to_deploy")
        #     dummy_output["additional_data"]["total_hiring_budget"] = \
        #         randint(requirement_data["total_hiring_budget"] - 10000, requirement_data["total_hiring_budget"])
        #     dummy_output["additional_data"]["project_fulfillment"] = randint(80, 99)
        #     dummy_output["additional_data"]["graph_data"] = []

        return dummy_output
