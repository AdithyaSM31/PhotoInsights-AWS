# Getting Started - Serverless Photo Gallery

## 🚀 Quick Start Guide

This guide will walk you through building the Serverless Photo Gallery from scratch.

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] **AWS Account** (with Free Tier eligible)
- [ ] **Credit/Debit Card** (for AWS account verification - won't be charged if staying in Free Tier)
- [ ] **Email Address** (for AWS notifications)
- [ ] **Text Editor/IDE** (VS Code recommended)
- [ ] **Git** installed on your computer
- [ ] **Node.js** (v18+ recommended) or **Python** (v3.9+)
- [ ] **AWS CLI** (we'll install this)
- [ ] **Basic knowledge** of JavaScript/Python, HTML, CSS

---

## Phase 1: AWS Account Setup (Day 1)

### Step 1.1: Create AWS Account

1. Go to https://aws.amazon.com/
2. Click **"Create an AWS Account"**
3. Fill in:
   - Email address
   - Password
   - AWS account name (e.g., "PhotoGalleryProject")
4. Choose **Personal** account type
5. Fill in contact information
6. Enter credit/debit card details (for verification only)
7. Verify identity via phone call/SMS
8. Choose **"Basic Support - Free"** plan
9. Wait for account activation (few minutes to hours)

### Step 1.2: Secure Your Root Account

**IMPORTANT: Never use root account for daily work!**

1. Log in to AWS Console: https://console.aws.amazon.com/
2. Click your name (top right) → **Security credentials**
3. Enable **Multi-Factor Authentication (MFA)**
   - Download Google Authenticator or Authy app
   - Scan QR code
   - Enter two consecutive MFA codes
4. Save your MFA recovery codes safely!

### Step 1.3: Set Up Billing Alerts

**Protect yourself from unexpected charges!**

1. Go to **Billing Dashboard**: https://console.aws.amazon.com/billing/
2. Click **Billing Preferences** (left sidebar)
3. Enable:
   - ✅ Receive PDF Invoice By Email
   - ✅ Receive Free Tier Usage Alerts
   - ✅ Receive Billing Alerts
4. Enter your email and **Save preferences**
5. Go to **CloudWatch** (search in top bar)
6. Change region to **US East (N. Virginia)** - us-east-1 (required for billing alarms)
7. Click **Alarms** → **Billing** → **Create Alarm**
8. Set threshold: **$5 USD**
9. Create SNS topic for notifications
10. Confirm email subscription

### Step 1.4: Create IAM Admin User

**Never use root account for development!**

1. Go to **IAM Console**: https://console.aws.amazon.com/iam/
2. Click **Users** (left sidebar) → **Add users**
3. Username: `admin-user` (or your name)
4. Check ✅ **Provide user access to the AWS Management Console**
5. Choose **I want to create an IAM user**
6. Set custom password or auto-generate
7. ❌ Uncheck "Users must create a new password at next sign-in" (optional)
8. Click **Next**
9. Choose **Attach policies directly**
10. Search and check: **AdministratorAccess**
11. Click **Next** → **Create user**
12. ⚠️ **SAVE** the console sign-in URL and password!

**Sign-in URL format:**
```
https://YOUR-ACCOUNT-ID.signin.aws.amazon.com/console
```

### Step 1.5: Install AWS CLI

**Windows (PowerShell):**
```powershell
# Download AWS CLI installer
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Verify installation
aws --version
```

**Alternative - Using winget:**
```powershell
winget install Amazon.AWSCLI
```

### Step 1.6: Create Access Keys for CLI

1. In IAM Console, click your **admin-user**
2. Go to **Security credentials** tab
3. Scroll to **Access keys**
4. Click **Create access key**
5. Choose **Command Line Interface (CLI)**
6. Check the confirmation box
7. Click **Next** → **Create access key**
8. ⚠️ **DOWNLOAD** the CSV file or copy keys immediately!
   - Access Key ID: `AKIA...`
   - Secret Access Key: `xxxxx...`
9. **DO NOT SHARE THESE KEYS!**

### Step 1.7: Configure AWS CLI

```powershell
# Configure AWS CLI with your credentials
aws configure

# You'll be prompted for:
AWS Access Key ID [None]: AKIA..................
AWS Secret Access Key [None]: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Default region name [None]: us-east-1
Default output format [None]: json
```

**Verify configuration:**
```powershell
# Test AWS CLI
aws sts get-caller-identity

# Should return your account ID and user ARN
```

---

## Phase 2: Project Structure Setup (Day 1)

### Step 2.1: Create Project Directory

```powershell
# Navigate to your Downloads folder
cd C:\Users\adith\Downloads\aws_da3

# Create project folders
New-Item -ItemType Directory -Path "lambda-functions"
New-Item -ItemType Directory -Path "frontend"
New-Item -ItemType Directory -Path "infrastructure"
New-Item -ItemType Directory -Path "scripts"
New-Item -ItemType Directory -Path "docs"

# Create subdirectories for Lambda functions
New-Item -ItemType Directory -Path "lambda-functions\get-upload-url"
New-Item -ItemType Directory -Path "lambda-functions\process-image"
New-Item -ItemType Directory -Path "lambda-functions\analyze-image"
New-Item -ItemType Directory -Path "lambda-functions\get-images"
New-Item -ItemType Directory -Path "lambda-functions\delete-image"
New-Item -ItemType Directory -Path "lambda-functions\search-images"

# Create frontend subdirectories
New-Item -ItemType Directory -Path "frontend\src"
New-Item -ItemType Directory -Path "frontend\src\components"
New-Item -ItemType Directory -Path "frontend\src\services"
New-Item -ItemType Directory -Path "frontend\src\styles"
New-Item -ItemType Directory -Path "frontend\public"
```

### Step 2.2: Initialize Git Repository

```powershell
# Initialize Git
git init

# Set up Git user
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Step 2.3: Create .gitignore

```powershell
# This will be created in the next step
```

### Step 2.4: Create README

```powershell
# README.md will be created
```

---

## Phase 3: Create S3 Buckets (Day 1-2)

### Step 3.1: Create Uploads Bucket

1. Go to **S3 Console**: https://s3.console.aws.amazon.com/s3/
2. Click **Create bucket**
3. **Bucket name:** `photogallery-uploads-[random-number]`
   - Example: `photogallery-uploads-23brs1079`
   - Must be globally unique!
4. **Region:** US East (N. Virginia) us-east-1
5. **Object Ownership:** ACLs disabled (recommended)
6. **Block Public Access:** Keep all checked ✅ (default)
7. **Versioning:** Enable
8. **Encryption:** Server-side encryption (SSE-S3)
9. Click **Create bucket**

### Step 3.2: Create Processed Images Bucket

1. Click **Create bucket**
2. **Bucket name:** `photogallery-processed-[random-number]`
3. Same settings as uploads bucket
4. Enable **Versioning** and **Encryption**
5. Click **Create bucket**

### Step 3.3: Create Website Bucket

1. Click **Create bucket**
2. **Bucket name:** `photogallery-website-[random-number]`
3. ❌ **Uncheck** "Block all public access" (website needs to be public)
4. Check the acknowledgment box
5. Enable **Versioning** and **Encryption**
6. Click **Create bucket**

### Step 3.4: Configure Website Bucket

1. Click on your **website bucket**
2. Go to **Properties** tab
3. Scroll to **Static website hosting**
4. Click **Edit**
5. Enable **Static website hosting**
6. **Index document:** `index.html`
7. **Error document:** `error.html`
8. Click **Save changes**
9. Note the **Bucket website endpoint** URL

### Step 3.5: Add Bucket Policy for Website

1. Go to **Permissions** tab
2. Scroll to **Bucket policy**
3. Click **Edit**
4. Paste this policy (replace `YOUR-BUCKET-NAME`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
    }
  ]
}
```

5. Click **Save changes**

### Step 3.6: Configure CORS for Uploads Bucket

1. Click on **uploads bucket**
2. Go to **Permissions** tab
3. Scroll to **Cross-origin resource sharing (CORS)**
4. Click **Edit**
5. Paste this CORS configuration:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["PUT", "POST", "GET"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": ["ETag"]
  }
]
```

6. Click **Save changes**
7. Repeat for **processed bucket**

### Step 3.7: Save Bucket Names

Create a file to store your bucket names:

```powershell
# We'll create a config file in the next step
```

---

## Phase 4: Set Up Amazon Cognito (Day 2)

### Step 4.1: Create User Pool

1. Go to **Cognito Console**: https://console.aws.amazon.com/cognito/
2. Click **Create user pool**
3. **Step 1: Configure sign-in experience**
   - Cognito user pool sign-in options: ✅ **Email**
   - Click **Next**

4. **Step 2: Configure security requirements**
   - Password policy: **Cognito defaults** (or customize)
   - Multi-factor authentication: **No MFA** (for simplicity)
   - Click **Next**

5. **Step 3: Configure sign-up experience**
   - Self-service sign-up: ✅ **Enable**
   - Attribute verification: ✅ **Email**
   - Required attributes: Keep **email** (already selected)
   - Click **Next**

6. **Step 4: Configure message delivery**
   - Email provider: **Send email with Cognito**
   - FROM email address: `no-reply@verificationemail.com` (default)
   - Click **Next**

7. **Step 5: Integrate your app**
   - User pool name: `PhotoGalleryUserPool`
   - Hosted UI: ❌ Don't use (we'll build custom)
   - Initial app client:
     - App client name: `PhotoGalleryWebClient`
     - Client secret: **Don't generate** (for web apps)
   - Click **Next**

8. **Step 6: Review and create**
   - Review all settings
   - Click **Create user pool**

### Step 4.2: Get User Pool Details

1. Click on your newly created user pool
2. Note down:
   - **User Pool ID**: `us-east-1_xxxxxxxxx`
   - Go to **App integration** tab
   - Click on your app client
   - Note **Client ID**: `xxxxxxxxxxxxxxxxxxxx`

### Step 4.3: Configure App Client Settings

1. In app client page, scroll to **Hosted UI settings**
2. We won't use Hosted UI, but note the settings for future

---

## Phase 5: Create DynamoDB Table (Day 2)

### Step 5.1: Create Images Table

1. Go to **DynamoDB Console**: https://console.aws.amazon.com/dynamodb/
2. Click **Create table**
3. **Table details:**
   - Table name: `PhotoGallery-Images`
   - Partition key: `userId` (String)
   - Sort key: `imageId` (String)
4. **Table settings:**
   - Choose **Default settings** (or customize)
   - Table class: **DynamoDB Standard**
5. **Read/write capacity:**
   - Capacity mode: **On-demand** (pay per request)
6. Click **Create table**

### Step 5.2: Create Global Secondary Index

1. Wait for table to be **Active** (refresh page)
2. Click on your table **PhotoGallery-Images**
3. Go to **Indexes** tab
4. Click **Create index**
5. **Index details:**
   - Partition key: `userId` (String)
   - Sort key: `uploadTimestamp` (Number)
   - Index name: `UploadTimeIndex`
6. Click **Create index**

### Step 5.3: Enable Point-in-Time Recovery (Optional)

1. Go to **Backups** tab
2. Click **Edit** under Point-in-time recovery
3. Enable **Point-in-time recovery**
4. Click **Save**

---

## Phase 6: Create IAM Roles for Lambda (Day 2-3)

### Step 6.1: Create Lambda Execution Role

1. Go to **IAM Console**: https://console.aws.amazon.com/iam/
2. Click **Roles** → **Create role**
3. **Trusted entity type:** AWS service
4. **Use case:** Lambda
5. Click **Next**
6. **Add permissions:** Search and check:
   - ✅ `AWSLambdaBasicExecutionRole` (for CloudWatch Logs)
7. Click **Next**
8. **Role name:** `PhotoGalleryLambdaRole`
9. Click **Create role**

### Step 6.2: Add Inline Policies

1. Click on **PhotoGalleryLambdaRole**
2. Go to **Permissions** tab
3. Click **Add permissions** → **Create inline policy**
4. Switch to **JSON** tab
5. Paste this policy (replace bucket names and table name):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::photogallery-uploads-*",
        "arn:aws:s3:::photogallery-uploads-*/*",
        "arn:aws:s3:::photogallery-processed-*",
        "arn:aws:s3:::photogallery-processed-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-1:*:table/PhotoGallery-Images",
        "arn:aws:dynamodb:us-east-1:*:table/PhotoGallery-Images/index/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "rekognition:DetectLabels",
        "rekognition:DetectText",
        "rekognition:DetectFaces",
        "rekognition:DetectModerationLabels"
      ],
      "Resource": "*"
    }
  ]
}
```

6. Click **Next**
7. Policy name: `PhotoGalleryLambdaPolicy`
8. Click **Create policy**

---

## Next Steps

Now you're ready to start creating Lambda functions! 

**What to do next:**
1. ✅ Verify all AWS resources are created
2. 📝 Save all IDs, ARNs, and bucket names in a config file
3. 💻 Start developing Lambda functions (next phase)

**In the next guide, we'll cover:**
- Writing Lambda functions for image processing
- Setting up API Gateway
- Building the frontend application

---

## Configuration Summary

Save this information in a safe place:

```yaml
AWS Configuration:
  Region: us-east-1
  Account ID: [Your Account ID]
  
S3 Buckets:
  Uploads: photogallery-uploads-[your-id]
  Processed: photogallery-processed-[your-id]
  Website: photogallery-website-[your-id]
  
Cognito:
  User Pool ID: us-east-1_xxxxxxxxx
  App Client ID: xxxxxxxxxxxxxxxxxxxx
  
DynamoDB:
  Table Name: PhotoGallery-Images
  
IAM:
  Lambda Role ARN: arn:aws:iam::ACCOUNT:role/PhotoGalleryLambdaRole
```

---

## Troubleshooting

### Common Issues:

**1. Bucket name already exists**
- Bucket names must be globally unique
- Add random numbers: `photogallery-uploads-123456`

**2. AWS CLI not configured**
```powershell
aws configure
# Re-enter your access keys
```

**3. Permission denied errors**
- Make sure you're using the IAM admin user, not root
- Check IAM role has correct policies

**4. Region mismatch**
- Keep everything in **us-east-1** for consistency
- Check AWS CLI default region: `aws configure get region`

---

## Cost Tracking

Monitor your usage regularly:

1. **Billing Dashboard**: https://console.aws.amazon.com/billing/
2. Check **Free Tier** usage
3. Review **Cost Explorer**
4. Ensure billing alarm is active

**Expected costs (within Free Tier): $0 - $2/month**

---

## Team Collaboration

If working as a team:

1. **Do NOT share AWS access keys!**
2. Create separate IAM users for each team member
3. Use Git for code collaboration
4. Document everything in your repository

---

## Ready to Code? 🎉

You've completed Phase 1 (AWS Setup)! Now let's build the application.

**Continue to:** `LAMBDA_FUNCTIONS_GUIDE.md` (next guide)
