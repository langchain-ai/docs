// :snippet-start: resolve-evaluators-go
package main

import (
	"context"
	"fmt"
	"time"

	"github.com/langchain-ai/langsmith-go"
)

func main() {
	ctx := context.Background()
	client := langsmith.NewClient()
	evaluators := langsmith.NewEvaluatorAddress()
	// :remove-start:
	// Evaluator traces go to the workspace's project named "evaluators".
	if _, err := client.Sessions.New(ctx, langsmith.SessionNewParams{
		Name:   langsmith.F("evaluators"),
		Upsert: langsmith.F(true),
	}); err != nil {
		panic(err.Error())
	}
	// :remove-end:

	project, err := client.Sessions.Resolve(ctx, langsmith.NewSessionResolveParams(evaluators))
	if err != nil {
		panic(err.Error())
	}

	runs, err := client.Runs.QueryV2(ctx, langsmith.RunQueryV2Params{
		ProjectIDs:   langsmith.F([]string{project.SessionID}),
		MinStartTime: langsmith.F(time.Now().UTC().AddDate(0, -1, 0)),
	})
	if err != nil {
		panic(err.Error())
	}
	for _, run := range runs.Items {
		fmt.Println(run.ID)
	}
	// :remove-start:
	fmt.Println("✓ resolve-evaluators validated")
	// :remove-end:
}

// :snippet-end:
