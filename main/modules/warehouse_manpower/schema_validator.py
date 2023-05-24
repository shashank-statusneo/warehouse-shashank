from marshmallow import Schema, fields
from marshmallow.validate import Range

from main.utils import greater_or_equal_to_current_date


class WarehouseAndCategoryValidator(Schema):
    name = fields.String(required=True)
    description = fields.String()


class BulkWarehouseValidator(Schema):
    warehouses = fields.List(fields.Nested(WarehouseAndCategoryValidator()), required=True)


class BulkCategoryValidator(Schema):
    category = fields.List(fields.Nested(WarehouseAndCategoryValidator()), required=True)


class BenchmarkProductivityValidator(Schema):
    productivity_experienced_employee = fields.Float(required=True)
    productivity_new_employee = fields.Float(required=True)
    warehouse_id = fields.Integer(required=True)
    category_id = fields.Integer(required=True)


class BulkBenchmarkProductivityValidator(Schema):
    productivity = fields.List(fields.Nested(BenchmarkProductivityValidator()), required=True)


class UpdateOnlyFieldBenchmarkProductivity(Schema):
    id = fields.Float(required=True)
    productivity_experienced_employee = fields.Float(required=False, validate=Range(min=0))
    productivity_new_employee = fields.Float(required=False, validate=Range(min=0))


class UpdateBenchmarkProductivityValidator(Schema):
    productivity = fields.List(fields.Nested(UpdateOnlyFieldBenchmarkProductivity()), required=True)


class DemandValidator(Schema):
    warehouse_id = fields.Integer(required=True)
    category_id = fields.Integer(required=True)
    date = fields.Date(required=True, validate=greater_or_equal_to_current_date)
    demand = fields.Integer(required=True, validate=Range(min=0))


class BulkDemandValidator(Schema):
    demands = fields.List(fields.Nested(DemandValidator()), required=True)


class UpdateOnlyFieldDemand(Schema):
    id = fields.Integer(required=True)
    demand = fields.Integer(required=False, validate=Range(min=0))


class UpdateDemandValidator(Schema):
    demands = fields.List(fields.Nested(UpdateOnlyFieldDemand()), required=True)


class RequirementValidator(Schema):
    warehouse_id = fields.Integer(required=True)
    num_current_employees = fields.Integer(required=True)
    plan_from_date = fields.Date(required=True, validate=greater_or_equal_to_current_date)
    plan_to_date = fields.Date(required=True, validate=greater_or_equal_to_current_date)
    percentage_absent_expected = fields.Integer(required=True)
    day_working_hours = fields.Integer(required=True, validate=Range(min=1, max=24))
    cost_per_employee_per_month = fields.Integer(required=True)
    total_hiring_budget = fields.Integer(required=True)
