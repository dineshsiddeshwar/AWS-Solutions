module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-pass-iam-database-authentication-enabled-true.sentinel"
  }
}

test {
    rules = {
        main = true
    }
}
