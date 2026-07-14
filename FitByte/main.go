package main

import (
	"database/sql"
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	auth "github.com/cantr1/internal"
	"github.com/cantr1/internal/database"
	"github.com/google/uuid"
	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
)

// --- Begin Struct Definitions
type apiCfg struct {
	Port              string
	FilepathRoot      string
	UserCreationToken string
	AdminKey          string
	dbQueries         database.Queries
	tokenDuration     int
	tokenSecret       string
}

type User struct {
	ID        uuid.UUID `json:"user_id"`
	Email     string    `json:"email"`
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

type SleepSession struct {
	ID            uuid.UUID     `json:"id"`
	CreatedAt     time.Time     `json:"created_at"`
	UpdatedAt     time.Time     `json:"updated_at"`
	SleepStart    time.Time     `json:"sleep_start"`
	SleepEnd      time.Time     `json:"sleep_end"`
	REMDuration   time.Duration `json:"rem_duration_mins"`
	LightDuration time.Duration `json:"light_duration_mins"`
	DeepDuration  time.Duration `json:"deep_duration_mins"`
	UserID        uuid.UUID     `json:"user_id"`
}

type ExerciseSession struct {
	ID           uuid.UUID `json:"id"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
	WorkoutStart time.Time `json:"workout_start"`
	WorkoutEnd   time.Time `json:"workout_end"`
	WorkoutName  string    `json:"workout_name"`
	Zone1Mins    int32     `json:"zone1_mins"`
	Zone2Mins    int32     `json:"zone2_mins"`
	Zone3Mins    int32     `json:"zone3_mins"`
	Strain       int32     `json:"strain"`
	UserID       uuid.UUID `json:"user_id"`
}

type MeditationSession struct {
	ID              uuid.UUID `json:"id"`
	CreatedAt       time.Time `json:"created_at"`
	UpdatedAt       time.Time `json:"updated_at"`
	MeditationStart time.Time `json:"meditation_start"`
	MeditationEnd   time.Time `json:"meditation_end"`
	StartingHr      int32     `json:"starting_hr"`
	EndingHr        int32     `json:"ending_hr"`
	UserID          uuid.UUID `json:"user_id"`
}

// --- End Struct Definitions

func main() {
	// Load Env Vars
	godotenv.Load()
	dbURL := os.Getenv("DB_URL")

	// open connection to database
	db, err := sql.Open("postgres", dbURL)
	if err != nil {
		log.Printf("Failure to open connection to backend DB: %v", err)
		return
	}

	// Construct apiCfg for interfacing with env vars and DB
	var apiCfg apiCfg
	apiCfg.Port = os.Getenv("PORT")
	apiCfg.FilepathRoot = os.Getenv("FILEPATH_ROOT")
	apiCfg.UserCreationToken = os.Getenv("USER_CREATION_TOKEN")
	apiCfg.AdminKey = os.Getenv("ADMIN_KEY")
	apiCfg.dbQueries = *database.New(db)
	apiCfg.tokenDuration, _ = strconv.Atoi(os.Getenv("TOKEN_DURATION")) // Defaults to 3600 - one hour
	apiCfg.tokenSecret = os.Getenv("TOKEN_SECRET")

	// Create a multiplexer
	var mux = http.NewServeMux()

	// --- Begin API Endpoint Definitions

	// Check health of API
	mux.HandleFunc("GET /api/healthy", func(w http.ResponseWriter, req *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		type statusOKMsg struct {
			Status string `json:"string"`
		}
		response := statusOKMsg{
			Status: "online/healthy",
		}
		data, err := json.Marshal(response)
		if err != nil {
			log.Printf("Error marshaling to JSON: %v", err)
			http.Error(w, "Error marshaling JSON", http.StatusInternalServerError)
			return
		}
		w.WriteHeader(http.StatusOK)
		w.Write(data)
	})

	// Create User in DB
	mux.HandleFunc("POST /api/users", func(w http.ResponseWriter, req *http.Request) {
		// Check Access Token in Request
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			log.Printf("Error parsing token: %v", err)
			http.Error(w, "Error parsing access token", http.StatusUnauthorized)
			return
		}
		if token != apiCfg.UserCreationToken {
			log.Printf("User creation request attempted w bad token")
			http.Error(w, "Access denied", http.StatusForbidden)
			return
		}

		// Set response header type
		w.Header().Set("Content-Type", "application/json")

		// Parse parameters from request
		type parameters struct {
			Email    string `json:"email"`
			Password string `json:"password"`
		}
		decoder := json.NewDecoder(req.Body)
		params := parameters{}
		err = decoder.Decode(&params)
		if err != nil {
			log.Printf("Error decoding parameters: %v", err)
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

		// Hash the user password for the DB
		hashedPW, err := auth.HashPassword(params.Password)
		if err != nil {
			log.Printf("Error hashing PW: %v", err)
			http.Error(w, "Error hashing user password", http.StatusInternalServerError)
			return
		}

		// Parse info into database struct
		dbParams := database.CreateUserParams{
			Email:        params.Email,
			PasswordHash: hashedPW,
		}

		// Create user in the DB
		userDB, err := apiCfg.dbQueries.CreateUser(req.Context(), dbParams)

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
			log.Printf("Error marshaling JSON into user struct: %v", err)
			http.Error(w, "Error marshaling user data to struct", http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusCreated)
		w.Write(data)
	})

	// Login w/ User PW
	mux.HandleFunc("POST /api/login", func(w http.ResponseWriter, req *http.Request) {
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
		userDB, err := apiCfg.dbQueries.QueryUserEmail(req.Context(), params.Email)
		if err != nil {
			if err == sql.ErrNoRows {
				http.Error(w, "User not found in DB", http.StatusNotFound)
				return
			}
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}

		// Check passwords match
		match, err := auth.CheckPasswordHash(params.Password, userDB.PasswordHash)
		if err != nil {
			http.Error(w, "Internal server error", http.StatusInternalServerError)
			return
		}
		if !match {
			http.Error(w, "Incorrect Password", http.StatusUnauthorized)
			return
		}

		// Generate JWT - time.Duration defaults to nanoseconds (that was fun to learn)
		token, err := auth.MakeJWT(userDB.ID, apiCfg.tokenSecret, time.Duration(apiCfg.tokenDuration)*time.Second)
		if err != nil {
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
		_, err = apiCfg.dbQueries.CreateRefreshToken(req.Context(), refreshTokenParams)

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
			http.Error(w, "Internal server error - unable to marshal user data", http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusOK)
		w.Write(dat)
	})

	// Refresh
	mux.HandleFunc("POST /api/refresh", func(w http.ResponseWriter, req *http.Request) {
		// Get Refresh Token from header
		passedToken, err := auth.GetBearerToken(*req)
		if err != nil || passedToken == "" {
			http.Error(w, "Auth Headers with Token Required", http.StatusBadRequest)
			return
		}

		// Check Refresh Token Exists
		refreshTokenDB, err := apiCfg.dbQueries.QueryRefreshToken(req.Context(), passedToken)
		if errors.Is(err, sql.ErrNoRows) {
			http.Error(w, "Invalid refresh token", http.StatusUnauthorized)
			return
		}
		if err != nil {
			log.Printf("Database error: %v", err)
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
		token, err := auth.MakeJWT(refreshTokenDB.UserID, apiCfg.tokenSecret, time.Duration(apiCfg.tokenDuration)*time.Second)
		if err != nil {
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
			http.Error(w, "Unable to marshal token into JSON", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(dat)
	})

	// Revoke
	mux.HandleFunc("POST /api/revoke", func(w http.ResponseWriter, req *http.Request) {
		// Get Refresh Token from header
		passedToken, err := auth.GetBearerToken(*req)
		if err != nil || passedToken == "" {
			http.Error(w, "Auth Headers with Token Required", http.StatusBadRequest)
			return
		}

		// Check Refresh Token Exists
		refreshTokenDB, err := apiCfg.dbQueries.QueryRefreshToken(req.Context(), passedToken)
		if errors.Is(err, sql.ErrNoRows) {
			http.Error(w, "Invalid refresh token", http.StatusUnauthorized)
			return
		}
		if err != nil {
			http.Error(w, "Database error", http.StatusInternalServerError)
			return
		}

		// Check Refresh Token not already revoked
		if refreshTokenDB.RevokedAt.Valid {
			http.Error(w, "Token already revoked", http.StatusBadRequest)
			return
		}

		// Revoke in DB
		err = apiCfg.dbQueries.RevokeRefreshToken(req.Context(), refreshTokenDB.Token)
		if err != nil {
			http.Error(w, "Error revoking token in internal DB", http.StatusInternalServerError)
			return
		}

		w.WriteHeader(http.StatusNoContent)
	})

	// Reset the Users DB
	mux.HandleFunc("DELETE /api/users", func(w http.ResponseWriter, req *http.Request) {
		// Check Admin Key in headers
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			log.Printf("Error parsing token: %v", err)
			http.Error(w, "Error parsing access token", http.StatusUnauthorized)
			return
		}
		if token != apiCfg.AdminKey {
			log.Printf("User creation request attempted w bad token")
			http.Error(w, "Access denied", http.StatusForbidden)
			return
		}

		err = apiCfg.dbQueries.RemoveUsers(req.Context())
		if err != nil {
			log.Printf("Error resetting users DB: %v", err)
			http.Error(w, "Error performing DB reset", http.StatusInternalServerError)
			return
		}

		log.Printf("Users DB has been reset")
		w.WriteHeader(http.StatusNoContent)
	})

	// - Sleep Functions -
	// Create Sleep Session
	mux.HandleFunc("POST /api/sleeps", func(w http.ResponseWriter, req *http.Request) {
		// Check Access Token in Request
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			log.Printf("Error parsing token: %v", err)
			http.Error(w, "Error parsing access token", http.StatusUnauthorized)
			return
		}

		// Check Token is Valid - Returns user ID
		userDBID, err := auth.ValidateJWT(token, apiCfg.tokenSecret)
		if err != nil {
			if err == auth.ErrInvalidToken {
				log.Printf("Invalid token use attempted - need to use refresh")
				http.Error(w, "Error - Invalid token", http.StatusUnauthorized)
				return
			}
			log.Printf("Error processing token: %v", err)
			http.Error(w, "Error processing token", http.StatusUnauthorized)
			return
		}

		// TODO / Improvements: Find a way to handle generating a refresh token with
		// JWT expired

		// Parse out the parameters for the entry
		type parameters struct {
			SleepStart    *time.Time     `json:"sleep_start"`
			SleepEnd      *time.Time     `json:"sleep_end"`
			REMDuration   *time.Duration `json:"rem_duration_mins"`
			LightDuration *time.Duration `json:"light_duration_mins"`
			DeepDuration  *time.Duration `json:"deep_duration_mins"`
		}

		decoder := json.NewDecoder(req.Body)
		params := parameters{}
		err = decoder.Decode(&params)
		if err != nil {
			log.Printf("Error decoding parameters: %v", err)
			http.Error(w, "Error decoding parameters", http.StatusBadRequest)
			return
		}

		// Check that all values exists and are not empty
		if params.SleepStart == nil || params.SleepStart.IsZero() {
			log.Printf("Error - sleep start required in request body")
			http.Error(w, "Sleep start required", http.StatusBadRequest)
			return
		}
		if params.SleepEnd == nil || params.SleepEnd.IsZero() {
			log.Printf("Error - sleep end required in request body")
			http.Error(w, "Sleep end required", http.StatusBadRequest)
			return
		}
		if !params.SleepEnd.After(*params.SleepStart) {
			log.Printf("Error - sleep end must be after sleep start")
			http.Error(w, "Sleep end must be after sleep start", http.StatusBadRequest)
			return
		}
		if params.REMDuration == nil {
			log.Printf("Error - REM duration required in request body")
			http.Error(w, "REM duration required", http.StatusBadRequest)
			return
		}
		if params.LightDuration == nil {
			log.Printf("Error - light duration required in request body")
			http.Error(w, "Light duration required", http.StatusBadRequest)
			return
		}
		if params.DeepDuration == nil {
			log.Printf("Error - deep duration required in request body")
			http.Error(w, "Deep duration required", http.StatusBadRequest)
			return
		}
		if *params.REMDuration < 0 || *params.LightDuration < 0 || *params.DeepDuration < 0 {
			log.Printf("Error - sleep stage durations cannot be negative")
			http.Error(w, "Sleep stage durations cannot be negative", http.StatusBadRequest)
			return
		}

		// Parse request body parameters into DB struct
		databaseParams := database.CreateSleepSessionParams{
			SleepStart:        *params.SleepStart,
			SleepEnd:          *params.SleepEnd,
			RemDurationMins:   int32(*params.REMDuration),
			LightDurationMins: int32(*params.LightDuration),
			DeepDurationMins:  int32(*params.DeepDuration),
			UserID:            userDBID,
		}

		// Push data to the DB
		data, err := apiCfg.dbQueries.CreateSleepSession(req.Context(), databaseParams)
		if err != nil {
			log.Printf("Error writing sleep session to the DB: %v", err)
			http.Error(w, "Error writing sleep session to the DB", http.StatusInternalServerError)
			return
		}

		// Parse data to the return struct
		dat, err := json.Marshal(data)
		if err != nil {
			log.Printf("Error marshaling sleep session to JSON: %v", err)
			http.Error(w, "Error marshaling sleep session to JSON", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		w.Write(dat)

	})

	// Get sleep data by user ID
	mux.HandleFunc("GET /api/sleeps", func(w http.ResponseWriter, req *http.Request) {
		// Check Access Token in Request
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			log.Printf("Error parsing token: %v", err)
			http.Error(w, "Error parsing access token", http.StatusUnauthorized)
			return
		}

		// Check Token is Valid - Returns user ID
		userDBID, err := auth.ValidateJWT(token, apiCfg.tokenSecret)
		if err != nil {
			if err == auth.ErrInvalidToken {
				log.Printf("Invalid token use attempted - need to use refresh")
				http.Error(w, "Error - Invalid token", http.StatusUnauthorized)
				return
			}
			log.Printf("Error processing token: %v", err)
			http.Error(w, "Error processing token", http.StatusUnauthorized)
			return
		}

		// Query DB by user ID
		DBData, err := apiCfg.dbQueries.QueryUserSleepSessions(req.Context(), userDBID)
		if err != nil {
			if errors.Is(err, sql.ErrNoRows) {
				log.Printf("Recieved query for user data that does not exist")
				http.Error(w, "User does not have sessions recorded", http.StatusNotFound)
				return
			}
			log.Printf("Error getting user data from DB: %v", err)
			http.Error(w, "Error getting User Data", http.StatusInternalServerError)
			return
		}

		// Parse the data from the DB into a slice of sessions
		var sleepSessions []SleepSession

		for _, session := range DBData {
			sesh := SleepSession{
				ID:            session.ID,
				CreatedAt:     session.CreatedAt,
				UpdatedAt:     session.UpdatedAt,
				SleepStart:    session.SleepStart,
				SleepEnd:      session.SleepEnd,
				REMDuration:   time.Duration(session.RemDurationMins),
				LightDuration: time.Duration(session.LightDurationMins),
				DeepDuration:  time.Duration(session.DeepDurationMins),
				UserID:        session.UserID,
			}
			sleepSessions = append(sleepSessions, sesh)
		}

		// Marshal data and return
		data, err := json.Marshal(sleepSessions)
		if err != nil {
			log.Printf("Error marshaling sleep data: %v", err)
			http.Error(w, "Error marshaling sleep data", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusAccepted)
		w.Write(data)
	})

	// Reset the Sleep DB
	mux.HandleFunc("DELETE /api/sleeps", func(w http.ResponseWriter, req *http.Request) {
		// Check Admin Key in headers
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			log.Printf("Error parsing token: %v", err)
			http.Error(w, "Error parsing access token", http.StatusUnauthorized)
			return
		}
		if token != apiCfg.AdminKey {
			log.Printf("User creation request attempted w bad token")
			http.Error(w, "Access denied", http.StatusForbidden)
			return
		}

		err = apiCfg.dbQueries.RemoveSleeps(req.Context())
		if err != nil {
			log.Printf("Error resetting sleep DB: %v", err)
			http.Error(w, "Error performing DB reset", http.StatusInternalServerError)
			return
		}

		log.Printf("Sleep DB has been reset")
		w.WriteHeader(http.StatusNoContent)
	})

	// - Exercise Functions -
	// Create Exercise Session
	mux.HandleFunc("POST /api/exercises", func(w http.ResponseWriter, req *http.Request) {
		// Check Access Token in Request
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			log.Printf("Error parsing token: %v", err)
			http.Error(w, "Error parsing access token", http.StatusUnauthorized)
			return
		}

		// Check Token is Valid - Returns user ID
		userDBID, err := auth.ValidateJWT(token, apiCfg.tokenSecret)
		if err != nil {
			if err == auth.ErrInvalidToken {
				log.Printf("Invalid token use attempted - need to use refresh")
				http.Error(w, "Error - Invalid token", http.StatusUnauthorized)
				return
			}
			log.Printf("Error processing token: %v", err)
			http.Error(w, "Error processing token", http.StatusUnauthorized)
			return
		}

		// Parse out the parameters for the entry
		type parameters struct {
			WorkoutStart *time.Time `json:"workout_start"`
			WorkoutEnd   *time.Time `json:"workout_end"`
			WorkoutName  string     `json:"workout_name"`
			Zone1Mins    *int32     `json:"zone1_mins"`
			Zone2Mins    *int32     `json:"zone2_mins"`
			Zone3Mins    *int32     `json:"zone3_mins"`
			Strain       *int32     `json:"strain"`
		}

		decoder := json.NewDecoder(req.Body)
		params := parameters{}
		err = decoder.Decode(&params)
		if err != nil {
			log.Printf("Error decoding parameters: %v", err)
			http.Error(w, "Error decoding parameters", http.StatusBadRequest)
			return
		}

		// Check that all values exist and are valid
		if params.WorkoutStart == nil || params.WorkoutStart.IsZero() {
			log.Printf("Error - workout start required in request body")
			http.Error(w, "Workout start required", http.StatusBadRequest)
			return
		}
		if params.WorkoutEnd == nil || params.WorkoutEnd.IsZero() {
			log.Printf("Error - workout end required in request body")
			http.Error(w, "Workout end required", http.StatusBadRequest)
			return
		}
		if !params.WorkoutEnd.After(*params.WorkoutStart) {
			log.Printf("Error - workout end must be after workout start")
			http.Error(w, "Workout end must be after workout start", http.StatusBadRequest)
			return
		}
		if params.WorkoutName == "" {
			log.Printf("Error - workout name required in request body")
			http.Error(w, "Workout name required", http.StatusBadRequest)
			return
		}
		if params.Zone1Mins == nil {
			log.Printf("Error - zone 1 minutes required in request body")
			http.Error(w, "Zone 1 minutes required", http.StatusBadRequest)
			return
		}
		if params.Zone2Mins == nil {
			log.Printf("Error - zone 2 minutes required in request body")
			http.Error(w, "Zone 2 minutes required", http.StatusBadRequest)
			return
		}
		if params.Zone3Mins == nil {
			log.Printf("Error - zone 3 minutes required in request body")
			http.Error(w, "Zone 3 minutes required", http.StatusBadRequest)
			return
		}
		if *params.Zone1Mins < 0 || *params.Zone2Mins < 0 || *params.Zone3Mins < 0 {
			log.Printf("Error - zone minutes cannot be negative")
			http.Error(w, "Zone minutes cannot be negative", http.StatusBadRequest)
			return
		}
		if params.Strain == nil {
			log.Printf("Error - strain required in request body")
			http.Error(w, "Strain required", http.StatusBadRequest)
			return
		}
		if *params.Strain < 0 || *params.Strain > 10 {
			log.Printf("Error - strain must be between 0 and 10")
			http.Error(w, "Strain must be between 0 and 10", http.StatusBadRequest)
			return
		}

		// Parse request body parameters into DB struct
		databaseParams := database.CreateExerciseSessionParams{
			WorkoutStart: *params.WorkoutStart,
			WorkoutEnd:   *params.WorkoutEnd,
			WorkoutName:  params.WorkoutName,
			Zone1Mins:    *params.Zone1Mins,
			Zone2Mins:    *params.Zone2Mins,
			Zone3Mins:    *params.Zone3Mins,
			Strain:       *params.Strain,
			UserID:       userDBID,
		}

		// Push data to the DB
		data, err := apiCfg.dbQueries.CreateExerciseSession(req.Context(), databaseParams)
		if err != nil {
			log.Printf("Error writing exercise session to the DB: %v", err)
			http.Error(w, "Error writing exercise session to the DB", http.StatusInternalServerError)
			return
		}

		exerciseSession := ExerciseSession{
			ID:           data.ID,
			CreatedAt:    data.CreatedAt,
			UpdatedAt:    data.UpdatedAt,
			WorkoutStart: data.WorkoutStart,
			WorkoutEnd:   data.WorkoutEnd,
			WorkoutName:  data.WorkoutName,
			Zone1Mins:    data.Zone1Mins,
			Zone2Mins:    data.Zone2Mins,
			Zone3Mins:    data.Zone3Mins,
			Strain:       data.Strain,
			UserID:       data.UserID,
		}

		// Parse data to the return struct
		dat, err := json.Marshal(exerciseSession)
		if err != nil {
			log.Printf("Error marshaling exercise session to JSON: %v", err)
			http.Error(w, "Error marshaling exercise session to JSON", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		w.Write(dat)
	})

	// Get exercise data by user ID
	mux.HandleFunc("GET /api/exercises", func(w http.ResponseWriter, req *http.Request) {
		// Check Access Token in Request
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			log.Printf("Error parsing token: %v", err)
			http.Error(w, "Error parsing access token", http.StatusUnauthorized)
			return
		}

		// Check Token is Valid - Returns user ID
		userDBID, err := auth.ValidateJWT(token, apiCfg.tokenSecret)
		if err != nil {
			if err == auth.ErrInvalidToken {
				log.Printf("Invalid token use attempted - need to use refresh")
				http.Error(w, "Error - Invalid token", http.StatusUnauthorized)
				return
			}
			log.Printf("Error processing token: %v", err)
			http.Error(w, "Error processing token", http.StatusUnauthorized)
			return
		}

		// Query DB by user ID
		DBData, err := apiCfg.dbQueries.QueryUserExercieSessions(req.Context(), userDBID)
		if err != nil {
			log.Printf("Error getting user exercise data from DB: %v", err)
			http.Error(w, "Error getting User Exercise Data", http.StatusInternalServerError)
			return
		}

		// Parse the data from the DB into a slice of sessions
		exerciseSessions := []ExerciseSession{}

		for _, session := range DBData {
			sesh := ExerciseSession{
				ID:           session.ID,
				CreatedAt:    session.CreatedAt,
				UpdatedAt:    session.UpdatedAt,
				WorkoutStart: session.WorkoutStart,
				WorkoutEnd:   session.WorkoutEnd,
				WorkoutName:  session.WorkoutName,
				Zone1Mins:    session.Zone1Mins,
				Zone2Mins:    session.Zone2Mins,
				Zone3Mins:    session.Zone3Mins,
				Strain:       session.Strain,
				UserID:       session.UserID,
			}
			exerciseSessions = append(exerciseSessions, sesh)
		}

		// Marshal data and return
		data, err := json.Marshal(exerciseSessions)
		if err != nil {
			log.Printf("Error marshaling exercise data: %v", err)
			http.Error(w, "Error marshaling exercise data", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(data)
	})

	// Reset the Exercise DB
	mux.HandleFunc("DELETE /api/exercises", func(w http.ResponseWriter, req *http.Request) {
		// Check Admin Key in headers
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			log.Printf("Error parsing token: %v", err)
			http.Error(w, "Error parsing access token", http.StatusUnauthorized)
			return
		}
		if token != apiCfg.AdminKey {
			log.Printf("Exercise reset request attempted w bad token")
			http.Error(w, "Access denied", http.StatusForbidden)
			return
		}

		err = apiCfg.dbQueries.RemoveExercises(req.Context())
		if err != nil {
			log.Printf("Error resetting exercise DB: %v", err)
			http.Error(w, "Error performing DB reset", http.StatusInternalServerError)
			return
		}

		log.Printf("Exercise DB has been reset")
		w.WriteHeader(http.StatusNoContent)
	})

	// - Meditation Functions -
	// Create Meditation Session
	mux.HandleFunc("POST /api/meditations", func(w http.ResponseWriter, req *http.Request) {
		// Check Access Token in Request
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			log.Printf("Error parsing token: %v", err)
			http.Error(w, "Error parsing access token", http.StatusUnauthorized)
			return
		}

		// Check Token is Valid - Returns user ID
		userDBID, err := auth.ValidateJWT(token, apiCfg.tokenSecret)
		if err != nil {
			if err == auth.ErrInvalidToken {
				log.Printf("Invalid token use attempted - need to use refresh")
				http.Error(w, "Error - Invalid token", http.StatusUnauthorized)
				return
			}
			log.Printf("Error processing token: %v", err)
			http.Error(w, "Error processing token", http.StatusUnauthorized)
			return
		}

		// Parse out the parameters for the entry
		type parameters struct {
			MeditationStart *time.Time `json:"meditation_start"`
			MeditationEnd   *time.Time `json:"meditation_end"`
			StartingHr      *int32     `json:"starting_hr"`
			EndingHr        *int32     `json:"ending_hr"`
		}

		decoder := json.NewDecoder(req.Body)
		params := parameters{}
		err = decoder.Decode(&params)
		if err != nil {
			log.Printf("Error decoding parameters: %v", err)
			http.Error(w, "Error decoding parameters", http.StatusBadRequest)
			return
		}

		// Check that all values exist and are valid
		if params.MeditationStart == nil || params.MeditationStart.IsZero() {
			log.Printf("Error - meditation start required in request body")
			http.Error(w, "Meditation start required", http.StatusBadRequest)
			return
		}
		if params.MeditationEnd == nil || params.MeditationEnd.IsZero() {
			log.Printf("Error - meditation end required in request body")
			http.Error(w, "Meditation end required", http.StatusBadRequest)
			return
		}
		if !params.MeditationEnd.After(*params.MeditationStart) {
			log.Printf("Error - meditation end must be after meditation start")
			http.Error(w, "Meditation end must be after meditation start", http.StatusBadRequest)
			return
		}
		if params.StartingHr == nil {
			log.Printf("Error - starting heart rate required in request body")
			http.Error(w, "Starting heart rate required", http.StatusBadRequest)
			return
		}
		if params.EndingHr == nil {
			log.Printf("Error - ending heart rate required in request body")
			http.Error(w, "Ending heart rate required", http.StatusBadRequest)
			return
		}
		if *params.StartingHr < 40 || *params.StartingHr > 180 || *params.EndingHr < 40 || *params.EndingHr > 180 {
			log.Printf("Error - meditation heart rates must be between 40 and 180")
			http.Error(w, "Meditation heart rates must be between 40 and 180", http.StatusBadRequest)
			return
		}

		// Parse request body parameters into DB struct
		databaseParams := database.CreateMeditationSessionParams{
			MeditationStart: *params.MeditationStart,
			MeditationEnd:   *params.MeditationEnd,
			StartingHr:      *params.StartingHr,
			EndingHr:        *params.EndingHr,
			UserID:          userDBID,
		}

		// Push data to the DB
		data, err := apiCfg.dbQueries.CreateMeditationSession(req.Context(), databaseParams)
		if err != nil {
			log.Printf("Error writing meditation session to the DB: %v", err)
			http.Error(w, "Error writing meditation session to the DB", http.StatusInternalServerError)
			return
		}

		meditationSession := MeditationSession{
			ID:              data.ID,
			CreatedAt:       data.CreatedAt,
			UpdatedAt:       data.UpdatedAt,
			MeditationStart: data.MeditationStart,
			MeditationEnd:   data.MeditationEnd,
			StartingHr:      data.StartingHr,
			EndingHr:        data.EndingHr,
			UserID:          data.UserID,
		}

		// Parse data to the return struct
		dat, err := json.Marshal(meditationSession)
		if err != nil {
			log.Printf("Error marshaling meditation session to JSON: %v", err)
			http.Error(w, "Error marshaling meditation session to JSON", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusCreated)
		w.Write(dat)
	})

	// Get meditation data by user ID
	mux.HandleFunc("GET /api/meditations", func(w http.ResponseWriter, req *http.Request) {
		// Check Access Token in Request
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			log.Printf("Error parsing token: %v", err)
			http.Error(w, "Error parsing access token", http.StatusUnauthorized)
			return
		}

		// Check Token is Valid - Returns user ID
		userDBID, err := auth.ValidateJWT(token, apiCfg.tokenSecret)
		if err != nil {
			if err == auth.ErrInvalidToken {
				log.Printf("Invalid token use attempted - need to use refresh")
				http.Error(w, "Error - Invalid token", http.StatusUnauthorized)
				return
			}
			log.Printf("Error processing token: %v", err)
			http.Error(w, "Error processing token", http.StatusUnauthorized)
			return
		}

		// Query DB by user ID
		DBData, err := apiCfg.dbQueries.QueryUserMeditationSessions(req.Context(), userDBID)
		if err != nil {
			log.Printf("Error getting user meditation data from DB: %v", err)
			http.Error(w, "Error getting User Meditation Data", http.StatusInternalServerError)
			return
		}

		// Parse the data from the DB into a slice of sessions
		meditationSessions := []MeditationSession{}

		for _, session := range DBData {
			sesh := MeditationSession{
				ID:              session.ID,
				CreatedAt:       session.CreatedAt,
				UpdatedAt:       session.UpdatedAt,
				MeditationStart: session.MeditationStart,
				MeditationEnd:   session.MeditationEnd,
				StartingHr:      session.StartingHr,
				EndingHr:        session.EndingHr,
				UserID:          session.UserID,
			}
			meditationSessions = append(meditationSessions, sesh)
		}

		// Marshal data and return
		data, err := json.Marshal(meditationSessions)
		if err != nil {
			log.Printf("Error marshaling meditation data: %v", err)
			http.Error(w, "Error marshaling meditation data", http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write(data)
	})

	// Reset the Meditation DB
	mux.HandleFunc("DELETE /api/meditations", func(w http.ResponseWriter, req *http.Request) {
		// Check Admin Key in headers
		token, err := auth.GetBearerToken(*req)
		if err != nil {
			log.Printf("Error parsing token: %v", err)
			http.Error(w, "Error parsing access token", http.StatusUnauthorized)
			return
		}
		if token != apiCfg.AdminKey {
			log.Printf("Meditation reset request attempted w bad token")
			http.Error(w, "Access denied", http.StatusForbidden)
			return
		}

		err = apiCfg.dbQueries.RemoveMeditations(req.Context())
		if err != nil {
			log.Printf("Error resetting meditation DB: %v", err)
			http.Error(w, "Error performing DB reset", http.StatusInternalServerError)
			return
		}

		log.Printf("Meditation DB has been reset")
		w.WriteHeader(http.StatusNoContent)
	})

	// --- Web Application Endpoint

	mux.HandleFunc("GET /{$}", func(w http.ResponseWriter, req *http.Request) {
		http.Redirect(w, req, "/web/", http.StatusSeeOther)
	})

	mux.Handle("/web/", http.StripPrefix("/web/", http.FileServer(http.Dir(apiCfg.FilepathRoot))))

	// --- End API Endpoint Definitions

	// Start Server
	server := &http.Server{
		Addr:    apiCfg.Port,
		Handler: mux,
	}

	log.Fatal(server.ListenAndServe())
}
