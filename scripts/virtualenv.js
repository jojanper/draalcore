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
const virtualFolder = options.virtualname || 'virtualenv2.7';

commands = [
    format('mkdir -p %s', virtualFolder),
    format('cd %s', virtualFolder),
    format('virtualenv -p %s --no-site-packages %s', python, folder),
    'cd ..',
    format('. ./%s/%s/bin/activate', virtualFolder, folder),
    'pip install -U pip setuptools',
    'npm run install-pytools'
];

shelljs.exec(commands.join(' && '), function(code, stdout, stderr) {
    shelljs.exit(code);
});
