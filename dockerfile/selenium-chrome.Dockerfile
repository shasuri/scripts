# Dockerfile for gathering image from google with Selenium-Chrome

FROM selenium/standalone-chrome:latest
RUN pip3 install selenium && \
	rm -rf /var/lib/apt/lists/*
