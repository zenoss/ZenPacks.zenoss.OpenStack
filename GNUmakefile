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

PYTHON=python
ZP_DIR=$(PWD)/ZenPacks/zenoss/OpenStack
BIN_DIR=$(ZP_DIR)/bin

default: egg

egg:
	# setup.py will call 'make build' before creating the egg
	python setup.py bdist_egg

build:
	@echo

clean:
	rm -rf build dist *.egg-info
	rm -rf src/*/{build,dist,*.egg-info}
	find . -name '*.pyc' | xargs rm -f
	rm -rf $(BIN_DIR)
	mkdir $(BIN_DIR)

docs:
	pandoc -f mediawiki README.mediawiki -o /tmp/openstack.html
