from project import db
from project.models.warehouse import (
    InputDemand,
    Category
)
from project.utils import (
    remove_unwanted_keys,
    update_model_object
)
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError


class DemandManager:

    @classmethod
    def add_demand_in_bulk(cls, demand_data: dict) -> tuple[list, list]:
        new_demand_with_ids = []
        error_data = []
        for demand in demand_data:
            new_category = InputDemand(**remove_unwanted_keys(InputDemand, demand))
            try:
                db.session.add(new_category)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                old_demand = InputDemand.query.filter_by(category_id=demand["category_id"], warehouse_id=demand["warehouse_id"], date=demand["date"]).first()
                update_model_object(old_demand, demand)
                db.session.commit()
            except Exception as e:
                demand["error"] = str(e)
                error_data.append(demand)
                db.session.rollback()
                continue
            demand.update({"id": new_category.id})
            new_demand_with_ids.append(demand)
        return new_demand_with_ids, error_data

    @classmethod
    def get_demands_by_warehouse_id(cls, warehouse_id, start_date, end_date):
        records = db.session.query(InputDemand, Category).join(Category, Category.id == InputDemand.category_id).filter(
            InputDemand.date >= start_date).filter(InputDemand.date <= end_date).filter(InputDemand.warehouse_id ==
                                                                                        warehouse_id)
        if records:
            return cls.create_input_demands_data(records)
        return None

    @classmethod
    def update_demand(cls, update_demand_data: list):
        for updated_demand in update_demand_data:
            old_demand = InputDemand.query.filter_by(
                id=updated_demand["id"]).first()

            if old_demand:
                update_model_object(old_demand, updated_demand)

        db.session.commit()

    @staticmethod
    def create_input_demands_data(records):
        output = {"total": {}}
        for record in records:
            str_date = str(record.InputDemand.date)
            if str_date not in output:
                output[str_date] = {}
            category_name = record.Category.name
            output[str_date][category_name] = {
                "id": record.InputDemand.id,
                "demand": record.InputDemand.demand,
                "created_on": record.InputDemand.created_on,
                "category_id": record.Category.id,
                "updated_on": record.InputDemand.updated_on
            }
            output[str_date]["total"] = output[str_date].get("total", 0) + record.InputDemand.demand
            output["total"][category_name] = output["total"].get(category_name, 0) + record.InputDemand.demand
            output["total"]["total"] = output["total"].get("total", 0) + record.InputDemand.demand

        return output

    @classmethod
    def check_and_convert_excel_data_according_to_input_demand(cls, start_date, end_date, data, warehouse_id):
        category_name_to_id_mapping = Category.category_name_to_id_mapping()
        error_data, output_data = [], []
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        days = (end_date - start_date).days
        valid_dates = [start_date + timedelta(days=i) for i in range(days + 1)]
        for record in data:
            try:
                date = datetime.fromtimestamp(record["date"]/1000).date()
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
                        decimal_part = str(record[key]).split('.')[1]
                        if decimal_part != "0":
                            raise
                    demand = int(record[key])
                except Exception:
                    error_data.append(f"Invalid Demand ({record[key]}) for date : {date} category : {key}")
                    continue
                if demand <= 0:
                    error_data.append(f"Demand ({record[key]}) should be greater then 0 for date : {date} category : {key}")
                    continue
                output_data.append(
                    {
                        "warehouse_id": warehouse_id,
                        "category_id": category_name_to_id_mapping[key],
                        "date": date,
                        "demand": demand
                    }
                )
        if valid_dates:
            error_data.append(f"Data not found for : [{', '.join(str(date) for date in valid_dates)}]")
        return output_data, error_data
