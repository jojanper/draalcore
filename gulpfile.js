var gulp = require('gulp');
var shell = require('gulp-shell')

gulp.task('lint', shell.task('flake8 --config=flake8 --verbose .'));
