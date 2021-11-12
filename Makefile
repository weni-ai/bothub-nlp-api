init_development_env:
	@echo "${INFO}Starting init environment...${NC}"
	@echo "ENVIRONMENT=development" >> .env
	@echo "SUPPORTED_LANGUAGES=en|de|es|pt|fr|it|nl|pt_br" >> .env
	@echo "BOTHUB_ENGINE_URL=https://localhost" >> .env
	@echo "BOTHUB_SERVICE_TRAIN=celery" >> .env
	@echo "${SUCCESS}Finish...${NC}"


## Colors
SUCCESS = \033[0;32m
INFO = \033[0;36m
WARNING = \033[0;33m
DANGER = \033[0;31m
NC = \033[0m
