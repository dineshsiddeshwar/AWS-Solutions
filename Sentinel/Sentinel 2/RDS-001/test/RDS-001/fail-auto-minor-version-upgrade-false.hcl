module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-fail-auto-minor-version-upgrade-false.sentinel"
  }
}

test {
    rules = {
        main = false
    }
}
