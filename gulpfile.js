var gulp = require('gulp');
var shell = require('gulp-shell')

gulp.task('lint', shell.task('flake8 --config=flake8 --verbose --exclude=virtualenv .'));

var testCommands = [
    'coverage run --source=. manage.py test --verbosity=2 --settings=project.test_settings',
    'coverage report --omit=./virtualenv**,setup.py -m'
];

gulp.task('unittest', shell.task(testCommands.join(' && ')));
