Deprecated since version 0.0.34: Use langchain_upstage.ChatUpstage instead.


```python
import os

os.environ["SOLAR_API_KEY"] = "SOLAR_API_KEY"

from langchain_community.chat_models.solar import SolarChat
from langchain_core.messages import HumanMessage, SystemMessage

chat = SolarChat(max_tokens=1024)

messages = [
    SystemMessage(
        content="You are a helpful assistant who translates English to Korean."
    ),
    HumanMessage(
        content="Translate this sentence from English to Korean. I want to build a project of large language model."
    ),
]

chat.invoke(messages)
```



```output
AIMessage(content='저는 대형 언어 모델 프로젝트를 구축하고 싶습니다.')
```



```python

```
