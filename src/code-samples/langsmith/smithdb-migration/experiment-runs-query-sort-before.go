// :snippet-start: experiment-runs-query-sort-before-go
// :codegroup-tab: Before
package main

import (
	"context"

	"github.com/langchain-ai/langsmith-go"
	// :remove-start:
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/langchain-ai/langsmith-go/shared"
	// :remove-end:
)

// :remove-start:
func setupFixture(ctx context.Context, client *langsmith.Client) (string, string) {
	fixtureDatasetName := "docs-experiment-runs-query-fixture"
	existingDatasets, err := client.Datasets.List(ctx, langsmith.DatasetListParams{
		Name: langsmith.F(fixtureDatasetName),
	})
	if err != nil {
		panic(err.Error())
	}
	var datasetID string
	if len(existingDatasets.Items) > 0 {
		datasetID = existingDatasets.Items[0].ID
	} else {
		dataset, err := client.Datasets.New(ctx, langsmith.DatasetNewParams{
			Name: langsmith.F(fixtureDatasetName),
		})
		if err != nil {
			panic(err.Error())
		}
		datasetID = dataset.ID

		qa := [][2]string{{"2 + 2", "4"}, {"3 + 3", "6"}, {"4 + 4", "9"}}
		for _, pair := range qa {
			_, err := client.Examples.New(ctx, langsmith.ExampleNewParams{
				DatasetID: langsmith.F(datasetID),
				Inputs:    langsmith.F(map[string]interface{}{"question": pair[0]}),
				Outputs:   langsmith.F(map[string]interface{}{"answer": pair[1]}),
			})
			if err != nil {
				panic(err.Error())
			}
		}
	}

	// The experiment is shared across every experiment-runs-query sample (this
	// file and its siblings): created once, ever, and reused afterward so the
	// suite doesn't spend a real evaluation run per file.
	experimentName := "docs-experiment-runs-query-fixture-experiment"
	existingSessions, err := client.Sessions.List(ctx, langsmith.SessionListParams{
		Name: langsmith.F(experimentName),
	})
	if err != nil {
		panic(err.Error())
	}
	if len(existingSessions.Items) > 0 {
		return datasetID, existingSessions.Items[0].ID
	}

	examples, err := client.Examples.List(ctx, langsmith.ExampleListParams{
		Dataset: langsmith.F(datasetID),
	})
	if err != nil {
		panic(err.Error())
	}

	session, err := client.Sessions.New(ctx, langsmith.SessionNewParams{
		Name:               langsmith.F(experimentName),
		ReferenceDatasetID: langsmith.F(datasetID),
	})
	if err != nil {
		panic(err.Error())
	}
	experimentID := session.ID

	now := time.Now().Format(time.RFC3339)
	for _, example := range examples.Items {
		question, _ := example.Inputs["question"].(string)
		var a, b int
		fmt.Sscanf(question, "%d + %d", &a, &b)
		answer := fmt.Sprintf("%d", a+b)

		runID := uuid.New().String()
		_, err := client.Runs.New(ctx, langsmith.RunNewParams{
			RunIngest: langsmith.RunIngestParam{
				ID:                 langsmith.F(runID),
				Name:               langsmith.F("target"),
				RunType:            langsmith.F(langsmith.RunIngestRunTypeChain),
				SessionID:          langsmith.F(experimentID),
				ReferenceExampleID: langsmith.F(example.ID),
				Inputs:             langsmith.F(example.Inputs),
				Outputs:            langsmith.F(map[string]interface{}{"answer": answer}),
				StartTime:          langsmith.F(now),
				EndTime:            langsmith.F(now),
			},
		})
		if err != nil {
			panic(err.Error())
		}

		score := 0.0
		if referenceAnswer, ok := example.Outputs["answer"].(string); ok && answer == referenceAnswer {
			score = 1.0
		}
		_, err = client.Feedback.New(ctx, langsmith.FeedbackNewParams{
			FeedbackCreateSchema: langsmith.FeedbackCreateSchemaParam{
				Key:   langsmith.F("correctness"),
				RunID: langsmith.F(runID),
				Score: langsmith.F[langsmith.FeedbackCreateSchemaScoreUnionParam](shared.UnionFloat(score)),
			},
		})
		if err != nil {
			panic(err.Error())
		}
	}
	return datasetID, experimentID
}

func main() {
// :remove-end:
ctx := context.Background()
client := langsmith.NewClient()
// :remove-start:
datasetID, experimentID := setupFixture(ctx, client)
// :remove-end:
examplesWithRuns, err := client.Datasets.Runs.Query(ctx, datasetID, langsmith.DatasetRunQueryParams{
	SessionIDs: langsmith.F([]string{experimentID}),
	SortParams: langsmith.F(langsmith.SortParamsForRunsComparisonView{
		SortBy:    langsmith.F("correctness"),
		SortOrder: langsmith.F(langsmith.SortParamsForRunsComparisonViewSortOrderAsc),
	}),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
_ = examplesWithRuns
}
// :remove-end:
// :snippet-end:
