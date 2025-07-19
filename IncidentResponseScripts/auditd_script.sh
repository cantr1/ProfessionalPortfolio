#!/bin/bash
# This script process auditd logs into a human readable format
# Written by: Kelly Cantrell - 4/27/25

TODAY=$(date +%d-%m-%Y)


echo "=== Audit Report --- $(hostname) ---  Date = $TODAY ==="

echo ""

echo "===== CURRENT USERS ====="
w



# 1. SUDO COMMANDS

echo "===== SUDO COMMANDS ====="

sudo ausearch --input-logs -k sudo-commands -ts today | awk '

/^----$/ { if (cmd != "") { print timestamp, user, cmd; cmd=""; user=""; timestamp="" } }

/time->/ {

    gsub("time->", "", $0);

    timestamp = $0

}

/auid=/ {

    match($0, /auid=[0-9]+/, m);

    if (m[0] != "") {

        split(m[0], a, "=");

        user_id = a[2];

        # Look up username from UID

        cmd_user = "getent passwd " user_id " | cut -d: -f1";

        cmd_user | getline user;

        close(cmd_user);

    }

}

/type=EXECVE/ {

    for (i=1; i<=NF; i++) {

        if ($i ~ /^a[0-9]=/) {

            gsub(/^a[0-9]=/, "", $i);

            gsub(/"/, "", $i);

            cmd = cmd $i " ";

        }

    }

}

END { if (cmd != "") { print timestamp, user, cmd } }

'

echo ""

# 2. SYSTEM CALLS
# System calls made the log 5mb, so for now I will leave these out
#echo "===== SYSTEM CALLS ====="


#sudo aureport --input-logs --syscall --start today | grep -v cron


#echo ""



# 3. LOGIN EVENTS


echo "===== LOGIN EVENTS ====="


sudo aureport --input-logs --auth --start today


echo ""



# 4. ANOMALOUS EVENTS


echo "===== ANOMALOUS EVENTS ====="


sudo aureport --input-logs --anomaly --start today


echo ""



# 5. AUDIT CONFIG CHANGES

echo "===== AUDIT CONFIG CHANGES ====="

sudo ausearch --input-logs -m CONFIG_CHANGE -ts today | awk '

/^----$/ {

    if (timestamp != "" && user != "" && exe != "") {

        print timestamp, user, exe, config;

    }

    timestamp=""; user=""; exe=""; config="";

}


/time->/ {

    gsub("time->", "", $0);

    timestamp = $0;

}


/auid=/ {

    match($0, /auid=[0-9]+/, m);

    if (m[0] != "") {

        split(m[0], a, "=");

        user_id = a[2];

        cmd_user = "getent passwd " user_id " | cut -d: -f1";

        cmd_user | getline user;

        close(cmd_user);

    }

}


/exe="/ {

    match($0, /exe="[^"]+"/, m);

    if (m[0] != "") {

        gsub(/exe="/, "", m[0]);

        gsub(/"/, "", m[0]);

        exe = m[0];

    }

}


/cmdline=/ {

    match($0, /cmdline="[^"]+"/, m);

    if (m[0] != "") {

        gsub(/cmdline="/, "", m[0]);

        gsub(/"/, "", m[0]);

        config = m[0];

    }

}

END {

    if (timestamp != "" && user != "" && exe != "") {

        print timestamp, user, exe, config;

    }

}

'

echo ""

# 6. MONITOR CONFIG FILES
echo "===== MONITORED SYSTEM FILE CHANGES ====="


# Build a simple temporary UID to username map

awk -F: '{print $3, $1}' /etc/passwd > /tmp/uid_username_map.txt


# Now parse audit events without causing any new file reads

sudo ausearch --input-logs -ts today | awk '

BEGIN {

    while ((getline < "/tmp/uid_username_map.txt") > 0) {

        uid_to_user[$1] = $2;

    }

}


/time->/ {

    gsub("time->", "", $0);

    timestamp = $0;

}


/auid=/ {

    match($0, /auid=[0-9]+/, m);

    if (m[0] != "") {

        split(m[0], a, "=");

        user = uid_to_user[a[2]];

        if (user == "") {

            user = "unknown";

        }

    }

}


/name="/ {

    match($0, /name="[^"]+"/, m);

    if (m[0] != "") {

        gsub(/name="/, "", m[0]);

        gsub(/"/, "", m[0]);

        path = m[0];

        if (path ~ "^/etc/hosts" || path ~ "^/etc/ssh/sshd_config" || path ~ "^/etc/sudoers" || path ~ "^/etc/hostname" || path ~ "^/etc/netplan/" || path ~ "^/etc/passwd" || path ~ "^/etc/shadow" || path ~ "^/etc/group" || path ~ "^/etc/fstab") {

            key = timestamp " " user " " path;

            if (!seen[key]++) {

                print timestamp, user, path;

            }

        }

    }

}

'

echo ""