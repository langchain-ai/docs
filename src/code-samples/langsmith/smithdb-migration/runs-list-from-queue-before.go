// :snippet-start: runs-list-from-queue-before-go
// :codegroup-tab: Before
package main

import (
	"context"
	"fmt"
	// :remove-start:
	"time"
	// :remove-end:

	"github.com/langchain-ai/langsmith-go"
)

// :remove-start:
func seedQueue(ctx context.Context, client *langsmith.Client) (string, string) {
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
	return queue.ID, found.Items[0].ID
}

func main() {
// :remove-end:
ctx := context.Background()
client := langsmith.NewClient()

queueID := "<queue-id>"
// :remove-start:
queueID, seededRunID := seedQueue(ctx, client)
// :remove-end:
size, err := client.AnnotationQueues.GetSize(ctx, queueID, langsmith.AnnotationQueueGetSizeParams{
	Status: langsmith.F(langsmith.AnnotationQueueGetSizeParamsStatusNeedsMyReview),
})
if err != nil {
	panic(err.Error())
}
fmt.Println(size.Size)

runs, err := client.AnnotationQueues.Runs.List(ctx, queueID, langsmith.AnnotationQueueRunListParams{
	Status: langsmith.F(langsmith.AnnotationQueueRunListParamsStatusNeedsMyReview),
})
if err != nil {
	panic(err.Error())
}
for _, run := range *runs {
	fmt.Println(run.Name)
}

firstRun, err := client.AnnotationQueues.GetRun(ctx, queueID, 0, langsmith.AnnotationQueueGetRunParams{})
if err != nil {
	panic(err.Error())
}
// :remove-start:
if size.Size != 1 {
	panic(fmt.Sprintf("expected size 1, got %d", size.Size))
}
if len(*runs) != 1 {
	panic(fmt.Sprintf("expected 1 run, got %d", len(*runs)))
}
if firstRun.ID != seededRunID {
	panic("index 0 returned a different run")
}
fmt.Println("✓ runs-list-from-queue-before validated")
}

// :remove-end:
// :snippet-end:
