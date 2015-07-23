##########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import logging
log = logging.getLogger('zen.OpenStackFacade')

import json
import os.path
from urlparse import urlparse
import subprocess

from zope.event import notify
from zope.interface import implements
from ZODB.transact import transact

from Products.Zuul.catalog.events import IndexingEvent
from Products.Zuul.facades import ZuulFacade
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.OpenStack.interfaces import IOpenStackFacade


OPENSTACK_DEVICE_PATH = "/Devices/OpenStack/User"


def zenpack_path(path):
    return os.path.join(os.path.dirname(__file__), path)

_helper = zenpack_path('openstack_helper.py')


class KeystoneError(Exception):
    pass


def _runcommand(cmd):
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    if p.returncode == 0:
        return json.loads(stdout)
    else:
        try:
            message = json.loads(stdout)['error']
        except Exception:
            message = stderr

        log.exception(subprocess.CalledProcessError(p.returncode, cmd=cmd, output=message))
        raise KeystoneError(message)


class OpenStackFacade(ZuulFacade):
    implements(IOpenStackFacade)

    def addOpenStack(self, device_name, username, api_key, project_id, auth_url,
                     region_name=None, collector='localhost'):
        """Add a new OpenStack endpoint to the system."""
        parsed_url = urlparse(auth_url.strip())

        if parsed_url.scheme == "" or parsed_url.hostname is None:
            return False, _t("'%s' is not a valid URL." % auth_url)

        # Verify that this device does not already exist.
        deviceRoot = self._dmd.getDmdRoot("Devices")
        device = deviceRoot.findDeviceByIdExact(device_name)
        if device:
            return False, _t("A device named %s already exists." % device_name)

        zProperties = {
            'zCommandUsername': username,
            'zCommandPassword': api_key,
            'zOpenStackProjectId': project_id,
            'zOpenStackAuthUrl': auth_url,
            'zOpenstackComputeApiVersion': 2,
            'zOpenStackRegionName': region_name or '',
            }

        @transact
        def create_device():
            dc = self._dmd.Devices.getOrganizer(OPENSTACK_DEVICE_PATH)

            device = dc.createInstance(device_name)
            device.setPerformanceMonitor(collector)

            device.username = username
            device.password = api_key

            for prop, val in zProperties.items():
                device.setZenProperty(prop, val)

            device.index_object()
            notify(IndexingEvent(device))

        # This must be committed before the following model can be
        # scheduled.
        create_device()

        # Schedule a modeling job for the new device.
        device = deviceRoot.findDeviceByIdExact(device_name)
        device.collectDevice(setlog=False, background=True)

        return True, 'Device addition scheduled'

    def getRegions(self, username, api_key, project_id, auth_url):
        """Get a list of available regions, given a keystone endpoint and credentials."""

        cmd = [_helper, "getRegions"]
        cmd.append("--username=%s" % username)
        cmd.append("--api_key=%s" % api_key)
        cmd.append("--project_id=%s" % project_id)
        cmd.append("--auth_url=%s" % auth_url)

        return _runcommand(cmd)
