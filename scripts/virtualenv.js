/**
 * Setup virtual environment for local development.
 */

const format = require('util').format;
const options = require('minimist')(process.argv.slice(1));

const { execute } = require('./utils');

const folder = 'draalcore';
const python = options.python || '/usr/bin/python3.6';
const virtualFolder = options.virtualname || 'virtualenv3.6';

commands = [
    format('mkdir -p %s', virtualFolder),
    format('cd %s', virtualFolder),
    format('virtualenv -p %s %s', python, folder),
    'cd ..',
    format('. ./%s/%s/bin/activate', virtualFolder, folder),
    'pip install -U pip setuptools',
    'npm run install-pytools'
];

execute(commands.join(' && ')).then(process.exit).catch(process.exit);
