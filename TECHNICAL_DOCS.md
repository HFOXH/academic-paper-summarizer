# PaperAI - Technical Documentation

AI-powered academic research paper analyzer that transforms complex research into clear, structured insights.

## Project Overview

PaperAI accepts research paper text and generates structured analysis including:
- Plain Language Summary
- Key Findings & Methodology
- Critical Analysis & Follow-up Questions

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│  API Gateway│────▶│   Lambda    │
│  (Next.js)  │     │   (AWS)     │     │  (FastAPI)  │
└─────────────┘     └─────────────┘     └─────────────┘
                                            │
                                            ▼
                                     ┌─────────────┐
                                     │  OpenAI API │
                                     └─────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| Authentication | Clerk (Next.js SDK v6) |
| Backend | FastAPI, Python 3.12 |
| AI | OpenAI GPT-4o-mini |
| Infrastructure | AWS Lambda, API Gateway, S3, CloudFront, Terraform |
| CI/CD | GitHub Actions |

## Project Structure

```
twin/
├── backend/                 # FastAPI backend
│   ├── server.py           # Main application
│   ├── lambda_handler.py   # AWS Lambda entry point
│   ├── deploy.py          # Deployment script
│   ├── requirements.txt   # Python dependencies
│   └── tests/
│       └── test_api.py    # API tests
├── frontend/               # Next.js frontend
│   ├── app/
│   │   ├── page.tsx       # Landing page
│   │   ├── analyze/       # Analysis tool page
│   │   ├── layout.tsx     # Root layout
│   │   └── globals.css    # Global styles
│   ├── components/
│   │   └── PaperTool.tsx  # Main analysis component
│   └── package.json
├── terraform/              # Infrastructure as Code
│   ├── main.tf            # Main resources
│   ├── variables.tf       # Input variables
│   ├── outputs.tf         # Output values
│   └── versions.tf        # Provider versions
├── scripts/               # Deployment scripts
│   ├── deploy.sh         # Unix deployment
│   └── deploy.ps1        # Windows deployment
└── workflows/
    └── ci.yml            # GitHub Actions CI
```

## Backend API

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/analyze` | Analyze a research paper |
| GET | `/health` | Health check |

### Analyze Request

```json
{
  "paper_title": "string (required, 10-300 chars)",
  "paper_text": "string (required, 100-5000 chars)",
  "research_field": "string",
  "target_audience_level": "undergraduate | graduate | expert",
  "session_id": "string (optional)"
}
```

### Analyze Response

```json
{
  "response": "string (markdown)",
  "session_id": "string"
}
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `OPENAI_MODEL` | Model name (default: `gpt-4o-mini`) | No |
| `CORS_ORIGINS` | Allowed CORS origins | No |
| `USE_S3` | Enable S3 memory storage | No |
| `S3_BUCKET` | S3 bucket name | No |

## Frontend Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://127.0.0.1:8000` |

## Infrastructure (AWS)

### Resources Created

- **Lambda Function**: Python 3.12 runtime, handles API requests
- **API Gateway**: HTTP API with CORS support
- **S3 Bucket (memory)**: Stores conversation history
- **S3 Bucket (frontend)**: Hosts static Next.js build
- **CloudFront Distribution**: CDN with SSL, serves frontend

### Optional Resources

- **ACM Certificate**: For custom domain HTTPS
- **Route53 Records**: DNS configuration for custom domain

### Deployment

```bash
cd terraform
terraform init
terraform apply -var="project_name=paperai" -var="environment=prod" -var="openai_api_key=YOUR_KEY"
```

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Deployment

### Prerequisites

- AWS credentials configured
- OpenAI API key
- Terraform >= 1.0
- Node.js >= 18

### Steps

1. Build frontend: `cd frontend && npm run build`
2. Package backend: `cd backend && python deploy.py`
3. Deploy infrastructure: `cd terraform && terraform apply`
4. Upload frontend: Sync build output to S3 frontend bucket

## Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Lint (Frontend)

```bash
cd frontend
npm run lint
```

## Security

- API Gateway throttling: 5 req/s, burst 10
- S3 buckets: Private with public read policy only for frontend
- CloudFront: HTTPS enforced (redirect-to-https)
- Environment variables: Stored in AWS Lambda, marked sensitive in Terraform
- Authentication: Clerk handles user authentication

## Dependencies

### Backend

```
fastapi
uvicorn
python-dotenv
python-multipart
boto3
pypdf
mangum
openai
pytest
```

### Frontend

```
next: 16.2.1
react: 19.2.4
@clerk/nextjs: ^6.39.0
lucide-react: ^0.577.0
react-markdown: ^10.1.0
tailwindcss: ^4
```