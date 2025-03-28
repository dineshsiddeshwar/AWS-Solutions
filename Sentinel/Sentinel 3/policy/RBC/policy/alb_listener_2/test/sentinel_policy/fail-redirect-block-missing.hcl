module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-fail-redirect-block-missing.sentinel"
  }
}

test {
    rules = {
        main = false
    }
}
