module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-pass-s3-acl-private.sentinel"
  }
}

test {
    rules = {
        main = true
    }
}
