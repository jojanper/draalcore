/**
 * Library release script.
 *
 * @module scripts/release.
 */

shelljs = require('shelljs');
var options = require('minimist')(process.argv.slice(1));
var logger = require('log-symbols');


if (!options.version) {
    console.log(logger.error, 'No --version=<version> argument defined!');
    process.exit(1);
}

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
    'git tag -a ' + options.version + ' -m "Release ' + options.version + '"',
    'git push origin master'
];

shelljs.exec(cmds.join(' && '), function(code) {
    process.exit(code);
});
