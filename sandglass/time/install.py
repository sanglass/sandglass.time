# pylint: disable=C0103

from fixture import DataSet
from fixture import SQLAlchemyFixture
from fixture.style import NamedDataStyle

from sandglass.time import _
from sandglass.time import security
from sandglass.time.models import META
from sandglass.time.models import MODEL_REGISTRY
from sandglass.time.models import scan_models


def model_permission_data_class_factory(cls_name):
    """
    Create DataSet class with all registered models permissions.

    Returns a DataSet class.

    """
    if not MODEL_REGISTRY:
        scan_models('sandglass.time.models')

    current_id = 1
    attrs = {}
    # Keep track of parsed models to avoid generating data
    # for a model registered with more than one name.
    # This happens, for example, during unittest because
    # fixtures "binds" dataset and model by registering
    # models under different names.
    parsed_model_list = []
    # Iterate all registered models
    for name, model in MODEL_REGISTRY.iteritems():
        if name.startswith('_') or model in parsed_model_list:
            continue
        else:
            parsed_model_list.append(model)

        # Get permissions for current model and create classes
        # for each permission. Each class will be assigned to
        # the new "DataSet" class being created.
        for permission in model.get_full_permission_list():
            inner_cls_name = permission
            fields = {
                'id': current_id,
                'name': str(permission),
                # TODO: Add description for permissions
                'description': u'',
            }
            attrs[inner_cls_name] = type(inner_cls_name, (), fields)
            current_id += 1

    return type(cls_name, (DataSet, ), attrs)


# Dataset with all model permissions.
PermissionData = model_permission_data_class_factory('PermissionData')


def permission_list(model_name, flags):
    """
    Get a list of permissions for a model.

    Returns a List of permissions.

    """
    prefix = 'time_{}_'.format(model_name.lower())
    permissions = []
    for flag in flags.lower():
        if flag == 'c':
            suffix = 'create'
        elif flag == 'r':
            suffix = 'read'
        elif flag == 'u':
            suffix = 'update'
        elif flag == 'd':
            suffix = 'delete'
        elif flag == 'a':
            suffix = 'action'
        else:
            continue

        permission = getattr(PermissionData, prefix + suffix, None)
        if permission and (permission not in permissions):
            permissions.append(permission)

    return permissions


USERS_GROUP_PERMISSIONS = (
    permission_list('tag', 'cruda') +
    permission_list('group', 'r') +
    permission_list('permission', 'r') +
    permission_list('project', 'cruda') +
    permission_list('task', 'cruda') +
    permission_list('client', 'ra') +
    permission_list('user', 'ra') +
    permission_list('activity', 'cruda')
)


MANAGERS_GROUP_PERMISSIONS = (
    USERS_GROUP_PERMISSIONS +
    permission_list('group', 'cuda') +
    permission_list('permission', 'ua') +
    permission_list('client', 'cud') +
    permission_list('user', 'cud') +
    # TODO: Implement a better way of getting permission strings
    [PermissionData.time_project_set_is_public]
)


class GroupData(DataSet):
    """
    Dataset with Group data.

    """
    class Admins:
        name = security.Administrators
        id = 1
        description = _(u"Administrators")

    class Users:
        name = security.Users
        id = 2
        description = _(u"Users")
        permissions = USERS_GROUP_PERMISSIONS

    class Managers:
        name = security.Managers
        id = 3
        description = _(u"Managers")
        permissions = MANAGERS_GROUP_PERMISSIONS


# Datasets to be inserted in database during install
DEFAULT_DATASETS = (
    GroupData,
    PermissionData,
)


def database_insert_default_data():
    """
    Insert initial database data.

    This must be called only once to setup initial database recods.

    Returns a FixtureData.

    """
    fixture = SQLAlchemyFixture(
        env=MODEL_REGISTRY,
        engine=META.bind,
        style=NamedDataStyle())
    data = fixture.data(*DEFAULT_DATASETS)
    data.setup()
    return data
