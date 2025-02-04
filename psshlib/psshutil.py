# Copyright (c) 2009-2012, Andrew McNabb
# Copyright (c) 2003-2008, Brent N. Chun

import fcntl
import fnmatch
import re
import sys
import os

from psshlib.groupsets import GroupSet

HOST_FORMAT = 'Host format is [user@]host[:port] [user]'
GROUP_CONF = '~/.config/pssh/hostgroups'
GROUP_CONF_ABS = os.path.expanduser(GROUP_CONF)


def read_host_groups(groups, default_user=None, default_port=None):
    """Reads given host groups and returns list of (host, port, user) triples."""
    grpset = GroupSet(GROUP_CONF_ABS)
    grps = [grpset[g] for g in groups]
    grps = [x for x in set([i for o in grps for i in o])]
    grps.sort()
    return [parse_host_entry(x, default_user, default_port) for x in grps]


def read_host_files(paths, host_glob, default_user=None, default_port=None):
    """Reads the given host files.

    Returns a list of (host, port, user) triples.
    """
    hosts = []
    if paths:
        for path in paths:
            hosts.extend(read_host_file(path, host_glob, default_user=default_user))
    return hosts


def read_host_file(path, host_glob, default_user=None, default_port=None):
    """Reads the given host file.

    Lines are of the form: host[:port] [login].
    Returns a list of (host, port, user) triples.
    """
    lines = []
    f = open(path)
    for line in f:
        lines.append(line.strip())
    f.close()

    hosts = []
    for line in lines:
        # remove trailing comments
        line = re.sub('#.*', '', line)
        line = line.strip()
        # skip blank lines (or lines with only comments)
        if not line:
            continue
        host, port, user = parse_host_entry(line, default_user, default_port)
        if host and (not host_glob or fnmatch.fnmatch(host, host_glob)):
            hosts.append((host, port, user))
    return hosts


# TODO: deprecate the second host field and standardize on the
# [user@]host[:port] format.
def parse_host_entry(line, default_user, default_port):
    """Parses a single host entry.

    This may take either the of the form [user@]host[:port] or
    host[:port][ user].

    Returns a (host, port, user) triple.
    """
    fields = line.split()
    if len(fields) > 2:
        sys.stderr.write('Bad line: "%s". Format should be'
                         ' [user@]host[:port] [user]\n' % line)
        return None, None, None
    host_field = fields[0]
    host, port, user = parse_host(host_field, default_port=default_port)
    if len(fields) == 2:
        if user is None:
            user = fields[1]
        else:
            sys.stderr.write('User specified twice in line: "%s"\n' % line)
            return None, None, None
    if user is None:
        user = default_user
    return host, port, user


def parse_host_string(host_string, default_user=None, default_port=None):
    """Parses a whitespace-delimited string of "[user@]host[:port]" entries.

    Returns a list of (host, port, user) triples.
    """
    hosts = []
    entries = host_string.split()
    for entry in entries:
        hosts.append(parse_host(entry, default_user, default_port))
    return hosts


def parse_host(host, default_user=None, default_port=None):
    """Parses host entries of the form "[user@]host[:port]".

    Returns a (host, port, user) triple.
    """
    user = default_user
    port = default_port
    if '@' in host:
        user, host = host.split('@', 1)
    if ':' in host:
        host, port = host.rsplit(':', 1)
    return (host, port, user)


def set_cloexec(filelike):
    """Sets the underlying filedescriptor to automatically close on exec.

    If set_cloexec is called for all open files, then subprocess.Popen does
    not require the close_fds option.
    """
    fcntl.fcntl(filelike.fileno(), fcntl.FD_CLOEXEC, 1)
