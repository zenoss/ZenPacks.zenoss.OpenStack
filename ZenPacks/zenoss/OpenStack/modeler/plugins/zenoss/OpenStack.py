###########################################################################
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
log = logging.getLogger('zen.OpenStack')

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId

from ZenPacks.zenoss.OpenStack.util import addLocalLibPath
addLocalLibPath()

from twisted.internet.defer import inlineCallbacks, returnValue

from ZenPacks.zenoss.OpenStack.apiclients.session import SessionManager
from ZenPacks.zenoss.OpenStack.apiclients.txapiclient import NovaClient


class OpenStack(PythonPlugin):
    deviceProperties = PythonPlugin.deviceProperties + (
        'zCommandUsername',
        'zCommandPassword',
        'zOpenStackProjectId',
        'zOpenStackAuthUrl',
        'zOpenStackInsecure',
        'zOpenStackRegionName',
        'zOpenstackComputeApiVersion'
    )

    @inlineCallbacks
    def collect(self, device, unused):
        region_name = None
        if device.zOpenStackRegionName:
            region_name = device.zOpenStackRegionName

        if not device.zCommandUsername or not device.zCommandPassword:
            log.error("Password/Username should be set to proper values. Check your Openstack credentials.")
            returnValue({})

        if not device.zOpenStackAuthUrl or not device.zOpenStackProjectId or not device.zOpenStackRegionName:
            log.error("Openstack credentials should be set to proper values. Check your OpenStackAuthUrl, OpenStackProjectId and OpenStackRegionName")
            returnValue({})

        sm = SessionManager(
            device.zCommandUsername,
            device.zCommandPassword,
            device.zOpenStackAuthUrl,
            device.zOpenStackProjectId,
            region_name)
        nova = NovaClient(session_manager=sm)

        results = {}

        log.info('Requesting flavors')
        results['flavors'] = yield nova.flavors(detailed=True, is_public=None)
        results['flavors'] = results['flavors'].get('flavors', [])

        log.info('Requesting images')
        results['images'] = yield nova.images(limit=0)
        results['images'] = results['images'].get('images', [])

        log.info('Requesting servers')
        results['servers'] = yield nova.servers(detailed=True)
        results['servers'] = results['servers'].get('servers', [])

        returnValue(results)

    def process(self, devices, results, unused):
        flavors = []

        for flavor in results['flavors']:
            flavors.append(ObjectMap(data=dict(
                id=prepId('flavor{0}'.format(flavor['id'])),
                title=flavor.get('name', flavor['id']),  # 256 server
                flavorId=flavor['id'],  # performance1-1
                flavorRAM=flavor.get('ram', 0) * 1024 * 1024,  # 256
                flavorDisk=flavor.get('disk', 0) * 1024 * 1024 * 1024,  # 10
            )))

        flavorsMap = RelationshipMap(
            relname='flavors',
            modname='ZenPacks.zenoss.OpenStack.Flavor',
            objmaps=flavors)

        images = []
        for image in results['images']:
            images.append(ObjectMap(data=dict(
                id=prepId('image{0}'.format(image['id'])),
                title=image.get('name', image['id']),  # Red Hat Enterprise Linux 5.5
                imageId=image['id'],  # 346eeba5-a122-42f1-94e7-06cb3c53f690
                imageStatus=image.get('status'),  # ACTIVE
                imageCreated=image.get('created', ''),  # 2010-09-17T07:19:20-05:00
                imageUpdated=image.get('updated', ''),  # 2010-09-17T07:19:20-05:00
            )))

        imagesMap = RelationshipMap(
            relname='images',
            modname='ZenPacks.zenoss.OpenStack.Image',
            objmaps=images)

        servers = []
        for server in results['servers']:
            # Backup support is optional. Guard against it not existing.
            backup_schedule_enabled = server.get('backup_schedule',
                                                 {}).get('enabled', False)
            backup_schedule_daily = server.get('backup_schedule',
                                               {}).get('daily', 'DISABLED')
            backup_schedule_weekly = server.get('backup_schedule',
                                                {}).get('weekly', 'DISABLED')

            # Get and classify IP addresses into public and private: (fixed/floating)
            public_ips = set()
            private_ips = set()

            access_ipv4 = server.get('accessIPv4')
            if access_ipv4:
                public_ips.add(access_ipv4)

            access_ipv6 = server.get('accessIPv6')
            if access_ipv6:
                public_ips.add(access_ipv6)

            address_group = server.get('addresses')
            if address_group:
                for network_name, net_addresses in address_group.items():
                    for address in net_addresses:
                        if address.get('OS-EXT-IPS:type') == 'fixed':
                            private_ips.add(address.get('addr'))
                        elif address.get('OS-EXT-IPS:type') == 'floating':
                            public_ips.add(address.get('addr'))
                        else:
                            log.info("Address type not found for %s", address.get('addr'))
                            log.info("Adding %s to private_ips", address.get('addr'))
                            private_ips.add(address.get('addr'))

            # Flavor and Image IDs could be specified two different ways.
            flavor_id = server.get('flavorId', None) or \
                server.get('flavor', {}).get('id', None)

            server_dict = dict(
                id=prepId('server{0}'.format(server['id'])),
                title=server.get('name', server['id']),  # cloudserver01
                serverId=server['id'],  # 847424
                serverStatus=server.get('status', ''),  # ACTIVE
                serverBackupEnabled=backup_schedule_enabled,  # False
                serverBackupDaily=backup_schedule_daily,  # DISABLED
                serverBackupWeekly=backup_schedule_weekly,  # DISABLED
                publicIps=list(public_ips),  # 50.57.74.222
                privateIps=list(private_ips),  # 10.182.13.13
                setFlavorId=flavor_id,  # performance1-1

                # a84303c0021aa53c7e749cbbbfac265f
                hostId=server.get('hostId'),
            )

            # Some Instances are created from pre-existing volumes
            # This implies no image exists.
            image_id = None
            if 'imageId' in server:
                image_id = server['imageId']
            elif 'image' in server \
                    and isinstance(server['image'], dict) \
                    and 'id' in server['image']:
                image_id = server['image']['id']

            if image_id:
                server_dict['setImageId'] = prepId('image{0}'.format(image_id))

            servers.append(ObjectMap(data=server_dict))

        serversMap = RelationshipMap(
            relname='servers',
            modname='ZenPacks.zenoss.OpenStack.Server',
            objmaps=servers)

        return(flavorsMap, imagesMap, serversMap)
