# PhotoInsights - AI-Powered Photo Gallery# Serverless Photo Gallery - AWS Project



![PhotoInsights](logo.png)A fully serverless web application for managing and processing photos using AWS services.



A serverless, AI-powered photo gallery application built with AWS services. Upload photos, get automatic AI-generated tags using Amazon Rekognition, and search your photo library intelligently.



## 🌟 Features

- **🔐 Secure Authentication** - AWS Cognito user management

- **🤖 AI-Powered Tagging** - Automatic image analysis using Amazon Rekognition

  - Object & scene detection

  - Face detection and counting

  - Text extraction (OCR)This project demonstrates a serverless architecture using AWS services to build an automated photo gallery with AI-powered image tagging, processing, and secure user authentication.

  - Content moderation

- **🔍 Smart Search** - Search photos by tags, faces, text, and date

- **📱 Responsive Design** - Google Photos-inspired UI with dark mode

- **☁️ Fully Serverless** - No servers to manage```

- **🚀 CloudFront CDN** - Fast, secure HTTPS delivery worldwideUser → CloudFront → S3 (Website) → API Gateway → Lambda

- **🎨 Modern UI** - Material Design with light/dark themes                                                     ↓

                                            DynamoDB + Rekognition

## 🏗️ Architecture```



### AWS Services Used



- **S3** - Object storage for images (uploads, processed, website hosting)- **Amazon S3** - Storage and hosting

- **Lambda** - Serverless functions (6 functions)- **AWS Lambda** - Serverless compute

- **DynamoDB** - NoSQL database for metadata and tags- **Amazon API Gateway** - REST API endpoints

- **API Gateway** - RESTful API endpoints- **Amazon DynamoDB** - Metadata database

- **Cognito** - User authentication and authorization- **Amazon Cognito** - User authentication

- **Rekognition** - AI image analysis- **Amazon CloudFront** - Content delivery

- **CloudFront** - CDN for HTTPS and global delivery- **Amazon Rekognition** - AI image analysis

- **IAM** - Security and access control

## ✨ Features

## 🚀 Live Demo

- 🔐 Secure user authentication (sign up, login, password reset)

- **HTTPS URL**: https://d9qrjo3ggcl4l.cloudfront.net- 📤 Direct image upload to S3 with pre-signed URLs

- **API Endpoint**: https://fjr24hbqvb.execute-api.us-east-1.amazonaws.com/prod- 🎨 Automatic image processing (resize, watermark, format conversion)

- 🤖 AI-powered tagging using Amazon Rekognition

## 📁 Project Structure- 🔍 Search images by tags, filename, or date

- 🖼️ Responsive photo gallery with full-screen viewer

```- ⚡ Fast global content delivery via CloudFront

PhotoInsights-AWS/- 📊 Metadata storage and retrieval

├── lambda-functions/          # 6 Lambda functions

│   ├── get-upload-url/       # Pre-signed S3 URLs## 📁 Project Structure

│   ├── get-images/           # Retrieve gallery

│   ├── search-images/        # Smart search```

│   ├── delete-image/         # Delete photosaws_da3/

│   ├── process-image/        # Image processing├── lambda-functions/          # Lambda function code

│   └── analyze-image/        # AI analysis│   ├── get-upload-url/

├── frontend/                 # Web application│   ├── process-image/

│   ├── index.html           # Main UI│   ├── analyze-image/

│   ├── styles.css           # Styling│   ├── get-images/

│   ├── app.js              # Core logic│   ├── delete-image/

│   └── ui.js               # UI helpers│   └── search-images/

├── infrastructure/          # AWS configs├── frontend/                  # Web application

└── docs/                   # Documentation│   ├── src/

```│   │   ├── components/

│   │   ├── services/

## 🛠️ Technologies│   │   └── styles/

│   └── public/

- **Backend**: AWS Lambda (Python 3.11), API Gateway, DynamoDB├── infrastructure/            # IaC templates (optional)

- **Storage**: Amazon S3, CloudFront├── scripts/                   # Deployment scripts

- **AI/ML**: Amazon Rekognition├── docs/                      # Additional documentation

- **Auth**: AWS Cognito├── PROJECT_DOCUMENTATION.md   # Detailed project docs

- **Frontend**: Vanilla JavaScript, Material Design, CSS Variables├── GETTING_STARTED.md        # Setup guide

└── README.md                 # This file

## 👨‍💻 Author```



**Adithya SM**## 🚀 Getting Started

- GitHub: [@AdithyaSM31](https://github.com/AdithyaSM31)

- Email: adithyasankarmenon@gmail.com### Prerequisites



## 📝 License- AWS Account (Free Tier eligible)

- Node.js (v18+) or Python (v3.9+)

MIT License - feel free to use this project for learning and development!- AWS CLI configured

- Git

---

### Quick Setup

**⭐ Star this repository if you found it helpful!**

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

## 🙏 Acknowledgments

- AWS Documentation and Tutorials
- Open source libraries and tools used

---

**Project Status**: 🔨 In Development
