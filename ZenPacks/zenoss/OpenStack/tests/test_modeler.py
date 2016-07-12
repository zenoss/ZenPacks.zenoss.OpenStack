##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import json
import os

from zope.event import notify

from Products.DataCollector.ApplyDataMap import ApplyDataMap
from Products.Five import zcml
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.Zuul.catalog.events import IndexingEvent

import ZenPacks.zenoss.OpenStack
from ZenPacks.zenoss.OpenStack.modeler.plugins.zenoss.OpenStack \
    import OpenStack as OpenStackModeler
from ZenPacks.zenoss.OpenStack.tests.utils import convertDictToObjects


class TestModel(BaseTestCase):

    disableLogging = False

    def afterSetUp(self):
        super(TestModel, self).afterSetUp()

        dc = self.dmd.Devices.createOrganizer('/Devices/OpenStack')

        dc.setZenProperty('zPythonClass', 'ZenPacks.zenoss.OpenStack.Endpoint')
        dc.setZenProperty('zOpenStackAuthUrl', '')
        dc.setZenProperty('zOpenstackComputeApiVersion', [])
        dc.setZenProperty('zOpenStackProjectId', [])
        dc.setZenProperty('zOpenStackInsecure', [])
        dc.setZenProperty('zOpenStackRegionName', 'RegionOne')

        self.d = dc.createInstance('zenoss.OpenStack.testDevice')
        self.d.setPerformanceMonitor('localhost')
        self.d.index_object()

        notify(IndexingEvent(self.d))
        self.applyDataMap = ApplyDataMap()._applyDataMap

        zcml.load_config('configure.zcml', ZenPacks.zenoss.OpenStack)

        self._loadModelData()

    def _loadModelData(self):
        if hasattr(self, '_modeled'):
            return

        modeler = OpenStackModeler()
        modelDataFile = os.path.join(os.path.dirname(__file__), 'data/modeldata.json')
        with open(modelDataFile) as json_file:
            results = json.load(json_file)

        results = convertDictToObjects(results)

        for data_map in modeler.process(self.d, results, None):
            self.applyDataMap(self.d, data_map)
        self._modeled = True

    def testFlavor(self):
        self.assertTrue(self._modeled)

        flavors = self.d.getDeviceComponents(type='OpenStackFlavor')
        self.assertEquals(len(flavors), 6)
        flavornames = [f.name() for f in flavors]
        flavorids = [f.id for f in flavors]

        self.assertTrue('m1.tiny' in flavornames)
        self.assertTrue('m1.small' in flavornames)
        self.assertTrue('m1.medium' in flavornames)
        self.assertTrue('m1.large' in flavornames)
        self.assertTrue('m1.xlarge' in flavornames)
        self.assertTrue('flavor1' in flavorids)
        self.assertTrue('flavor2' in flavorids)
        self.assertTrue('flavor3' in flavorids)
        self.assertTrue('flavor4' in flavorids)
        self.assertTrue('flavor5' in flavorids)

    def testImage(self):
        self.assertTrue(self._modeled)

        images = self.d.getDeviceComponents(type='OpenStackImage')
        self.assertEquals(len(images), 2)
        self.assertEquals('imageb5ac0c5f-bf91-4ab6-bcaa-d895a8df90bb', images[0].id)
        self.assertEquals('cirros', images[0].name())

    def testServers(self):
        self.assertTrue(self._modeled)

        images = self.d.getDeviceComponents(type='OpenStackServer')
        self.assertEquals(len(images), 2)
        self.assertEquals('server0aa87c33-aa73-4c02-976b-321f5e2df205', images[0].id)
        self.assertEquals('tiny1', images[0].name())
