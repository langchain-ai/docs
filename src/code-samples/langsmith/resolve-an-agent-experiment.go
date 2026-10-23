// :snippet-start: resolve-experiment-go
package main

import (
	"context"
	"fmt"
	"time"

	"github.com/langchain-ai/langsmith-go"
	// :remove-start:
	"github.com/google/uuid"
	// :remove-end:
)

func main() {
	ctx := context.Background()
	client := langsmith.NewClient()
	experimentID := "<experiment-id>"
	// :remove-start:
	dataset, err := client.Datasets.New(ctx, langsmith.DatasetNewParams{
		Name: langsmith.F("docs-resolve-an-agent-" + uuid.NewString()[:8]),
	})
	if err != nil {
		panic(err.Error())
	}
	seeded, err := client.Sessions.New(ctx, langsmith.SessionNewParams{
		Name:               langsmith.F("docs-resolve-an-agent-" + uuid.NewString()[:8]),
		ReferenceDatasetID: langsmith.F(dataset.ID),
	})
	if err != nil {
		panic(err.Error())
	}
	experimentID = seeded.ID
	// :remove-end:
	experiment, err := langsmith.NewExperimentAddress(experimentID)
	if err != nil {
		panic(err.Error())
	}

	project, err := client.Sessions.Resolve(ctx, langsmith.NewSessionResolveParams(experiment))
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
	if err := client.Sessions.Delete(ctx, experimentID); err != nil {
		panic(err.Error())
	}
	if _, err := client.Datasets.Delete(ctx, dataset.ID); err != nil {
		panic(err.Error())
	}
	fmt.Println("✓ resolve-experiment validated")
	// :remove-end:
}

// :snippet-end:
