# Wires and Rails: Workflow Post-Processing Tasks

## Pre-commit hook

Enforces `pylint` success on commit.

```
ln -sf ../../bin/pre-commit .git/hooks/pre-commit
```

## Development

ocropy isn't very OSX friendly. For development purposes, running ocropy in the Docker container is most convenient.

```
docker build -t wires-and-rails-workflow-processing .
docker run -t -d --name wires-and-rails-workflow-processor wires-and-rails-workflow-processing
docker exec -it wires-and-rails-workflow-processor bash
```
