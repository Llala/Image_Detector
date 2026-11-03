import os
import subprocess

url = "https://www.sportmaster.ru/upload/mdm/media_content/05e/175336730299.jpg"

result = subprocess.run(
    [
        "/usr/bin/curl",
        "-q",
        "-4",
        "--noproxy", "*",
        "--connect-timeout", "10",
        "--max-time", "30",
        "-v",
        "-o", "/tmp/test_curl.jpg",
        url,
    ],
    env={
        "HOME": os.path.expanduser("~"),
        "PATH": "/usr/bin:/bin",
    },
    capture_output=True,
    text=True,
    timeout=35,
)

print("Return code:", result.returncode)
print("stderr:", result.stderr)