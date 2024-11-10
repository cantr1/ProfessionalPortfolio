# Apache Web Server Project

## Purpose
The purpose of this project is to enhance my Linux skills and knowledge by setting up an Apache web server. This involves configuring the server, securing it, and creating a basic HTML website.

## Goals
- Configure a web server on my local network
- Create a simple website using HTML
- Ensure security by configuring permissions and a firewall

---

## Process

### 1. Set Up
1. **Install Ubuntu on a VM**  
   Begin by installing Ubuntu in a virtual machine environment, then ensure the system is up to date.
   
   ![Complete](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/apt-upgrade.PNG)

2. **Edit Hostname and Hosts File**  
   Set the hostname and update the `/etc/hosts` file to reflect the name of your web server.
   
   ![Complete](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/edit-hosts.PNG)
   
   ![Complete](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/hosts.PNG)

4. **Disable Root Login**  
   For added security, disable SSH root login to prevent remote root access.
   
   ![Disable root SSH login](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/ssh-config.PNG)

   ![Disable root SSH login](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/permit-root.PNG)

   This disables root login but still allows for remote administration by users. Individuals on Windows systems can use PowerShell to remote into the server via SSH.

   ![Disable root SSH login](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/powershell-ssh.PNG)

---

### 2. Apache Installation
1. **Install Apache**  
   Install Apache along with any necessary packages for the server.

   ![](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/install-apache.PNG)

2. **Verify Service Status**  
   Confirm that the Apache service is running as expected.

   ![](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/apache-running.PNG)

   We can now check the status via a web browser. We land on our default page, meaning everything is working as expected.

   ![](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/default-page.PNG)

4. **Disable Default Page**  
   To improve security, disable Apache's default page and reload the service to apply the change.

   ![](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/disable-default.PNG)

---

### 3. Firewall Configuration
1. **Enable Firewall**  
   Configure the firewall to allow only necessary applications, and enable it for enhanced security.

   ![](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/firewall.PNG)

---

### 4. Website Setup
1. **Create Directory Structure**  
   Set up the directory structure for your web server files, including folders for HTML files, logs, and backups.

   ![Disable root SSH login](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/set-up-directories.PNG)

2. **Configure Apache Site**  
   Create a virtual host configuration file in the Apache sites-available directory. Set the appropriate parameters, including the server name, document root, and log locations, then enable the site and reload Apache.

   ![Disable root SSH login](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/set-up-config.PNG)

   ![HTML content creation](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/web-server-conf.PNG)

4. **Add HTML Content**  
   In the `public_html` directory, add the HTML files, including an `index.html` as the homepage.

   ![HTML content creation](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/set-up-html.PNG)

   ![HTML content creation](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/add-some-html.PNG)
   

---

## Project Completion
With these steps, the project is complete, and the web server is functional.

![Complete](https://github.com/cantr1/ProfessionalPortfolio/blob/main/Apache%20Web%20Server/Images/web-sever-complete.PNG)

---

## Future Improvements
- Implement SSL/TLS for secure HTTPS connections
- Set up automated backups and monitoring
