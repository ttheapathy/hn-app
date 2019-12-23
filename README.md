# HackerNews Parser

This project is a test task for appfollow

## Requirements

* Docker
* Docker-compose

## Running

    docker-compose.prod.yml up -d --build

## Usage

get posts:
`curl -X GET http://localhost/posts`

ordering:
`curl -X GET http://localhost/posts?order=-id`

ordering:
`curl -X GET http://localhost/posts?order=-id`

limit:
`curl -X GET http://localhost/posts?limit=2`

offset:
`curl -X GET http://localhost/posts?offset=10`

multiple:
`curl -X GET http://localhost/posts?offset=2&offset=4&order=title`

manual fetch new posts:
`curl -X GET http://localhost/posts/_fetch`
