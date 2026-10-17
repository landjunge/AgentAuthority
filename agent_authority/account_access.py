"""Authenticated own Help Center grants; external model identity stays unknown.

The peer URL, bridge credential and service key come only from private operator
configuration. No browser supplied host, scope or subject is accepted.
"""
import http.client
import socket
import json
import secrets
import time
import threading
from dataclasses import replace
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import urlsplit
from agent_authority.browser_contracts import Principal, Scope, Session, Problem
from agent_authority.observations import TOKEN


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class GrantPeer:
    def __init__(self, url, bridge, key):
        self.unix = url if url.startswith('/run/ki-hilfezentrum/') and url.endswith('.sock') else None
        parsed = urlsplit(url)
        if not self.unix and (parsed.scheme != 'http' or parsed.hostname != '127.0.0.1' or parsed.path != '/api/internal/authority-grant' or parsed.query or parsed.fragment or parsed.username):
            raise ValueError('Fixed private loopback peer required')
        if min(len(bridge), len(key)) < 32:
            raise ValueError('Strong private service credentials required')
        self.url, self.bridge, self.key = url, bridge, key

    def __call__(self, operation, credential):
        body = json.dumps({'operation': operation, 'credential': credential}).encode()
        headers = {'Content-Type': 'application/json', 'X-Bridge-Key': self.bridge, 'X-KH-AA-Key': self.key, 'X-Bot-Source': 'aa-own-service'}
        if self.unix:
            connection = http.client.HTTPConnection('localhost', timeout=3)
            connection.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            connection.sock.settimeout(3)
            try:
                connection.sock.connect(self.unix)
                connection.request('POST', '/api/internal/authority-grant', body, headers)
                response = connection.getresponse()
                raw = response.read(16001)
                if response.status != 200 or len(raw) > 16000:
                    raise ValueError('Peer refused grant')
                return json.loads(raw)
            except Exception:
                raise Problem(401, 'HELP_ACCOUNT_UNAVAILABLE_OR_REVOKED') from None
            finally:
                connection.close()
        req = Request(self.url, data=json.dumps({'operation': operation, 'credential': credential}).encode(),
                      headers={'Content-Type': 'application/json', 'X-Bridge-Key': self.bridge,
                               'X-KH-AA-Key': self.key, 'X-Bot-Source': 'aa-own-service'})
        try:
            with build_opener(NoRedirect).open(req, timeout=3) as response:
                raw = response.read(16001)
                if len(raw) > 16000:
                    raise ValueError('Peer response too large')
                return json.loads(raw)
        except Exception:
            raise Problem(401, 'HELP_ACCOUNT_UNAVAILABLE_OR_REVOKED') from None


class AccountAccess:
    contract_version = 1

    def __init__(self, local, peer):
        self.local, self.peer = local, peer
        self.sessions = {}
        self.lock = threading.RLock()

    def checked(self, data):
        try:
            assert data['issuer'] == 'ki-hilfezentrum-account-v1'
            assert data['audience'] == 'agent-authority-browser-v1'
            assert data['agent_identity_verified'] is False
            assert data['external_authority'] == 'unknown'
            assert time.time() < data['expires_at'] <= time.time()+301
            assert data['adapters'] == ['report']
            assert all(isinstance(data[k], str) and TOKEN.fullmatch(data[k]) for k in ('subject', 'sourceId', 'jobId'))
            return Principal(data['subject'], (Scope(data['sourceId'], data['jobId'], ('report',)),))
        except (KeyError, TypeError, AssertionError):
            raise Problem(401, 'INVALID_HELP_ACCOUNT_GRANT') from None

    def exchange(self, body):
        if not isinstance(body, dict) or set(body) != {'ticket'} or not isinstance(body['ticket'], str) or len(body['ticket']) != 43:
            raise Problem(422, 'INVALID_HELP_ACCOUNT_TICKET')
        with self.lock:
            self.sessions = {k:v for k,v in self.sessions.items() if v[2] > time.time()}
            if len(self.sessions) >= 128:
                raise Problem(429, 'SESSION_LIMIT')
            data = self.peer('redeem', body['ticket'])
            principal = self.checked(data)
            token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
            self.sessions[token] = (data['credential'], csrf, data['expires_at'], principal.subject)
            return Session(token, replace(principal, session_id=token), csrf)

    def authenticate(self, authorization):
        return self.local.authenticate(authorization)

    def refresh(self, principal):
        with self.lock:
            row = self.sessions.get(principal.session_id)
            if row is None:
                return self.local.refresh(principal)
            if row[2] <= time.time() or row[3] != principal.subject:
                raise Problem(401, 'AUTH_REQUIRED')
            current = self.checked(self.peer('inspect', row[0]))
            if current.subject != row[3]:
                raise Problem(401, 'AUTH_REQUIRED')
            return replace(current, session_id=principal.session_id)

    def resolve(self, cookie):
        tokens = [v[11:] for v in cookie.split('; ') if v.startswith('aa_session=')]
        if len(tokens) != 1:
            raise Problem(401, 'AUTH_REQUIRED')
        with self.lock:
            row = self.sessions.get(tokens[0])
            if row is None:
                return self.local.resolve(cookie)
            principal = self.refresh(Principal(row[3], (), tokens[0]))
            return Session(tokens[0], principal, row[1])

    def authorize(self, principal, source, job, adapter):
        current = self.refresh(principal)
        if not any(s.source_id == source and s.job_id == job and adapter in s.adapters for s in current.scopes):
            raise Problem(403, 'SCOPE_FORBIDDEN')
        return current

    def identity_metadata(self, principal):
        principal = self.refresh(principal)
        own = principal.session_id in self.sessions
        return {'syntheticAccount': not own,
                'accessIdentity': 'helpcenter-account' if own else 'synthetic-private-account',
                'agentIdentityVerified': False}

    def context(self, principal):
        principal = self.refresh(principal)
        row = self.sessions.get(principal.session_id)
        if row is None:
            raise Problem(403, 'HELP_ACCOUNT_REQUIRED')
        return self.peer('inspect', row[0])['context']

    def revoke(self, token):
        with self.lock:
            row = self.sessions.pop(token, None)
            if row:
                self.peer('revoke', row[0])
            else:
                self.local.revoke(token)

    def close(self):
        with self.lock:
            self.sessions.clear()
            self.local.close()
