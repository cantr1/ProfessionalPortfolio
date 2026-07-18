package main

import (
	"database/sql"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"os"
	"strconv"
	"sync/atomic"
	"time"

	auth "github.com/cantr1/yoga/internal"
	"github.com/cantr1/yoga/internal/database"
	"github.com/google/uuid"
	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
)

type apiMetrics struct {
	fileServerHits         atomic.Int32
	userCreationHits       atomic.Int32
	instructorCreationHits atomic.Int32
	sessionCreationHits    atomic.Int32
	classRegistrationHits  atomic.Int32
	userLogins             atomic.Int32
	tokenRefreshes         atomic.Int32
	tokenRevokes           atomic.Int32
}

type apiMetricsResponse struct {
	FileServerHits         int32 `json:"file_server_hits"`
	UserCreationHits       int32 `json:"user_creation_hits"`
	InstructorCreationHits int32 `json:"instructor_creation_hits"`
	SessionCreationHits    int32 `json:"session_creation_hits"`
	ClassRegistrationHits  int32 `json:"class_registration_hits"`
	UserLogins             int32 `json:"user_logins"`
	TokenRefreshes         int32 `json:"token_refreshes"`
	TokenRevokes           int32 `json:"token_revokes"`
}

func (m *apiMetrics) snapshot() apiMetricsResponse {
	return apiMetricsResponse{
		FileServerHits:         m.fileServerHits.Load(),
		UserCreationHits:       m.userCreationHits.Load(),
		InstructorCreationHits: m.instructorCreationHits.Load(),
		SessionCreationHits:    m.sessionCreationHits.Load(),
		ClassRegistrationHits:  m.classRegistrationHits.Load(),
		UserLogins:             m.userLogins.Load(),
		TokenRefreshes:         m.tokenRefreshes.Load(),
		TokenRevokes:           m.tokenRevokes.Load(),
	}
}

type apiCfg struct {
	Port                    string
	FilepathRoot            string
	InstructorCreationToken string
	AdminKey                string
	dbQueries               database.Queries
	dbURL                   string
	tokenDuration           int
	tokenSecret             string
	metrics                 apiMetrics
	inDev                   string
}

func (cfg *apiCfg) middlewareCreateUser(w http.ResponseWriter, req *http.Request) {
	// Set response header type
	w.Header().Set("Content-Type", "application/json")

	// Parse parameters from request
	type parameters struct {
		Email    string `json:"email"`
		Password string `json:"password"`
		Name     string `json:"name"`
	}
	decoder := json.NewDecoder(req.Body)
	params := parameters{}
	err := decoder.Decode(&params)
	if err != nil {
		logRequestError(req, "error decoding parameters", err)
		http.Error(w, "Error decoding parameters", http.StatusBadRequest)
		return
	}

	// Check required parameters exist
	if params.Email == "" {
		http.Error(w, "Invalid JSON - `email` required", http.StatusBadRequest)
		return
	}

	if params.Password == "" {
		http.Error(w, "Invalid JSON - `password` required", http.StatusBadRequest)
		return
	}
	if params.Name == "" {
		http.Error(w, "Invalid JSON - `name` required", http.StatusBadRequest)
		return
	}

	// Hash the user password for the DB
	hashedPW, err := auth.HashPassword(params.Password)
	if err != nil {
		logRequestError(req, "error hashing password", err)
		http.Error(w, "Error hashing user password", http.StatusInternalServerError)
		return
	}

	// Parse info into database struct
	dbParams := database.CreateUserParams{
		Email:        params.Email,
		Name:         params.Name,
		PasswordHash: hashedPW,
		IsInstructor: sql.NullBool{Bool: false, Valid: true},
	}

	// Create user in the DB
	userDB, err := cfg.dbQueries.CreateUser(req.Context(), dbParams)
	if err != nil {
		logRequestError(req, "error creating user", err)
		http.Error(w, "Error creating user", http.StatusInternalServerError)
		return
	}

	// Parse returned SQL data into user struct to return in response body
	user := User{
		ID:        userDB.ID,
		CreatedAt: userDB.CreatedAt,
		UpdatedAt: userDB.UpdatedAt,
		Email:     userDB.Email,
	}

	// Marshal to JSON and return
	data, err := json.Marshal(&user)
	if err != nil {
		logRequestError(req, "error marshaling user response to JSON", err)
		http.Error(w, "Error marshaling user data to struct", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	w.Write(data)
	cfg.metrics.userCreationHits.Add(1)
}

func (cfg *apiCfg) middlewareCreateInstructor(w http.ResponseWriter, req *http.Request) {
	// Check Access Token in Request
	token, err := auth.GetBearerToken(*req)
	if err != nil {
		logRequestError(req, "error parsing token", err)
		http.Error(w, "Error parsing access token", http.StatusUnauthorized)
		return
	}
	if token != cfg.InstructorCreationToken {
		logRequestError(req, "instructor creation request attempted with bad token", nil)
		http.Error(w, "Access denied", http.StatusForbidden)
		return
	}

	// Set response header type
	w.Header().Set("Content-Type", "application/json")

	// Parse parameters from request
	type parameters struct {
		Email    string `json:"email"`
		Password string `json:"password"`
		Name     string `json:"name"`
	}
	decoder := json.NewDecoder(req.Body)
	params := parameters{}
	err = decoder.Decode(&params)
	if err != nil {
		logRequestError(req, "error decoding parameters", err)
		http.Error(w, "Error decoding parameters", http.StatusBadRequest)
		return
	}

	// Check required parameters exist
	if params.Email == "" {
		http.Error(w, "Invalid JSON - `email` required", http.StatusBadRequest)
		return
	}

	if params.Password == "" {
		http.Error(w, "Invalid JSON - `password` required", http.StatusBadRequest)
		return
	}
	if params.Name == "" {
		http.Error(w, "Invalid JSON - `name` required", http.StatusBadRequest)
		return
	}

	// Hash the user password for the DB
	hashedPW, err := auth.HashPassword(params.Password)
	if err != nil {
		logRequestError(req, "error hashing password", err)
		http.Error(w, "Error hashing user password", http.StatusInternalServerError)
		return
	}

	// Parse info into database struct
	dbParams := database.CreateUserParams{
		Email:        params.Email,
		Name:         params.Name,
		PasswordHash: hashedPW,
		IsInstructor: sql.NullBool{Bool: true, Valid: true},
	}

	// Create user in the DB
	userDB, err := cfg.dbQueries.CreateUser(req.Context(), dbParams)
	if err != nil {
		logRequestError(req, "error creating instructor", err)
		http.Error(w, "Error creating instructor", http.StatusInternalServerError)
		return
	}

	// Parse returned SQL data into user struct to return in response body
	instructor := Instructor{
		ID:        userDB.ID,
		CreatedAt: userDB.CreatedAt,
		UpdatedAt: userDB.UpdatedAt,
		Email:     userDB.Email,
		Name:      userDB.Name,
	}

	// Marshal to JSON and return
	data, err := json.Marshal(&instructor)
	if err != nil {
		logRequestError(req, "error marshaling instructor response to JSON", err)
		http.Error(w, "Error marshaling user data to struct", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	w.Write(data)
	cfg.metrics.instructorCreationHits.Add(1)
}

func (cfg *apiCfg) middlewareCreateSession(w http.ResponseWriter, req *http.Request) {
	// Check Access Token in Request
	token, err := auth.GetBearerToken(*req)
	if err != nil {
		logRequestError(req, "error parsing token", err)
		http.Error(w, "Error parsing access token", http.StatusUnauthorized)
		return
	}

	userIDFromToken, err := auth.ValidateJWT(token, cfg.tokenSecret)
	if err != nil {
		logRequestError(req, "invalid session creation token", err)
		http.Error(w, http.StatusText(http.StatusUnauthorized), http.StatusUnauthorized)
		return
	}

	// Get user info from DB
	userDB, err := cfg.dbQueries.QueryUserID(req.Context(), userIDFromToken)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			logRequestError(req, "session creator user not found", err)
			http.Error(w, http.StatusText(http.StatusNotFound), http.StatusNotFound)
			return
		}

		logRequestError(req, "error querying session creator", err)
		http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
		return
	}

	if !userDB.IsInstructor.Valid || !userDB.IsInstructor.Bool {
		logRequestError(req, "Standard user attempted to create session", nil)
		http.Error(w, http.StatusText(http.StatusForbidden), http.StatusForbidden)
		return
	}

	// Parse parameters from request
	type parameters struct {
		StartTime   time.Time `json:"start_time"`
		EndTime     time.Time `json:"end_time"`
		Difficulty  int32     `json:"difficulty"`
		ClassSize   int32     `json:"class_size"`
		Description string    `json:"description"`
	}
	decoder := json.NewDecoder(req.Body)
	params := parameters{}
	err = decoder.Decode(&params)
	if err != nil {
		logRequestError(req, "error decoding parameters", err)
		http.Error(w, "Error decoding parameters", http.StatusBadRequest)
		return
	}

	if params.StartTime.IsZero() {
		http.Error(w, "Invalid JSON - `start_time` required", http.StatusBadRequest)
		return
	}

	if params.EndTime.IsZero() {
		http.Error(w, "Invalid JSON - `end_time` required", http.StatusBadRequest)
		return
	}

	if !params.EndTime.After(params.StartTime) {
		http.Error(w, "Invalid JSON - `end_time` must be after `start_time`", http.StatusBadRequest)
		return
	}

	if params.Difficulty < 1 || params.Difficulty > 5 {
		http.Error(w, "Invalid JSON - `difficulty` must be between 1 and 5", http.StatusBadRequest)
		return
	}

	if params.ClassSize <= 0 {
		http.Error(w, "Invalid JSON - `class_size` must be greater than 0", http.StatusBadRequest)
		return
	}

	if params.Description == "" {
		http.Error(w, "Invalid JSON - `description` required", http.StatusBadRequest)
		return
	}

	// Parse info into database struct
	dbParams := database.CreateSessionParams{
		StartTime:    params.StartTime,
		EndTime:      params.EndTime,
		InstructorID: userIDFromToken,
		Difficulty:   params.Difficulty,
		ClassSize:    params.ClassSize,
		Description:  params.Description,
	}

	// Create session in the DB
	sessionDB, err := cfg.dbQueries.CreateSession(req.Context(), dbParams)
	if err != nil {
		logRequestError(req, "error creating session", err)
		http.Error(w, "Error creating session", http.StatusInternalServerError)
		return
	}

	// Parse returned SQL data into session response.
	session := Session{
		ID:           sessionDB.ID,
		CreatedAt:    sessionDB.CreatedAt,
		UpdatedAt:    sessionDB.UpdatedAt,
		StartTime:    sessionDB.StartTime,
		EndTime:      sessionDB.EndTime,
		InstructorID: sessionDB.InstructorID,
		Difficulty:   sessionDB.Difficulty,
		ClassSize:    sessionDB.ClassSize,
		Description:  sessionDB.Description,
	}

	// Marshal to JSON and return
	data, err := json.Marshal(&session)
	if err != nil {
		logRequestError(req, "error marshaling session response to JSON", err)
		http.Error(w, "Error marshaling session data to struct", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	w.Write(data)
	cfg.metrics.sessionCreationHits.Add(1)
}

func (cfg *apiCfg) middlewareRegisterForClass(w http.ResponseWriter, req *http.Request) {
	token, err := auth.GetBearerToken(*req)
	if err != nil {
		logRequestError(req, "error parsing token", err)
		http.Error(w, "Error parsing access token", http.StatusUnauthorized)
		return
	}

	userIDFromToken, err := auth.ValidateJWT(token, cfg.tokenSecret)
	if err != nil {
		logRequestError(req, "invalid class registration token", err)
		http.Error(w, http.StatusText(http.StatusUnauthorized), http.StatusUnauthorized)
		return
	}

	_, err = cfg.dbQueries.QueryUserID(req.Context(), userIDFromToken)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			logRequestError(req, "class registration user not found", err)
			http.Error(w, http.StatusText(http.StatusNotFound), http.StatusNotFound)
			return
		}

		logRequestError(req, "error querying class registration user", err)
		http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
		return
	}

	sessionID, err := uuid.Parse(req.PathValue("session_id"))
	if err != nil {
		logRequestError(req, "invalid session id for class registration", err)
		http.Error(w, "Invalid session id", http.StatusBadRequest)
		return
	}

	sessionDB, err := cfg.dbQueries.QuerySessionID(req.Context(), sessionID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			logRequestError(req, "class registration session not found", err)
			http.Error(w, http.StatusText(http.StatusNotFound), http.StatusNotFound)
			return
		}

		logRequestError(req, "error querying class registration session", err)
		http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
		return
	}

	sessionRegistrations, err := cfg.dbQueries.QuerySessionIDRegistrations(req.Context(), sessionID)
	if err != nil {
		logRequestError(req, "error querying session registrations", err)
		http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
		return
	}

	var registeredCount int32
	for _, registration := range sessionRegistrations {
		if registration.Status == "registered" {
			registeredCount++
		}
		if registration.UserID == userIDFromToken {
			http.Error(w, "User is already registered for this session", http.StatusConflict)
			return
		}
	}

	if registeredCount >= sessionDB.ClassSize {
		http.Error(w, "Session is full", http.StatusConflict)
		return
	}

	dbParams := database.CreateRegistrationParams{
		UserID:    userIDFromToken,
		SessionID: sessionID,
		Status:    "registered",
	}

	registrationDB, err := cfg.dbQueries.CreateRegistration(req.Context(), dbParams)
	if err != nil {
		logRequestError(req, "error creating class registration", err)
		http.Error(w, "Error creating class registration", http.StatusInternalServerError)
		return
	}

	registration := ClassRegistration{
		UserID:    registrationDB.UserID,
		SessionID: registrationDB.SessionID,
		CreatedAt: registrationDB.CreatedAt,
		Status:    registrationDB.Status,
	}

	data, err := json.Marshal(&registration)
	if err != nil {
		logRequestError(req, "error marshaling class registration response to JSON", err)
		http.Error(w, "Error marshaling class registration data to struct", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	w.Write(data)
	cfg.metrics.classRegistrationHits.Add(1)
}

func (cfg *apiCfg) middlewareUnregisterFromClass(w http.ResponseWriter, req *http.Request) {
	token, err := auth.GetBearerToken(*req)
	if err != nil {
		logRequestError(req, "error parsing token", err)
		http.Error(w, "Error parsing access token", http.StatusUnauthorized)
		return
	}

	userIDFromToken, err := auth.ValidateJWT(token, cfg.tokenSecret)
	if err != nil {
		logRequestError(req, "invalid class unregister token", err)
		http.Error(w, http.StatusText(http.StatusUnauthorized), http.StatusUnauthorized)
		return
	}

	_, err = cfg.dbQueries.QueryUserID(req.Context(), userIDFromToken)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			logRequestError(req, "class unregister user not found", err)
			http.Error(w, http.StatusText(http.StatusNotFound), http.StatusNotFound)
			return
		}

		logRequestError(req, "error querying class unregister user", err)
		http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
		return
	}

	sessionID, err := uuid.Parse(req.PathValue("session_id"))
	if err != nil {
		logRequestError(req, "invalid session id for class unregister", err)
		http.Error(w, "Invalid session id", http.StatusBadRequest)
		return
	}

	_, err = cfg.dbQueries.QuerySessionID(req.Context(), sessionID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			logRequestError(req, "class unregister session not found", err)
			http.Error(w, http.StatusText(http.StatusNotFound), http.StatusNotFound)
			return
		}

		logRequestError(req, "error querying class unregister session", err)
		http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
		return
	}

	sessionRegistrations, err := cfg.dbQueries.QuerySessionIDRegistrations(req.Context(), sessionID)
	if err != nil {
		logRequestError(req, "error querying session registrations for unregister", err)
		http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
		return
	}

	userIsRegistered := false
	for _, registration := range sessionRegistrations {
		if registration.UserID == userIDFromToken {
			userIsRegistered = true
			break
		}
	}

	if !userIsRegistered {
		http.Error(w, "User is not registered for this session", http.StatusNotFound)
		return
	}

	dbParams := database.DeleteUserSessionRegistrationParams{
		UserID:    userIDFromToken,
		SessionID: sessionID,
	}

	err = cfg.dbQueries.DeleteUserSessionRegistration(req.Context(), dbParams)
	if err != nil {
		logRequestError(req, "error deleting class registration", err)
		http.Error(w, "Error deleting class registration", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

func (cfg *apiCfg) middlewareLogin(w http.ResponseWriter, req *http.Request) {
	type parameters struct {
		Password string `json:"password"`
		Email    string `json:"email"`
	}

	w.Header().Set("Content-Type", "application/json")

	// decode JSON
	decoder := json.NewDecoder(req.Body)
	params := parameters{}
	err := decoder.Decode(&params)
	if err != nil {
		logRequestError(req, "error decoding login parameters", err)
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	if params.Email == "" {
		http.Error(w, "Email is required", http.StatusBadRequest)
		return
	}

	if params.Password == "" {
		http.Error(w, "Password is required", http.StatusBadRequest)
		return
	}

	// Grab User data via email
	userDB, err := cfg.dbQueries.QueryUserEmail(req.Context(), params.Email)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			logRequestError(req, "login user not found", err)
			http.Error(w, "User not found in DB", http.StatusNotFound)
			return
		}
		logRequestError(req, "error querying login user", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	// Check passwords match
	match, err := auth.CheckPasswordHash(params.Password, userDB.PasswordHash)
	if err != nil {
		logRequestError(req, "error checking password hash", err)
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}
	if !match {
		http.Error(w, "Incorrect Password", http.StatusUnauthorized)
		return
	}

	// Generate JWT - time.Duration defaults to nanoseconds (that was fun to learn)
	token, err := auth.MakeJWT(userDB.ID, cfg.tokenSecret, time.Duration(cfg.tokenDuration)*time.Second)
	if err != nil {
		logRequestError(req, "error generating login JWT", err)
		http.Error(w, "Unable to generate JWT", http.StatusInternalServerError)
		return
	}

	// Generate Refresh Token
	refreshToken := auth.MakeRefreshToken()
	// Insert Refresh Token into DB
	refreshTokenParams := database.CreateRefreshTokenParams{
		Token:  refreshToken,
		UserID: userDB.ID,
	}
	_, err = cfg.dbQueries.CreateRefreshToken(req.Context(), refreshTokenParams)
	if err != nil {
		logRequestError(req, "error creating refresh token", err)
		http.Error(w, "Unable to create refresh token", http.StatusInternalServerError)
		return
	}

	// Successful login - return user data w/o PW
	user := Login{
		ID:           userDB.ID,
		CreatedAt:    userDB.CreatedAt,
		UpdatedAt:    userDB.UpdatedAt,
		Email:        userDB.Email,
		Token:        token,
		RefreshToken: refreshToken,
	}

	dat, err := json.Marshal(user)
	if err != nil {
		logRequestError(req, "error marshaling login response to JSON", err)
		http.Error(w, "Internal server error - unable to marshal user data", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusOK)
	w.Write(dat)
	cfg.metrics.userLogins.Add(1)
}

func (cfg *apiCfg) middlewareTokenRefresh(w http.ResponseWriter, req *http.Request) {
	// Get Refresh Token from header
	passedToken, err := auth.GetBearerToken(*req)
	if err != nil || passedToken == "" {
		logRequestError(req, "missing refresh token", err)
		http.Error(w, "Auth Headers with Token Required", http.StatusUnauthorized)
		return
	}

	// Check Refresh Token Exists
	refreshTokenDB, err := cfg.dbQueries.QueryRefreshToken(req.Context(), passedToken)
	if errors.Is(err, sql.ErrNoRows) {
		logRequestError(req, "refresh token not found", err)
		http.Error(w, "Invalid refresh token", http.StatusUnauthorized)
		return
	}
	if err != nil {
		logRequestError(req, "error querying refresh token", err)
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}

	// Check Refresh Token not revoked / expired
	now := time.Now()
	if refreshTokenDB.RevokedAt.Valid {
		http.Error(w, "Token revoked", http.StatusUnauthorized)
		return
	}

	if now.After(refreshTokenDB.ExpiresAt) {
		http.Error(w, "Token expired", http.StatusUnauthorized)
		return
	}

	// Generate New JWT
	token, err := auth.MakeJWT(refreshTokenDB.UserID, cfg.tokenSecret, time.Duration(cfg.tokenDuration)*time.Second)
	if err != nil {
		logRequestError(req, "error generating refreshed JWT", err)
		http.Error(w, "Unable to generate JWT", http.StatusInternalServerError)
		return
	}

	type RespToken struct {
		Token string `json:"token"`
	}

	respBody := RespToken{
		Token: token,
	}

	dat, err := json.Marshal(respBody)
	if err != nil {
		logRequestError(req, "error marshaling refreshed token response to JSON", err)
		http.Error(w, "Unable to marshal token into JSON", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write(dat)
	cfg.metrics.tokenRefreshes.Add(1)
}

func (cfg *apiCfg) middlewareTokenRevoke(w http.ResponseWriter, req *http.Request) {
	// Get Refresh Token from header
	passedToken, err := auth.GetBearerToken(*req)
	if err != nil || passedToken == "" {
		logRequestError(req, "missing refresh token for revoke", err)
		http.Error(w, "Auth Headers with Token Required", http.StatusUnauthorized)
		return
	}

	// Check Refresh Token Exists
	refreshTokenDB, err := cfg.dbQueries.QueryRefreshToken(req.Context(), passedToken)
	if errors.Is(err, sql.ErrNoRows) {
		logRequestError(req, "revoke token not found", err)
		http.Error(w, "Invalid refresh token", http.StatusUnauthorized)
		return
	}
	if err != nil {
		logRequestError(req, "error querying refresh token for revoke", err)
		http.Error(w, "Database error", http.StatusInternalServerError)
		return
	}

	// Check Refresh Token not already revoked
	if refreshTokenDB.RevokedAt.Valid {
		http.Error(w, "Token already revoked", http.StatusBadRequest)
		return
	}

	// Revoke in DB
	err = cfg.dbQueries.RevokeRefreshToken(req.Context(), refreshTokenDB.Token)
	if err != nil {
		logRequestError(req, "error revoking refresh token", err)
		http.Error(w, "Error revoking token in internal DB", http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
	cfg.metrics.tokenRevokes.Add(1)
}

type User struct {
	ID        uuid.UUID `json:"user_id"`
	Email     string    `json:"email"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type Instructor struct {
	ID        uuid.UUID `json:"user_id"`
	Email     string    `json:"email"`
	Name      string    `json:"instructor_name"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type Login struct {
	ID           uuid.UUID `json:"id"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
	Email        string    `json:"email"`
	Token        string    `json:"token"`
	RefreshToken string    `json:"refresh_token"`
}

type Session struct {
	ID             uuid.UUID `json:"id"`
	CreatedAt      time.Time `json:"created_at"`
	UpdatedAt      time.Time `json:"updated_at"`
	StartTime      time.Time `json:"start_time"`
	EndTime        time.Time `json:"end_time"`
	InstructorID   uuid.UUID `json:"instructor_id"`
	InstructorName string    `json:"instructor_name,omitempty"`
	Difficulty     int32     `json:"difficulty"`
	ClassSize      int32     `json:"class_size"`
	Description    string    `json:"description"`
}

type ClassRegistration struct {
	UserID    uuid.UUID `json:"user_id"`
	SessionID uuid.UUID `json:"session_id"`
	CreatedAt time.Time `json:"created_at"`
	Status    string    `json:"status"`
}

func logRequestError(req *http.Request, message string, err error) {
	if err == nil {
		log.Printf(
			"method=%s path=%s pattern=%q message=%q",
			req.Method,
			req.URL.Path,
			req.Pattern,
			message,
		)
		return
	}

	log.Printf(
		"method=%s path=%s pattern=%q message=%q error=%v",
		req.Method,
		req.URL.Path,
		req.Pattern,
		message,
		err,
	)
}

func main() {
	// Load environment variables and parse to apiCfg
	godotenv.Load()

	var apiCfg apiCfg
	apiCfg.Port = os.Getenv("PORT")
	apiCfg.FilepathRoot = os.Getenv("FILEPATH_ROOT")
	apiCfg.InstructorCreationToken = os.Getenv("INSTRUCTOR_CREATION_TOKEN")
	apiCfg.AdminKey = os.Getenv("ADMIN_KEY")
	apiCfg.tokenDuration, _ = strconv.Atoi(os.Getenv("TOKEN_DURATION")) // Defaults to 3600 - one hour
	apiCfg.tokenSecret = os.Getenv("TOKEN_SECRET")
	apiCfg.dbURL = os.Getenv("DB_URL")
	apiCfg.metrics = apiMetrics{}      // struct to track api usage
	apiCfg.inDev = os.Getenv("IN_DEV") // track if in prod / dev - determines if certain endpoints are allowed

	// Open DB Connection
	db, err := sql.Open("postgres", apiCfg.dbURL)
	if err != nil {
		log.Printf("Failure to open connection to backend DB: %v", err)
		return
	}

	// This attribute allows the API to interact with DB methods
	apiCfg.dbQueries = *database.New(db)

	// Create a multiplexer to handle http server
	var mux = http.NewServeMux()
	filepathRoot := apiCfg.FilepathRoot
	if filepathRoot == "" {
		filepathRoot = "web"
	}
	fileServer := http.FileServer(http.Dir(filepathRoot))

	// Start Server
	server := &http.Server{
		Addr:    apiCfg.Port,
		Handler: mux,
	}

	// === API Endpoint Definitions ===
	// Check server health
	mux.HandleFunc("GET /api/health", func(w http.ResponseWriter, req *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		type StatusOKMSG struct {
			Status string `json:"status"`
		}
		response := StatusOKMSG{
			Status: "online",
		}
		data, err := json.Marshal(response)
		if err != nil {
			logRequestError(req, "error marshaling response to JSON", err)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}
		w.WriteHeader(http.StatusOK)
		w.Write(data)
	})

	// View metrics - admin only endpoint
	mux.HandleFunc("GET /api/metrics", func(w http.ResponseWriter, req *http.Request) {
		// Check admin key
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			logRequestError(req, "Error parsing token from request", err)
			http.Error(w, http.StatusText(http.StatusUnauthorized), http.StatusUnauthorized)
			return
		}

		if token != apiCfg.AdminKey {
			logRequestError(req, "Attempt to access metrics with incorrect admin key", err)
			http.Error(w, http.StatusText(http.StatusForbidden), http.StatusForbidden)
			return
		}

		// Request authorized - parse metrics data and return
		data, err := json.Marshal(apiCfg.metrics.snapshot())
		if err != nil {
			logRequestError(req, "error marshaling response to JSON", err)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(data)
	})

	// Reset the DB - used for DEV
	mux.HandleFunc("POST /api/reset", func(w http.ResponseWriter, req *http.Request) {
		if apiCfg.inDev != "true" {
			logRequestError(req, "attempt to reset database outside dev mode", nil)
			http.Error(w, http.StatusText(http.StatusForbidden), http.StatusForbidden)
			return
		}

		// Check admin key
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			logRequestError(req, "error parsing token from request", err)
			http.Error(w, http.StatusText(http.StatusUnauthorized), http.StatusUnauthorized)
			return
		}

		if token != apiCfg.AdminKey {
			logRequestError(req, "attempt to reset database with incorrect admin key", nil)
			http.Error(w, http.StatusText(http.StatusForbidden), http.StatusForbidden)
			return
		}

		// Reset dependents first
		err = apiCfg.dbQueries.RemoveRegistrations(req.Context())
		if err != nil {
			logRequestError(req, "error removing class registrations during reset", err)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}

		err = apiCfg.dbQueries.RemoveSessions(req.Context())
		if err != nil {
			logRequestError(req, "error removing sessions during reset", err)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}

		err = apiCfg.dbQueries.RemoveUsers(req.Context())
		if err != nil {
			logRequestError(req, "error removing users during reset", err)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}

		apiCfg.metrics.fileServerHits.Store(0)
		apiCfg.metrics.userCreationHits.Store(0)
		apiCfg.metrics.instructorCreationHits.Store(0)
		apiCfg.metrics.sessionCreationHits.Store(0)
		apiCfg.metrics.classRegistrationHits.Store(0)
		apiCfg.metrics.userLogins.Store(0)
		apiCfg.metrics.tokenRefreshes.Store(0)
		apiCfg.metrics.tokenRevokes.Store(0)

		w.WriteHeader(http.StatusNoContent)
	})

	// Get all Sessions from the DB
	mux.HandleFunc("GET /api/sessions", func(w http.ResponseWriter, req *http.Request) {
		// Check key is valid
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			logRequestError(req, "Error parsing token from request", err)
			http.Error(w, http.StatusText(http.StatusUnauthorized), http.StatusUnauthorized)
			return
		}

		// Returns user ID - not needed in this case
		_, err = auth.ValidateJWT(token, apiCfg.tokenSecret)
		if err != nil {
			logRequestError(req, "invalid class registration token", err)
			http.Error(w, http.StatusText(http.StatusUnauthorized), http.StatusUnauthorized)
			return
		}

		// Get data from the DB
		sessionsDB, err := apiCfg.dbQueries.GetAllSessionsWithInstructor(req.Context())
		if err != nil {
			logRequestError(req, "Error getting sessions data from the DB", err)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}

		// Parse data to a slice
		var sessionsSlice []Session
		for _, sesh := range sessionsDB {
			tmpSesh := Session{
				ID:             sesh.ID,
				CreatedAt:      sesh.CreatedAt,
				UpdatedAt:      sesh.UpdatedAt,
				StartTime:      sesh.StartTime,
				EndTime:        sesh.EndTime,
				InstructorID:   sesh.InstructorID,
				InstructorName: sesh.InstructorName,
				Difficulty:     sesh.Difficulty,
				ClassSize:      sesh.ClassSize,
				Description:    sesh.Description,
			}
			sessionsSlice = append(sessionsSlice, tmpSesh)
		}

		// Marshal data and return
		data, err := json.Marshal(sessionsSlice)
		if err != nil {
			logRequestError(req, "Error marshaling JSON data", err)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(data)
	})

	// Get Sessions from the DB by ID
	mux.HandleFunc("GET /api/sessions/{session_id}", func(w http.ResponseWriter, req *http.Request) {
		// Check key is valid
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			logRequestError(req, "Error parsing token from request", err)
			http.Error(w, http.StatusText(http.StatusUnauthorized), http.StatusUnauthorized)
			return
		}

		// Returns user ID - not needed in this case
		_, err = auth.ValidateJWT(token, apiCfg.tokenSecret)
		if err != nil {
			logRequestError(req, "invalid class registration token", err)
			http.Error(w, http.StatusText(http.StatusUnauthorized), http.StatusUnauthorized)
			return
		}

		// Get Session ID
		sessionID, err := uuid.Parse(req.PathValue("session_id"))
		if err != nil {
			logRequestError(req, "invalid session id for class registration", err)
			http.Error(w, "Invalid session id", http.StatusBadRequest)
			return
		}

		// Get data from the DB
		sessionsDB, err := apiCfg.dbQueries.QuerySessionIDWithInstructor(req.Context(), sessionID)
		if err != nil {
			if errors.Is(err, sql.ErrNoRows) {
				logRequestError(req, "session not found", err)
				http.Error(w, http.StatusText(http.StatusNotFound), http.StatusNotFound)
				return
			}

			logRequestError(req, "Error getting session data from the DB", err)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}

		// Parse data to a slice
		session := Session{
			ID:             sessionsDB.ID,
			CreatedAt:      sessionsDB.CreatedAt,
			UpdatedAt:      sessionsDB.UpdatedAt,
			StartTime:      sessionsDB.StartTime,
			EndTime:        sessionsDB.EndTime,
			InstructorID:   sessionsDB.InstructorID,
			InstructorName: sessionsDB.InstructorName,
			Difficulty:     sessionsDB.Difficulty,
			ClassSize:      sessionsDB.ClassSize,
			Description:    sessionsDB.Description,
		}

		// Marshal data and return
		data, err := json.Marshal(session)
		if err != nil {
			logRequestError(req, "Error marshaling JSON data", err)
			http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(data)
	})

	// Create User
	mux.HandleFunc("POST /api/users", apiCfg.middlewareCreateUser)

	// Create Instructor
	mux.HandleFunc("POST /api/instructors", apiCfg.middlewareCreateInstructor)

	// Create Session
	mux.HandleFunc("POST /api/sessions", apiCfg.middlewareCreateSession)

	// Register for Class
	mux.HandleFunc("POST /api/sessions/{session_id}/registrations", apiCfg.middlewareRegisterForClass)

	// Unregister from Class
	mux.HandleFunc("DELETE /api/sessions/{session_id}/registrations", apiCfg.middlewareUnregisterFromClass)

	// Login
	mux.HandleFunc("POST /api/login", apiCfg.middlewareLogin)

	// Refresh Access Token
	mux.HandleFunc("POST /api/refresh", apiCfg.middlewareTokenRefresh)

	// Revoke Refresh Token
	mux.HandleFunc("POST /api/revoke", apiCfg.middlewareTokenRevoke)

	// Serve the frontend from the web directory.
	mux.HandleFunc("GET /", func(w http.ResponseWriter, req *http.Request) {
		apiCfg.metrics.fileServerHits.Add(1)
		fileServer.ServeHTTP(w, req)
	})

	log.Fatal(server.ListenAndServe())
}
