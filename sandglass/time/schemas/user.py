from colander import Email
from colander import Length
from colander import SchemaNode
from colander import String
from colander import drop
from colander import SequenceSchema

from sandglass.time.schemas import BaseModelSchema
from sandglass.time.schemas import Dictionary


class UserSchema(BaseModelSchema):
    """
    Schema definition for user model.

    """
    email = SchemaNode(
        String(),
        validator=Email())
    first_name = SchemaNode(
        String(),
        validator=Length(max=60))
    last_name = SchemaNode(
        String(),
        validator=Length(max=80))
    password = SchemaNode(
        String(),
        validator=Length(max=255),
        missing=drop)
    data = SchemaNode(
        Dictionary(),
        missing=drop)


class UserListSchema(SequenceSchema):
    user = UserSchema()


class UserSignupSchema(UserSchema):
    """
    Schema definition for user signup.

    """
    password = SchemaNode(
        String(),
        validator=Length(max=30))


class UserSigninSchema(BaseModelSchema):
    """
    Schema definition for user logins.

    """
    email = SchemaNode(
        String(),
        validator=Email())
    password = SchemaNode(
        String(),
        validator=Length(max=30))
