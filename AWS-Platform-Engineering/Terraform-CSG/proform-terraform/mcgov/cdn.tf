resource "aws_cloudfront_distribution" "s3_cdn" {
  aliases = ["apex-qaa-content.proformprofessionals.com",
    "earthnetworks-qaa-content.proformprofessionals.com",
    "thewashingtonhome-qaa-content.proformprofessionals.com",
    "meta-qaa-content.proformprofessionals.com",
    "montgomerycountymd-qaa-content.proformprofessionals.com",
    "mcgov-qaa-content.proformprofessionals.com",
    "qaa-content.proformprofessionals.com",
    "guggenheiminvestments-qaa-content.proformprofessionals.com",
    "mufg-qaa-content.proformprofessionals.com",
    "csgsol-qaa-content.proformprofessionals.com",
    "cobbsystemsgroup-qaa-content.proformprofessionals.com",
    "kaila-qaa-content.proformprofessionals.com",
    "ampit-qaa-content.proformprofessionals.com",
    "bosch-qaa-content.proformprofessionals.com",
    "qss-qaa-content.proformprofessionals.com",
    "bitsight-qaa-content.proformprofessionals.com"]

  enabled         = true
  comment         = "${var.env}-s3cdn"
  is_ipv6_enabled = true
  price_class     = "PriceClass_200"
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  logging_config {
    include_cookies = "false"
    bucket          = "qauatlogs.s3.amazonaws.com"
    prefix          = "qa/s3cloudfront"
  }

  origin {
    domain_name = "qaproform.s3.amazonaws.com"
    origin_id   = "S3-qaproform"

    s3_origin_config {
      origin_access_identity = "origin-access-identity/cloudfront/E1S1NDM6FYF8U"
    }
  }
  # Cache behavior 
  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-qaproform"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    forwarded_values {
      query_string = false
      headers      = ["Origin", "Access-Control-Request-Headers", "Access-Control-Request-Method"]

      cookies {
        forward = "none"
      }
    }

    lambda_function_association {
      event_type = "origin-response"
      lambda_arn = "arn:aws:lambda:us-east-1:876984124922:function:UATSECURITYRESPONSES3:13"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = false
    acm_certificate_arn            = "arn:aws:acm:us-east-1:876984124922:certificate/3ab0a1b2-25bc-4c0f-9446-97cae8321d8a"
    ssl_support_method             = "sni-only"
    minimum_protocol_version       = "TLSv1.1_2016"
  }

}