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
SRC_DIR=$(PWD)/src
ZP_DIR=$(PWD)/ZenPacks/zenoss/OpenStack
BIN_DIR=$(ZP_DIR)/bin
LIB_DIR=$(ZP_DIR)/lib

default: egg

egg:
	# setup.py will call 'make build' before creating the egg
	python setup.py bdist_egg

build:	
	mkdir -p $(BIN_DIR) $(LIB_DIR)
	cd $(SRC_DIR)/pip-1.4.1 && \
		PYTHONPATH="$(PYTHONPATH):$(LIB_DIR)" $(PYTHON) setup.py install \
			--install-lib="$(LIB_DIR)" --install-scripts="$(BIN_DIR)"
	cd $(SRC_DIR)/prettytable-0.7.2 && \
		PYTHONPATH="$(PYTHONPATH):$(LIB_DIR)" $(PYTHON) setup.py build
	cp -r $(SRC_DIR)/prettytable-0.7.2/build/lib*/prettytable.py $(ZP_DIR)/lib

	rm -rf $(SRC_DIR)/Babel-1.3/build
	cd $(SRC_DIR)/Babel-1.3 && \
		PYTHONPATH="$(PYTHONPATH):$(LIB_DIR)" $(PYTHON) setup.py build
	mkdir -p $(ZP_DIR)/lib/babel
	cp -r $(SRC_DIR)/Babel-1.3/build/lib*/babel/* $(ZP_DIR)/lib/babel

	rm -rf $(SRC_DIR)/requests-2.0.0/build
	cd $(SRC_DIR)/requests-2.0.0 && \
		PYTHONPATH="$(PYTHONPATH):$(LIB_DIR)" $(PYTHON) setup.py build
	mkdir -p $(ZP_DIR)/lib/requests
	cp -r $(SRC_DIR)/requests-2.0.0/build/lib*/requests/* $(ZP_DIR)/lib/requests

	rm -rf $(SRC_DIR)/iso8601-0.1.4/build
	cd $(SRC_DIR)/iso8601-0.1.4 && \
		PYTHONPATH="$(PYTHONPATH):$(LIB_DIR)" $(PYTHON) setup.py build
	mkdir -p $(ZP_DIR)/lib/iso8601
	cp -r $(SRC_DIR)/iso8601-0.1.4/build/lib*/iso8601/* $(ZP_DIR)/lib/iso8601

	rm -rf $(SRC_DIR)/python-novaclient-2.15.0/build
	cd $(SRC_DIR)/simplejson-3.3.1 && \
		PYTHONPATH="$(PYTHONPATH):$(LIB_DIR)" $(PYTHON) setup.py build
	mkdir -p $(ZP_DIR)/lib/simplejson
	cp -r $(SRC_DIR)/simplejson-3.3.1/build/lib*/simplejson/* $(ZP_DIR)/lib*/simplejson

	# convince novaclient not to try to download any dependencies. We have already taken
	# care of them above.
	cp /dev/null $(SRC_DIR)/python-novaclient-2.15.0/requirements.txt
	# Remove pbr requirement
	cp $(SRC_DIR)/python-novaclient-2.15.0-patches/setup.py $(SRC_DIR)/python-novaclient-2.15.0/
	cp $(SRC_DIR)/python-novaclient-2.15.0-patches/__init__.py $(SRC_DIR)/python-novaclient-2.15.0/novaclient/
	rm -rf $(SRC_DIR)/python-novaclient-2.15.0/build
	cd $(SRC_DIR)/python-novaclient-2.15.0 && \
		PYTHONPATH="$(PYTHONPATH):$(LIB_DIR)" $(PYTHON) setup.py build
	mkdir -p $(ZP_DIR)/lib/novaclient
	cp -r $(SRC_DIR)/python-novaclient-2.15.0/build/lib*/novaclient/* $(ZP_DIR)/lib*/novaclient

	# Note: some files were patched, but I did not check in the patched versions.
	# to tell git not to pester you about them, you may want to do the following:
	# git update-index --assume-unchanged src/python-novaclient-2.15.0/novaclient/__init__.py src/python-novaclient-2.15.0/setup.py			

clean:
	rm -rf build dist *.egg-info
	rm -rf src/*/{build,dist,*.egg-info}
	find . -name '*.pyc' | xargs rm -f
	rm -rf $(BIN_DIR) $(LIB_DIR)
