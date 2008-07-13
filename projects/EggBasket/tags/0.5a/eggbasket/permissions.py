# -*- coding: UTF-8 -*-

__all__ = [
    'has_permission'
]

import logging

import turbogears.config as tgconf
import turbogears.identity as tgid

from eggbasket import model

class has_permission(tgid.Predicate, tgid.IdentityPredicateHelper):
    """Checks if user attached to current identity has given permission.
    
    This extends the standard ``identity.has_permission`` predicate in
    that it allows to define extra groups for anonymous users (named
    "anonymous" per default) and all authenticated users ("authenticated")
    to which additional permissions for these groups of users can be attached.
    
    You can set the names of the extra groups in the configuration with the
    ``identity.anonymous_groups`` resp. ``identity.authenticated_groups``.
    Both settings expect a list of group names. Appropriatly named groups
    must be created in the database, but if they are missing the check will
    still work but always fail for anonymous users.

    """
    
    error_message= "Permission denied: %(permission_name)s"

    def __init__(self, permission_name, error_message=None):
        self.permission_name = permission_name
        if error_message:
            self.error_message = error_message

    def eval_with_object(self, identity, errors=None):
        if identity.anonymous:
            extra_groups = tgconf.get('identity.anonymous_groups',
                [u'anonymous'])
        else:
            extra_groups = tgconf.get('identity.authenticated_groups',
                [u'authenticated'])

        # Turn group names into model.Group objects
        extra_groups = model.Group.query().filter(
            model.Group.c.group_name.in_(extra_groups)).all()
        # Build set of permissions from extra groups
        permissions = set(identity.permissions)
        [permissions.update(p.permission_name for p in group.permissions)
            for group in extra_groups]

        if self.permission_name in permissions:
            return True
        
        self.append_error_message(errors)
        return False
