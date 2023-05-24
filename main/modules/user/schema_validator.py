from marshmallow import Schema, fields


class UpdateProfile(Schema):
    """
    Required schema to update user profile.
    """

    first_name = fields.String(required=False)
    last_name = fields.String(required=False)
    department = fields.String(required=False)
    function = fields.String(required=False)
    role = fields.String(required=False)
    mobile_number = fields.String(required=False)
