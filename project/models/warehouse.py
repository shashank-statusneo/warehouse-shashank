from datetime import datetime

from project import db


class Warehouse(db.Model):
    __tablename__ = "warehouse"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=True)

    # BenchmarkProductivity = db.relationship("BenchmarkProductivity", cascade="all,delete", backref="warehouse")


class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(100), unique=False, nullable=True)

    @classmethod
    def category_id_to_name_mapping(cls):
        return {record.id: record.name for record in Category.query.all()}

    @classmethod
    def category_name_to_id_mapping(cls):
        return {record.name: record.id for record in Category.query.all()}

    @classmethod
    def get_category_by_id(cls, category_id: int):
        return Category.query.filter_by(id=category_id).first()


class BenchmarkProductivity(db.Model):
    __tablename__ = "input_benchmark_productivity"

    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.ForeignKey('warehouse.id'), nullable=False)
    category_id = db.Column(db.ForeignKey('category.id'), nullable=False)
    productivity_experienced_employee = db.Column(db.Float, nullable=False)
    productivity_new_employee = db.Column(db.Float, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now())
    created_by = db.Column(db.String, default="test")  # add logged in user
    updated_on = db.Column(db.DateTime, default=datetime.now())
    updated_by = db.Column(db.String, default="test")  # add logged in user
    soft_delete_flag = db.Column(db.Integer)

    __table_args__ = (db.UniqueConstraint(warehouse_id, category_id),)


class InputDemand(db.Model):
    __tablename__ = "input_demand"

    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.ForeignKey('warehouse.id'))
    date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.ForeignKey('category.id'), nullable=False)
    demand = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now())
    created_by = db.Column(db.String, default="test")  # add logged in user
    updated_on = db.Column(db.DateTime, default=datetime.now())
    updated_by = db.Column(db.String, default="test")  # add logged in user
    soft_delete_flag = db.Column(db.Integer)

    __table_args__ = (db.UniqueConstraint(warehouse_id, category_id, date),)


class InputRequirements(db.Model):
    __tablename__ = "input_requirements"

    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.ForeignKey('warehouse.id'))
    num_current_employees = db.Column(db.Integer, nullable=False)
    plan_from_date = db.Column(db.Date)
    plan_to_date = db.Column(db.Date)
    percentage_absent_expected = db.Column(db.Float, nullable=False)
    day_working_hours = db.Column(db.Integer, nullable=False)
    cost_per_employee_per_month = db.Column(db.Integer, nullable=False)
    total_hiring_budget = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now())
    created_by = db.Column(db.String, default="test")  # add logged in user
    updated_on = db.Column(db.DateTime, default=datetime.now())
    updated_by = db.Column(db.String, default="test")  # add logged in user
    soft_delete_flag = db.Column(db.Integer)


class ManpowerPlanningResult(db.Model):
    __tablename__ = "result_manpower_planning_overall"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    requirement_id = db.Column(db.ForeignKey('input_requirements.id'))
    category_id = db.Column(db.ForeignKey('category.id'), nullable=False)
    num_existing_to_be_deployed = db.Column(db.Integer, nullable=False)
    num_new_to_be_deployed = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now())
    created_by = db.Column(db.String, default="test")  # add logged in user

    __table_args__ = (db.UniqueConstraint(requirement_id, category_id, date),)
