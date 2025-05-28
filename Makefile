ALEMBIC_INI=app/db/alembic.ini

.PHONY: migration
migration:
ifndef message
	$(error message is undefined. Use: make migration message="Your message")
endif
	alembic -c $(ALEMBIC_INI) revision --autogenerate -m "$(message)"

.PHONY: migrate
migrate:
	alembic -c $(ALEMBIC_INI) upgrade head

.PHONY: downgrade
downgrade:
ifndef rev
	$(error rev is undefined. Use: make downgrade rev=<revision>)
endif
	alembic -c $(ALEMBIC_INI) downgrade $(rev)
