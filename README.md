# acme

Acme Workflow test knowledge

## Commands

### Run project

**Run project**

`docker-compose up -d`

**Create django admin superuser**

`docker-compose run --rm django python manage.py createsuperuser`

**Login into django admin**

http://localhost:8000/admin/

**Create workflow user**

http://localhost:8000/admin/workflow/user/

with the following data `user_id=105398891` and `pin=2090`

**Create account**

http://localhost:8000/admin/workflow/account/add/

with the following data `user_id=105398891` and `balance=0`

**Upload workflow**

Use the postman collection `./postman/ACME.postman_collection.json` and upload the workflow file `./postman/workflow_example.json`

**See results**

http://localhost:8000/admin/workflow/upload/

### Run tests

`docker-compose run --rm django python manage.py test --noinput`

## Resources

- Django with Docker boilerplate https://github.com/pydanny/cookiecutter-django