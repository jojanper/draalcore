/**
 * Library release script.
 *
 * @module scripts/release.
 */

const shelljs = require('shelljs');
const options = require('minimist')(process.argv.slice(1));
const logger = require('log-symbols');
const format = require('util').format;


if (!options.version) {
    console.log(logger.error, 'No --version=<major.minor.patch> option defined!');
    process.exit(1);
}

// Available remotes
const remotes = (options.remotes) ? options.remotes.split(',') : ['origin'];

// Python version file generator
var pyVersion = [
    '#!/usr/bin/env python',
    '# -*- coding: utf-8 -*-',
    "__version__ = '" + options.version + "'",
    "__author__ = 'Juha Ojanperä'",
    "__contact__ = 'juha.ojanpera@gmail.com'"
];

var cmds = [

    // Update python application version
    'echo \"' + pyVersion.join('\\n') + '\" > draalcore/__init__.py',

    // Update package.json version
    'npm version --no-git-tag-version ' + options.version,

    // Commit the new release
    'git add package.json',
    'git add draalcore/__init__.py',
    'git commit -m "Release ' + options.version + '"',
    'git tag -a v' + options.version + ' -m "Release ' + options.version + '"'
];

for (let remote of remotes) {
    cmds.push(format('git push %s v%s', remote, options.version));
    cmds.push(format('git push %s master', remote));
}

shelljs.exec(cmds.join(' && '), function(code) {
    process.exit(code);
});
