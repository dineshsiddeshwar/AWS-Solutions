package wiz

default result = "pass"


days_30_ns := time.parse_duration_ns("720h")             # 30 days

result = "fail" {
	time.parse_rfc3339_ns(input.ValidTo) - time.parse_rfc3339_ns(input.CreationDate) < days_30_ns
    }
    
  ## Expiry time minus the Creation time less than 30 days will result into fail.
  ## Expiry time minus the Creation time more than 30 days will result into pass.