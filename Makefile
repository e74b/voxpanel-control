
.PHONY: tests
tests:
	rm -f piccolo.sqlite
	ENV=test piccolo migrations forward users
	ENV=test piccolo migrations forward control
	ENV=test pytest 


