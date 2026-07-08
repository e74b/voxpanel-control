
.PHONY: tests
tests:
	ENV=test piccolo migrations forward users
	ENV=test pytest && rm ./piccolo.sqlite


