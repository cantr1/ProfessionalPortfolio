#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <ctype.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#if __has_include(<cjson/cJSON.h>)
#include <cjson/cJSON.h>
#elif __has_include(<cJSON.h>)
#include <cJSON.h>
#elif __has_include("/opt/homebrew/include/cjson/cJSON.h")
#include "/opt/homebrew/include/cjson/cJSON.h"
#else
#error "cJSON header not found. Install libcjson-dev (or equivalent) and configure include paths."
#endif

#define MAX_PATH_LEN 300
#define MAX_JSON_LEN 2048
#define PORT 8080
#define BUFFER_SIZE 4096

typedef struct {
    char *entry_name;
    char *entry_username;
    char *entry_pw;
    char action;
} t_entry;

bool validate_entry(const t_entry *entry);
void generate_file_path(const t_entry *entry, char *buffer, size_t size);
int create_vault_entry(t_entry *entry);
int read_vault_entry(const t_entry *entry, char *response_json, size_t response_json_size);
int update_vault_entry(const t_entry *entry);
int delete_vault_entry(const t_entry *entry);

static char method_to_action_char(const char *method) {
    if (method == NULL) {
        return '\0';
    }
    if (strcasecmp(method, "CREATE") == 0 || strcasecmp(method, "POST") == 0 || strcasecmp(method, "C") == 0) {
        return 'C';
    }
    if (strcasecmp(method, "READ") == 0 || strcasecmp(method, "GET") == 0 || strcasecmp(method, "R") == 0) {
        return 'R';
    }
    if (strcasecmp(method, "UPDATE") == 0 || strcasecmp(method, "PUT") == 0 || strcasecmp(method, "PATCH") == 0 || strcasecmp(method, "U") == 0) {
        return 'U';
    }
    if (strcasecmp(method, "DELETE") == 0 || strcasecmp(method, "D") == 0) {
        return 'D';
    }
    return '\0';
}

static bool get_json_string_field(cJSON *json, const char *key, char **dest, bool required) {
    cJSON *field = cJSON_GetObjectItemCaseSensitive(json, key);
    if (field == NULL || !cJSON_IsString(field) || field->valuestring == NULL) {
        if (required) {
            printf("Missing or invalid string field: %s\n", key);
            return false;
        }
        *dest = NULL;
        return true;
    }

    *dest = field->valuestring;
    return true;
}

static bool populate_entry_from_json(cJSON *json, t_entry *entry) {
    char *method = NULL;
    char *action = NULL;
    // Validate data from JSON before populating
    if (!get_json_string_field(json, "entry_name", &entry->entry_name, true)) {
        return false;
    }
    if (!get_json_string_field(json, "entry_username", &entry->entry_username, false)) {
        return false;
    }
    if (!get_json_string_field(json, "entry_pw", &entry->entry_pw, false)) {
        return false;
    }
    if (!get_json_string_field(json, "method", &method, false)) {
        return false;
    }
    if (!get_json_string_field(json, "action", &action, false)) {
        return false;
    }

    // Convert method from HTTP to char we can evaluate
    if (method != NULL) {
        entry->action = method_to_action_char(method);
    } else if (action != NULL) {
        entry->action = method_to_action_char(action);
    } else {
        entry->action = '\0';
    }

    if (entry->action == '\0') {
        printf("JSON must include a valid method/action (CREATE/READ/UPDATE/DELETE or POST/GET/PUT/PATCH/DELETE)\n");
        return false;
    }

    return true;
}

static int process_json_payload(const char *json_payload, char *response_body, size_t response_body_size) {
    int rc = 1;

    if (json_payload == NULL) {
        printf("No JSON payload provided\n");
        snprintf(response_body, response_body_size, "{\"status\":\"failure\"}");
        return rc;
    }

    cJSON *json = cJSON_Parse(json_payload);
    if (json == NULL) {
        printf("Error parsing JSON\n");
        snprintf(response_body, response_body_size, "{\"status\":\"failure\"}");
        return rc;
    }

    t_entry entry = {0};
    if (!populate_entry_from_json(json, &entry)) {
        cJSON_Delete(json);
        return rc;
    }

    if (validate_entry(&entry)) {
        switch (entry.action) {
        case 'C':
            rc = create_vault_entry(&entry);
            break;
        case 'R':
            rc = read_vault_entry(&entry, response_body, response_body_size);
            break;
        case 'U':
            rc = update_vault_entry(&entry);
            break;
        case 'D':
            rc = delete_vault_entry(&entry);
            break;
        default:
            printf("Unrecognized Entry Action\nPlease try again\n");
        }
    } else {
        printf("Invalid entry\n");
    }

    if (entry.action != 'R') {
        if (rc == 0) {
            snprintf(response_body, response_body_size, "{\"status\":\"success\"}");
        } else {
            snprintf(response_body, response_body_size, "{\"status\":\"failure\"}");
        }
    }

    cJSON_Delete(json);
    return rc;
}

bool validate_entry(const t_entry *entry) {
    if (entry->action != 'C' && entry->action != 'R' && entry->action != 'U' && entry->action != 'D' ) {
        printf("Entry must have a valid action type");
        return false;
    }

    if (entry->action == 'C' || entry->action == 'U') {
        if (entry->entry_name == NULL || entry->entry_username == NULL || entry->entry_pw == NULL) {
            printf("Create / Update Action requires username / password and valid entry name");
            return false;
        }
    } else if (entry->action == 'D' || entry->action == 'R') {
        if (entry->entry_name == NULL) {
            printf("Delete / Read Action requires valid entry name");
            return false;
        }
    } 

    return true;
}

void generate_file_path(const t_entry *entry, char *buffer, size_t size) {
    const char *base_file_path = "./";
    snprintf(buffer, size, "%s%s_vault.txt", base_file_path, entry->entry_name);
}

int create_vault_entry(t_entry *entry) {
    int rc = 1;
    char file_path[MAX_PATH_LEN];

    generate_file_path(entry, file_path, sizeof(file_path));

    FILE *fptr = fopen(file_path, "w");
    if (fptr != NULL) {
        fprintf(fptr, "Username: %s\nPassword: %s", entry->entry_username, entry->entry_pw);
        fclose(fptr);

        printf("Wrote the following to %s\n", file_path);
        printf("Entry Username: %s\n", entry->entry_username);
        printf("Entry Value: %s\n", entry->entry_pw);
        rc = 0;
    } else {
        printf("Unable to create new entry");
    }

    return rc;
}

int read_vault_entry (const t_entry *entry, char *response_json, size_t response_json_size) {
    int rc = 1;
    char file_path[MAX_PATH_LEN];
    char username[256] = {0};
    char password[256] = {0};

    generate_file_path(entry, file_path, sizeof(file_path));

    if (access(file_path, F_OK) != 0) {
        printf("File not found --- Unable to update\n");
        snprintf(response_json, response_json_size, "{\"status\":\"failure\"}");
        return rc;
    }

    FILE *fptr = fopen(file_path, "r");

    if (fptr != NULL) {
        char file_content[256];

        while (fgets(file_content, sizeof(file_content), fptr)) {
            if (strncmp(file_content, "Username: ", 10) == 0) {
                strncpy(username, file_content + 10, sizeof(username) - 1);
                username[strcspn(username, "\r\n")] = '\0';
            } else if (strncmp(file_content, "Password: ", 10) == 0) {
                strncpy(password, file_content + 10, sizeof(password) - 1);
                password[strcspn(password, "\r\n")] = '\0';
            }
        }

        fclose(fptr);

        cJSON *response = cJSON_CreateObject();
        if (response == NULL) {
            printf("Unable to allocate JSON response\n");
            snprintf(response_json, response_json_size, "{\"status\":\"failure\"}");
            return rc;
        }

        cJSON_AddStringToObject(response, "status", "success");
        cJSON_AddStringToObject(response, "entry_name", entry->entry_name);
        cJSON_AddStringToObject(response, "entry_username", username);
        cJSON_AddStringToObject(response, "entry_pw", password);

        char *serialized = cJSON_PrintUnformatted(response);
        if (serialized != NULL) {
            snprintf(response_json, response_json_size, "%s", serialized);
            free(serialized);
            rc = 0;
        } else {
            printf("Unable to serialize JSON response\n");
            snprintf(response_json, response_json_size, "{\"status\":\"failure\"}");
        }

        cJSON_Delete(response);
    } else {
        printf("Unable to read from file.");
        snprintf(response_json, response_json_size, "{\"status\":\"failure\"}");
    }

    return rc;
}

int update_vault_entry(const t_entry *entry) {
    int rc = 1;
    char file_path[MAX_PATH_LEN];

    generate_file_path(entry, file_path, sizeof(file_path));

    if (access(file_path, F_OK) != 0) {
        printf("File not found --- Unable to update\n");
        return rc;
    }

    // Write new info to file path
    FILE *fptr = fopen(file_path, "w");
    if (fptr != NULL) {
        fprintf(fptr, "Username: %s\nPassword: %s", entry->entry_username, entry->entry_pw);
        fclose(fptr);
        rc = 0;
    } else {
        printf("Unable to write data to file.");
    }

    return rc;
}

int delete_vault_entry(const t_entry *entry) {
    int rc = 1;
    char file_path[MAX_PATH_LEN];

    generate_file_path(entry, file_path, sizeof(file_path));
    
    // Check file exists
    if (access(file_path, F_OK) == 0) {
        printf("Successfully located vault file\nAttempting deletion\n");
        if (remove(file_path) == 0) {
            printf("File deleted successfully\n");
            rc = 0;
        } else {
            perror("Error deleting file");
        }
    } else {
        printf("File not found"); 
    }

    return rc;
}

int main(int argc, char *argv[]) {
    char json_buffer[MAX_JSON_LEN] = {0};
    char response_body[BUFFER_SIZE] = {0};

    int server_fd;
    struct sockaddr_in address;
    int addrlen = sizeof(address);

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == 0) {
        perror("socket failed");
        return 1;
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        return 1;
    }

    if (listen(server_fd, 10) < 0) {
        perror("listen");
        return 1;
    }

    printf("Listening on port %d...\n", PORT);

    while (1) {
        int client_fd = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen);
        if (client_fd < 0) {
            perror("accept");
            continue;
        }

        char buffer[BUFFER_SIZE] = {0};

        ssize_t bytes_read = read(client_fd, buffer, BUFFER_SIZE - 1);

        if (bytes_read > 0) {
            printf("Request:\n%s\n", buffer);
            
            // Get HTTP body
            char *json_body = strstr(buffer, "\r\n\r\n");

            if (json_body != NULL) {
                json_body += 4;
                int rc = process_json_payload(json_body, response_body, sizeof(response_body));

                const char *response;
                char http_response[BUFFER_SIZE + 256] = {0};

                if (rc == 0) {
                    snprintf(http_response, sizeof(http_response),
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: application/json\r\n"
                        "Content-Length: %zu\r\n"
                        "\r\n"
                        "%s",
                        strlen(response_body), response_body);
                    response = http_response;
                } else {
                    snprintf(http_response, sizeof(http_response),
                        "HTTP/1.1 400 Bad Request\r\n"
                        "Content-Type: application/json\r\n"
                        "Content-Length: %zu\r\n"
                        "\r\n"
                        "%s",
                        strlen(response_body), response_body);
                    response = http_response;

                }
                write(client_fd, response, strlen(response));
                }
            }
        close(client_fd);
    }

    return process_json_payload(json_buffer, response_body, sizeof(response_body));
}
