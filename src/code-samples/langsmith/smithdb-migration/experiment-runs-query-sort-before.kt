///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.13

// :snippet-start: experiment-runs-query-sort-before-kt
// :codegroup-tab: Before
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.datasets.runs.RunQueryParams
import com.langchain.smith.models.datasets.runs.SortParamsForRunsComparisonView

// :remove-start:
fun main() {
    if (false) {
// :remove-end:
// :remove-start:
val datasetId = "00000000-0000-0000-0000-000000000000"
val experimentId = "00000000-0000-0000-0000-000000000001"
// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()
val examplesWithRuns = client.datasets().runs().query(
    datasetId,
    RunQueryParams.builder()
        .addSessionId(experimentId)
        .sortParams(
            SortParamsForRunsComparisonView.builder()
                .sortBy("correctness")
                .sortOrder(SortParamsForRunsComparisonView.SortOrder.ASC)
                .build()
        )
        .build()
)
// :remove-start:
    }
}
// :remove-end:
// :snippet-end:
