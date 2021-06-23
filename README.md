# draalcore
> Utility library (Django based) for backend application development.

## Usage

### Install dependencies
```
npm install
npm run setup
source virtualenv3.6/draalcore/bin/activate
```

This installs NPM, virtualenv and library (both npm and python) dependencies. Default python version
is 3.6. To install other python versions under virtualenv:

```
npm run setup -- --virtualname=virtualenv3.8 --python=/usr/bin/python3.8
source virtualenv3.8/draalcore/bin/activate
```

### Run Python code styling
```
npm run lint
```

### Run unit tests
```
npm test (using django-nose test runner)
npm test -- --djangorunner=true (using django's own test runner, faster)
npm test -- --testapp=draalcore.test_apps.test_models.tests.test_actions:ModelActionsTestCase.test_model_actions_listing (run specific test case)
```

### Run code styling + unit tests
```
npm run cibuild
```

### Build library
Build into `build` directory.
```
npm run build
```

### Create release
```
npm run release -- --version=<major.minor.patch>
npm run release -- --version=<major.minor.patch> --remotes=remote1,remote2 (optional)
```

## Project structure
This distribution contains the following project structure :

* draalcore
    * Library code.
* project
    * Django project settings for library.
* scripts
    * Build scripts.

## What's Inside?

Django based library with ReST API and related functionality to simplify actual application development.

### Continuous Integration (CI)

#### GitHub Actions
https://github.com/jojanper/draalcore/actions
