import subprocess


def execute(host, command):

    result = subprocess.run(
        ["ssh", host, command],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout