from datetime import datetime, timedelta
from random import randint, random

from sqlalchemy.exc import IntegrityError

from main.modules.warehouse_manpower.model import (
    BenchmarkProductivity,
    Category,
    InputDemand,
    InputRequirements,
    ManpowerPlanningResult,
    Warehouse,
    db,
)


class WarehouseController:
    """
    This is the controller class which is used to handle all the logical and CURD operations of warehouse.
    """

    @classmethod
    def add_warehouses(cls, warehouses_data: list) -> tuple[list, list]:
        """
        Function to add new warehouses
        :param warehouses_data:
        :return:
        """
        new_warehouses_with_ids = []
        error_data = []
        for warehouse in warehouses_data:
            try:
                new_warehouse = Warehouse.create(warehouse)
            except Exception as e:
                warehouse["error"] = str(e)
                error_data.append(warehouse)
                Warehouse.rollback()
                continue
            warehouse.update({"id": new_warehouse.id})
            new_warehouses_with_ids.append(warehouse)
        return new_warehouses_with_ids, error_data

    @classmethod
    def get_warehouses(cls) -> list:
        """
        Function to get list of warehouses.
        :return:
        """
        warehouses = Warehouse.query.all()
        return [warehouse.serialize() for warehouse in warehouses]

    @classmethod
    def get_warehouse_by_id(cls, warehouse_id: int):
        """
        Function to get warehouse by id.
        :param warehouse_id:
        :return:
        """
        return Warehouse.query.filter_by(id=warehouse_id).first()


class CategoryController:
    @classmethod
    def add_bulk_category(cls, category_data: list) -> tuple[list, list]:
        """
        Function to add multiple category at a time.
        :param category_data:
        :return:
        """
        new_category_with_ids = []
        error_data = []
        for category in category_data:
            try:
                new_category = Category.create(category)
            except Exception as e:
                category["error"] = str(e)
                error_data.append(category)
                Category.rollback()
                continue
            category.update({"id": new_category.id})
            new_category_with_ids.append(category)
        return new_category_with_ids, error_data

    @classmethod
    def get_categories(cls) -> list:
        """
        Function to get the list of categories.
        :return:
        """
        categories = Category.query.all()
        return [category.serialize() for category in categories]

    @classmethod
    def get_category_by_id(cls, category_id: int):
        """
        Function to get category by id.
        :param category_id:
        :return:
        """
        return Category.query.filter_by(id=category_id).first()

    @classmethod
    def convert_excel_file_data_according_category(cls, data: list) -> (list, list):
        """
        Function to check if excel file data is valid or not and convert it according to category requirement.
        :param data:
        :return:
        """
        category_data, error_data = [], []
        for record in data:
            try:
                if isinstance(record["productivity_experienced_employee"], float):
                    decimal_part = str(record["productivity_experienced_employee"]).split(".")[1]
                    if decimal_part != "0":
                        raise

                if isinstance(record["productivity_new_employee"], float):
                    decimal_part = str(record["productivity_new_employee"]).split(".")[1]
                    if decimal_part != "0":
                        raise
                int(record["productivity_experienced_employee"])
                int(record["productivity_new_employee"])
                category_data.append({"name": record["category"], "description": record["category"]})
            except Exception:
                error_data.append(f"Invalid value(s) for : {record['category']}")

        return category_data, error_data

    @staticmethod
    def check_invalid_categories(categories: list) -> list:
        """
        Function to check and return a list of invalid categories.
        :param categories:
        :return:
        """
        return [
            category_name for category_name in categories if category_name not in Category.category_name_to_id_mapping()
        ]


class BenchmarkProductivityController:
    @classmethod
    def add_bulk_benchmark_productivity(cls, benchmark_productivity: list) -> tuple[list, list]:
        """
        Function to add benchmark productivity.
        :param benchmark_productivity:
        :return:
        """
        new_productivity_with_ids = []
        error_data = []
        for productivity in benchmark_productivity:
            try:
                _productivity = BenchmarkProductivity.create(productivity)
            except IntegrityError:
                BenchmarkProductivity.rollback()
                _productivity = BenchmarkProductivity.query.filter_by(
                    category_id=productivity["category_id"], warehouse_id=int(productivity["warehouse_id"])
                ).first()
                _productivity.update(productivity)
            except Exception as e:
                productivity["error"] = str(e)
                error_data.append(productivity)
                continue
            productivity.update({"id": _productivity.id})
            new_productivity_with_ids.append(productivity)
        return new_productivity_with_ids, error_data

    @classmethod
    def update_benchmark_productivity(cls, list_of_updated_productivity: list):
        """
        Function to update benchmark productivity.
        :param list_of_updated_productivity:
        :return:
        """
        for new_benchmark_productivity in list_of_updated_productivity:
            old_benchmark_productivity = BenchmarkProductivity.query.filter_by(
                id=new_benchmark_productivity["id"]
            ).first()
            if old_benchmark_productivity:
                old_benchmark_productivity.update(new_benchmark_productivity)

    @classmethod
    def get_benchmark_productivity_by_warehouse_id(cls, warehouse_id: int) -> list[dict] or None:
        """
        Function to get all benchmark productivity of a warehouse.
        :param warehouse_id:
        :return:
        """
        records = BenchmarkProductivity.query.filter_by(warehouse_id=warehouse_id)
        return [record.serialize() for record in records]

    @classmethod
    def add_benchmark_category_from_excel_file_data(cls, file_data: list, warehouse_id: int):
        """
        Function to get the benchmark category from an excel file.
        :param file_data:
        :param warehouse_id:
        :return:
        """
        category_name_to_id_mapping = Category.category_name_to_id_mapping()

        benchmark_productivity_data = [
            {
                "category_id": category_name_to_id_mapping[record["category"]],
                "warehouse_id": warehouse_id,
                "productivity_experienced_employee": record["productivity_experienced_employee"],
                "productivity_new_employee": record["productivity_new_employee"],
            }
            for record in file_data
        ]
        return cls.add_bulk_benchmark_productivity(benchmark_productivity_data)


class DemandController:
    @classmethod
    def add_demand_in_bulk(cls, demand_data: dict) -> tuple[list, list]:
        """
        Function to add demands.
        :param demand_data:
        :return:
        """
        new_demand_with_ids = []
        error_data = []
        for demand in demand_data:
            try:
                _demand = InputDemand.create(demand)
            except IntegrityError:
                InputDemand.rollback()
                _demand = InputDemand.query.filter_by(
                    category_id=demand["category_id"], warehouse_id=demand["warehouse_id"], date=demand["date"]
                ).first()
                _demand.update(demand)
            except Exception as e:
                demand["error"] = str(e)
                error_data.append(demand)
                continue
            demand.update({"id": _demand.id})
            new_demand_with_ids.append(demand)
        return new_demand_with_ids, error_data

    @classmethod
    def get_demands_by_warehouse_id(cls, warehouse_id: int, start_date: type, end_date: type):
        """
        Function to get demands of a warehouse between a date range.
        :param warehouse_id:
        :param start_date:
        :param end_date:
        :return:
        """

        records = (
            db.session.query(InputDemand, Category)
            .join(Category, Category.id == InputDemand.category_id)
            .filter(InputDemand.date >= start_date)
            .filter(InputDemand.date <= end_date)
            .filter(InputDemand.warehouse_id == warehouse_id)
        )
        return cls.create_input_demands_data(records) if records else None

    @classmethod
    def update_demand(cls, update_demand_data: list):
        """
        Function to update demands value.
        :param update_demand_data:
        :return:
        """
        for updated_demand in update_demand_data:
            old_demand = InputDemand.query.filter_by(id=updated_demand["id"]).first()

            if old_demand:
                old_demand.update(updated_demand)

    @staticmethod
    def create_input_demands_data(records) -> dict:
        """
        Function to create input demands data.
        :param records:
        :return:
        """
        output = {"total": {}}
        for record in records:
            str_date = str(record.InputDemand.date)
            if str_date not in output:
                output[str_date] = {}
            category_name = record.Category.name
            output[str_date][category_name] = {
                "id": record.InputDemand.id,
                "demand": record.InputDemand.demand,
                "created_on": record.InputDemand.created_at,
                "category_id": record.Category.id,
                "updated_on": record.InputDemand.updated_at,
            }
            output[str_date]["total"] = output[str_date].get("total", 0) + record.InputDemand.demand
            output["total"][category_name] = output["total"].get(category_name, 0) + record.InputDemand.demand
            output["total"]["total"] = output["total"].get("total", 0) + record.InputDemand.demand

        return output

    @classmethod
    def check_and_convert_excel_data_according_to_input_demand(
        cls, start_date, end_date, data: list, warehouse_id: int
    ):
        """
        Function to check demand file and convert file data.
        :param start_date:
        :param end_date:
        :param data:
        :param warehouse_id:
        :return:
        """
        category_name_to_id_mapping = Category.category_name_to_id_mapping()
        error_data, output_data = [], []
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        days = (end_date - start_date).days
        valid_dates = [start_date + timedelta(days=i) for i in range(days + 1)]
        for record in data:
            try:
                date = datetime.fromtimestamp(record["date"] / 1000).date()
                if date not in valid_dates:
                    error_data.append(f"Invalid Date : {date}")
                    continue
                else:
                    valid_dates.remove(date)
            except Exception:
                error_data.append(f"Invalid format for date : {record['date']}")
                continue

            for key in record:
                if key == "date":
                    continue
                try:
                    if isinstance(record[key], float):
                        decimal_part = str(record[key]).split(".")[1]
                        if decimal_part != "0":
                            raise
                    demand = int(record[key])
                except Exception:
                    error_data.append(f"Invalid Demand ({record[key]}) for date : {date} category : {key}")
                    continue
                if demand <= 0:
                    error_data.append(
                        f"Demand ({record[key]}) should be greater then 0 for date : {date} category : {key}"
                    )
                    continue
                output_data.append(
                    {
                        "warehouse_id": warehouse_id,
                        "category_id": category_name_to_id_mapping[key],
                        "date": date,
                        "demand": demand,
                    }
                )
        if valid_dates:
            error_data.append(f"Data not found for : [{', '.join(str(date) for date in valid_dates)}]")
        return output_data, error_data


class RequirementController:
    @classmethod
    def add_requirement(cls, requirement_data):
        new_requirement = InputRequirements.create(requirement_data)
        return new_requirement

    @classmethod
    def get_requirements(cls, warehouse_id: int):
        records = InputRequirements.query.filter_by(warehouse_id=warehouse_id)
        return [record.serialize() for record in records]


class ResultController:
    @classmethod
    def add_bulk_results(cls, requirement_id: int, result_data: dict):
        category_name_to_id_mapping = Category.category_name_to_id_mapping()

        for date in result_data:
            if date in ["total", "additional_data"]:
                continue
            new_data = {"requirement_id": requirement_id, "date": datetime.strptime(date, "%Y-%m-%d").date()}

            for category in result_data[date]:
                new_data["num_existing_to_be_deployed"] = result_data[date][category]["num_of_existing_to_deploy"]
                new_data["num_new_to_be_deployed"] = result_data[date][category]["num_of_new_to_deploy"]
                new_data["category_id"] = category_name_to_id_mapping[category]
                ManpowerPlanningResult.create(new_data)

    @classmethod
    def get_results_by_requirement_id(cls, requirement_id: int) -> list[dict] or None:
        records = ManpowerPlanningResult.query.filter_by(requirement_id=requirement_id)
        if records:
            return [
                {
                    "id": record.id,
                    "date": record.date,
                    "category_name": Category.get_category_by_id(record.category_id).name,
                    "num_existing_to_be_deployed": record.num_existing_to_be_deployed,
                    "num_new_to_be_deployed": record.num_new_to_be_deployed,
                    "created_on": record.created_on,
                }
                for record in records
            ]
        return None

    @classmethod
    def calculate_manpower(cls, requirement_data: dict) -> dict:
        """
        Function to calculate manpower.
        :param requirement_data:
        :return:
        """
        new_requirement = RequirementController.add_requirement(requirement_data)
        expected_demand = DemandController.get_demands_by_warehouse_id(
            new_requirement.warehouse_id, new_requirement.plan_from_date, new_requirement.plan_to_date
        )

        productivity = BenchmarkProductivityController.get_benchmark_productivity_by_warehouse_id(
            new_requirement.warehouse_id
        )

        requirement_data["expected_demand"] = expected_demand
        requirement_data["productivity"] = productivity

        result = cls.get_dummy_output(requirement_data)
        # ResultController.add_bulk_results(new_requirement.id, result)  # uncomment this if want to store result.

        additional_data = {
            "project_fulfillment": randint(80, 96),
            "total_hiring_budget": requirement_data["total_hiring_budget"] - randint(100, 1000),
        }
        return {
            "input_data": requirement_data,
            "requirement_id": new_requirement.id,
            "output": result,
            "demand_vs_fulfillment_data": cls.get_demand_vs_fulfillment_dummy_data(requirement_data),
            "additional_data": additional_data,
            "warehouse_name": WarehouseController.get_warehouse_by_id(new_requirement.warehouse_id).name,
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
                    "total": existing + new,
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
                        "fulfillment_with_total": requirement_data["expected_demand"][date][category]
                        + randint(-250, 250),
                    }
                else:
                    dummy_output[date][category] = {
                        "expected_demand": requirement_data["expected_demand"][date][category]["demand"],
                        "fulfillment_with_current": int(
                            requirement_data["expected_demand"][date][category]["demand"] * random()
                        ),
                        "fulfillment_with_total": requirement_data["expected_demand"][date][category]["demand"]
                        + randint(-50, 60),
                        "category_id": category_name_to_id_mapping[category],
                    }

        return dummy_output
