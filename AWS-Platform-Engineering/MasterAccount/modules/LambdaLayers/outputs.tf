# Requests Lambda Layer
output "requests_lambda_layer_arn" {
  value = aws_lambda_layer_version.requests_lambda_layer.arn
}

# Cryptography Lambda Layer
output "cryptography_lambda_layer_arn" {
  value = aws_lambda_layer_version.cryptography_lambda_layer.arn
}

# MSAL Lambda Layer
output "msal_lambda_layer_arn" {
  value = aws_lambda_layer_version.msal_lambda_layer.arn
}


# PyJWT Lambda Layer
output "pyjwt_lambda_layer_arn" {
  value = aws_lambda_layer_version.pyjwt_lambda_layer.arn
}

# CFFI Lambda Layer
output "cffi_lambda_layer_arn" {
  value = aws_lambda_layer_version.cffi_lambda_layer.arn
}