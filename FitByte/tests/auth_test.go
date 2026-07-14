package tests

import (
	"testing"

	auth "github.com/cantr1/internal"
)

func TestFailCreateHash(t *testing.T) {
	password := "12345"
	_, err := auth.HashPassword(password)
	if err != nil {
		t.Errorf("Unable to create hashed PW: %v", err)
	}
}

func TestHashMatch(t *testing.T) {
	password := "12345"
	hashed_password, err := auth.HashPassword(password)
	if err != nil {
		t.Errorf("Unable to create hashed PW: %v", err)
	}
	match, err := auth.CheckPasswordHash(password, hashed_password)
	if err != nil {
		t.Errorf("Unable to run password match")
	}
	if !match {
		t.Errorf("Passwords do not match")
	}
}

func TestBadHashMatch(t *testing.T) {
	password := "12345"
	hashed_password, err := auth.HashPassword(password)
	if err != nil {
		t.Errorf("Unable to create hashed PW: %v", err)
	}
	match, err := auth.CheckPasswordHash("54321", hashed_password)
	if err != nil {
		t.Errorf("Unable to run password match")
	}
	if match {
		t.Errorf("Passwords match when they should not!")
	}
}