/**
 * Execute unit tests with coverage report.
 *
 * @module scripts/unittest
 */

const shelljs = require('shelljs');

commands = [
    'coverage run --source=. manage.py test --verbosity=2 --settings=project.test_settings',
    'coverage report --omit=./virtualenv**,setup.py -m'
];

shelljs.exec(commands.join(' && '), function(code, stdout, stderr) {
    shelljs.exit(code);
});
