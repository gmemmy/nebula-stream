# NebulaStream

NebulaStream is a serverless data pipeline that collects, processes, and analyzes cryptocurrency price data in real-time. Built on AWS, it provides a scalable and cost-effective solution for cryptocurrency market data analysis.

## Overview

The pipeline consists of three main phases:

### Phase 1: Data Ingestion
- Automated collection of cryptocurrency prices (BTC, ETH, SOL) every 5 minutes
- Secure storage of raw JSON data in an encrypted S3 bucket
- Serverless architecture using AWS Lambda and EventBridge

### Phase 2: Data Processing
- Automated schema discovery using AWS Glue Crawler
- Conversion of raw JSON data to optimized Parquet format
- Partitioned storage for efficient querying
- Data quality checks and validation

### Phase 3: Data Analysis
- Interactive querying using Amazon Athena
- Real-time price monitoring and historical analysis
- Custom visualization capabilities

## Project Structure

```
nebula-stream/
├── infra/                    # Infrastructure as Code
│   └── nebula-stream.yml    # CloudFormation template
│
├── src/                      # Source code
│   └── lambda/
│       └── fetch_price/      # Data ingestion Lambda
│           ├── handler.py    # Main Lambda function
│           └── tests/        # Unit tests
│
├── scripts/                  # Build and deployment scripts
├── data/                     # Sample data and test payloads
└── docs/                     # Documentation and diagrams
```

## Data Flow

1. **Collection**: Lambda function fetches price data from crypto API
2. **Storage**: Raw JSON data stored in encrypted S3 bucket
3. **Processing**: Glue jobs transform data to Parquet format
4. **Analysis**: Athena queries enable data exploration
5. **Visualization**: Optional integration with BI tools

## Technology Stack

- **AWS Lambda**: Serverless compute
- **Amazon S3**: Data storage
- **AWS Glue**: Data processing
- **Amazon Athena**: Query engine
- **Python**: Programming language
- **CloudFormation**: Infrastructure as Code

---
