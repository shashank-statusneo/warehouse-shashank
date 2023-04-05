from random import randint, random

from project.managers import (
    DemandManager,
    BenchmarkProductivityManager,
    RequirementManager,
    ResultManager,
    WarehouseManager,
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

        additional_data = {
            "project_fulfillment": randint(80, 96),
            "total_hiring_budget": requirement_data["total_hiring_budget"] - randint(100, 1000)
        }
        return {
            "input_data": requirement_data,
            "requirement_id": new_requirement.id,
            "output": result,
            "demand_vs_fulfillment_data": cls.get_demand_vs_fulfillment_dummy_data(requirement_data),
            "additional_data": additional_data,
            "warehouse_name": WarehouseManager.get_warehouse_by_id(new_requirement.warehouse_id).name
        }

    @staticmethod
    def get_dummy_output(requirement_data):
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

        return dummy_output

    @staticmethod
    def get_demand_vs_fulfillment_dummy_data(requirement_data):
        category_name_to_id_mapping = Category.category_name_to_id_mapping()
        dummy_output = {}
        for date in requirement_data["expected_demand"]:
            if date == "extra" or date == "total":
                continue
            if date not in dummy_output:
                dummy_output[date] = dict()
            for category in requirement_data["expected_demand"][date]:
                if category == "total":
                    dummy_output[date][category] = {
                        "expected_demand": requirement_data["expected_demand"][date][category],
                        "fulfillment_with_current": int(requirement_data["expected_demand"][date][category] * random()),
                        "fulfillment_with_total": requirement_data["expected_demand"][date][category] + randint(-250, 250)
                    }
                else:
                    dummy_output[date][category] = {
                        "expected_demand": requirement_data["expected_demand"][date][category]["demand"],
                        "fulfillment_with_current":
                            int(requirement_data["expected_demand"][date][category]["demand"] * random()),
                        "fulfillment_with_total":
                            requirement_data["expected_demand"][date][category]["demand"] + randint(-50, 60),
                        "category_id": category_name_to_id_mapping[category],
                    }

        return dummy_output

