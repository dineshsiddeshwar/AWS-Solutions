# Requests Lambda Layer
resource "aws_lambda_layer_version" "requests_lambda_layer" {
  filename   = "${path.module}/Layers/Payload0001_RequestsLayer/python.zip"
  layer_name = "Requests"
  description = "Requests Layer"
  skip_destroy = true
  compatible_runtimes = ["python3.8"]
}

# Cryptography Lambda Layer
resource "aws_lambda_layer_version" "cryptography_lambda_layer" {
  filename   = "${path.module}/Layers/Payload0002_CryptographyLayer/cryptography.zip"
  layer_name = "cryptography"
  description = "Cryptography Layer"
  skip_destroy = true
  compatible_runtimes = ["python3.8","python3.7","python3.9"]
}

# MSAL Lambda Layer
resource "aws_lambda_layer_version" "msal_lambda_layer" {
  filename   = "${path.module}/Layers/Payload0003_MSALLayer/msal2.zip"
  layer_name = "msal"
  description = "Microsoft Active Directory Layer"
  skip_destroy = true
  compatible_runtimes = ["python3.8","python3.7","python3.9"]
}

# PyJWT Lambda Layer
resource "aws_lambda_layer_version" "pyjwt_lambda_layer" {
  filename   = "${path.module}/Layers/Payload0004_PyJWTLayer/pyjwt.zip"
  layer_name = "pyjwt"
  description = "Java Web Tokens for Python Layer"
  skip_destroy = true
  compatible_runtimes = ["python3.8","python3.7","python3.9"]
}

# CFFI Lambda Layer
resource "aws_lambda_layer_version" "cffi_lambda_layer" {
  filename   = "${path.module}/Layers/Payload0005_CFFILayer/cffi.zip"
  layer_name = "cffi"
  description = "Java Web Tokens for Python Layer"
  skip_destroy = true
  compatible_runtimes = ["python3.8","python3.10","python3.9"]
}








