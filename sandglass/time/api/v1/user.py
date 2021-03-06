import datetime

from colander import DateTime
from colander import String
from pyramid.exceptions import NotFound

from sandglass.time import _
from sandglass.time.api import API
from sandglass.time.filters.search import BySearchFields
from sandglass.time.filters.search import Filter
from sandglass.time.models.activity import Activity
from sandglass.time.models.group import Group
from sandglass.time.models.user import User
from sandglass.time.resource.action import collection_action
from sandglass.time.resource.action import member_action
from sandglass.time.resource.model import ModelResource
from sandglass.time.resource.model import use_schema
from sandglass.time.response import error_response
from sandglass.time.schemas.user import UserListSchema
from sandglass.time.schemas.user import UserSigninSchema
from sandglass.time.schemas.user import UserSignupSchema
from sandglass.time.schemas.user import UserSchema
from sandglass.time.security import Users
from sandglass.time.security import PUBLIC

from .error import APIV1Error

SEARCH_FILTERS = [
    Filter(
        'email',
        String(),
        ops=('eq', 'contains', 'starts', 'ends'),
    ),
    Filter(
        'first_name',
        String(),
        ops=('eq', 'contains', 'starts', 'ends'),
    ),
    Filter(
        'last_name',
        String(),
        ops=('eq', 'contains', 'starts', 'ends'),
    ),
    Filter(
        'token',
        String(),
        ops=('eq', ),
    ),
    Filter(
        'created',
        DateTime(),
        ops=('eq', 'gt', 'gte', 'lt', 'lte'),
    ),
]


class UserResource(ModelResource):
    """
    REST API resource for User model.

    """
    name = 'users'
    model = User
    schema = UserSchema
    list_schema = UserListSchema

    @classmethod
    def get_query_filters(cls):
        filters = super(UserResource, cls).get_query_filters()
        # Allow simple search of users
        return filters + (BySearchFields(User, SEARCH_FILTERS), )

    @use_schema(UserSigninSchema)
    @collection_action(methods='POST', permission=PUBLIC)
    def signin(self):
        """
        Signin (login) a user.

        User `email` and `password` are used to find and validate
        signing process.

        Returns a user.

        """
        data = self.submitted_member_data
        user = User.query().filter_by(email=data['email']).first()
        if (not user) or not user.is_valid_password(data['password']):
            raise APIV1Error('INVALID_SIGNIN')

        return user

    @use_schema(UserSignupSchema)
    @collection_action(methods='POST', permission=PUBLIC)
    def signup(self):
        """
        Create a new user.

        New users are assigned to `time.Users` group.

        Returns the new user.

        """
        # TODO: Validate user by sending a link to the email
        data = self.submitted_member_data
        if User.query().filter_by(email=data['email']).count():
            raise APIV1Error('USER_EMAIL_EXISTS')

        user = User(**data)
        session = User.new_session()
        session.add(user)
        session.flush()

        # By default assign new users to Users group
        query = Group.query(session).filter_by(name=Users)
        group = query.first()
        if group:
            user.groups.append(group)

        return user

    @collection_action(methods='GET')
    def search(self):
        """
        Get a User by email or token.

        Returns a User or raise HTTP 404.

        """
        user = None
        email = self.request.GET.get('email')
        if email:
            user = User.get_by_email(email)
            if user:
                return user

        token = self.request.GET.get('token')
        if token:
            user = User.get_by_token(token)
            if user:
                return user

        raise APIV1Error('USER_NOT_FOUND')

    @member_action(methods='GET')
    def activities(self):
        """
        Get activities for current user.

        By default activities are getted only for current day.
        Different date range can be queried using `from` and `to`
        arguments in the request.

        Returns a List of Activity.

        """
        if not self.is_valid_object:
            raise NotFound()

        try:
            (from_date, to_date) = self.get_filter_from_to()
        except (TypeError, ValueError):
            return error_response(_('Invalid date format'))

        # When no dates are given use current date as default
        if not from_date and not to_date:
            from_date = datetime.date.today()
            to_date = from_date + datetime.timedelta(days=1)

        query = Activity.query()
        query = query.filter(Activity.user_id == self.pk_value)
        if from_date:
            query = query.filter(Activity.start >= from_date)
        if to_date:
            query = query.filter(Activity.start < to_date)

        return query.all()


API.register('v1', UserResource)
