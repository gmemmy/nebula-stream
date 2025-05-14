# NebulaStream

**NebulaStream** is a lightweight, serverless pipeline that fetches cryptocurrency price data at regular intervals and makes it available for ad-hoc analysis.

## What’s being built

1. **Phase 1: Raw Ingestion**

   * A Python AWS Lambda function polls a public crypto API every five minutes.
   * Raw JSON price data is written to an encrypted S3 bucket (SSE-S3).

2. **Phase 2: Catalog & Transform**

   * AWS Glue Crawler discovers the JSON schema.
   * A Glue PySpark job converts and writes partitioned Parquet files to a staging S3 bucket.

3. **Phase 3: Query & Visualize**

   * Amazon Athena queries the Parquet data lake.
   * (Optional) Connect QuickSight or Tableau for dashboards.

## Getting Started

1. **Clone the repo** and configure your AWS credentials in `.env`.
2. **Deploy Phase 1 infra** with the CloudFormation template in `infra/`.
3. **Develop & test** the ingestion Lambda under `src/lambda/fetch_price`.
4. **Package & deploy** via the `scripts/build-lambda.sh` script or GitLab CI/CD pipeline.

## Project Layout

```text
nebula-stream/
├── infra/        # CloudFormation templates & deploy scripts
├── src/          # Lambda code (`fetch_price`)
├── scripts/      # Helper scripts (build, test, deploy)
├── data/         # Sample payloads for unit tests
└── docs/         # Architecture diagrams and notes
```

---

*Let’s build and learn together—one phase at a time!*
