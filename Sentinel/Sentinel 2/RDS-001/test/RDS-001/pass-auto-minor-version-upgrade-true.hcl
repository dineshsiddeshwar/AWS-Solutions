module "tfplan-functions" {
    source = "../../common-functions/tfplan-functions/tfplan-functions.sentinel"
}

mock "tfplan/v2" {
  module {
    source = "mock-tfplan-pass-auto-minor-version-upgrade-true.sentinel"
  }
}

test {
    rules = {
        main = true
    }
}
