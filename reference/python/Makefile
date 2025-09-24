.PHONY: clean build

clean:
	rm -rf ../dist/python
	mkdir -p ../dist/python

build: clean
	curl -L https://github.com/langchain-ai/langchain-api-docs-html/archive/refs/heads/main.tar.gz | tar -xz --strip-components=1 -C ../dist/python
	mv ../dist/python/api_reference_build/html/* ../dist/python/
	rm -rf ../dist/python/api_reference_build
