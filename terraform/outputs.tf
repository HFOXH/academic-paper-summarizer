output "frontend_bucket" {
  value = aws_s3_bucket.frontend.id
}

output "s3_frontend_bucket" {
  value = aws_s3_bucket.frontend.id
}

output "cloudfront_url" {
  value = aws_cloudfront_distribution.main.domain_name
}

output "api_gateway_url" {
  value = aws_apigatewayv2_api.main.api_endpoint
}

output "custom_domain_url" {
  value = ""
}