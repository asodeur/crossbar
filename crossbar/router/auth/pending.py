#####################################################################################
#
#  Copyright (C) Tavendo GmbH
#
#  Unless a separate license agreement exists between you and Tavendo GmbH (e.g. you
#  have purchased a commercial license), the license terms below apply.
#
#  Should you enter into a separate license agreement after having received a copy of
#  this software, then the terms of such license agreement replace the terms below at
#  the time at which such license agreement becomes effective.
#
#  In case a separate license agreement ends, and such agreement ends without being
#  replaced by another separate license agreement, the license terms below apply
#  from the time at which said agreement ends.
#
#  LICENSE TERMS
#
#  This program is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License, version 3, as published by the
#  Free Software Foundation. This program is distributed in the hope that it will be
#  useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  See the GNU Affero General Public License Version 3 for more details.
#
#  You should have received a copy of the GNU Affero General Public license along
#  with this program. If not, see <http://www.gnu.org/licenses/agpl-3.0.en.html>.
#
#####################################################################################

from __future__ import absolute_import

from autobahn.wamp import types
from autobahn.wamp.exception import ApplicationError

__all__ = ('PendingAuth',)


class PendingAuth:

    """
    Base class for pending WAMP authentications.

    After creating a pending authentication first call ``open()`` and
    then ``verify()`` (each should be called exactly once, and in this order).
    """

    AUTHMETHOD = u'abstract'

    def __init__(self, session, config):
        """

        :param session: The authenticating session.
        :type session: obj
        :param config: Authentication configuration to apply for the pending auth.
        :type config: dict
        """
        # Details about the authenticating session
        self._session_details = {
            'transport': session._transport._transport_info,
            'session': session._pending_session_id,
        }

        # The router factory we are working for
        self._router_factory = session._router_factory

        # WAMP-Ticket configuration to apply for the pending auth
        self._config = config

        # The authentication ID of the authenticating principal.
        self._authid = None

        # The role under which the principal will be authenticated when
        # the authentication succeeds.
        self._authrole = None

        # Optional authentication provider (URI of procedure to call).
        self._authprovider = None

        # The authentication method
        self._authmethod = self.AUTHMETHOD

        # The URI of the authenticator procedure to call (filled only in dynamic mode).
        self._authenticator = None

        # The session over which to issue the call to the authenticator (filled only in dynamic mode).
        self._authenticator_session = None

    def _assign_principal(self, principal):
        # allow to override realm request, redirect realm or set default realm
        if u'realm' in principal:
            self._realm = principal['realm']

        if not self._realm:
            return types.Deny(ApplicationError.NO_SUCH_REALM, message=u'no realm assigned')

        # check if effective realm exists on router
        if self._realm not in self._router_factory:
            return types.Deny(ApplicationError.NO_SUCH_REALM, message=u'no realm "{}" exists on this router'.format(self._realm))

        # effective authrole
        if u'role' in principal:
            self._authrole = principal[u'role']
        elif u'default-role' in self._config:
            self._authrole = self._config[u'default-role']
        else:
            return types.Deny(ApplicationError.NO_SUCH_ROLE, message=u'no authrole assigned')

        # check if role exists on realm
        if not self._router_factory[self._realm].has_role(self._authrole):
            return types.Deny(ApplicationError.NO_SUCH_ROLE, message=u'realm "{}" has no role "{}"'.format(self._realm, self._authrole))

        # allow overriding effectively assigned authid
        if u'authid' in principal:
            self._authid = principal[u'authid']

        if not self._authid:
            return types.Deny(ApplicationError.NO_SUCH_PRINCIPAL, message=u'no authid assigned')

    def _init_dynamic_authenticator(self):
        self._authenticator = self._config['authenticator']

        authenticator_realm = None
        if u'authenticator-realm' in self._config:
            authenticator_realm = self._config[u'authenticator-realm']
            if authenticator_realm not in self._router_factory:
                return types.Deny(ApplicationError.NO_SUCH_REALM, message=u"explicit realm <{}> configured for dynamic authenticator does not exist".format(authenticator_realm))
        else:
            if not self._realm:
                return types.Deny(ApplicationError.NO_SUCH_REALM, message=u"client did not specify a realm to join (and no explicit realm was configured for dynamic authenticator)")
            authenticator_realm = self._realm

        self._authenticator_session = self._router_factory.get(authenticator_realm)._realm.session

    def _marshal_dynamic_authenticator_error(self, err):
        error = ApplicationError.AUTHENTICATION_FAILED
        message = u'dynamic authenticator failed: {}'.format(err.value)
        return types.Deny(error, message)

    def hello(self, realm, details):
        """
        When a HELLO message is received, this gets called to open the pending authentication.

        :param realm: The realm to client wishes to join (if the client did announance a realm).
        :type realm: unicode or None
        :param details: The details of the client provided for HELLO.
        :type details: dict
        """
        raise Exception("not implemented")

    def authenticate(self, signature):
        """
        The WAMP client has answered with a WAMP AUTHENTICATE message. Verify the message and
        return `types.Accept` or `types.Deny`.
        """
        raise Exception("not implemented")
