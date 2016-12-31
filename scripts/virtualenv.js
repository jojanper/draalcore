/**
 * Setup virtual environment for local development.
 *
 * @module scripts/virtualenv
 */

const shelljs = require('shelljs');
const format = require('util').format;

const folder = 'draalcore';

commands = [
    'mkdir -p virtualenv',
    'cd virtualenv',
    format('virtualenv -p /usr/bin/python2.7 --no-site-packages %s', folder),
    'cd ..',
    format('. ./virtualenv/%s/bin/activate', folder),
    'npm run prepare'
];

shelljs.exec(commands.join(' && '), function(code, stdout, stderr) {
    shelljs.exit(code);
});
