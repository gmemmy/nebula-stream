#!/usr/bin/env bash
set -euo pipefail

if [ -f ../.env ]; then
  export $(grep -v '^#' ../.env | xargs)
else
  echo ".env not found. please create one based on the .env.example file"
  exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity \
  --profile $AWS_PROFILE \
  --region $AWS_REGION \
  --query "Account" \
  --output text)

echo "Deploying NebulaStream [$ENV] in account $ACCOUNT_ID / region $AWS_REGION"

echo "Debug: Command parameters: --parameter-overrides Environment=$ENV CryptoApiKey='$CRYPTO_KEY' CryptoApiUrl=$CRYPTO_API_URL ArtifactsBucket=$ARTIFACTS_BUCKET CodeS3Key=$ENV/fetch_price.zip"

aws cloudformation deploy \
  --profile $AWS_PROFILE \
  --region $AWS_REGION \
  --stack-name nebula-stream-${ENV} \
  --template-file nebula-stream.yml \
  --parameter-overrides Environment=$ENV CryptoApiKey=$CRYPTO_KEY CryptoApiUrl=$CRYPTO_API_URL ArtifactsBucket=$ARTIFACTS_BUCKET CodeS3Key=$ENV/fetch_price.zip \
  --capabilities CAPABILITY_NAMED_IAM

echo "nebula-stream-$ENV stack deployed successfully"
  