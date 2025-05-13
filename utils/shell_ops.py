import subprocess
import pexpect

def create_user(username, password, fullname, room, workphone, homephone, other):
    try:
        child = pexpect.spawn(f"sudo adduser {username}")
        child.timeout = 10

        child.expect("New password:")
        child.sendline(password)

        child.expect("Retype new password:")
        child.sendline(password)

        child.expect("Full Name")
        child.sendline(fullname)

        child.expect("Room Number")
        child.sendline(room)

        child.expect("Work Phone")
        child.sendline(workphone)

        child.expect("Home Phone")
        child.sendline(homephone)

        child.expect("Other")
        child.sendline(other)

        child.expect("Is the information correct?")
        child.sendline("Y")

        child.expect(pexpect.EOF)

        return True, f"User '{username}' created successfully."

    except Exception as e:
        return False, f"Error during user creation: {str(e)}"


def delete_user(username):
    try:
        child = pexpect.spawn(f"sudo deluser {username}")

        # Set a timeout in case something hangs
        child.timeout = 10

        child.expect("Removing user")
        child.sendline("Y")

        child.expect(pexpect.EOF)  # Wait for process to end

        return True, f"User '{username}' deleted successfully."

    except Exception as e:
        #return False, f"Error during user deletion: {str(e)}"
        return False, f"User {username} does not exist or is not a system user."

def list_users():
    try:
        # Fetch users with UID >= 1000 (non-system users)
        child = pexpect.spawn("awk -F: '$3 >= 1000 && $3 < 65534 { print $1 }' /etc/passwd")
        child.timeout = 10
        child.expect(pexpect.EOF)
        users = child.before.decode().splitlines()
        return True, users
    except Exception as e:
        return False, f"Error during user listing: {str(e)}"

def get_inactive_users(days=30):
    try:
        # Run the `lastlog` command and filter users inactive for `days`
        result = subprocess.run(
            ["lastlog", "--time", str(days)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()

        # Parse the output and extract inactive users
        lines = result.stdout.splitlines()
        inactive_users = []
        for line in lines[1:]:
            parts = line.split()
            if len(parts) > 0:
                username = parts[0]
                # Check if the user is a human user (UID >= 1000)
                user_info = subprocess.run(
                    ["id", "-u", username],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if user_info.returncode == 0:
                    uid = int(user_info.stdout.strip())
                    if uid >= 1000:
                        if "Never logged in" in line or "No login" in line:
                            inactive_users.append(username)

        return True, inactive_users
    except Exception as e:
        return False, f"Error fetching inactive users: {str(e)}"

def get_gpu_stats():
    try:
        # Run the `nvidia-smi` command
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,utilization.gpu,utilization.memory,memory.total,memory.used,memory.free,temperature.gpu", "--format=csv,noheader,nounits"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            return False, result.stderr.strip()

        # Parse the output
        gpu_stats = []
        for line in result.stdout.strip().split("\n"):
            fields = line.split(", ")
            gpu_stats.append({
                "index": int(fields[0]),
                "name": fields[1],
                "gpu_util": int(fields[2]),
                "mem_util": int(fields[3]),
                "mem_total": int(fields[4]),
                "mem_used": int(fields[5]),
                "mem_free": int(fields[6]),
                "temperature": int(fields[7])
            })

        return True, gpu_stats
    except Exception as e:
        return False, f"Error fetching GPU stats: {str(e)}"

