###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2011-2019, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

from Products.ZenModel.Device import Device
from Products.ZenRelations.RelSchema import ToManyCont, ToOne
from Products import Zuul
from zenoss.protocols.protobufs.zep_pb2 import (
    STATUS_NEW, STATUS_ACKNOWLEDGED,
    SEVERITY_CRITICAL,
)


class Endpoint(Device):
    meta_type = portal_type = 'OpenStackEndpoint'

    _relations = Device._relations + (
        ('flavors', ToManyCont(ToOne,
            'ZenPacks.zenoss.OpenStack.Flavor.Flavor',
            'endpoint',
            ),
        ),
        ('images', ToManyCont(ToOne,
            'ZenPacks.zenoss.OpenStack.Image.Image',
            'endpoint',
            ),
        ),
        ('servers', ToManyCont(ToOne,
            'ZenPacks.zenoss.OpenStack.Server.Server',
            'endpoint',
            ),
        ),
    )

    def getIconPath(self):
        return '/++resource++openstack/img/openstack.png'

    def getStatus(self, statusclass="/Status/*", **kwargs):
        # This is identical the behavior provided by ZPL- once this zenpack
        # is converted to ZPL, this method can be removed.
        if not self.monitorDevice():
            return None

        zep = Zuul.getFacade("zep", self.dmd)
        try:
            event_filter = zep.createEventFilter(
                tags=[self.getUUID()],
                element_sub_identifier=[""],
                severity=[SEVERITY_CRITICAL],
                status=[STATUS_NEW, STATUS_ACKNOWLEDGED],
                event_class=filter(None, [statusclass]))

            result = zep.getEventSummaries(0, filter=event_filter, limit=0)
        except Exception:
            return None

        return int(result['total'])
