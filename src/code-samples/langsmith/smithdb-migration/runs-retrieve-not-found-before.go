// :snippet-start: runs-retrieve-not-found-before-go
// :codegroup-tab: Before
package main

import (
	"context"
	"errors"
	"fmt"
	// :remove-start:
	"crypto/rand"
	// :remove-end:

	"github.com/langchain-ai/langsmith-go"
)

// :remove-start:
func main() {
// :remove-end:
ctx := context.Background()
client := langsmith.NewClient()

runID := "<run-id>"
// :remove-start:
b := make([]byte, 16)
_, _ = rand.Read(b)
b[6] = (b[6] & 0x0f) | 0x40
b[8] = (b[8] & 0x3f) | 0x80
runID = fmt.Sprintf("%x-%x-%x-%x-%x", b[0:4], b[4:6], b[6:8], b[8:10], b[10:16])
// :remove-end:
_, err := client.Runs.Get(ctx, runID, langsmith.RunGetParams{})
if err != nil {
	var apiErr *langsmith.Error
	if errors.As(err, &apiErr) && apiErr.StatusCode == 404 {
		fmt.Printf("Run %s not found\n", runID)
	} else {
		panic(err)
	}
}
// :remove-start:
}

// :remove-end:
// :snippet-end:
