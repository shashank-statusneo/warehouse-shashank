from copy import deepcopy
from datetime import date, datetime


def update_model_object(model, values_obj):
    for k, v in values_obj.items():
        if hasattr(model, k):
            setattr(model, k, v)
    if hasattr(model, "updated_on"):
        setattr(model, "updated_on", datetime.now())
    return model


def remove_unwanted_keys(model, json_object):
    new_json_obj = deepcopy(json_object)
    for k, v in json_object.items():
        if not hasattr(model, k):
            del new_json_obj[k]
    return new_json_obj


def greater_or_equal_to_current_date(input_date):
    today = date.today()
    return input_date >= today

