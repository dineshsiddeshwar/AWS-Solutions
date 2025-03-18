module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-fail-action-all-effect-allow-2.sentinel"
  }
}

test {
    rules = {
        main = false
    }
}
