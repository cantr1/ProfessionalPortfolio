#!/bin/bash
# This script deploys a config for pam that sets up fail lock for local accounts
# Written By: Kelly Cantrell (7/14/25)

sudo tee /etc/pam.d/common-auth > /dev/null << 'EOF'
# Delay brute-force attacks
auth    required                        pam_faildelay.so delay=3000000

# Check if account should be locked *before* authentication
auth    required                        pam_faillock.so preauth silent deny=3 unlock_time=1200 even_deny_root

# Primary auth modules
auth    [success=2 default=ignore]      pam_unix.so nullok
auth    [success=1 default=ignore]      pam_sss.so use_first_pass

# Register failed login attempt
auth    [default=die]                   pam_faillock.so authfail deny=3 unlock_time=1200 even_deny_root

# Clear faillock on success
auth    sufficient                      pam_faillock.so authsucc deny=3 unlock_time=1200 even_deny_root

# Deny if nothing else succeeded
auth    requisite                       pam_deny.so

# Permit if nothing above failed
auth    required                        pam_permit.so

# Optional capabilities module
auth    optional                        pam_cap.so

# end of pam-auth-update config
EOF

sudo tee /etc/pam.d/common-account > /dev/null << 'EOF'
# here are the per-package modules (the "Primary" block)
account required                        pam_faillock.so
account [success=1 new_authtok_reqd=done default=ignore]        pam_unix.so
# here's the fallback if no module succeeds
account requisite                       pam_deny.so
# prime the stack with a positive return value if there isn't one already;
# this avoids us returning an error just because nothing sets a success code
# since the modules above will each just jump around
account required                        pam_permit.so
# and here are more per-package modules (the "Additional" block)
account sufficient                      pam_localuser.so
account [default=bad success=ok user_unknown=ignore]    pam_sss.so
# end of pam-auth-update config
EOF

sudo systemctl restart sshd