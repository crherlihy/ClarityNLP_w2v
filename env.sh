# IDENTITY PROVIDER
export ASPNETCORE_URLS=http://*:5000

# NLP API
export NLP_API_HOSTNAME=nlp-api
export NLP_API_HOST_PORT=5000
export NLP_API_CONTAINER_PORT=5000
export NLP_API_DEBUG_MODE=true
export NLP_API_THREADED=true
export NLP_API_TMP_DIR=/data/tmp
export NLP_API_LOG_DIR=/tmp
export NLP_API_URL=http://localhost:5000
export BATCH_SIZE=25
export OHDSI_WEBAPI_URL=http://api.ohdsi.org/WebAPI
export SOLR_TEXT_FIELD=report_text
export SOLR_ID_FIELD=id
export SOLR_REPORT_ID_FIELD=report_id
export SOLR_SOURCE_FIELD=source
export SOLR_REPORT_DATE_FIELD=report_date
export SOLR_SUBJECT_FIELD=subject
export SOLR_REPORT_TYPE_FIELD=report_type
export USE_MEMORY_CACHING=false
export USE_PRECOMPUTED_SEGMENTATION=false
export USE_REORDERED_NLPQL=false
export USE_REDIS_CACHING=false

# LUIGI
export SCHEDULER_HOSTNAME=scheduler
export SCHEDULER_HOST_PORT=8082
export SCHEDULER_CONTAINER_PORT=8082
export LUIGI_WORKERS=1
export LUIGI_URL=http://localhost:8082
export LUIGI_SCHEDULER_URL=http://scheduler:8082

# NLP SOLR
export NLP_SOLR_HOSTNAME=nlp-solr
export NLP_SOLR_HOST_PORT=8983
export NLP_SOLR_CONTAINER_PORT=8983
export NLP_CORE_NAME=sample
export NLP_SOLR_URL=http://nlp-solr:8983/solr/sample
export NLP_SOLR_URL_TOP_LEVEL=http://nlp-solr:8983
export SOLR_HEAP=4096m

# NLP MONGO
export NLP_MONGO_HOSTNAME=nlp-mongo
export NLP_MONGO_HOST_PORT=27017
export NLP_MONGO_CONTAINER_PORT=27017
export NLP_MONGO_DATABASE=nlp
export NLP_MONGO_WORKING_INDEX=job_id
export NLP_MONGO_WORKING_COLLECTION=pipeline_temp
export NLP_MONGO_USERNAME=admin
export NLP_MONGO_PASSWORD=password

# NLP POSTGRES
export NLP_PG_HOSTNAME=nlp-postgres
export NLP_PG_HOST_PORT=5433
export NLP_PG_CONTAINER_PORT=5432
export NLP_PG_USER=pg
export NLP_PG_PASSWORD=pg
export NLP_PG_DATABASE=clarity

# MAPPER API
export MAPPER_API_HOSTNAME=mapper-api
export MAPPER_API_HOST_PORT=1337
export MAPPER_API_CONTAINER_PORT=1337
export MAPPER_API_URL=http://mapper-api:1337/api
export MAPPER_API_KEY=3hku4mnXxY6AAzZR6a2HRYk
export MAPPER_API_INSTITUTE=1

# MAPPER CLIENT
export MAPPER_CLIENT_HOSTNAME=mapper-client
export MAPPER_CLIENT_HOST_PORT=8000
export MAPPER_CLIENT_CONTAINER_PORT=8000

#MAPPER POSTGRES
export MAPPER_PG_HOSTNAME=mapper-pg
export MAPPER_PG_HOST_PORT=5432
export MAPPER_PG_CONTAINER_PORT=5432
export MAPPER_PG_USER=sails
export MAPPER_PG_PASSWORD=sails
export MAPPER_PG_DATABASE=report-type-mapper

# INGEST API
export INGEST_API_HOSTNAME=ingest-api
export INGEST_API_HOST_PORT=1340
export INGEST_API_CONTAINER_PORT=1337
export INGEST_API_LOG_LEVEL=info

# INGEST MONGO
export INGEST_MONGO_HOSTNAME=ingest-mongo
export INGEST_MONGO_CONTAINER_NAME=INGEST_MONGO
export INGEST_MONGO_DATABASE=ingest
export INGEST_MONGO_HOST_PORT=27020
export INGEST_MONGO_CONTAINER_PORT=27017
export INGEST_MONGO_USERNAME=admin
export INGEST_MONGO_PASSWORD=password

# INGEST CLIENT
export INGEST_CLIENT_HOSTNAME=ingest-client
export INGEST_CLIENT_HOST_PORT=8500
export INGEST_CLIENT_CONTAINER_PORT=8500
export INGEST_CLIENT_CHOKIDAR_USEPOLLING=true

# REDIS
export REDIS_HOSTNAME=redis
export REDIS_HOST_PORT=6379
export REDIS_CONTAINER_PORT=6379

# MAPPER SWAGGER
export MAPPER_SWAGGER_HOSTNAME=swagger
export MAPPER_SWAGGER_API_URL=http://localhost:1337/v1/swagger.json
export MAPPER_SWAGGER_HOST_PORT=3001
export MAPPER_SWAGGER_CONTAINER_PORT=8080

# RESULTS CLIENT
export RESULTS_CLIENT_HOSTNAME=results-client
export RESULTS_CLIENT_HOST_PORT=8200
export RESULTS_CLIENT_CONTAINER_PORT=3000
export RESULTS_URL=http://localhost:8200/

# GENERIC
export BASE_URL=http://localhost
