## Flag for custom config file
CONFIGFILE := ''

all: build

deb:
	dpkg-buildpackage -rfakeroot -tc -sa -us -uc -I".directory" -I".git" -I"buildpackage.sh" -I".crowdin.key"

bower:
	ajenti-dev-multitool --bower install

build:
	ajenti-dev-multitool --msgfmt
	ajenti-dev-multitool --build

run:
	/usr/local/bin/ajenti-panel -v --autologin --stock-plugins --plugins usr/lib/linuxmuster-webui/plugins $(CONFIGFILE)

rundev:
	/usr/local/bin/ajenti-panel -v --autologin --stock-plugins --plugins usr/lib/linuxmuster-webui/plugins --dev $(CONFIGFILE)

rundevlogin:
	/usr/local/bin/ajenti-panel -v --stock-plugins --plugins usr/lib/linuxmuster-webui/plugins --dev $(CONFIGFILE)

runprod:
	/usr/local/bin/ajenti-panel --stock-plugins --plugins usr/lib/linuxmuster-webui/plugins $(CONFIGFILE)

push-crowdin:
	ajenti-dev-multitool --xgettext
	ajenti-dev-multitool --push-crowdin

pull-crowdin:
	ajenti-dev-multitool --pull-crowdin
	ajenti-dev-multitool --msgfmt

doc:
	sphinx-build -b html -d docs/doctrees  docs_src docs

##################################################
## Will be later activated
# test:
# 	cd e2e && ./run
#
# webdriver:
# 	cd e2e && node_modules/protractor/bin/webdriver-manager start
#
# webdriver-update:
# 	cd e2e && node_modules/protractor/bin/webdriver-manager update
#
# karma:
# 	cd tests-karma && node_modules/karma/bin/karma start karma.conf.coffee --no-single-run --auto-watch
#
# nose:
# 	cd tests-nose && nosetests tests/
