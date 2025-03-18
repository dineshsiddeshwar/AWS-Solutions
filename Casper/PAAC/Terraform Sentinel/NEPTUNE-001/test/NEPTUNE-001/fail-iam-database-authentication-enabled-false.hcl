module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-fail-iam-database-authentication-enabled-false.sentinel"
  }
}

test {
    rules = {
        main = false
    }
}
