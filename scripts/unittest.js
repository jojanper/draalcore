/**
 * Execute unit tests with coverage report.
 */
const format = require('util').format;
const options = require('minimist')(process.argv.slice(1));

const { execute } = require('./utils');

const OPTIONS = '--keepdb --verbosity=2 --settings=project.test_settings';

// Run only subset sets?
const app = options.testapp || '';

// Use Django's test runner instead of nose runner
const djangoRunner = (options.djangorunner) ? 'DJANGO_TEST_RUNNER=1' : '';

commands = [
    format('%s coverage run --source=. manage.py test %s %s', djangoRunner, OPTIONS, app),
    'coverage report --omit=./virtualenv**,setup.py -m'
];

execute(commands.join(' && ')).then(process.exit).catch(process.exit);
