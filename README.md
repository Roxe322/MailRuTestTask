# Test task for Mail.Ru
https://gist.github.com/VadimPushtaev/fa2940d0a86846c558a4000784164fa7

## Running
```bash
pip install poetry
poetry install
docker run --rm -it -p 6379:6379 redis:latest (or run your local)
poetry run python -m converter [config_file_name]
```
