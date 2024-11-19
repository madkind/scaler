

Worklog:

2024.11.14 
- [2h] Init backend project. I would challenge you asking for an unreleased version of django, but I suppose you challenge me!
2024.11.18-19
- [~11h] On plane, in flight wifi. Approx half of 22h journey from Indonesia to Italy. Suboptimal working conditions, but not impossible. I do my best to deliver a working backend.


I am striving to demonstrate my skills in a quick manner. Best practices I am not implementing, however I am aware of:
- Slim docker images with multi stage build
- indexed full text search, maybe with vector extension of PG
- consumer driven contract testing ?!
- separate file for dev requirements
- Authentication (employee model could extend AbstractUser)
- Deal with admin ui
- create fixtures that can be loaded into db for demo purposes (I hope you are fine with the integration tests).

- I never wrote unit tests in startup environments, but I can adjust



Unfortunately I do not have the time or the gear to work on the frontend before deadline. 
Actually the exercise made my flight fun and exciting, thank you so much! I had a nice time revisiting django :)


HOW TO RUN:
- "docker-compose up" or "docker compose up"
- run tests
    -  docker compose exec web pytest --no-migrations --create-db  -vv
- run app: (no time)
    - docker compose run web python manage.py migrate
    - docker compose restart web
    -  curl -X GET "http://localhost:8000/api/appointments/?date=2024-11-19"
