resource "aws_cloudfront_distribution" "cdn_alb" {
   aliases = ["qaa.proformprofessionals.com",
    "montgomerycountymd-qaa.proformprofessionals.com",
    "qaa-apilogs.proformprofessionals.com",
    "qaa-ssapi.proformprofessionals.com",
    "qaa-oauth.proformprofessionals.com",
    "meta-qaa.proformprofessionals.com",
    "csgsol-qaa.proformprofessionals.com",
    "qaa-devex.proformprofessionals.com",
    "automationcustomer-qaa.proformprofessionals.com",
    "qaa-data.proformprofessionals.com",
    "qaa-pdfconverter.proformprofessionals.com",
    "qaa-cq.proformprofessionals.com",
    "qaa-geo.proformprofessionals.com",
    "qaa-devex-utils.proformprofessionals.com",
    "mcgov-qaa.proformprofessionals.com",
    "qaa-proform-internal.proformprofessionals.com",
    "qaa-proformlicensing.proformprofessionals.com"]

   enabled = true
   is_ipv6_enabled = true
   comment         = "${var.env}-cdn_alb"
   price_class     = "PriceClass_All"

  logging_config {
    include_cookies = "false"
    bucket          = "qauatlogs.s3.amazonaws.com"
    prefix          = "qa/elbcloudfront/"
  }

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["US", "IN"]
    }
  }

  origin {
    domain_name = "mcqaprivatecontent.s3.amazonaws.com"
    origin_id   = "S3-mcqaprivatecontent"
    s3_origin_config {
      origin_access_identity = "origin-access-identity/cloudfront/EN6ZEP42M10ON"
    }
  }

  origin {
    domain_name = "qa-testresources.s3.amazonaws.com"
    origin_id   = "S3-qa-testresources"
    s3_origin_config {
      origin_access_identity = "origin-access-identity/cloudfront/E1AK9HUKN6BQWC"
    }
  }

  origin {
    domain_name = "qaproform.s3.amazonaws.com"
    origin_id   = "S3-qaproform"
    s3_origin_config {
      origin_access_identity = "origin-access-identity/cloudfront/E1S1NDM6FYF8U"
    }
  }

  origin {
    domain_name = "internalstrength.s3.amazonaws.com"
    origin_id   = "S3-internalstrength"
    s3_origin_config {
      origin_access_identity = "origin-access-identity/cloudfront/EYGVIBAESUFY3"
    }
  }

  origin {
    domain_name = "mcqa-tutorialcontent.s3.amazonaws.com"
    origin_id   = "S3-mcqa-tutorialcontent"
    s3_origin_config {
      origin_access_identity = "origin-access-identity/cloudfront/EPWQ8T9RBV1EL"
    }
  }

  origin {
    domain_name = "pfimagecontent.s3.amazonaws.com"
    origin_id   = "S3-pfimagecontent"
    
    s3_origin_config {
      origin_access_identity = "origin-access-identity/cloudfront/E3BBZ6J295YQN3"
    }
  }

  origin {
    domain_name = "qa-exercise-customreport-exports.s3.amazonaws.com"
    origin_id   = "S3-qa-exercise-customreport-exports"
    s3_origin_config {
      origin_access_identity = "origin-access-identity/cloudfront/E2TOPGHHJ1NIKA"
    }
  }

  origin {
    domain_name = "qa-template-contents.s3.amazonaws.com"
    origin_id   = "S3-qa-template-contents"
    s3_origin_config {
      origin_access_identity = "origin-access-identity/cloudfront/E167AXWBPPZ3QL"
    }
  }
  #origin {
    #domain_name = "PFAPPS-ALB-62703121.us-east-1.elb.amazonaws.com"
    #origin_id   = "PFAPPS-ALB-62703121.us-east-1.elb.amazonaws.com"
    #custom_origin_config {
      #http_port                = 80
      #https_port               = 443
      #origin_keepalive_timeout = 180
      #origin_read_timeout      = 180
      #origin_protocol_policy   = "https-only"
      #origin_ssl_protocols     = ["TLSv1"]
    #}
    #custom_header {
      #name  = "Access-Control-Allow-Origin"
      #value = "*.proformprofessionals.com"
    #}
  #}

  ###Cache behavior with precedence0*****
  ordered_cache_behavior {
    path_pattern           = "/robots.txt/*"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-internalstrength"
    viewer_protocol_policy = "allow-all"

    forwarded_values {
      query_string = false
      
            cookies {
        forward = "none"
      }
    }
  }
###Cache behavior with precedence1 ####
  ordered_cache_behavior {
    path_pattern           = "/private-content/*"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-mcqaprivatecontent"
    viewer_protocol_policy = "allow-all"
    trusted_signers        = ["self"]

    forwarded_values {
      query_string = true
     
      cookies {
        forward = "all"
      }
    }
    lambda_function_association {
      event_type = "origin-response"
      lambda_arn = "arn:aws:lambda:us-east-1:876984124922:function:UATSECURITYRESPONSE:6"
    }
  }

  # Cache behavior with precedence 2
  ordered_cache_behavior {
    path_pattern           = "custom-report-content/*"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-mcqaprivatecontent"
    viewer_protocol_policy = "allow-all"
    trusted_signers        = ["self"]

    forwarded_values {
      query_string = true
      
      cookies {
        forward = "all"
      }
    }
    lambda_function_association {
      event_type = "viewer-response"
      lambda_arn = "arn:aws:lambda:us-east-1:876984124922:function:Uatsecurity-response-x-frame-options:1"
    }
  }

  # Cache behavior with precedence 3
  ordered_cache_behavior {
    path_pattern           = "/v2/*"
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-qaproform"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    forwarded_values {
      query_string = false
      headers      = ["Origin","Access-Control-Request-Method","Access-Control-Request-Headers"]

     cookies {
        forward = "none"
      }
    }
    lambda_function_association {
      event_type = "viewer-request"
      lambda_arn = "arn:aws:lambda:us-east-1:876984124922:function:mcqaangularlatest:5"
    }

    lambda_function_association {
      event_type = "origin-response"
      lambda_arn = "arn:aws:lambda:us-east-1:876984124922:function:UATSECURITYRESPONSE:6"
    }
  }

  # Cache behavior with precedence 4
  ordered_cache_behavior {
    path_pattern           = "/customer-image-content/*"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true
    target_origin_id       = "S3-pfimagecontent"
    viewer_protocol_policy = "allow-all"

    forwarded_values {
      query_string = true
       cookies {
        forward = "all"
      }
    }
  }

  # Cache behavior with precedence 5
  ordered_cache_behavior {
    path_pattern           = "/image-content/*"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-pfimagecontent"
    compress               = true
    viewer_protocol_policy = "allow-all"

    forwarded_values {
      query_string = true
      
      cookies {
        forward = "all"
      }
    }
  }

  # Cache behavior with precedence 6
  ordered_cache_behavior {
    path_pattern           = "/test-resources/*"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-qa-testsources"
    compress               = true
    viewer_protocol_policy = "allow-all"
    trusted_signers        = ["self"]

    forwarded_values {
      query_string = true
                 
      cookies {
        forward = "all"
      }
    }
  }
  # Cache behavior with precedence 7
  ordered_cache_behavior {
    path_pattern           = "/tutorialcontent/*"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-mcqa-tutorialcontent"
    compress               = true
    viewer_protocol_policy = "allow-all"
    trusted_signers        = ["self"]

    forwarded_values {
      query_string = true
     
      cookies {
        forward = "all"
      }
    }
  }
  # Cache behavior with precedence 8
  ordered_cache_behavior {
    path_pattern           = "/exportExerciseCustomReport/*"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-qa-exercise-customreport-exports"
    compress               = true
    viewer_protocol_policy = "allow-all"
    trusted_signers        = ["self"]

    forwarded_values {
      query_string = true
   
         cookies {
        forward = "all"
      }
    }
    lambda_function_association {
      event_type = "viewer-response"
      lambda_arn = "arn:aws:lambda:us-east-1:876984124922:function:Uatsecurity-response-x-frame-options:1"
    }
  }
  # Cache behavior with precedence 9
  ordered_cache_behavior {
    path_pattern           = "/template-content/*"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-qa-template-contents"
    compress               = true
    viewer_protocol_policy = "allow-all"
    trusted_signers        = ["self"]

    forwarded_values {
      query_string = true
      
      cookies {
        forward = "all"
      }
    }
  }
  # Cache behavior with precedence 10
  ordered_cache_behavior {
    path_pattern           = "/exerciseComparisonReport/*"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-qa-exercise-customreport-exports"
    compress               = true
    viewer_protocol_policy = "allow-all"
    trusted_signers        = ["self"]

    forwarded_values {
      query_string = true
      
      cookies {
        forward = "all"
      }
    }
    lambda_function_association {
      event_type = "viewer-response"
      lambda_arn = "arn:aws:lambda:us-east-1:876984124922:function:Uatsecurity-response-x-frame-options:1"
    }
  }
  # Cache behavior with precedence 11
  ordered_cache_behavior {
    path_pattern           = "/job-custom-report/*"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-qa-exercise-customreport-exports"
    compress               = true
    viewer_protocol_policy = "allow-all"
    trusted_signers        = ["self"]


    forwarded_values {
      query_string = true
                     
      cookies {
        forward = "all"
      }
    }
    lambda_function_association {
      event_type = "viewer-response"
      lambda_arn = "arn:aws:lambda:us-east-1:876984124922:function:Uatsecurity-response-x-frame-options:1"
    }
  }
  # Cache behavior with precedence 12
   default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-qa-exercise-customreport-exports"
    compress               = true
    viewer_protocol_policy = "allow-all"
    trusted_signers        = ["self"]

    forwarded_values {
      query_string = true
      
      cookies {
        forward = "all"
      }
    }
    lambda_function_association {
      event_type = "viewer-response"
      lambda_arn = "arn:aws:lambda:us-east-1:876984124922:function:Uatsecurity-response-x-frame-options:1"
    }
  }
  # Cache behavior with precedence 13
  #default_cache_behavior {
    #allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    #cached_methods         = ["GET", "HEAD"]
    #target_origin_id       = "PFAPPS-ALB-62703121.us-east-1.elb.amazonaws.com"
    #compress               = false
    #viewer_protocol_policy = "allow-all"

    #forwarded_values {
      #query_string = true
      #headers      = ["*"]

      #cookies {
        #forward = "all"
      #}
    #}
  #}

  viewer_certificate {
    cloudfront_default_certificate = false
    acm_certificate_arn            = "arn:aws:acm:us-east-1:876984124922:certificate/3ab0a1b2-25bc-4c0f-9446-97cae8321d8a"
    ssl_support_method             = "sni-only"
    minimum_protocol_version       = "TLSv1.2_2018"
  }
}
