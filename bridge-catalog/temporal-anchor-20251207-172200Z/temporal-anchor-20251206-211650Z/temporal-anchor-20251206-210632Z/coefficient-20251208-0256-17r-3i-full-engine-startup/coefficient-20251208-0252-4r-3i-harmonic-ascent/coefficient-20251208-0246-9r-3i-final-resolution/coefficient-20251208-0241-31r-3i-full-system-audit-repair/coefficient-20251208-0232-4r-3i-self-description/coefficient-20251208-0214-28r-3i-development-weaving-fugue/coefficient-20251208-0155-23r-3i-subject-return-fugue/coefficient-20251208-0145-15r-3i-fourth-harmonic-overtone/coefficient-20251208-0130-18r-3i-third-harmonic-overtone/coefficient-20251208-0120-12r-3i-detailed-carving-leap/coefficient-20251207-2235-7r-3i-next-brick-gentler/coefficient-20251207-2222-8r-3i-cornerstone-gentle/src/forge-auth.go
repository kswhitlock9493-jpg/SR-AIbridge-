package main

import (
"crypto/hmac"
"crypto/sha256"
"encoding/base64"
"encoding/json"
"fmt"
"os"
"time"
)

// ForgeToken represents an ephemeral runtime token
type ForgeToken struct {
NodeID    string    `json:"node_id"`
IssuedAt  time.Time `json:"issued_at"`
ExpiresAt time.Time `json:"expires_at"`
Scope     string    `json:"scope"`
Signature string    `json:"signature"`
}

// ForgeDominion handles Forge authentication and token management
type ForgeDominion struct {
rootKey []byte
}

// NewForgeDominion creates a new Forge Dominion auth handler
func NewForgeDominion() (*ForgeDominion, error) {
rootKeyStr := os.Getenv("FORGE_DOMINION_ROOT")
if rootKeyStr == "" {
return nil, fmt.Errorf("FORGE_DOMINION_ROOT not set")
}

rootKey, err := base64.URLEncoding.DecodeString(rootKeyStr)
if err != nil {
return nil, fmt.Errorf("invalid FORGE_DOMINION_ROOT: %w", err)
}

return &ForgeDominion{
rootKey: rootKey,
}, nil
}

// RequestToken generates a new ephemeral token for runtime operations
func (fd *ForgeDominion) RequestToken(nodeID string, scope string, ttl time.Duration) (*ForgeToken, error) {
now := time.Now()
token := &ForgeToken{
NodeID:    nodeID,
IssuedAt:  now,
ExpiresAt: now.Add(ttl),
Scope:     scope,
}

// Create signature
payload := fmt.Sprintf("%s:%s:%d:%s",
token.NodeID,
token.Scope,
token.IssuedAt.Unix(),
token.ExpiresAt.Unix(),
)

h := hmac.New(sha256.New, fd.rootKey)
h.Write([]byte(payload))
token.Signature = base64.URLEncoding.EncodeToString(h.Sum(nil))

return token, nil
}

// ValidateToken checks if a token is valid and not expired
func (fd *ForgeDominion) ValidateToken(token *ForgeToken) error {
// Check expiration
if time.Now().After(token.ExpiresAt) {
return fmt.Errorf("token expired at %s", token.ExpiresAt)
}

// Verify signature
payload := fmt.Sprintf("%s:%s:%d:%s",
token.NodeID,
token.Scope,
token.IssuedAt.Unix(),
token.ExpiresAt.Unix(),
)

h := hmac.New(sha256.New, fd.rootKey)
h.Write([]byte(payload))
expectedSig := base64.URLEncoding.EncodeToString(h.Sum(nil))

if token.Signature != expectedSig {
return fmt.Errorf("invalid token signature")
}

return nil
}

// RenewToken creates a new token based on an existing valid token
func (fd *ForgeDominion) RenewToken(oldToken *ForgeToken, ttl time.Duration) (*ForgeToken, error) {
// Validate old token first
if err := fd.ValidateToken(oldToken); err != nil {
return nil, fmt.Errorf("cannot renew invalid token: %w", err)
}

// Create new token with same scope
return fd.RequestToken(oldToken.NodeID, oldToken.Scope, ttl)
}

// SaveToken saves a token to a file for runtime use
func SaveToken(token *ForgeToken, filepath string) error {
data, err := json.MarshalIndent(token, "", "  ")
if err != nil {
return fmt.Errorf("failed to marshal token: %w", err)
}

if err := os.WriteFile(filepath, data, 0600); err != nil {
return fmt.Errorf("failed to write token file: %w", err)
}

return nil
}

// LoadToken loads a token from a file
func LoadToken(filepath string) (*ForgeToken, error) {
data, err := os.ReadFile(filepath)
if err != nil {
return nil, fmt.Errorf("failed to read token file: %w", err)
}

var token ForgeToken
if err := json.Unmarshal(data, &token); err != nil {
return nil, fmt.Errorf("failed to unmarshal token: %w", err)
}

return &token, nil
}

func main() {
// Example usage
fd, err := NewForgeDominion()
if err != nil {
fmt.Fprintf(os.Stderr, "Failed to initialize Forge Dominion: %v\n", err)
os.Exit(1)
}

// Request a new token
token, err := fd.RequestToken("bridge-runtime-001", "runtime:execute", 1*time.Hour)
if err != nil {
fmt.Fprintf(os.Stderr, "Failed to request token: %v\n", err)
os.Exit(1)
}

fmt.Printf("Generated token for node %s\n", token.NodeID)
fmt.Printf("Valid until: %s\n", token.ExpiresAt.Format(time.RFC3339))

// Save token
if err := SaveToken(token, "/tmp/forge_token.json"); err != nil {
fmt.Fprintf(os.Stderr, "Failed to save token: %v\n", err)
os.Exit(1)
}

fmt.Println("Token saved successfully")
}
