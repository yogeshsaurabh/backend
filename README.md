# Backend

Backend repo for Evolve

## Installation

To run the API Locally, you need to follow the following steps:

1. Clone the repo.
2. Create a Python virtual environment and activate it:

```sh
$ cd backend/
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $
```

### Install dependencies

```sh
(venv) $ pip install -r requirements.txt
```

## Commit Message Convention

- `add`: adding to existing feature/module
- `build`: Build related changes (eg: npm related/ adding external dependencies)
- `chore`: A code change that external user won't see (eg: change to .gitignore file or .prettierrc file)
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation related changes
- `refactor`: A code that neither fix bug nor adds a feature. (eg: You can use this when there is semantic changes like renaming a variable/ function name)
- `perf`: A code that improves performance
- `style`: A code that is related to styling
- `test`: Adding new test or making changes to existing test
