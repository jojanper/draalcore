var gulp = require('gulp');
var shell = require('gulp-shell')

gulp.task('lint', shell.task('flake8 --config=flake8 --verbose .'));

var testCommands = [
    'coverage run --source=. manage.py test --verbosity=2 --settings=test.test_settings',
    'coverage report -m'
];

gulp.task('unittest', shell.task(testCommands.join(' && ')));
