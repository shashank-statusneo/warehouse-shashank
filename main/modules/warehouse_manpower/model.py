from main.db import BaseModel, db


class Warehouse(BaseModel):
    """
    Model for Warehouse
    """

    __tablename__ = "warehouse"

    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=True)


class Category(BaseModel):
    """
    Model for Category
    """

    __tablename__ = "category"

    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(100), unique=False, nullable=True)

    @classmethod
    def category_id_to_name_mapping(cls):
        """
        Category id to name mapping
        :return:
        """
        return {record.id: record.name for record in Category.query.all()}

    @classmethod
    def category_name_to_id_mapping(cls):
        return {record.name: record.id for record in Category.query.all()}

    @classmethod
    def get_category_by_id(cls, category_id: int):
        return Category.query.filter_by(id=category_id).first()


class BenchmarkProductivity(BaseModel):
    __tablename__ = "input_benchmark_productivity"

    warehouse_id = db.Column(db.ForeignKey("warehouse.id"), nullable=False)
    category_id = db.Column(db.ForeignKey("category.id"), nullable=False)
    productivity_experienced_employee = db.Column(db.Float, nullable=False)
    productivity_new_employee = db.Column(db.Float, nullable=False)
    created_by = db.Column(db.ForeignKey("auth_user.id"))
    updated_by = db.Column(db.ForeignKey("auth_user.id"), default=None)
    soft_delete_flag = db.Column(db.Integer)

    category = db.relationship("Category", backref=db.backref("input_benchmark_productivity", lazy=True))

    __table_args__ = (db.UniqueConstraint(warehouse_id, category_id),)

    def serialize(self) -> dict:
        """
        Override serialize function to add extra functionality
        :return:
        """
        dict_data = {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name != "category_id"}
        dict_data["category_name"] = self.category.name if self.category else None
        return dict_data


class InputDemand(BaseModel):
    __tablename__ = "input_demand"

    warehouse_id = db.Column(db.ForeignKey("warehouse.id"))
    date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.ForeignKey("category.id"), nullable=False)
    demand = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.ForeignKey("auth_user.id"))
    updated_by = db.Column(db.ForeignKey("auth_user.id"), default=None)
    soft_delete_flag = db.Column(db.Integer)

    __table_args__ = (db.UniqueConstraint(warehouse_id, category_id, date),)


class InputRequirements(BaseModel):
    __tablename__ = "input_requirements"

    warehouse_id = db.Column(db.ForeignKey("warehouse.id"))
    num_current_employees = db.Column(db.Integer, nullable=False)
    plan_from_date = db.Column(db.Date)
    plan_to_date = db.Column(db.Date)
    percentage_absent_expected = db.Column(db.Float, nullable=False)
    day_working_hours = db.Column(db.Integer, nullable=False)
    cost_per_employee_per_month = db.Column(db.Integer, nullable=False)
    total_hiring_budget = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.ForeignKey("auth_user.id"))
    updated_by = db.Column(db.ForeignKey("auth_user.id"), default=None)
    soft_delete_flag = db.Column(db.Integer)


class ManpowerPlanningResult(BaseModel):
    __tablename__ = "result_manpower_planning_overall"

    requirement_id = db.Column(db.ForeignKey("input_requirements.id"))
    date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.ForeignKey("category.id"), nullable=False)
    num_existing_to_be_deployed = db.Column(db.Integer, nullable=False)
    num_new_to_be_deployed = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.ForeignKey("auth_user.id"))

    __table_args__ = (db.UniqueConstraint(requirement_id, category_id),)
