# Mirumon
Mirumon is a simple hardware monitroing service. 
The goal of this project is to provide a simple user-friendly API 
to monitor your devices remotely.

It is based on the [Agent architecture](https://people.ucalgary.ca/~far/Lectures/SENG697/PDF/tutorials/2002/Agent-Based_System_Architecture_and_Organization.pdf). 
An [Device Agent](https://github.com/mirumon/mirumon-desktop-client) is installed 
on the PC, and is connected to the server via a websocket.

Server provides an open REST API to interact with its components. 
As of now, the only officially supported client is the for [Android](https://github.com/mirumon/mirumon-android) phones and tablets.

Implemented features:
- User registration and authorization
- Device registration and authorization
- Providing the device connection status (online/offline)
- Providing the information about the system (OS, users, etc.)
- Providing a list of all installed software
- Providing information about device's hardware
- Remote shell command executing and shutting off the device

In development:
- User permission groups
- Periodical synchronisation of the device
- Websocket client API with push notifications
- Active Directory authorization
- Powering up the device
## Development

### Prepare environment and infrastucture

To start working on project install dependencies
```bash
  pip install poetry
  poetry install
```

Create env file from template
```bash
  cp .env.template .env
```

Run databases and broker containers
```bash
  docker-compose up -d postgres rabbitmq redis
```

Up migrations
```bash
  alembic upgrade head
```

### Create first user and run server

Create first superuser
```bash
  ./scripts/create_superuser.py admin pass
```

Run dev server with all necessary configs
```bash
  ./scripts/runserver
```

Register and connect fake device
```bash
  ./scripts/fake_device.py admin pass
```

### Format, lint and test
Format and lint code 
```bash
  nox -S format lint
```

Run tests
```bash
  nox -S test
```

or just

```bash
  pytest
```

