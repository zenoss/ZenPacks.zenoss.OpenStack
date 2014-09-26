##############################################################################
#
# Copyright (C) Zenoss, Inc. 2014, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


import logging
log = logging.getLogger('zen.migrate')

import Globals
from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.ZenPack import ZenPackMigration


class ChangeDeviceClass(ZenPackMigration):
    """
    ZenPacks.zenoss.OpenStack 1.2.3 moved the device class from /OpenStack
    to /OpenStack/User.
    """

    version = Version(1, 2, 3)

    def migrate(self, pack):
        for device in pack.dmd.Devices.getOrganizer('/OpenStack').devices():
            log.info("Moving device '%s' from /OpenStack to /OpenStack/User" % device.id)
            device.changeDeviceClass('/OpenStack/User')
