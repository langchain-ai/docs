// :snippet-start: runs-list-from-queue-after-go
// :codegroup-tab: After
package main

import (
	"context"
	"fmt"
	"time"

	"github.com/langchain-ai/langsmith-go"
)

// :remove-start:
func seedQueue(ctx context.Context, client *langsmith.Client) string {
	sessions, err := client.Sessions.List(ctx, langsmith.SessionListParams{
		Name:  langsmith.F("default"),
		Limit: langsmith.F(int64(1)),
	})
	if err != nil {
		panic(err.Error())
	}
	found, err := client.Runs.QueryV2(ctx, langsmith.RunQueryV2Params{
		ProjectIDs:   langsmith.F([]string{sessions.Items[0].ID}),
		MinStartTime: langsmith.F(time.Now().UTC().AddDate(0, 0, -30)),
		PageSize:     langsmith.F(int64(1)),
	})
	if err != nil {
		panic(err.Error())
	}
	if len(found.Items) == 0 {
		panic("expected at least one run in the 'default' project")
	}
	queue, err := client.AnnotationQueues.AnnotationQueues(ctx, langsmith.AnnotationQueueAnnotationQueuesParams{
		Name: langsmith.F("docs-smithdb-migration-" + time.Now().Format("20060102150405.000000000")),
	})
	if err != nil {
		panic(err.Error())
	}
	_, err = client.AnnotationQueues.Runs.New(ctx, queue.ID, langsmith.AnnotationQueueRunNewParams{
		Body: langsmith.AnnotationQueueRunNewParamsBodyRunsUuidArray([]string{found.Items[0].ID}),
	})
	if err != nil {
		panic(err.Error())
	}
	return queue.ID
}

func main() {
// :remove-end:
ctx := context.Background()
client := langsmith.NewClient()

queueID := "<queue-id>"
// :remove-start:
queueID = seedQueue(ctx, client)
names := []string{}
// :remove-end:
count, err := client.AnnotationQueues.Items.GetCount(ctx, queueID, langsmith.AnnotationQueueItemGetCountParams{
	Status: langsmith.F("needs_my_review"),
})
if err != nil {
	panic(err.Error())
}
fmt.Println(count.Count)

// Items carry the run's lookup keys, not its contents.
iter := client.AnnotationQueues.Items.ListAutoPaging(ctx, queueID, langsmith.AnnotationQueueItemListParams{
	Status:   langsmith.F(langsmith.AnnotationQueueItemListParamsStatusNeedsMyReview),
	ItemType: langsmith.F(langsmith.AnnotationQueueItemListParamsItemTypeRun),
})
for iter.Next() {
	item := iter.Current()
	startTime, err := time.Parse(time.RFC3339Nano, item.StartTime)
	if err != nil {
		panic(err.Error())
	}
	run, err := client.Runs.GetV2(ctx, item.RunID, langsmith.RunGetV2Params{
		ProjectID: langsmith.F(item.ProjectID),
		StartTime: langsmith.F(startTime),
		Selects: langsmith.F([]langsmith.RunGetV2ParamsSelect{
			langsmith.RunGetV2ParamsSelectName,
			langsmith.RunGetV2ParamsSelectStatus,
			langsmith.RunGetV2ParamsSelectInputs,
			langsmith.RunGetV2ParamsSelectOutputs,
		}),
	})
	if err != nil {
		panic(err.Error())
	}
	fmt.Println(run.Name, run.Status)
	// :remove-start:
	names = append(names, run.Name)
	// :remove-end:
}
if err := iter.Err(); err != nil {
	panic(err.Error())
}
// :remove-start:
if count.Count != 1 {
	panic(fmt.Sprintf("expected count 1, got %d", count.Count))
}
if len(names) != 1 || names[0] == "" {
	panic(fmt.Sprintf("expected 1 named run, got %v", names))
}
fmt.Println("✓ runs-list-from-queue-after validated")
}

// :remove-end:
// :snippet-end:
