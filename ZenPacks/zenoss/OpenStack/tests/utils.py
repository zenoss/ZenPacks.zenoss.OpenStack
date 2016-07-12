##############################################################################
#
# Copyright (C) Zenoss, Inc. 2016, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

__all__ = ('convertDictToObjects',)


def convertDictToObjects(results):
    new_result = {}
    for r in results:
        new_result[r] = [DictToObject(l) for l in results[r]]
    return new_result


class DictToObject(dict):
    def __init__(self, *args, **kwargs):
        super(DictToObject, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for key, value in arg.iteritems():
                    self[key] = value

        if kwargs:
            for key, value in kwargs.iteritems():
                self[key] = value

    def __getattr__(self, attr):
        return self.get(attr)

