module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-fail-action-iam-all-effect-allow-multiple-statements.sentinel"
  }
}

test {
    rules = {
        main = false
    }
}
