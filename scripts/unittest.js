/**
 * Execute unit tests with coverage report.
 *
 * @module scripts/unittest
 */

const shelljs = require('shelljs');
const format = require('util').format;
const options = require('minimist')(process.argv.slice(1));

// Run only subset sets?
const app = options.testapp || '';

// Use Django's test runner instead of nose runner
const baseRunner = (options.baserunner) ? 'DJANGO_TEST_RUNNER=1' : '';

commands = [
    format('%s coverage run --source=. manage.py test --verbosity=2 --settings=project.test_settings %s', baseRunner, app),
    'coverage report --omit=./virtualenv**,setup.py -m'
];

shelljs.exec(commands.join(' && '), function(code, stdout, stderr) {
    shelljs.exit(code);
});
