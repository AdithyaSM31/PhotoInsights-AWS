# Creating Pillow Lambda Layer

## Step 1: Create directory structure
```powershell
mkdir C:\Users\adith\Downloads\aws_da3\lambda-layers\pillow\python
cd C:\Users\adith\Downloads\aws_da3\lambda-layers\pillow
```

## Step 2: Install Pillow into the layer directory
```powershell
pip install --target python Pillow
```

## Step 3: Package the layer
```powershell
Compress-Archive -Path python -DestinationPath pillow-layer.zip -Force
```

## Step 4: Upload to AWS Lambda
```powershell
aws lambda publish-layer-version `
  --layer-name pillow-python311 `
  --description "Pillow (PIL) library for Python 3.11" `
  --zip-file fileb://pillow-layer.zip `
  --compatible-runtimes python3.11
```

This will return a Layer ARN that we'll use in the ProcessImage Lambda function.
