
.PHONY: tests
tests:
	rm -f piccolo.sqlite
	ENV=test piccolo migrations forward users
	ENV=test pytest 


