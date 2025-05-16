# Twitter Clone Web Application [![tests](https://github.com/RuiZhangg/CRUD-web/actions/workflows/tests.yml/badge.svg)](https://github.com/RuiZhangg/CRUD-web/actions/workflows/tests.yml)

## Overview

This is a full-stack Twitter clone built with Flask, PostgreSQL, and Docker. It supports user authentication, CRUD functionality, full-text search with RUM indexing, and efficient handling of datasets with 10M+ rows. The project includes automated CI via GitHub Actions and runs in both development and production environments.

## Features

- User registration, login/logout, and session management
- Post creation and feed display with pagination
- Full-text message search with relevance ranking and highlighting
- High-performance PostgreSQL queries using appropriate indexes
- Test data generation for large-scale performance testing
- Dockerized setup with persistent volumes and CI/CD integration

## Usage

### Start in Development

Start the development environment
```bash
$ docker compose up --build
```
Access the app at: <http://localhost:9876>

### Start in Production

Start production services with nginx proxy
```bash
$ docker compose -f docker-compose.prod.yml up -d --build

$ docker compose -f docker-compose.prod.yml up nginx
```
Access the app at: <http://localhost:1773>
