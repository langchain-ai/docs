///usr/bin/env jbang "$0" "$@" ; exit $?
//DEPS com.langchain.smith:langsmith-java:0.1.0-alpha.25
//DEPS com.openai:openai-java:4.30.0

// :snippet-start: run-tree-example-java
// :codegroup-tab: Java
import com.langchain.smith.client.LangsmithClient;
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient;
import com.langchain.smith.tracing.RunTree;
import com.langchain.smith.tracing.RunType;
import com.langchain.smith.tracing.TraceConfig;
import com.openai.client.OpenAIClient;
import com.openai.client.okhttp.OpenAIOkHttpClient;
import com.openai.models.ChatModel;
import com.openai.models.chat.completions.ChatCompletion;
import com.openai.models.chat.completions.ChatCompletionCreateParams;
import com.openai.models.chat.completions.ChatCompletionMessageParam;
import com.openai.models.chat.completions.ChatCompletionSystemMessageParam;
import com.openai.models.chat.completions.ChatCompletionUserMessageParam;
import java.time.Instant;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class RunTreeExample {
    public static void main(String[] args) throws InterruptedException {
        // :remove-start:
        if (System.getenv("LANGSMITH_API_KEY") == null
                || System.getenv("LANGSMITH_API_KEY").isBlank()
                || System.getenv("OPENAI_API_KEY") == null
                || System.getenv("OPENAI_API_KEY").isBlank()) {
            System.out.println(
                    "[run-tree-example] Skipping (LANGSMITH_API_KEY and OPENAI_API_KEY required).");
            return;
        }
        // :remove-end:
        LangsmithClient langsmith = LangsmithOkHttpClient.fromEnv();
        OpenAIClient openai = OpenAIOkHttpClient.fromEnv();
        ExecutorService executor = Executors.newSingleThreadExecutor();

        try {
            String question = "Can you summarize this morning's meetings?";
            String runId = "01990f3e-7f97-74c5-a9b6-8d3f7e8e2f11";

            RunTree pipeline = RunTree.builder()
                .id(runId)
                .name("Chat Pipeline")
                .runType(RunType.CHAIN)
                .inputs(Collections.singletonMap("question", question))
                .client(langsmith)
                .executor(executor)
                .build();
            pipeline.postRun();

            String context = "During this morning's meeting, we solved all world conflict.";
            List<ChatCompletionMessageParam> messages = Arrays.asList(
                ChatCompletionMessageParam.ofSystem(
                    ChatCompletionSystemMessageParam.builder()
                        .content(
                            "You are a helpful assistant. Please respond to the user's " +
                                "request only based on the given context.")
                        .build()),
                ChatCompletionMessageParam.ofUser(
                    ChatCompletionUserMessageParam.builder()
                        .content("Question: " + question + "\nContext: " + context)
                        .build()));

            RunTree childRun = pipeline.createChild(
                TraceConfig.builder().name("OpenAI Call").runType(RunType.LLM).build());
            childRun.setInputs(Collections.singletonMap("messages", messages));
            childRun.postRun();

            ChatCompletion chatCompletion = openai.chat().completions().create(
                ChatCompletionCreateParams.builder()
                    .model(ChatModel.GPT_5_CHAT_LATEST)
                    .messages(messages)
                    .build());

            String answer = chatCompletion.choices().get(0).message().content().orElse("");
            System.out.println(answer);

            childRun.setOutputs(Collections.singletonMap("response", chatCompletion.toString()));
            childRun.setEndTime(Instant.now().toString());
            childRun.patchRun();

            pipeline.setOutputs(Collections.singletonMap(
                "answer", answer));
            pipeline.setEndTime(Instant.now().toString());
            pipeline.patchRun();
        } finally {
            executor.shutdown();
            if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
                throw new IllegalStateException(
                    "Timed out waiting for LangSmith traces to submit");
            }
        }
    }
}

// :snippet-end:
