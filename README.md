# draalcore
> Utility library (Django based) for backend application development.

## Usage

### Install dependencies
```
npm install
npm run setup
source virtualenv/draalcore/bin/activate
```

This installs NPM, virtualenv and library (both npm and python) dependencies.

### Run Python code styling
```
npm run lint
```

### Run unit tests
```
npm test
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

#### Travis CI
https://travis-ci.org/jojanper/draalcore
