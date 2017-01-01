/**
 * Setup virtual environment for local development.
 *
 * @module scripts/virtualenv
 */

const shelljs = require('shelljs');
const format = require('util').format;
const options = require('minimist')(process.argv.slice(1));

const folder = 'draalcore';
const python = options.python || '/usr/bin/python2.7';

commands = [
    'mkdir -p virtualenv',
    'cd virtualenv',
    format('virtualenv -p %s --no-site-packages %s', python, folder),
    'cd ..',
    format('. ./virtualenv/%s/bin/activate', folder),
    'npm run prepare'
];

shelljs.exec(commands.join(' && '), function(code, stdout, stderr) {
    shelljs.exit(code);
});
