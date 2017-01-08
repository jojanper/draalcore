/**
 * Execute unit tests with coverage report.
 *
 * @module scripts/unittest
 */

const shelljs = require('shelljs');
const format = require('util').format;
const options = require('minimist')(process.argv.slice(1));

const app = options.testapp || '';

commands = [
    format('coverage run --source=. manage.py test --verbosity=2 --settings=project.test_settings %s', app),
    'coverage report --omit=./virtualenv**,setup.py -m'
];

shelljs.exec(commands.join(' && '), function(code, stdout, stderr) {
    shelljs.exit(code);
});
