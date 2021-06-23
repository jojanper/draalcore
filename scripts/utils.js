const childProcess = require('child_process');

function execute(cmd, cbStdout) {
    const method = cbStdout ? 'exec' : 'spawn';

    return new Promise((resolve, reject) => {
        const child = childProcess[method](cmd, {
            shell: true,
            stdio: 'inherit'
        });

        if (cbStdout) {
            // Live console output
            child.stdout.on('data', data => {
                console.log(data.trim());
                cbStdout(data);
            });

            child.stderr.on('data', data => {
                console.log(data.trim());
            });
        }

        child.on('exit', code => {
            if (code !== 0) {
                return reject(code);
            }

            resolve(code);
        });
    });
}

module.exports = {
    execute
};
