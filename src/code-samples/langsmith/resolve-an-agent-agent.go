// :snippet-start: resolve-agent-go
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
	agent, err := langsmith.NewAgentAddress("checkout", "production")
	if err != nil {
		panic(err.Error())
	}
	// :remove-start:
	seedAgent(ctx, client, agent)
	// :remove-end:

	project, err := client.Sessions.Resolve(ctx, langsmith.NewSessionResolveParams(agent))
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
	fmt.Println("✓ resolve-agent validated")
	// :remove-end:
}

// :snippet-end:

// :remove-start:
// An agent exists once it has received a trace, and ingestion is asynchronous.
func seedAgent(ctx context.Context, client *langsmith.Client, agent langsmith.AgentAddress) {
	id := uuid.New()
	start := time.Now().UTC()
	order := fmt.Sprintf("%s%06dZ%s", start.Format("20060102T150405"), start.Nanosecond()/1000, id)
	if err := client.CreateRun(&langsmith.RunCreate{
		ID: id, TraceID: id, Name: "docs-resolve-an-agent-seed", RunType: "chain",
		StartTime: start, DottedOrder: order, Address: agent, Inputs: map[string]any{},
	}); err != nil {
		panic(err.Error())
	}
	if err := client.UpdateRun(&langsmith.RunUpdate{
		ID: id, TraceID: id, DottedOrder: order, EndTime: time.Now().UTC(),
		Outputs: map[string]any{},
	}); err != nil {
		panic(err.Error())
	}
	client.Close()

	deadline := time.Now().Add(120 * time.Second)
	for {
		_, err := client.Sessions.Resolve(ctx, langsmith.NewSessionResolveParams(agent))
		if err == nil {
			return
		}
		if time.Now().After(deadline) {
			panic(err.Error())
		}
		time.Sleep(3 * time.Second)
	}
}

// :remove-end:
