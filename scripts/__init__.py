# 开发环境
# python scripts/start_dev.py
#
# # 或者直接使用uvicorn
# uvicorn app.main:app --reload --env-file .env
#
# # 生产环境
# python scripts/start_prod.py
#
# # 或者使用环境变量指定配置文件
# UVICORN_ENV_FILE=.env.production uvicorn app.main:app