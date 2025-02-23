IMAGE_NAME := kulasis-ai-search-exp
CONTAINER_NAME := kulasis-ai-search-exp
PORT := 8501

all: build

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run -it --rm -v C:\new\kulasis-ai-search\experiments/app -p $(PORT):$(PORT) --name $(CONTAINER_NAME) $(IMAGE_NAME) bash

unzip:
	unzip -d data/ data/raw.zip

.PHONY: all build run exec stop clean
