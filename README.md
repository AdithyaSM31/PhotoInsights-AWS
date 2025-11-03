# Serverless Photo Gallery - AWS Project

A fully serverless web application for managing and processing photos using AWS services.

## 👥 Team Members

- **Adithya Sankar Menon** - 23BRS1079
- **Karthick Swaminathan** - 23BRS1063
- **Sambari Bhuvan** - 23BRS1189

## 🎯 Project Overview

This project demonstrates a serverless architecture using AWS services to build an automated photo gallery with AI-powered image tagging, processing, and secure user authentication.

## 🏗️ Architecture

```
User → CloudFront → S3 (Website) → API Gateway → Lambda
                                                     ↓
                                            DynamoDB + Rekognition
```

## 🔧 AWS Services Used

- **Amazon S3** - Storage and hosting
- **AWS Lambda** - Serverless compute
- **Amazon API Gateway** - REST API endpoints
- **Amazon DynamoDB** - Metadata database
- **Amazon Cognito** - User authentication
- **Amazon CloudFront** - Content delivery
- **Amazon Rekognition** - AI image analysis

## ✨ Features

- 🔐 Secure user authentication (sign up, login, password reset)
- 📤 Direct image upload to S3 with pre-signed URLs
- 🎨 Automatic image processing (resize, watermark, format conversion)
- 🤖 AI-powered tagging using Amazon Rekognition
- 🔍 Search images by tags, filename, or date
- 🖼️ Responsive photo gallery with full-screen viewer
- ⚡ Fast global content delivery via CloudFront
- 📊 Metadata storage and retrieval

## 📁 Project Structure

```
aws_da3/
├── lambda-functions/          # Lambda function code
│   ├── get-upload-url/
│   ├── process-image/
│   ├── analyze-image/
│   ├── get-images/
│   ├── delete-image/
│   └── search-images/
├── frontend/                  # Web application
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── styles/
│   └── public/
├── infrastructure/            # IaC templates (optional)
├── scripts/                   # Deployment scripts
├── docs/                      # Additional documentation
├── PROJECT_DOCUMENTATION.md   # Detailed project docs
├── GETTING_STARTED.md        # Setup guide
└── README.md                 # This file
```

## 🚀 Getting Started

### Prerequisites

- AWS Account (Free Tier eligible)
- Node.js (v18+) or Python (v3.9+)
- AWS CLI configured
- Git

### Quick Setup

1. **Clone the repository**
   ```powershell
   cd C:\Users\adith\Downloads\aws_da3
   git init
   ```

2. **Follow the setup guide**
   - Read `GETTING_STARTED.md` for detailed AWS setup instructions
   - Create S3 buckets, Cognito User Pool, DynamoDB table
   - Set up IAM roles and permissions

3. **Configure AWS resources**
   - Update `config.json` with your resource IDs
   - Deploy Lambda functions
   - Set up API Gateway

4. **Deploy frontend**
   - Build the web application
   - Upload to S3 static website bucket
   - Configure CloudFront

## 📖 Documentation

- **[Getting Started Guide](GETTING_STARTED.md)** - Step-by-step AWS setup
- **[Project Documentation](PROJECT_DOCUMENTATION.md)** - Complete technical details
- **[Lambda Functions Guide](docs/LAMBDA_FUNCTIONS_GUIDE.md)** - Function development (coming soon)
- **[Frontend Guide](docs/FRONTEND_GUIDE.md)** - UI development (coming soon)

## 🔒 Security

- All API requests require JWT authentication
- S3 buckets use server-side encryption
- IAM roles follow least privilege principle
- HTTPS enforced on all endpoints
- Input validation and sanitization

## 💰 Cost Estimation

**Within AWS Free Tier: $0 - $5/month**

- Lambda: 1M requests/month (FREE)
- S3: 5GB storage (FREE)
- DynamoDB: 25GB storage (FREE)
- Cognito: 50K MAU (FREE)
- Rekognition: 5K images/month (FREE)

## 📊 Project Timeline

- **Week 1**: AWS infrastructure setup
- **Week 2**: Backend Lambda functions
- **Week 3**: Image processing pipeline
- **Week 4**: Frontend development
- **Week 5**: CloudFront & optimization
- **Week 6**: Testing & deployment

## 🧪 Testing

```powershell
# Test AWS CLI configuration
aws sts get-caller-identity

# Test Lambda function locally (if using SAM)
sam local invoke FunctionName

# Run frontend dev server
cd frontend
npm run dev
```

## 🚀 Deployment

```powershell
# Deploy Lambda functions
cd lambda-functions
# Follow deployment scripts

# Deploy frontend
cd frontend
npm run build
aws s3 sync dist/ s3://your-website-bucket/
```

## 📝 Development Log

Track progress in `docs/DEVELOPMENT_LOG.md`

## 🤝 Contributing

Team members:
1. Fork the repository
2. Create feature branches
3. Commit changes
4. Push and create pull requests

## 📧 Contact

For questions or issues, contact any team member:
- Adithya Sankar Menon - 23BRS1079
- Karthick Swaminathan - 23BRS1063
- Sambari Bhuvan - 23BRS1189

## 📄 License

This project is for educational purposes as part of DA3 submission.

## 🙏 Acknowledgments

- AWS Documentation and Tutorials
- Course Instructor and Teaching Assistants
- Open source libraries and tools used

---

**Project Status**: 🔨 In Development

**Last Updated**: October 29, 2025
