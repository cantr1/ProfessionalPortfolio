#!/bin/bash
# This script must be run as root
# This script creates login banners to reflect ownership
# and warn against misuse
# Written By: Kelly Cantrell

# Step 1: Create the login banner file in /etc/ssh
BANNER_FILE="/etc/ssh/login-banner.txt"

echo "Creating login banner at $BANNER_FILE"
echo "

*************************************************
*  WARNING: Unauthorized access prohibited!     *
*  This system is the property of Quanta        *
*  Nashville and for authorized users only.     *
*  By proceeding, you consent to monitoring     *
*  and agree to all terms of use.               *
*  Disconnect immediately if unauthorized.      *
*************************************************

" | sudo tee /etc/ssh/login-banner.txt



# Step 2: Edit /etc/ssh/sshd_config
SSHD_CONFIG="/etc/ssh/sshd_config"
echo "Modifying $SSHD_CONFIG"

# Replace "#Banner none" with our banner file path
sudo sed -i 's/^#Banner none/Banner \/etc\/ssh\/login-banner.txt/' "$SSHD_CONFIG"

# Change "#PrintLastLog yes" to "PrintLastLog no"
sudo sed -i 's/^#PrintLastLog yes/PrintLastLog no/' "$SSHD_CONFIG"

# Change "#PrintMotd no" to "PrintMotd yes"
sudo sed -i 's/^PrintMotd no/PrintMotd yes/' "$SSHD_CONFIG"


# Step 3: Edit /etc/pam.d/sshd to disable default MOTD
PAM_SSHD="/etc/pam.d/sshd"
echo "Modifying $PAM_SSHD to disable default MOTD sessions"

# Comment out the line: session  optional  pam_motd.so motd=/run/motd.dynamic
sudo sed -i '/^session\s\+optional\s\+pam_motd\.so\s\+motd=\/run\/motd\.dynamic/s/^/#/' "$PAM_SSHD"

# Comment out the line: session  optional  pam_motd.so noupdate
sudo sed -i '/^session\s\+optional\s\+pam_motd\.so\s\+noupdate/s/^/#/' "$PAM_SSHD"

# Comment out the line: session  optional  pam_mail.so standard noenv # [1]
sudo sed -i '/^session\s\+optional\s\+pam_mail\.so\s\+standard\s\+noenv\s\+# \[1\]/s/^/#/' "$PAM_SSHD"


# Step 4: Create the post-login banner in /etc/motd
MOTD_FILE="/etc/motd"
echo "Creating post-login banner at $MOTD_FILE"
echo "

********************************************************************
*                     AUTHORIZED ACCESS ONLY                      *
********************************************************************
* This system is the property of Quanta Nashville. Unauthorized   *
* access, use, or modification is strictly prohibited.            *
*                                                                 *
* Quanta Nashville reserves the right to monitor all activity on  *
* this system and to take disciplinary action, pursue civil       *
* liability, and/or initiate criminal prosecution against         *
* individuals engaging in unauthorized activities.                *
*                                                                 *
* By accessing these systems, you acknowledge and agree that you  *
* will comply with all applicable policies and laws. Failure to   *
* acknowledge this notice does not preclude consequences for      *
* policy violations or suspicious activity.                       *
*                                                                 *
* In the event of a policy violation or suspicious activity, the  *
* appropriate supervisor or manager will be notified.             *
*                                                                 *
* If you are not an authorized user, disconnect immediately.      *
********************************************************************

" | sudo tee /etc/motd

# Step 5: Disable other login messages
sudo chmod -x /etc/update-motd.d/*

# Step 6: Restart ssh services
sudo systemctl restart ssh