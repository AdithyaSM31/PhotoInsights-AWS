# Step-by-Step: Billing Alerts & IAM Admin User Setup

**Date:** November 3, 2025  
**Status:** ✅ AWS Account Created → Now Setting Up Security

---

## 🚨 Part 1: Set Up Billing Alerts ($5 Threshold)

### Why This Is Important?
Billing alerts protect you from unexpected charges. You'll receive an email when your AWS bill exceeds $5.

---

### Step 1.1: Enable Billing Alerts in Billing Console

1. **Log in to AWS Console** as **root user**
   - Go to: https://console.aws.amazon.com/
   - Use your root account email and password

2. **Navigate to Billing Dashboard**
   - Click your **account name** (top-right corner)
   - Select **"Billing and Cost Management"** from dropdown
   - OR directly go to: https://console.aws.amazon.com/billing/

3. **Enable Billing Preferences**
   - In the left sidebar, click **"Billing preferences"**
   - You'll see three checkboxes:
   
   ✅ **Check ALL three boxes:**
   - ✅ **Receive PDF Invoice By Email**
   - ✅ **Receive Free Tier Usage Alerts**
   - ✅ **Receive Billing Alerts**

4. **Enter Email Address**
   - Enter your email where you want to receive alerts
   - Click **"Save preferences"**

5. **Verify Email** (if prompted)
   - Check your inbox for verification email
   - Click the verification link

---

### Step 1.2: Create CloudWatch Billing Alarm

**Important:** Billing alarms MUST be created in **US East (N. Virginia)** region!

1. **Switch to US East (N. Virginia) Region**
   - Top-right corner, click the region dropdown
   - Select **"US East (N. Virginia)"** (us-east-1)
   - ⚠️ This is mandatory for billing alarms!

2. **Open CloudWatch Console**
   - In the search bar (top), type: **CloudWatch**
   - Click **"CloudWatch"** from results
   - OR go to: https://console.aws.amazon.com/cloudwatch/

3. **Navigate to Alarms**
   - In left sidebar, click **"Alarms"**
   - Click **"All alarms"** (if not already selected)

4. **Create Billing Alarm**
   - Click orange **"Create alarm"** button

5. **Select Metric**
   - Click **"Select metric"**
   - Click **"Billing"** category
   - Click **"Total Estimated Charge"**
   - ✅ Check the box next to **"EstimatedCharges"** (USD)
   - Click **"Select metric"** (bottom-right)

6. **Configure Metric Conditions**
   ```
   Metric name: EstimatedCharges
   Statistic: Maximum
   Period: 6 hours
   ```

   **Conditions:**
   - Threshold type: **Static**
   - Whenever EstimatedCharges is: **Greater** (choose from dropdown)
   - than: **5** (enter the number 5)
   
   Click **"Next"**

7. **Configure Actions (SNS Notification)**
   
   **Alarm state trigger:** Select **"In alarm"**
   
   **Send notification to:**
   - Select **"Create new topic"**
   - **Topic name:** `BillingAlertTopic`
   - **Email endpoint:** Enter your email address
   - Click **"Create topic"**
   
   Click **"Next"**

8. **Add Alarm Name**
   - **Alarm name:** `BillingAlert-5USD`
   - **Alarm description:** `Alert when AWS charges exceed $5`
   
   Click **"Next"**

9. **Preview and Create**
   - Review all settings
   - Click **"Create alarm"**

10. **Confirm Email Subscription** ⚠️ IMPORTANT!
    - Check your email inbox
    - Look for email from: **AWS Notifications**
    - Subject: "AWS Notification - Subscription Confirmation"
    - Click **"Confirm subscription"** link in the email
    - You should see a success page

11. **Verify Alarm Status**
    - Go back to CloudWatch Alarms page
    - Your alarm should show status: **OK** (green)
    - If it says "Insufficient data", wait a few minutes

---

## 👤 Part 2: Create IAM Admin User

### Why This Is Important?
**NEVER use root account for daily work!** Root has unlimited power. Create an admin user with MFA protection.

---

### Step 2.1: Navigate to IAM Console

1. **Search for IAM**
   - In AWS Console search bar (top), type: **IAM**
   - Click **"IAM"** from results
   - OR go to: https://console.aws.amazon.com/iam/

2. **You should see IAM Dashboard**
   - Shows security recommendations
   - Shows number of users, groups, roles

---

### Step 2.2: Create IAM User

1. **Click "Users" in Left Sidebar**
   - Under "Access management", click **"Users"**

2. **Add New User**
   - Click orange **"Add users"** or **"Create user"** button

3. **Step 1: Specify User Details**
   
   **User name:** `admin-user` (or `adithya-admin`, your choice)
   
   **Provide user access to AWS Management Console:**
   - ✅ Check this box
   
   **Select:** **"I want to create an IAM user"**
   
   **Console password:**
   - Choose **"Custom password"**
   - Enter a strong password (save it somewhere safe!)
   - Example: `PhotoGallery@2025!Admin`
   
   **Users must create new password at next sign-in:**
   - ❌ Uncheck this (so you can use the password immediately)
   - OR ✅ Check if you want to change password on first login
   
   Click **"Next"**

4. **Step 2: Set Permissions**
   
   Select: **"Attach policies directly"**
   
   **Search for policies:**
   - In the search box, type: `AdministratorAccess`
   - ✅ Check the box next to **"AdministratorAccess"**
   - This gives full admin access (safe for your IAM user with MFA)
   
   Click **"Next"**

5. **Step 3: Review and Create**
   
   Review the details:
   - User name: admin-user
   - Console access: Yes
   - Permissions: AdministratorAccess
   
   Click **"Create user"**

6. **⚠️ SAVE CREDENTIALS IMMEDIATELY!**
   
   You'll see a success page with:
   - **Console sign-in URL:** `https://YOUR-ACCOUNT-ID.signin.aws.amazon.com/console`
   - **User name:** admin-user
   - **Console password:** (the password you set)
   
   **IMPORTANT ACTIONS:**
   
   **Option 1:** Download .csv file
   - Click **"Download .csv file"** button
   - Save it in a secure location
   
   **Option 2:** Copy credentials manually
   - Copy the sign-in URL
   - Copy username
   - You already know the password
   
   **Save this information in a text file:**
   ```
   AWS IAM Admin User Credentials
   ===============================
   Console Sign-in URL: https://123456789012.signin.aws.amazon.com/console
   Username: admin-user
   Password: PhotoGallery@2025!Admin
   
   ⚠️ KEEP THIS SECURE! DO NOT SHARE!
   ```

7. **Click "Return to users list"**

---

### Step 2.3: Enable MFA for IAM User (Recommended)

1. **Click on Your New User**
   - In the users list, click **"admin-user"**

2. **Go to Security Credentials Tab**
   - Click **"Security credentials"** tab

3. **Scroll to "Multi-factor authentication (MFA)"**
   - Click **"Assign MFA device"**

4. **Choose Device Type**
   - Select **"Authenticator app"**
   - Click **"Next"**

5. **Set Up Authenticator App**
   - Open your authenticator app (Google Authenticator, Authy, Microsoft Authenticator)
   - Click **"Show QR code"** on AWS page
   - Scan the QR code with your app
   
   **Enter Two Consecutive MFA Codes:**
   - MFA code 1: (enter code from app)
   - Wait 30 seconds for new code
   - MFA code 2: (enter new code)
   
   Click **"Add MFA"**

6. **Success!**
   - You'll see MFA device assigned
   - Device name will be shown

---

### Step 2.4: Create Access Keys for AWS CLI

**Still in the admin-user Security credentials tab:**

1. **Scroll to "Access keys" Section**
   - Click **"Create access key"**

2. **Select Use Case**
   - Choose **"Command Line Interface (CLI)"**
   - ✅ Check the confirmation box: "I understand..."
   - Click **"Next"**

3. **Set Description (Optional)**
   - Description tag: `Local development CLI`
   - Click **"Create access key"**

4. **⚠️ SAVE ACCESS KEYS IMMEDIATELY!**
   
   You'll see:
   - **Access key ID:** `AKIAIOSFODNN7EXAMPLE`
   - **Secret access key:** `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`
   
   **IMPORTANT - THIS IS YOUR ONLY CHANCE TO SEE THE SECRET KEY!**
   
   **Option 1:** Download .csv file
   - Click **"Download .csv file"**
   - Save securely (you'll need this for AWS CLI)
   
   **Option 2:** Copy both keys to a secure file
   ```
   AWS CLI Access Keys
   ===================
   Access Key ID: AKIAIOSFODNN7EXAMPLE
   Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   
   ⚠️ NEVER COMMIT TO GIT! NEVER SHARE!
   ```

5. **Click "Done"**

---

### Step 2.5: Test IAM User Login

1. **Sign Out from Root Account**
   - Click your name (top-right)
   - Click **"Sign out"**

2. **Sign In with IAM User**
   - Go to your saved console sign-in URL
   - Example: `https://123456789012.signin.aws.amazon.com/console`
   - Enter username: `admin-user`
   - Enter password: (your password)
   - Enter MFA code if enabled
   - Click **"Sign in"**

3. **Success!**
   - You should now be logged in as IAM user
   - Top-right should show: `admin-user @ your-account-alias`

---

## 🔧 Part 3: Configure AWS CLI with IAM User

Now that you have your IAM user and access keys, let's configure AWS CLI.

### Step 3.1: Install AWS CLI (if not done)

**Check if already installed:**
```powershell
aws --version
```

**If not installed, install it:**
```powershell
# Using winget (Windows 10/11)
winget install Amazon.AWSCLI

# OR download installer
# Go to: https://awscli.amazonaws.com/AWSCLIV2.msi
# Run the installer
```

**Verify installation:**
```powershell
aws --version
# Should show: aws-cli/2.x.x ...
```

---

### Step 3.2: Configure AWS CLI

```powershell
# Run configuration command
aws configure

# You'll be prompted for 4 values:
```

**Prompts and Your Responses:**

```
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
(paste your Access Key ID from the CSV file)

AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
(paste your Secret Access Key from the CSV file)

Default region name [None]: us-east-1
(type: us-east-1)

Default output format [None]: json
(type: json)
```

---

### Step 3.3: Test AWS CLI Configuration

```powershell
# Test 1: Get your identity
aws sts get-caller-identity
```

**Expected Output:**
```json
{
    "UserId": "AIDAIOSFODNN7EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/admin-user"
}
```

✅ If you see your account number and "admin-user" ARN, you're successful!

```powershell
# Test 2: List S3 buckets (should return empty or existing buckets)
aws s3 ls
```

```powershell
# Test 3: Get current region
aws configure get region
# Should return: us-east-1
```

---

## ✅ Verification Checklist

Check off each item as you complete:

### Billing Alerts
- [ ] Logged in as root user
- [ ] Enabled billing preferences (all 3 checkboxes)
- [ ] Created CloudWatch billing alarm in us-east-1
- [ ] Set threshold to $5 USD
- [ ] Created SNS topic for notifications
- [ ] Confirmed email subscription
- [ ] Alarm status shows "OK" in CloudWatch

### IAM Admin User
- [ ] Created IAM user: `admin-user`
- [ ] Granted AdministratorAccess policy
- [ ] Saved console sign-in URL
- [ ] Saved username and password
- [ ] Enabled MFA for IAM user (recommended)
- [ ] Created access keys for CLI
- [ ] Downloaded/saved access key CSV file
- [ ] Tested IAM user login in console
- [ ] Never using root account for daily work

### AWS CLI
- [ ] AWS CLI installed
- [ ] Configured with `aws configure`
- [ ] Used IAM user access keys (not root)
- [ ] Set default region to us-east-1
- [ ] Tested with `aws sts get-caller-identity`
- [ ] Verified correct user ARN returned

---

## 🎯 What You Should Have Now

### Saved Credentials File (store securely, NOT in Git!)

Create a file: `C:\Users\adith\Documents\aws-credentials.txt`

```
===========================================
AWS PhotoGallery Project Credentials
===========================================

ROOT ACCOUNT (USE ONLY FOR ACCOUNT MANAGEMENT)
----------------------------------------------
Email: your-root-email@example.com
Password: [Your Root Password]
MFA Device: [Optional if enabled]

IAM ADMIN USER (USE FOR DAILY WORK)
------------------------------------
Console Sign-in URL: https://123456789012.signin.aws.amazon.com/console
Username: admin-user
Password: PhotoGallery@2025!Admin
MFA Device: [If enabled]

AWS CLI ACCESS KEYS (IAM USER)
------------------------------
Access Key ID: AKIAIOSFODNN7EXAMPLE
Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

AWS ACCOUNT INFO
----------------
Account ID: 123456789012
Default Region: us-east-1
Billing Alert: $5 USD
Billing Email: your-email@example.com

⚠️ SECURITY NOTES:
- NEVER commit this file to Git
- NEVER share these credentials
- NEVER post in forums/Discord
- Use IAM user for all development
- Only use root for account/billing issues
===========================================
```

---

## 🚨 Security Best Practices

### DO:
✅ Use IAM admin user for all development work
✅ Enable MFA on both root and IAM accounts
✅ Rotate access keys every 90 days
✅ Monitor billing dashboard weekly
✅ Use strong, unique passwords
✅ Store credentials securely (password manager)

### DON'T:
❌ Use root account for daily work
❌ Share access keys with anyone
❌ Commit credentials to Git
❌ Disable billing alerts
❌ Use same password across services
❌ Leave access keys in code

---

## 🆘 Troubleshooting

### Issue 1: Can't Find Billing Dashboard
**Solution:** Make sure you're logged in as root user. IAM users may need billing permissions.

### Issue 2: CloudWatch Billing Alarm Not Available
**Solution:** Ensure you're in **us-east-1** region. Billing metrics only available there.

### Issue 3: Didn't Receive SNS Confirmation Email
**Solution:** 
- Check spam folder
- Verify email address is correct
- Wait 5-10 minutes
- Recreate SNS topic if needed

### Issue 4: AWS CLI Says "Invalid Credentials"
**Solution:**
- Re-run `aws configure`
- Verify access keys are copied correctly (no spaces)
- Ensure using IAM user keys, not root

### Issue 5: Can't Create Access Keys
**Solution:** 
- Each IAM user can have max 2 access keys
- Delete old keys if you have 2 already

---

## 📊 Current Progress

```
✅ AWS Account Created
✅ Billing Alerts Set Up ($5 threshold)
✅ IAM Admin User Created
✅ AWS CLI Configured
⏭️ NEXT: Create Project Structure
⏭️ NEXT: Create S3 Buckets
```

---

## 🎯 Next Steps

Once you complete this guide:

1. **Update config.json:**
   ```json
   {
     "aws": {
       "region": "us-east-1",
       "accountId": "123456789012"  // ← Add your account ID here
     }
   }
   ```

2. **Verify Git Setup:**
   ```powershell
   cd C:\Users\adith\Downloads\aws_da3
   git status
   ```

3. **Create Project Folders:**
   ```powershell
   # Run the folder creation commands from README.md
   ```

4. **Tell me:** "Completed billing alerts and IAM user setup, ready for S3 buckets!"

---

## 📞 Need Help?

If you get stuck:
1. Take a screenshot of the error
2. Note which step you're on
3. Ask me for help with specific details

**Common questions welcome:**
- "Where do I find my account ID?"
- "How do I know if MFA is working?"
- "Can't find billing preferences"
- "AWS CLI not recognizing commands"

---

**Document Status:** ✅ Complete  
**Last Updated:** November 3, 2025  
**Next Guide:** S3 Buckets Setup
