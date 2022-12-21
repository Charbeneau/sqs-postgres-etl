# Background

This was done for a take home assignment during the interview process of a certain Firm.

The objective was to:

1. Read JSON data containing user login behavior from an AWS SQS Queue made available via [localstack](https://github.com/localstack/localstack);

2. Hide personal identifiable information ("PII") in the `device_id` and `ip` fields such that it would be easy for data analysts to identify duplicate values in those fields; and

3. Write each resulting record to a Postgres database running in Docker. The target table's DDL is:

```sql
-- Creation of user_logins table

CREATE TABLE IF NOT EXISTS user_logins(
    user_id             varchar(128),
    device_type         varchar(32),
    masked_ip           varchar(256),
    masked_device_id    varchar(256),
    locale              varchar(32),
    app_version         integer,
    create_date         date
);
```

# Prerequisites

Here's what you'll need to make it work on your machine.

- make
    - Ubuntu -- `apt-get -y install make`
    - Windows -- `choco install make`
    - Mac -- `brew install make`
- python3 -- [python install guide](https://www.python.org/downloads/)
- pip3 -- `python -m ensurepip --upgrade`
- docker -- [docker install guide](https://docs.docker.com/get-docker/)
- docker-compose -- [docker-compose install guide](https://docs.docker.com/compose/install/)

# Usage

0. Create a Python virtual environment called "my-venv".
```
python3 -m venv ./my-venv
source my-venv/bin/activate
```

1. Set environment variables.
```
export AWS_REGION=us-east-1
export AWS_PROFILE=localstack
export ENDPOINT_URL=http://localhost:4566
export QUEUE_NAME=login-queue
export MAX_MESSAGES=10
export WAIT_TIME=1
export USER=postgres
export PASSWORD=postgres
export HOST=localhost
export PORT=5432
export DATABASE=postgres
```

2. Install requirements.
```
make install
```

3. Install requirements for unit testing.
```
make install-test
```

4. Run unit tests.
```
make test
```

4. Build the Docker containers and start the services.
```
make start
```

5. Make sure you can read an SQS queue.
```
make message
```

6. Confirm that the DB works.
```
make db
```

Type the password given in the PASSWORD environment variable above, and then
```
postgres=# select * from user_logins;
 user_id | device_type | masked_ip | masked_device_id | locale | app_version | create_date 
---------+-------------+-----------+------------------+--------+-------------+-------------
(0 rows)
```

and
```
exit
```

7. Run the application.
```
make run
```

8. Confirm that there's data in the DB.
```
make db
[PASSWORD]
select * from user_logins;
exit
```

With any luck, there should be ninety-nine (99) rows.

9. Stop the services.
```
make stop
```

10. Clean up all things Docker, **including all volumes**, if you want.
```
make clean
```

# Questions from the Firm

**1.  How would you deploy this application in production?**

I've done something similar to this, using an AWS Fargate service.  It worked well, and I'd do that again.  That would require dockerizing the app, which should be straightforward.  I opted not to dockerize the app only so as to avoid any potential frustration with Docker networking.

Alternatively, on AWS, one could do something very similar with Lambda.

**2.  What other components would you want to add to make this production ready?**

In order to make this production ready, I'd invest time in the following areas:

- Testing, using an appropriate application of [these recommendations](https://martinfowler.com/articles/microservice-testing/), could add a lot of value

- Adding a dead letter queue (DLQ) associated with the "login-queue" SQS queue
    - That would affect the following section of main.py
    ```
    except Exception as e:

    print(f"Exception while processing message: {repr(e)}!")

    continue
    ```

- Using a better encryption strategy, like [this](https://cryptography.io/en/latest/fernet/) perhaps

- Rethinking and, hopefully, simplifying all `try...except...` logic

- Batching message reading and writing would speed things up **a lot** (ask me how I know...)

- Using CloudWatch alarms to monitor the queue and DLQ volume

- Possibly using [Application Auto Scaling](https://aws.amazon.com/premiumsupport/knowledge-center/ecs-fargate-service-auto-scaling/) together with CloudWatch alarms to increase the Fargate service's task count, if needed

- Improving the rather crude logging setup

- Logging to CloudWatch with a sensible retention period

**3.  How can this application scale with a growing data set.**

The application could scale by increasing Fargate tasks in the service, either using auto scaling, or manually.  I had good luck with the latter.

**4.  How can PII be recovered later on?**

PII can be recovered by Base64 decoding the relevant fields. Again, I did the simplest thing I could think of here and **do not** regard it as good enough for PROD.


# Commentary

After looking at the data a bit, I decided to assume that the SQS message body had to follow the schema in [utils.py](./app/utils.py).  There's an implicit [contract](https://developer.confluent.io/patterns/event/data-contract/) in all event data, and that one made sense to me.

I chose to make all **changes** to the data explicit in [process_message()](./app/utils.py).  However, Psycopg does its [thing](https://www.psycopg.org/docs/usage.html#query-parameters) with create_date, because it's a new data element.  

When working with data, I tend to think in terms of a directed acyclical graph ("DAG").  Or a Flow, if you like [Prefect](https://docs-v1.prefect.io/core/concepts/flows.html#overview).  As a result, my code tends to be rather DAG or Flow-like.

I looked around for SQS listeners/consumers that others had written, found a few, and decided to borrow heavily from this gentleman's [work](https://perandrestromhaug.com/posts/writing-an-sqs-consumer-in-python/).

I wrote a unit test so that the Firm would see that I know about unit tests. [Hypothesis](https://hypothesis.readthedocs.io/en/latest/), which I've been dying to use for real for real, might be a good tool to use here.

I used [Black](https://github.com/psf/black) for linting, because I hadn't used it before and wanted to.

I tried to follow [this](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings) standard for docstrings.